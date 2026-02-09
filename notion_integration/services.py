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

    def get_page_content(self, page_id: str, recursive: bool = True) -> Dict[str, Any]:
        """
        Get full page content including metadata and all blocks.
        
        Args:
            page_id: The Notion page ID
            recursive: If True, fetches nested blocks recursively
            
        Returns:
            Dict containing:
                - metadata: Page properties and metadata
                - blocks: List of all blocks with their content
                - text_content: Plain text extracted from all blocks
        """
        # Get page metadata
        page_metadata = self.retrieve_page(page_id)
        
        # Get all blocks
        all_blocks = self._get_all_blocks_recursive(page_id, recursive=recursive)
        
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
        recursive: bool = True
    ) -> list[Dict[str, Any]]:
        """
        Recursively fetch all blocks and their children.
        """
        all_blocks = []
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
                all_blocks.append(block)
                
                # If block has children and recursive is enabled, fetch them
                if recursive and block.get("has_children", False):
                    child_blocks = self._get_all_blocks_recursive(
                        block["id"], 
                        recursive=True
                    )
                    # Add children to the block
                    block["children"] = child_blocks
                    all_blocks.extend(child_blocks)
            
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")
        
        return all_blocks
    
    def _extract_text_from_blocks(self, blocks: list[Dict[str, Any]]) -> str:
        """
        Extract plain text content from Notion blocks.
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
                    if text_obj.get("type") == "text":
                        text_parts.append(text_obj.get("text", {}).get("content", ""))
            
            # Handle special block types
            elif block_type == "child_page":
                text_parts.append(f"[Child Page: {block_content.get('title', '')}]")
            
            elif block_type == "child_database":
                text_parts.append(f"[Child Database: {block_content.get('title', '')}]")
        
        return "\n".join(text_parts)
    
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

