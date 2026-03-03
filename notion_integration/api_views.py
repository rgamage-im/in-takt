"""
Notion API endpoints.
"""
from datetime import datetime, timezone
import logging
import time
import uuid
import hashlib
import threading
import requests

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes
from django.utils.dateparse import parse_datetime
from django.conf import settings
from django.utils import timezone as django_timezone
from django.db import close_old_connections

from .models import NotionContent, NotionSyncJob
from .services import NotionService

RAG_API_TIMEOUT = 90


def _property_to_text(prop: dict) -> str:
    if not isinstance(prop, dict):
        return ""
    prop_type = prop.get("type")

    if prop_type in {"title", "rich_text"}:
        parts = prop.get(prop_type, [])
        return "".join(p.get("plain_text", "") for p in parts).strip()
    if prop_type == "select":
        selected = prop.get("select")
        return selected.get("name", "") if selected else ""
    if prop_type == "multi_select":
        selected = prop.get("multi_select", [])
        return ", ".join(item.get("name", "") for item in selected if item.get("name"))
    if prop_type == "number":
        number = prop.get("number")
        return "" if number is None else str(number)
    if prop_type == "checkbox":
        return str(bool(prop.get("checkbox")))
    if prop_type == "url":
        return prop.get("url", "") or ""
    if prop_type == "email":
        return prop.get("email", "") or ""
    if prop_type == "phone_number":
        return prop.get("phone_number", "") or ""
    if prop_type == "date":
        date_val = prop.get("date")
        if not date_val:
            return ""
        start = date_val.get("start", "")
        end = date_val.get("end", "")
        return f"{start} - {end}".strip(" -")
    if prop_type == "status":
        status_val = prop.get("status")
        return status_val.get("name", "") if status_val else ""

    return ""


def _get_database_rows_text(notion: NotionService, database_id: str) -> str:
    lines = []
    cursor = None

    while True:
        response = notion.query_database(database_id=database_id, page_size=100, start_cursor=cursor)
        rows = response.get("results", [])
        for row in rows:
            row_title = notion.extract_title(row)
            properties = row.get("properties", {})
            property_parts = []
            for key, value in properties.items():
                text_value = _property_to_text(value)
                if text_value:
                    property_parts.append(f"{key}: {text_value}")

            if property_parts:
                lines.append(f"{row_title or row.get('id')}: " + " | ".join(property_parts))
            elif row_title:
                lines.append(row_title)

        if not response.get("has_more"):
            break
        cursor = response.get("next_cursor")
        if not cursor:
            break

    return "\n".join(lines)


def _parse_notion_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return parse_datetime(value)


def _parse_sync_params(request) -> dict:
    include_database_rows = request.query_params.get("include_database_rows", "true").lower() != "false"
    max_items_raw = request.query_params.get("max_items")
    max_items = int(max_items_raw) if max_items_raw else None
    recursive = request.query_params.get("recursive", "true").lower() != "false"
    max_blocks_raw = request.query_params.get("max_blocks_per_page")
    max_blocks_per_page = int(max_blocks_raw) if max_blocks_raw else 5000
    max_depth_raw = request.query_params.get("max_depth")
    max_depth = int(max_depth_raw) if max_depth_raw else 20
    debug = request.query_params.get("debug", "false").lower() == "true"
    return {
        "include_database_rows": include_database_rows,
        "max_items": max_items,
        "recursive": recursive,
        "max_blocks_per_page": max_blocks_per_page,
        "max_depth": max_depth,
        "debug": debug,
    }


