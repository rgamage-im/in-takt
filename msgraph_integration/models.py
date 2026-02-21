"""
Microsoft Graph Integration Models
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
import secrets


class GraphSubscription(models.Model):
    """
    Store Microsoft Graph webhook subscriptions
    """
    subscription_id = models.CharField(max_length=255, unique=True, db_index=True)
    resource = models.CharField(max_length=500, help_text="Microsoft Graph resource path (e.g., /teams/{id}/channels/{id}/messages)")
    change_type = models.CharField(max_length=100, help_text="Comma-separated list: created, updated, deleted")
    notification_url = models.URLField(help_text="Webhook endpoint URL")
    expiration_datetime = models.DateTimeField(help_text="When the subscription expires")
    client_state = models.CharField(max_length=255, help_text="Secret token for validation")
    
    # Optional fields
    lifecycle_notification_url = models.URLField(blank=True, null=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('deleted', 'Deleted'),
        ('error', 'Error'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional info
    team_id = models.CharField(max_length=255, blank=True, null=True, help_text="Teams team ID if applicable")
    channel_id = models.CharField(max_length=255, blank=True, null=True, help_text="Teams channel ID if applicable")
    description = models.TextField(blank=True, null=True, help_text="Human-readable description")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'expiration_datetime']),
        ]
    
    def __str__(self):
        return f"Subscription {self.subscription_id[:8]}... ({self.resource})"
    
    def is_expired(self):
        """Check if subscription has expired"""
        return timezone.now() >= self.expiration_datetime
    
    @staticmethod
    def generate_client_state():
        """Generate a secure random client state token"""
        return secrets.token_urlsafe(32)


class TeamsWebhookNotification(models.Model):
    """
    Log incoming webhook notifications from Microsoft Graph
    """
    subscription = models.ForeignKey(
        GraphSubscription, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True,
        blank=True
    )
    
    # Notification details
    notification_id = models.CharField(max_length=255, help_text="Unique ID from Microsoft Graph")
    graph_subscription_id = models.CharField(max_length=255, db_index=True, help_text="Subscription ID from notification")
    change_type = models.CharField(max_length=50, help_text="created, updated, or deleted")
    resource = models.CharField(max_length=500, help_text="Resource path from notification")
    resource_data_id = models.CharField(max_length=255, blank=True, null=True, help_text="Resource ID (e.g., message ID)")
    
    # Teams-specific fields
    tenant_id = models.CharField(max_length=255, blank=True, null=True)
    team_id = models.CharField(max_length=255, blank=True, null=True)
    channel_id = models.CharField(max_length=255, blank=True, null=True)
    message_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Full payload for debugging
    payload = models.JSONField(help_text="Full notification payload")
    
    # Metadata
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed = models.BooleanField(default=False, help_text="Whether this notification has been processed")
    
    class Meta:
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['graph_subscription_id', '-received_at']),
            models.Index(fields=['processed', '-received_at']),
        ]
    
    def __str__(self):
        return f"Notification {self.change_type} - {self.resource_data_id or 'N/A'} at {self.received_at}"


class CompanyAssistantSearchLog(models.Model):
    """
    Audit log for Company Assistant searches.
    """

    REQUEST_TYPE_CHAT = "chat"
    REQUEST_TYPE_RAW_SEARCH = "raw_search"
    REQUEST_TYPE_CHOICES = [
        (REQUEST_TYPE_CHAT, "Chat"),
        (REQUEST_TYPE_RAW_SEARCH, "Raw Search"),
    ]

    requested_at = models.DateTimeField(auto_now_add=True, db_index=True)
    query = models.TextField()
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="company_assistant_search_logs",
    )
    account_identifier = models.CharField(
        max_length=255,
        blank=True,
        help_text="User email or account name captured at request time.",
    )

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["request_type", "-requested_at"]),
        ]

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.account_identifier or 'unknown'} - {self.requested_at}"
