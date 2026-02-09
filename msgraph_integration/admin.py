from django.contrib import admin
from .models import GraphSubscription, TeamsWebhookNotification


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