def _run_notion_sync(params: dict, user_label: str, record) -> dict:
    started = time.monotonic()
    notion = NotionService()

    page_results = list(notion.iterate_search_results(query="", filter_type="page"))
    database_results = list(notion.iterate_search_results(query="", filter_type="database"))
    combined = page_results + database_results
    record(
        "search_discovery_complete",
        discovered_pages=len(page_results),
        discovered_databases=len(database_results),
        discovered_total=len(combined),
    )

    processed = 0
    created = 0
    updated = 0
    errors = []
    seen_ids = set()

    for item in combined:
        notion_id = item.get("id")
        if not notion_id or notion_id in seen_ids:
            continue
        seen_ids.add(notion_id)

        if params["max_items"] is not None and processed >= params["max_items"]:
            break

        object_type = item.get("object")
        if object_type not in {"page", "database"}:
            continue

        try:
            item_started = time.monotonic()
            record("item_started", notion_id=notion_id, object_type=object_type)
            if object_type == "page":
                record("item_stage", notion_id=notion_id, object_type=object_type, stage="fetch_page_content")
                page_payload = notion.get_page_content(
                    notion_id,
                    recursive=params["recursive"],
                    max_blocks=params["max_blocks_per_page"],
                    max_depth=params["max_depth"],
                )
                metadata = page_payload.get("metadata", {})
                plain_text = page_payload.get("text_content", "")
            else:
                record("item_stage", notion_id=notion_id, object_type=object_type, stage="fetch_database")
                metadata = notion.retrieve_database(notion_id)
                plain_text = ""
                if params["include_database_rows"]:
                    record("item_stage", notion_id=notion_id, object_type=object_type, stage="fetch_database_rows")
                    plain_text = _get_database_rows_text(notion, notion_id)

            title = notion.extract_title(metadata) or notion.extract_title(item)
            parent_type, parent_notion_id = notion.extract_parent_info(metadata)
            last_edited_time = _parse_notion_time(metadata.get("last_edited_time"))
            url = metadata.get("url") or item.get("url") or ""
            is_archived = bool(metadata.get("archived", False))

            _, was_created = NotionContent.objects.update_or_create(
                notion_id=notion_id,
                defaults={
                    "object_type": object_type,
                    "title": title,
                    "url": url,
                    "parent_type": parent_type,
                    "parent_notion_id": parent_notion_id,
                    "last_edited_time": last_edited_time,
                    "is_archived": is_archived,
                    "plain_text": plain_text,
                    "raw_metadata": metadata,
                },
            )
            created += int(was_created)
            updated += int(not was_created)
            processed += 1
            record(
                "item_finished",
                notion_id=notion_id,
                object_type=object_type,
                status="created" if was_created else "updated",
                elapsed_seconds=round(time.monotonic() - item_started, 3),
                text_chars=len(plain_text),
                processed=processed,
            )
        except Exception as exc:
            record("item_failed", notion_id=notion_id, object_type=object_type, error=str(exc))
            errors.append({"id": notion_id, "object": object_type, "error": str(exc)})

    duration = round(time.monotonic() - started, 3)
    record(
        "sync_finished",
        duration_seconds=duration,
        processed=processed,
        created=created,
        updated=updated,
        errors_count=len(errors),
    )
    return {
        "success": True,
        "duration_seconds": duration,
        "processed": processed,
        "created": created,
        "updated": updated,
        "errors_count": len(errors),
        "errors": errors[:25],
        "total_discovered": len(seen_ids),
        "include_database_rows": params["include_database_rows"],
        "recursive": params["recursive"],
        "max_blocks_per_page": params["max_blocks_per_page"],
        "max_depth": params["max_depth"],
        "user": user_label,
    }


