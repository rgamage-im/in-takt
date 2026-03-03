from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from rest_framework.test import APIClient
from django.urls import reverse
import requests
from django.utils import timezone

from .models import NotionContent, NotionSyncJob
from .services import NotionService
from .api_views import _run_sync_job_worker


class NotionAPITestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester", email="tester@example.com", password="password"
        )
        self.client = APIClient()

    def test_search_requires_authentication(self):
        url = reverse("notion:api-search")
        response = self.client.get(url, {"q": "plumbing"})
        self.assertEqual(response.status_code, 403)

    @mock.patch("notion_integration.api_views.NotionService.search")
    def test_search_returns_results(self, search_mock):
        search_mock.return_value = {"results": [{"id": "page-123"}], "has_more": False}

        self.client.force_authenticate(self.user)
        url = reverse("notion:api-search")
        response = self.client.get(url, {"q": "plumbing", "page_size": 5})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["id"], "page-123")
        search_mock.assert_called_once()

    @mock.patch("notion_integration.api_views.NotionService.retrieve_page")
    def test_page_detail(self, retrieve_mock):
        retrieve_mock.return_value = {"id": "page-123", "object": "page"}

        self.client.force_authenticate(self.user)
        url = reverse("notion:api-page-detail", args=["page-123"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], "page-123")

    @mock.patch("notion_integration.api_views.NotionService.list_block_children")
    def test_page_content(self, blocks_mock):
        blocks_mock.return_value = {"results": [{"id": "block-1"}], "has_more": False}

        self.client.force_authenticate(self.user)
        url = reverse("notion:api-page-content", args=["page-123"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["id"], "block-1")

    def test_sync_requires_authentication(self):
        url = reverse("notion:api-sync")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_sync_async_requires_authentication(self):
        url = reverse("notion:api-sync-async")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_sync_job_status_requires_authentication(self):
        job = NotionSyncJob.objects.create(job_id="job-1")
        url = reverse("notion:api-sync-job-status", args=[job.job_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sync_active_job_requires_authentication(self):
        url = reverse("notion:api-sync-jobs-active")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sync_latest_job_requires_authentication(self):
        url = reverse("notion:api-sync-jobs-latest")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sync_job_cancel_requires_authentication(self):
        job = NotionSyncJob.objects.create(job_id="job-cancel-auth")
        url = reverse("notion:api-sync-job-cancel", args=[job.job_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_ingest_rag_requires_authentication(self):
        url = reverse("notion:api-ingest-rag")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    @mock.patch("notion_integration.api_views.NotionService")
    def test_sync_ingests_page_and_database(self, notion_service_cls):
        notion = notion_service_cls.return_value
        notion.iterate_search_results.side_effect = [
            [
                {"id": "page-1", "object": "page", "url": "https://notion.so/page-1"},
            ],
            [
                {"id": "db-1", "object": "database", "url": "https://notion.so/db-1"},
            ],
        ]
        notion.get_page_content.return_value = {
            "metadata": {
                "id": "page-1",
                "object": "page",
                "url": "https://notion.so/page-1",
                "last_edited_time": "2026-03-02T12:00:00.000Z",
                "archived": False,
                "properties": {
                    "Title": {"type": "title", "title": [{"plain_text": "Page One"}]}
                },
                "parent": {"type": "workspace"},
            },
            "text_content": "hello world",
        }
        notion.retrieve_database.return_value = {
            "id": "db-1",
            "object": "database",
            "url": "https://notion.so/db-1",
            "last_edited_time": "2026-03-02T12:00:00.000Z",
            "archived": False,
            "title": [{"plain_text": "DB One"}],
            "parent": {"type": "workspace"},
        }
        notion.query_database.return_value = {"results": [], "has_more": False}
        notion.extract_title.side_effect = lambda obj: (
            "Page One" if obj.get("id") == "page-1" else "DB One" if obj.get("id") == "db-1" else ""
        )
        notion.extract_parent_info.return_value = ("workspace", "workspace")

        self.client.force_authenticate(self.user)
        url = reverse("notion:api-sync")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["processed"], 2)
        self.assertEqual(NotionContent.objects.count(), 2)

    @mock.patch("notion_integration.api_views.threading.Thread")
    def test_sync_async_creates_job(self, thread_mock):
        self.client.force_authenticate(self.user)
        url = reverse("notion:api-sync-async")
        response = self.client.post(url, {"max_items": 3})

        self.assertEqual(response.status_code, 202)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIn("job_id", payload)
        job = NotionSyncJob.objects.get(job_id=payload["job_id"])
        self.assertEqual(job.status, NotionSyncJob.STATUS_QUEUED)
        self.assertTrue(job.parameters.get("auto_ingest"))
        thread_mock.assert_called_once()

    def test_sync_job_status_owner_can_view(self):
        self.client.force_authenticate(self.user)
        job = NotionSyncJob.objects.create(
            job_id="job-owner-1",
            created_by=self.user,
            status=NotionSyncJob.STATUS_QUEUED,
            parameters={"max_items": 2},
            progress_log=[{"event": "sync_started"}],
        )
        url = reverse("notion:api-sync-job-status", args=[job.job_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["job_id"], "job-owner-1")
        self.assertEqual(payload["status"], NotionSyncJob.STATUS_QUEUED)

    def test_sync_job_status_other_user_cannot_view(self):
        other = get_user_model().objects.create_user(
            username="other", email="other@example.com", password="password"
        )
        job = NotionSyncJob.objects.create(
            job_id="job-other-1",
            created_by=other,
            status=NotionSyncJob.STATUS_QUEUED,
        )
        self.client.force_authenticate(self.user)
        url = reverse("notion:api-sync-job-status", args=[job.job_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_sync_job_cancel_owner_can_cancel_running(self):
        self.client.force_authenticate(self.user)
        job = NotionSyncJob.objects.create(
            job_id="job-cancel-running-1",
            created_by=self.user,
            status=NotionSyncJob.STATUS_RUNNING,
        )
        url = reverse("notion:api-sync-job-cancel", args=[job.job_id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        job.refresh_from_db()
        self.assertTrue(job.cancel_requested)
        self.assertEqual(job.status, NotionSyncJob.STATUS_CANCELED)
        self.assertIsNotNone(job.finished_at)
        self.assertIsNotNone(job.cancel_requested_at)

    def test_sync_job_cancel_owner_cancels_queued_immediately(self):
        self.client.force_authenticate(self.user)
        job = NotionSyncJob.objects.create(
            job_id="job-cancel-queued-1",
            created_by=self.user,
            status=NotionSyncJob.STATUS_QUEUED,
        )
        url = reverse("notion:api-sync-job-cancel", args=[job.job_id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        job.refresh_from_db()
        self.assertTrue(job.cancel_requested)
        self.assertEqual(job.status, NotionSyncJob.STATUS_CANCELED)
        self.assertIsNotNone(job.finished_at)

    def test_sync_job_cancel_other_user_cannot_cancel(self):
        other = get_user_model().objects.create_user(
            username="other2", email="other2@example.com", password="password"
        )
        job = NotionSyncJob.objects.create(
            job_id="job-cancel-other-1",
            created_by=other,
            status=NotionSyncJob.STATUS_RUNNING,
        )
        self.client.force_authenticate(self.user)
        url = reverse("notion:api-sync-job-cancel", args=[job.job_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_sync_job_cancel_terminal_job_returns_conflict(self):
        self.client.force_authenticate(self.user)
        job = NotionSyncJob.objects.create(
            job_id="job-cancel-terminal-1",
            created_by=self.user,
            status=NotionSyncJob.STATUS_SUCCEEDED,
        )
        url = reverse("notion:api-sync-job-cancel", args=[job.job_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 409)

    @mock.patch("notion_integration.api_views._run_notion_sync")
    def test_worker_marks_canceled_when_sync_result_canceled(self, sync_mock):
        job = NotionSyncJob.objects.create(
            job_id="job-worker-canceled-1",
            created_by=self.user,
            status=NotionSyncJob.STATUS_QUEUED,
            parameters={},
            progress_log=[],
            result={},
        )
        sync_mock.return_value = {
            "success": False,
            "canceled": True,
            "processed": 0,
            "created": 0,
            "updated": 0,
            "errors_count": 0,
            "errors": [],
        }

        _run_sync_job_worker(job.job_id)

        job.refresh_from_db()
        self.assertEqual(job.status, NotionSyncJob.STATUS_CANCELED)
        self.assertTrue(job.result.get("canceled"))
        self.assertIsNotNone(job.finished_at)

    def test_sync_active_job_returns_latest_for_user(self):
        self.client.force_authenticate(self.user)
        NotionSyncJob.objects.create(job_id="job-a", created_by=self.user, status=NotionSyncJob.STATUS_RUNNING)
        newest = NotionSyncJob.objects.create(job_id="job-b", created_by=self.user, status=NotionSyncJob.STATUS_QUEUED)
        url = reverse("notion:api-sync-jobs-active")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["has_active_job"])
        self.assertEqual(body["job"]["job_id"], newest.job_id)

    def test_sync_latest_job_returns_latest_for_user(self):
        self.client.force_authenticate(self.user)
        NotionSyncJob.objects.create(job_id="job-c", created_by=self.user, status=NotionSyncJob.STATUS_FAILED)
        newest = NotionSyncJob.objects.create(job_id="job-d", created_by=self.user, status=NotionSyncJob.STATUS_SUCCEEDED)
        url = reverse("notion:api-sync-jobs-latest")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["has_job"])
        self.assertEqual(body["job"]["job_id"], newest.job_id)

    @mock.patch("notion_integration.api_views.requests.post")
    def test_ingest_rag_ingests_new_row(self, post_mock):
        NotionContent.objects.create(
            notion_id="page-1",
            object_type="page",
            title="Policies",
            url="https://www.notion.so/page-1",
            plain_text="Policy text",
            raw_metadata={},
            last_edited_time=timezone.now(),
        )

        post_response = mock.MagicMock()
        post_response.raise_for_status.return_value = None
        post_response.json.return_value = {"document_id": "doc-123", "chunks_indexed": 2}
        post_mock.return_value = post_response

        self.client.force_authenticate(self.user)
        url = reverse("notion:api-ingest-rag")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["ingested"], 1)

        row = NotionContent.objects.get(notion_id="page-1")
        self.assertEqual(row.rag_document_id, "doc-123")
        self.assertTrue(bool(row.content_hash))
        self.assertIsNotNone(row.last_ingested_at)

    @mock.patch("notion_integration.api_views.requests.post")
    def test_ingest_rag_skips_unchanged_row(self, post_mock):
        row = NotionContent.objects.create(
            notion_id="page-2",
            object_type="page",
            title="Handbook",
            url="https://www.notion.so/page-2",
            plain_text="Same text",
            raw_metadata={},
            rag_document_id="doc-existing",
            last_edited_time=timezone.now(),
        )
        from notion_integration.api_views import _compute_notion_content_hash
        row.content_hash = _compute_notion_content_hash(row)
        row.save(update_fields=["content_hash"])

        self.client.force_authenticate(self.user)
        url = reverse("notion:api-ingest-rag")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["ingested"], 0)
        self.assertEqual(body["skipped_unchanged"], 1)
        post_mock.assert_not_called()


class NotionServiceRetryTestCase(SimpleTestCase):
    @mock.patch.dict("os.environ", {"NOTION_INTERNAL_TOKEN": "test-token", "NOTION_API_MAX_RETRIES": "2"})
    @mock.patch("notion_integration.services.time.sleep")
    @mock.patch("notion_integration.services.requests.request")
    def test_request_retries_on_429_then_succeeds(self, request_mock, sleep_mock):
        throttle_response = mock.MagicMock()
        throttle_response.status_code = 429
        throttle_response.headers = {"Retry-After": "0"}

        success_response = mock.MagicMock()
        success_response.status_code = 200
        success_response.headers = {}
        success_response.json.return_value = {"ok": True}

        request_mock.side_effect = [throttle_response, success_response]

        notion = NotionService()
        payload = notion._request("GET", "/test")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(request_mock.call_count, 2)
        sleep_mock.assert_called_once_with(0.0)

    @mock.patch.dict("os.environ", {"NOTION_INTERNAL_TOKEN": "test-token", "NOTION_API_MAX_RETRIES": "1"})
    @mock.patch("notion_integration.services.time.sleep")
    @mock.patch("notion_integration.services.requests.request")
    def test_request_raises_after_retry_limit(self, request_mock, sleep_mock):
        throttle_response_1 = mock.MagicMock()
        throttle_response_1.status_code = 429
        throttle_response_1.headers = {"Retry-After": "0"}

        throttle_response_2 = mock.MagicMock()
        throttle_response_2.status_code = 429
        throttle_response_2.headers = {"Retry-After": "0"}
        throttle_response_2.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests")

        request_mock.side_effect = [throttle_response_1, throttle_response_2]

        notion = NotionService()
        with self.assertRaises(requests.HTTPError):
            notion._request("GET", "/test")

        self.assertEqual(request_mock.call_count, 2)
        sleep_mock.assert_called_once_with(0.0)

    @mock.patch.dict("os.environ", {"NOTION_INTERNAL_TOKEN": "test-token", "NOTION_API_MAX_RETRIES": "2"})
    @mock.patch("notion_integration.services.time.sleep")
    @mock.patch("notion_integration.services.requests.request")
    def test_request_retries_on_timeout_then_succeeds(self, request_mock, sleep_mock):
        success_response = mock.MagicMock()
        success_response.status_code = 200
        success_response.headers = {}
        success_response.json.return_value = {"ok": True}

        request_mock.side_effect = [requests.exceptions.Timeout("read timed out"), success_response]

        notion = NotionService()
        payload = notion._request("GET", "/test")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(request_mock.call_count, 2)
        sleep_mock.assert_called_once_with(1.0)


class NotionServiceExtractionTestCase(SimpleTestCase):
    def test_extract_text_preserves_external_urls_and_captions(self):
        service = object.__new__(NotionService)
        blocks = [
            {
                "id": "b1",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "plain_text": "Read this",
                            "href": "https://contoso.sharepoint.com/sites/team/Shared%20Documents/file.docx",
                        }
                    ]
                },
            },
            {
                "id": "b2",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {"url": "https://images.example.com/diagram.png"},
                    "caption": [{"plain_text": "System diagram"}],
                },
            },
            {
                "id": "b3",
                "type": "bookmark",
                "bookmark": {"url": "https://integralmethods.sharepoint.com/sites/wiki"},
            },
        ]

        text = service._extract_text_from_blocks(blocks)

        self.assertIn("Read this", text)
        self.assertIn("[Link] https://contoso.sharepoint.com/sites/team/Shared%20Documents/file.docx", text)
        self.assertIn("[image URL] https://images.example.com/diagram.png", text)
        self.assertIn("[image Caption] System diagram", text)
        self.assertIn("[bookmark URL] https://integralmethods.sharepoint.com/sites/wiki", text)

    def test_extract_text_handles_null_rich_text_payloads(self):
        service = object.__new__(NotionService)
        blocks = [
            {
                "id": "b-null",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "plain_text": "ok", "text": None},
                        {"type": "text", "plain_text": "", "text": {"content": "fallback", "link": None}},
                        {"type": "text", "plain_text": "", "text": None},
                    ]
                },
            }
        ]

        text = service._extract_text_from_blocks(blocks)
        self.assertIn("ok", text)
        self.assertIn("fallback", text)
