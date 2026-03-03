from django.db import models


class NotionContent(models.Model):
    OBJECT_TYPE_CHOICES = (
        ("page", "Page"),
        ("database", "Database"),
    )

    notion_id = models.CharField(max_length=64, unique=True)
    object_type = models.CharField(max_length=16, choices=OBJECT_TYPE_CHOICES)
    title = models.CharField(max_length=512, blank=True, default="")
    url = models.URLField(max_length=1024, blank=True, default="")
    parent_type = models.CharField(max_length=64, blank=True, default="")
    parent_notion_id = models.CharField(max_length=64, blank=True, default="")
    last_edited_time = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    plain_text = models.TextField(blank=True, default="")
    raw_metadata = models.JSONField(default=dict, blank=True)
    content_hash = models.CharField(max_length=64, blank=True, default="")
    rag_document_id = models.CharField(max_length=64, blank=True, default="")
    last_ingested_at = models.DateTimeField(null=True, blank=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_edited_time", "-synced_at"]

    def __str__(self) -> str:
        return f"{self.object_type}:{self.title or self.notion_id}"