class NotionSearchAPIView(APIView):
    """
    Search Notion pages and databases.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Search Notion",
        parameters=[
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search query",
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Results to return (1-100, default 10)",
            ),
            OpenApiParameter(
                name="start_cursor",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Cursor for pagination",
            ),
            OpenApiParameter(
                name="filter",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Limit results to 'page' or 'database'",
            ),
        ],
        responses={200: dict, 400: dict, 500: dict},
        tags=["Notion"],
    )
    def get(self, request):
        query = request.query_params.get("q")
        if not query:
            return Response({"error": "Missing required parameter: q"}, status=status.HTTP_400_BAD_REQUEST)

        page_size = int(request.query_params.get("page_size", 10))
        start_cursor = request.query_params.get("start_cursor")
        filter_type = request.query_params.get("filter")

        try:
            notion = NotionService()
            results = notion.search(query, page_size=page_size, start_cursor=start_cursor, filter_type=filter_type)
            return Response(results, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotionPageDetailAPIView(APIView):
    """
    Retrieve Notion page metadata.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Notion page",
        responses={200: dict, 404: dict, 500: dict},
        tags=["Notion"],
    )
    def get(self, request, page_id: str):
        try:
            notion = NotionService()
            page = notion.retrieve_page(page_id)
            return Response(page, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotionPageContentAPIView(APIView):
    """
    Retrieve the blocks (content) of a page.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Notion page content",
        parameters=[
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Blocks to return (1-100, default 50)",
            ),
            OpenApiParameter(
                name="start_cursor",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Cursor for pagination",
            ),
        ],
        responses={200: dict, 404: dict, 500: dict},
        tags=["Notion"],
    )
    def get(self, request, page_id: str):
        page_size = int(request.query_params.get("page_size", 50))
        start_cursor = request.query_params.get("start_cursor")

        try:
            notion = NotionService()
            blocks = notion.list_block_children(page_id, page_size=page_size, start_cursor=start_cursor)
            return Response(blocks, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotionSyncAPIView(APIView):
    """
    Crawl and ingest Notion pages/databases into local DB.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Sync Notion content to DB",
        parameters=[
            OpenApiParameter(
                name="include_database_rows",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Include row summaries from each database (default true)",
            ),
            OpenApiParameter(
                name="max_items",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Optional cap for pages+databases processed in this run",
            ),
            OpenApiParameter(
                name="recursive",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Recursively traverse nested blocks for page content (default true)",
            ),
            OpenApiParameter(
                name="max_blocks_per_page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Safety cap for blocks traversed per page (default 5000)",
            ),
            OpenApiParameter(
                name="max_depth",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Safety cap for nested block depth when recursive=true (default 20)",
            ),
            OpenApiParameter(
                name="debug",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Include recent progress events in response payload",
            ),
        ],
        responses={200: dict, 500: dict},
        tags=["Notion"],
    )
    def post(self, request):
        params = _parse_sync_params(request)
        debug = params["debug"]
        run_id = str(uuid.uuid4())
        started = time.monotonic()
        logger = logging.getLogger(__name__)
        progress_log: list[dict] = []

        def record(event: str, **fields):
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "event": event,
                **fields,
            }
            progress_log.append(entry)
            logger.info("notion_sync run_id=%s event=%s details=%s", run_id, event, fields)

        try:
            record(
                "sync_started",
                include_database_rows=params["include_database_rows"],
                max_items=params["max_items"],
                recursive=params["recursive"],
                max_blocks_per_page=params["max_blocks_per_page"],
                max_depth=params["max_depth"],
                user=getattr(request.user, "email", request.user.username),
            )
            sync_result = _run_notion_sync(params, getattr(request.user, "email", request.user.username), record)
            sync_result["run_id"] = run_id
            sync_result["progress_tail"] = progress_log[-50:] if debug else []
            return Response(sync_result, status=status.HTTP_200_OK)
        except ValueError as exc:
            record("sync_failed", error=str(exc))
            return Response(
                {
                    "success": False,
                    "run_id": run_id,
                    "duration_seconds": round(time.monotonic() - started, 3),
                    "error": str(exc),
                    "progress_tail": progress_log[-50:] if debug else [],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            record("sync_failed", error=str(exc))
            return Response(
                {
                    "success": False,
                    "run_id": run_id,
                    "duration_seconds": round(time.monotonic() - started, 3),
                    "error": str(exc),
                    "progress_tail": progress_log[-50:] if debug else [],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def _run_sync_job_worker(job_id: str) -> None:
    close_old_connections()
    logger = logging.getLogger(__name__)

    try:
        job = NotionSyncJob.objects.get(job_id=job_id)
    except NotionSyncJob.DoesNotExist:
        logger.warning("notion_sync_job missing job_id=%s", job_id)
        return

    job.status = NotionSyncJob.STATUS_RUNNING
    job.started_at = django_timezone.now()
    job.save(update_fields=["status", "started_at"])

    progress_log = list(job.progress_log or [])

    def record(event: str, **fields):
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **fields,
        }
        progress_log.append(entry)
        if len(progress_log) > 400:
            del progress_log[: len(progress_log) - 400]

        job.progress_log = progress_log
        job.save(update_fields=["progress_log"])
        logger.info("notion_sync_async job_id=%s event=%s details=%s", job_id, event, fields)

    try:
        params = dict(job.parameters or {})
        user_label = job.created_by.email if job.created_by and job.created_by.email else (
            job.created_by.username if job.created_by else "system"
        )
        record("sync_started", **params, user=user_label)
        result = _run_notion_sync(params, user_label, record)
        result["job_id"] = job_id
        job.status = NotionSyncJob.STATUS_SUCCEEDED
        job.result = result
        job.finished_at = django_timezone.now()
        job.error_message = ""
        job.save(update_fields=["status", "result", "finished_at", "error_message"])
    except Exception as exc:
        record("sync_failed", error=str(exc))
        job.status = NotionSyncJob.STATUS_FAILED
        job.error_message = str(exc)
        job.finished_at = django_timezone.now()
        job.save(update_fields=["status", "error_message", "finished_at"])
    finally:
        close_old_connections()


class NotionSyncAsyncAPIView(APIView):
    """
    Kick off a background Notion sync job.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Start Notion sync job (async)",
        parameters=[
            OpenApiParameter(
                name="include_database_rows",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Include row summaries from each database (default true)",
            ),
            OpenApiParameter(
                name="max_items",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Optional cap for pages+databases processed in this run",
            ),
            OpenApiParameter(
                name="recursive",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Recursively traverse nested blocks for page content (default true)",
            ),
            OpenApiParameter(
                name="max_blocks_per_page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Safety cap for blocks traversed per page (default 5000)",
            ),
            OpenApiParameter(
                name="max_depth",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Safety cap for nested block depth when recursive=true (default 20)",
            ),
        ],
        responses={202: dict, 500: dict},
        tags=["Notion"],
    )
    def post(self, request):
        params = _parse_sync_params(request)
        params.pop("debug", None)
        job_id = str(uuid.uuid4())

        job = NotionSyncJob.objects.create(
            job_id=job_id,
            status=NotionSyncJob.STATUS_QUEUED,
            created_by=request.user,
            parameters=params,
            progress_log=[],
            result={},
            error_message="",
        )

        worker = threading.Thread(target=_run_sync_job_worker, args=(job_id,), daemon=True)
        worker.start()

        return Response(
            {
                "success": True,
                "job_id": job_id,
                "status": job.status,
                "poll_url": f"/notion/api/sync/jobs/{job_id}/",
                "parameters": params,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class NotionSyncJobStatusAPIView(APIView):
    """
    Poll status/progress for an async Notion sync job.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get async Notion sync job status",
        responses={200: dict, 404: dict},
        tags=["Notion"],
    )
    def get(self, request, job_id: str):
        try:
            job = NotionSyncJob.objects.select_related("created_by").get(job_id=job_id)
        except NotionSyncJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        # Allow staff to view all jobs; non-staff can view only their own.
        if not request.user.is_staff and job.created_by_id != request.user.id:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "job_id": job.job_id,
                "status": job.status,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "finished_at": job.finished_at,
                "parameters": job.parameters,
                "progress_tail": (job.progress_log or [])[-50:],
                "result": job.result or {},
                "error": job.error_message or None,
            },
            status=status.HTTP_200_OK,
        )


