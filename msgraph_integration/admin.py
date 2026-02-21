from django.contrib import admin
from .models import GraphSubscription, TeamsWebhookNotification, CompanyAssistantSearchLog


@admin.register(GraphSubscription)
class GraphSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscription_id', 'team_id', 'channel_id', 'status', 'expiration_datetime', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subscription_id', 'team_id', 'channel_id', 'description')
    readonly_fields = ('subscription_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Subscription Info', {
            'fields': ('subscription_id', 'resource', 'change_type', 'status')
        }),
        ('URLs', {
            'fields': ('notification_url', 'lifecycle_notification_url')
        }),
        ('Security', {
            'fields': ('client_state',),
            'classes': ('collapse',)
        }),
        ('Teams Info', {
            'fields': ('team_id', 'channel_id', 'description')
        }),
        ('Timing', {
            'fields': ('expiration_datetime', 'created_at', 'updated_at')
        }),
    )


@admin.register(TeamsWebhookNotification)
class TeamsWebhookNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'change_type', 'message_id', 'team_id', 'channel_id', 'received_at', 'processed')
    list_filter = ('change_type', 'processed', 'received_at')
    search_fields = ('graph_subscription_id', 'message_id', 'team_id', 'channel_id')
    readonly_fields = ('notification_id', 'graph_subscription_id', 'change_type', 'resource', 
                      'resource_data_id', 'tenant_id', 'team_id', 'channel_id', 
                      'message_id', 'payload', 'received_at')
    
    fieldsets = (
        ('Notification Info', {
            'fields': ('notification_id', 'graph_subscription_id', 'change_type', 'processed')
        }),
        ('Teams Details', {
            'fields': ('team_id', 'channel_id', 'message_id', 'tenant_id')
        }),
        ('Resource', {
            'fields': ('resource', 'resource_data_id')
        }),
        ('Payload', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('received_at',)
        }),
    )


@admin.register(CompanyAssistantSearchLog)
class CompanyAssistantSearchLogAdmin(admin.ModelAdmin):
    list_display = ('requested_at', 'request_type', 'account_identifier', 'query_preview')
    list_filter = ('request_type', 'requested_at')
    search_fields = ('account_identifier', 'query', 'user__username', 'user__email')
    readonly_fields = ('requested_at', 'request_type', 'query', 'user', 'account_identifier')
    ordering = ('-requested_at',)
    list_per_page = 50

    def query_preview(self, obj):
        return obj.query[:120] + ('...' if len(obj.query) > 120 else '')

    query_preview.short_description = 'Query'
