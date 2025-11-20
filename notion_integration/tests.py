from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse


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
