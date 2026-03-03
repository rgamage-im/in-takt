"""
Notion API service helpers.
"""
import os
import logging
import time
from typing import Any, Dict, Generator, Optional

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
        logger = logging.getLogger(__name__)
        max_retries = int(os.getenv("NOTION_API_MAX_RETRIES", "4"))
        base_delay_seconds = float(os.getenv("NOTION_API_RETRY_BASE_DELAY_SECONDS", "1"))
        max_delay_seconds = float(os.getenv("NOTION_API_RETRY_MAX_DELAY_SECONDS", "20"))
        retryable_status_codes = {429, 500, 502, 503, 504}

        last_response = None

        for attempt in range(max_retries + 1):
            response = requests.request(method, url, headers=self._headers, params=params, json=json, timeout=15)
            last_response = response

            if response.status_code in retryable_status_codes and attempt < max_retries:
                retry_after = self._parse_retry_after_seconds(response.headers.get("Retry-After"))
                backoff_seconds = min(base_delay_seconds * (2 ** attempt), max_delay_seconds)
                sleep_seconds = retry_after if retry_after is not None else backoff_seconds

                logger.warning(
                    "notion_api_retry method=%s path=%s status=%s attempt=%s/%s sleep_seconds=%s",
                    method,
                    path,
                    response.status_code,
                    attempt + 1,
                    max_retries + 1,
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)
                continue

            response.raise_for_status()
            return response.json()

        # Defensive fallback; loop should return or raise above.
        if last_response is not None:
            last_response.raise_for_status()
        raise RuntimeError("Notion request failed after retries")

    @staticmethod
    def _parse_retry_after_seconds(value: Optional[str]) -> Optional[float]:
        if not value:
            return None
        try:
            seconds = float(value)
            if seconds < 0:
                return None
            return seconds
        except (TypeError, ValueError):
            return None

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

    def retrieve_database(self, database_id: str) -> Dict[str, Any]:
        """
        Get database metadata.
        """
        return self._request("GET", f"/databases/{database_id}")

    def query_database(
        self,
        database_id: str,
        page_size: int = 100,
        start_cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Query rows in a database.
        """
        payload: Dict[str, Any] = {"page_size": min(max(page_size, 1), 100)}
        if start_cursor:
            payload["start_cursor"] = start_cursor
        return self._request("POST", f"/databases/{database_id}/query", json=payload)

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

    def get_page_content(
        self,
        page_id: str,
        recursive: bool = True,
        max_blocks: int = 5000,
        max_depth: int = 20,
    ) -> Dict[str, Any]:
        """
        Get full page content including metadata and all blocks.
        
        Args:
            page_id: The Notion page ID
            recursive: If True, fetches nested blocks recursively
            max_blocks: Maximum total blocks to traverse for this page
            max_depth: Maximum child nesting depth when traversing blocks
            
        Returns:
            Dict containing:
                - metadata: Page properties and metadata
                - blocks: List of all blocks with their content
                - text_content: Plain text extracted from all blocks
        """
        # Get page metadata
        page_metadata = self.retrieve_page(page_id)
        
        # Get all blocks with recursion safety guards
        logger = logging.getLogger(__name__)
        state = {
            "count": 0,
            "max_blocks": max_blocks,
            "max_depth": max_depth,
            "visited_block_ids": set(),
        }
        all_blocks = self._get_all_blocks_recursive(
            page_id,
            recursive=recursive,
            depth=0,
            state=state,
        )
        logger.info(
            "notion_page_fetch page_id=%s recursive=%s blocks=%s max_blocks=%s max_depth=%s",
            page_id,
            recursive,
            state["count"],
            max_blocks,
            max_depth,
        )
        
        # Extract plain text from blocks
        text_content = self._extract_text_from_blocks(all_blocks)
        
        return {
            "metadata": page_metadata,
            "blocks": all_blocks,
            "text_content": text_content
        }
    
    def _get_all_blocks_recursive(
        self,
        block_id: str,
        recursive: bool = True,
        depth: int = 0,
        state: Optional[Dict[str, Any]] = None,
    ) -> list[Dict[str, Any]]:
        """
        Recursively fetch all blocks and their children.
        """
        all_blocks = []
        if state is None:
            state = {"count": 0, "max_blocks": 5000, "max_depth": 20, "visited_block_ids": set()}

        if block_id in state["visited_block_ids"]:
            return all_blocks
        state["visited_block_ids"].add(block_id)

        if depth > state["max_depth"]:
            return all_blocks

        has_more = True
        start_cursor = None
        
        while has_more:
            response = self.list_block_children(
                block_id=block_id,
                page_size=100,
                start_cursor=start_cursor
            )
            
            blocks = response.get("results", [])
            
            for block in blocks:
                if state["count"] >= state["max_blocks"]:
                    return all_blocks
                all_blocks.append(block)
                state["count"] += 1
                
                # If block has children and recursive is enabled, fetch them
                if recursive and block.get("has_children", False):
                    child_blocks = self._get_all_blocks_recursive(
                        block["id"],
                        recursive=True,
                        depth=depth + 1,
                        state=state,
                    )
                    # Add children to the block
                    block["children"] = child_blocks
                    all_blocks.extend(child_blocks)
            
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")
        
        return all_blocks
    
    def _extract_text_from_blocks(self, blocks: list[Dict[str, Any]]) -> str:
        """
        Extract plain text and linkable resource references from Notion blocks.
        """
        text_parts = []
        
        for block in blocks:
            block_type = block.get("type")
            if not block_type:
                continue
            
            block_content = block.get(block_type, {})
            
            # Extract text from rich text arrays
            if "rich_text" in block_content:
                for text_obj in block_content["rich_text"]:
                    plain_text = text_obj.get("plain_text") or text_obj.get("text", {}).get("content", "")
                    if plain_text:
                        text_parts.append(plain_text)

                    # Preserve inline links so downstream retrieval can cite external URLs.
                    href = text_obj.get("href") or text_obj.get("text", {}).get("link", {}).get("url")
                    if href:
                        text_parts.append(f"[Link] {href}")
            
            # Handle special block types
            elif block_type == "child_page":
                text_parts.append(f"[Child Page: {block_content.get('title', '')}]")
            
            elif block_type == "child_database":
                text_parts.append(f"[Child Database: {block_content.get('title', '')}]")

            # Preserve URLs from external resources (images/files/embeds/bookmarks/etc).
            resource_url = self._extract_block_url(block_type, block_content)
            if resource_url:
                text_parts.append(f"[{block_type} URL] {resource_url}")

            # Include captions where available (common on image/file/media blocks).
            caption_parts = block_content.get("caption", [])
            if caption_parts:
                caption_text = " ".join(part.get("plain_text", "") for part in caption_parts).strip()
                if caption_text:
                    text_parts.append(f"[{block_type} Caption] {caption_text}")
        
        return "\n".join(text_parts)

    @staticmethod
    def _extract_block_url(block_type: str, block_content: Dict[str, Any]) -> str:
        """
        Extract URL from Notion block payload when present.
        """
        # Common direct URL field (bookmark, embed, link_preview, etc.)
        direct_url = block_content.get("url")
        if direct_url:
            return str(direct_url)

        # Notion file-style objects (image/file/video/pdf/audio) can have `external.url` or `file.url`.
        external = block_content.get("external")
        if isinstance(external, dict) and external.get("url"):
            return str(external["url"])

        file_obj = block_content.get("file")
        if isinstance(file_obj, dict) and file_obj.get("url"):
            return str(file_obj["url"])

        # Some link-like block types may expose nested link metadata.
        if block_type in {"link_to_page"}:
            page_id = block_content.get("page_id")
            if page_id:
                return f"https://www.notion.so/{page_id.replace('-', '')}"

        return ""
    
    def append_blocks_to_page(
        self, 
        page_id: str, 
        blocks: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Append new blocks to the end of a page.
        
        Args:
            page_id: The Notion page ID
            blocks: List of block objects to append
            
        Returns:
            Response from Notion API with created blocks
            
        Example blocks format:
            [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "Hello"}}]
                    }
                }
            ]
        """
        return self._request(
            "PATCH",
            f"/blocks/{page_id}/children",
            json={"children": blocks}
        )
    
    def update_block(
        self, 
        block_id: str, 
        block_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing block's content.
        
        Args:
            block_id: The block ID to update
            block_data: The updated block content
            
        Returns:
            Updated block object
        """
        return self._request("PATCH", f"/blocks/{block_id}", json=block_data)
    
    def delete_block(self, block_id: str) -> Dict[str, Any]:
        """
        Delete a block (moves to trash).
        
        Args:
            block_id: The block ID to delete
            
        Returns:
            Deleted block object with archived=True
        """
        return self._request("DELETE", f"/blocks/{block_id}")
    
    @staticmethod
    def create_text_block(
        text: str, 
        block_type: str = "paragraph",
        bold: bool = False,
        italic: bool = False,
        color: str = "default"
    ) -> Dict[str, Any]:
        """
        Helper to create a text block in Notion format.
        
        Args:
            text: The text content
            block_type: Block type (paragraph, heading_1, heading_2, heading_3, bulleted_list_item, etc.)
            bold: Whether text should be bold
            italic: Whether text should be italic
            color: Text color (default, gray, brown, orange, yellow, green, blue, purple, pink, red)
            
        Returns:
            Block object ready to be appended to a page
        """
        return {
            "object": "block",
            "type": block_type,
            block_type: {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": text},
                    "annotations": {
                        "bold": bold,
                        "italic": italic,
                        "color": color
                    }
                }]
            }
        }

    def iterate_search_results(
        self,
        query: str = "",
        filter_type: Optional[str] = None,
        page_size: int = 100,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Iterate all Notion search results using cursor pagination.
        """
        start_cursor: Optional[str] = None

        while True:
            response = self.search(
                query=query,
                page_size=page_size,
                start_cursor=start_cursor,
                filter_type=filter_type,
            )
            for result in response.get("results", []):
                yield result

            if not response.get("has_more"):
                break
            start_cursor = response.get("next_cursor")
            if not start_cursor:
                break

    @staticmethod
    def extract_title(obj: Dict[str, Any]) -> str:
        """
        Extract a human-readable title from a Notion page or database object.
        """
        title_from_property = ""
        properties = obj.get("properties", {})

        if obj.get("object") == "page":
            title_candidates = [
                value for value in properties.values() if isinstance(value, dict) and value.get("type") == "title"
            ]
            if title_candidates:
                rich = title_candidates[0].get("title", [])
                title_from_property = "".join(part.get("plain_text", "") for part in rich).strip()
        elif obj.get("object") == "database":
            rich = obj.get("title", [])
            title_from_property = "".join(part.get("plain_text", "") for part in rich).strip()

        return title_from_property

    @staticmethod
    def extract_parent_info(obj: Dict[str, Any]) -> tuple[str, str]:
        """
        Extract normalized parent type/id from Notion object payload.
        """
        parent = obj.get("parent", {}) or {}
        parent_type = parent.get("type", "")
        parent_id = ""

        if parent_type == "database_id":
            parent_id = parent.get("database_id", "")
        elif parent_type == "page_id":
            parent_id = parent.get("page_id", "")
        elif parent_type == "block_id":
            parent_id = parent.get("block_id", "")
        elif parent_type == "workspace":
            parent_id = "workspace"

        return parent_type, parent_id
