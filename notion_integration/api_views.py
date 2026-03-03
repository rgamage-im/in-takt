"""
Notion API endpoints.
"""
from datetime import datetime, timezone
import logging
import time
import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes
from django.utils.dateparse import parse_datetime

from .models import NotionContent
from .services import NotionService


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
        include_database_rows = request.query_params.get("include_database_rows", "true").lower() != "false"
        max_items_raw = request.query_params.get("max_items")
        max_items = int(max_items_raw) if max_items_raw else None
        recursive = request.query_params.get("recursive", "true").lower() != "false"
        max_blocks_raw = request.query_params.get("max_blocks_per_page")
        max_blocks_per_page = int(max_blocks_raw) if max_blocks_raw else 5000
        max_depth_raw = request.query_params.get("max_depth")
        max_depth = int(max_depth_raw) if max_depth_raw else 20
        debug = request.query_params.get("debug", "false").lower() == "true"
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
                include_database_rows=include_database_rows,
                max_items=max_items,
                recursive=recursive,
                max_blocks_per_page=max_blocks_per_page,
                max_depth=max_depth,
                user=getattr(request.user, "email", request.user.username),
            )
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

                if max_items is not None and processed >= max_items:
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
                            recursive=recursive,
                            max_blocks=max_blocks_per_page,
                            max_depth=max_depth,
                        )
                        metadata = page_payload.get("metadata", {})
                        plain_text = page_payload.get("text_content", "")
                    else:
                        record("item_stage", notion_id=notion_id, object_type=object_type, stage="fetch_database")
                        metadata = notion.retrieve_database(notion_id)
                        plain_text = ""
                        if include_database_rows:
                            record(
                                "item_stage",
                                notion_id=notion_id,
                                object_type=object_type,
                                stage="fetch_database_rows",
                            )
                            plain_text = self._get_database_rows_text(notion, notion_id)

                    title = notion.extract_title(metadata) or notion.extract_title(item)
                    parent_type, parent_notion_id = notion.extract_parent_info(metadata)
                    last_edited_time = self._parse_notion_time(metadata.get("last_edited_time"))
                    url = metadata.get("url") or item.get("url") or ""
                    is_archived = bool(metadata.get("archived", False))

                    obj, was_created = NotionContent.objects.update_or_create(
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
            return Response(
                {
                    "success": True,
                    "run_id": run_id,
                    "duration_seconds": duration,
                    "processed": processed,
                    "created": created,
                    "updated": updated,
                    "errors_count": len(errors),
                    "errors": errors[:25],
                    "total_discovered": len(seen_ids),
                    "include_database_rows": include_database_rows,
                    "recursive": recursive,
                    "max_blocks_per_page": max_blocks_per_page,
                    "max_depth": max_depth,
                    "progress_tail": progress_log[-50:] if debug else [],
                },
                status=status.HTTP_200_OK,
            )
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

    def _get_database_rows_text(self, notion: NotionService, database_id: str) -> str:
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
                    text_value = self._property_to_text(value)
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

    @staticmethod
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

    @staticmethod
    def _parse_notion_time(value: str | None) -> datetime | None:
        if not value:
            return None
        return parse_datetime(value)
