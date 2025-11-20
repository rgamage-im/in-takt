"""
Notion API service helpers.
"""
import os
from typing import Any, Dict, Optional

import requests


class NotionService:
    """
    Thin wrapper around the Notion REST API.
    """

    def __init__(self):
        token = os.getenv("NOTION_INTERNAL_TOKEN") or os.getenv("NOTION_API_TOKEN")
        if not token:
            raise ValueError("NOTION_INTERNAL_TOKEN environment variable is required for Notion access.")

        self.auth_token = token
        self.base_url = os.getenv("NOTION_API_BASE_URL", "https://api.notion.com/v1")
        self.notion_version = os.getenv("NOTION_VERSION", "2022-06-28")

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Notion-Version": self.notion_version,
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = requests.request(method, url, headers=self._headers, params=params, json=json, timeout=15)
        response.raise_for_status()
        return response.json()

    def search(
        self,
        query: str,
        page_size: int = 10,
        start_cursor: Optional[str] = None,
        filter_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search across pages and databases.
        """
        payload: Dict[str, Any] = {
            "query": query,
            "page_size": min(max(page_size, 1), 100),
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        }

        if start_cursor:
            payload["start_cursor"] = start_cursor

        if filter_type in {"page", "database"}:
            payload["filter"] = {"property": "object", "value": filter_type}

        return self._request("POST", "/search", json=payload)

    def retrieve_page(self, page_id: str) -> Dict[str, Any]:
        """
        Get page metadata.
        """
        return self._request("GET", f"/pages/{page_id}")

    def list_block_children(
        self,
        block_id: str,
        page_size: int = 50,
        start_cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get children blocks for a page or block.
        """
        params: Dict[str, Any] = {"page_size": min(max(page_size, 1), 100)}
        if start_cursor:
            params["start_cursor"] = start_cursor
        return self._request("GET", f"/blocks/{block_id}/children", params=params)
