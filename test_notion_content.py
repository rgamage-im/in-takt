#!/usr/bin/env python
"""
Test script for Notion content operations.

Usage:
    python test_notion_content.py <page_id>

Example:
    python test_notion_content.py abc123def456
"""
import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from notion_integration.services import NotionService


def test_read_page(page_id: str):
    """Test reading a Notion page."""
    print(f"\n{'='*60}")
    print(f"Testing Notion Page Read: {page_id}")
    print(f"{'='*60}\n")
    
    service = NotionService()
    
    # Get page content
    print("📖 Fetching page content...")
    content = service.get_page_content(page_id, recursive=True)
    
    # Display metadata
    print("\n📋 Page Metadata:")
    metadata = content["metadata"]
    print(f"  ID: {metadata.get('id')}")
    print(f"  Created: {metadata.get('created_time')}")
    print(f"  Last Edited: {metadata.get('last_edited_time')}")
    print(f"  URL: {metadata.get('url')}")
    
    # Display blocks
    blocks = content["blocks"]
    print(f"\n📦 Total Blocks: {len(blocks)}")
    
    if blocks:
        print("\n🧱 First 5 Blocks:")
        for i, block in enumerate(blocks[:5], 1):
            block_type = block.get("type")
            print(f"  {i}. {block_type} (ID: {block['id'][:8]}...)")
    
    # Display text content
    text_content = content["text_content"]
    print(f"\n📝 Extracted Text Content ({len(text_content)} characters):")
    print("-" * 60)
    print(text_content[:500] if len(text_content) > 500 else text_content)
    if len(text_content) > 500:
        print(f"\n... (truncated, {len(text_content) - 500} more characters)")
    print("-" * 60)
    
    return content


def test_append_block(page_id: str):
    """Test appending a block to a page."""
    print(f"\n{'='*60}")
    print(f"Testing Block Append")
    print(f"{'='*60}\n")
    
    service = NotionService()
    
    # Create test blocks
    blocks = [
        service.create_text_block(
            "🤖 Test from Teams Webhook Integration", 
            block_type="heading_2",
            bold=True,
            color="blue"
        ),
        service.create_text_block(
            f"This block was added by the test script at {__import__('datetime').datetime.now().isoformat()}",
            block_type="paragraph"
        ),
        service.create_text_block(
            "✅ Notion API integration is working!",
            block_type="bulleted_list_item",
            bold=True
        )
    ]
    
    print("📝 Appending blocks to page...")
    result = service.append_blocks_to_page(page_id, blocks)
    
    print(f"\n✅ Successfully added {len(result.get('results', []))} blocks")
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_notion_content.py <page_id>")
        print("\nExample:")
        print("  python test_notion_content.py abc123def456")
        print("\nTo find a page ID:")
        print("  1. Open a Notion page in your browser")
        print("  2. Copy the ID from the URL: notion.so/Your-Page-<THIS_IS_THE_ID>")
        sys.exit(1)
    
    page_id = sys.argv[1]
    
    try:
        # Test reading
        content = test_read_page(page_id)
        
        # Ask before appending
        print("\n" + "="*60)
        response = input("\n📝 Would you like to append a test block to this page? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            test_append_block(page_id)
            print("\n✅ Test completed successfully!")
        else:
            print("\n✅ Read test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