class NotionIngestToRAGAPIView(APIView):
    """
    Ingest locally synced Notion content rows into RAG pipeline.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Ingest synced Notion DB content into RAG",
        parameters=[
            OpenApiParameter(
                name="max_items",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Optional cap for items processed in this run",
            ),
            OpenApiParameter(
                name="only_changed",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Only ingest rows with changed content hash (default true)",
            ),
        ],
        responses={200: dict, 500: dict},
        tags=["Notion"],
    )
    def post(self, request):
        max_items_raw = request.query_params.get("max_items")
        max_items = int(max_items_raw) if max_items_raw else None
        only_changed = request.query_params.get("only_changed", "true").lower() != "false"

        run_id = str(uuid.uuid4())
        started = time.monotonic()
        logger = logging.getLogger(__name__)

        queryset = (
            NotionContent.objects
            .filter(is_archived=False)
            .exclude(plain_text="")
            .order_by("-last_edited_time", "id")
        )
        if max_items is not None:
            queryset = queryset[:max_items]

        processed = 0
        ingested = 0
        skipped_unchanged = 0
        failed = 0
        failures = []

        logger.info(
            "notion_rag_ingest run_id=%s started max_items=%s only_changed=%s",
            run_id,
            max_items,
            only_changed,
        )

        for row in queryset:
            processed += 1
            try:
                row_hash = self._compute_content_hash(row)
                if only_changed and row.rag_document_id and row.content_hash == row_hash:
                    skipped_unchanged += 1
                    continue

                # Replace prior RAG document when refreshing this Notion row.
                if row.rag_document_id:
                    self._delete_rag_document(row.rag_document_id)

                payload = {
                    "content": row.plain_text,
                    "metadata": {
                        "source": row.url or f"notion:{row.notion_id}",
                        "source_type": "notion",
                        "title": row.title or row.notion_id,
                        "file_type": "notion",
                        "notion_id": row.notion_id,
                        "notion_object_type": row.object_type,
                        "notion_parent_type": row.parent_type,
                        "notion_parent_id": row.parent_notion_id,
                    },
                }

                # Match existing search ACL filtering behavior so ingested docs are retrievable.
                acl = {}
                if request.user.email:
                    acl["allowed_users"] = [request.user.email]

                try:
                    social = request.user.social_auth.filter(provider="azuread-tenant-oauth2").first()
                    if social and social.extra_data:
                        user_groups = social.extra_data.get("groups", [])
                        if user_groups:
                            acl["allowed_groups"] = user_groups
                except Exception:
                    pass

                if acl:
                    payload["acl"] = acl

                response = requests.post(
                    f"{settings.RAG_API_BASE_URL}/api/v1/ingest/document",
                    headers={
                        "X-API-Key": settings.RAG_API_KEY,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=RAG_API_TIMEOUT,
                )
                response.raise_for_status()
                result = response.json()

                row.rag_document_id = result.get("document_id", row.rag_document_id)
                row.content_hash = row_hash
                row.last_ingested_at = django_timezone.now()
                row.save(update_fields=["rag_document_id", "content_hash", "last_ingested_at", "synced_at"])
                ingested += 1
            except Exception as exc:
                failed += 1
                failures.append({"notion_id": row.notion_id, "error": str(exc)})
                logger.warning(
                    "notion_rag_ingest run_id=%s notion_id=%s error=%s",
                    run_id,
                    row.notion_id,
                    str(exc),
                )

        duration = round(time.monotonic() - started, 3)
        logger.info(
            "notion_rag_ingest run_id=%s finished duration=%s processed=%s ingested=%s failed=%s skipped_unchanged=%s",
            run_id,
            duration,
            processed,
            ingested,
            failed,
            skipped_unchanged,
        )

        return Response(
            {
                "success": True,
                "run_id": run_id,
                "duration_seconds": duration,
                "processed": processed,
                "ingested": ingested,
                "skipped_unchanged": skipped_unchanged,
                "failed": failed,
                "failures": failures[:25],
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _compute_content_hash(row: NotionContent) -> str:
        hash_input = "||".join(
            [
                row.notion_id or "",
                row.object_type or "",
                row.title or "",
                row.url or "",
                row.plain_text or "",
            ]
        )
        return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    @staticmethod
    def _delete_rag_document(document_id: str) -> None:
        response = requests.delete(
            f"{settings.RAG_API_BASE_URL}/api/v1/ingest/document/{document_id}",
            headers={"X-API-Key": settings.RAG_API_KEY},
            timeout=RAG_API_TIMEOUT,
        )
        # Ignore not found; it means the old id was already gone.
        if response.status_code != 404:
            response.raise_for_status()
