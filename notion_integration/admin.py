from django.contrib import admin
from django.utils.html import format_html

from .models import NotionContent


@admin.register(NotionContent)
class NotionContentAdmin(admin.ModelAdmin):
    list_display = (
        "notion_id",
        "object_type",
        "title",
        "parent_type",
        "last_edited_time",
        "last_ingested_at",
        "synced_at",
        "is_archived",
        "text_preview",
        "source_link",
    )
    list_filter = ("object_type", "is_archived", "parent_type", "last_edited_time", "last_ingested_at")
    search_fields = ("notion_id", "title", "url", "plain_text")
    ordering = ("-last_edited_time", "-synced_at")
    list_per_page = 50
    list_max_show_all = 500
    date_hierarchy = "last_edited_time"

    readonly_fields = (
        "notion_id",
        "object_type",
        "title",
        "url",
        "parent_type",
        "parent_notion_id",
        "last_edited_time",
        "is_archived",
        "plain_text",
        "raw_metadata",
        "content_hash",
        "rag_document_id",
        "last_ingested_at",
        "synced_at",
    )

    fieldsets = (
        ("Core", {"fields": ("notion_id", "object_type", "title", "url")}),
        ("Hierarchy", {"fields": ("parent_type", "parent_notion_id")}),
        ("Timing", {"fields": ("last_edited_time", "last_ingested_at", "synced_at")}),
        ("Status", {"fields": ("is_archived",)}),
        ("RAG Tracking", {"fields": ("rag_document_id", "content_hash")}),
        ("Content", {"fields": ("plain_text",), "classes": ("collapse",)}),
        ("Raw Metadata", {"fields": ("raw_metadata",), "classes": ("collapse",)}),
    )

    def text_preview(self, obj: NotionContent) -> str:
        if not obj.plain_text:
            return ""
        preview = obj.plain_text[:120].replace("\n", " ").strip()
        return f"{preview}..." if len(obj.plain_text) > 120 else preview

    text_preview.short_description = "Text Preview"

    def source_link(self, obj: NotionContent) -> str:
        if not obj.url:
            return ""
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Open</a>', obj.url)

    source_link.short_description = "Source"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    def get_model_perms(self, request):
        return {
            "add": False,
            "change": False,
            "delete": False,
            "view": True,
        }
