# Teams Webhook Subscriptions

This feature enables the application to receive real-time notifications when messages are created or updated in Microsoft Teams channels via Microsoft Graph webhook subscriptions.

## Overview

The Teams webhook subscription system allows you to:
- Create subscriptions for specific Teams channels to monitor messages
- Receive notifications when messages are created, updated, or deleted
- Store and view notification history
- Manage subscription lifecycle (create, renew, delete)

## Architecture

### Components

1. **Models** (`msgraph_integration/models.py`):
   - `GraphSubscription`: Stores active subscriptions with metadata
   - `TeamsWebhookNotification`: Logs all incoming webhook notifications

2. **Webhook Endpoint** (`/graph/api/webhooks/teams/`):
   - Public endpoint (no authentication) for Microsoft Graph to send notifications
   - Handles validation tokens (GET) and notification payloads (POST)
   - Validates client state for security
   - Parses Teams-specific information from resource paths

3. **Subscription Management API**:
   - `POST /graph/api/subscriptions/create/` - Create new subscription
   - `GET /graph/api/subscriptions/` - List active subscriptions
   - `DELETE /graph/api/subscriptions/{id}/delete/` - Delete subscription
   - `GET /graph/api/notifications/` - List recent notifications

4. **UI** (`/graph/webhooks/teams/`):
   - Web interface to create and manage subscriptions
   - View active subscriptions and their expiration dates
   - Monitor recent notifications in real-time

## Setup

### Prerequisites

1. **Microsoft Graph API Permissions**
   
   Your Azure AD app registration must have the following **Application Permission**:
   - `ChannelMessage.Read.All` - Read all channel messages
   
   **Important**: Application permissions require admin consent in the Azure portal.

2. **Public HTTPS Endpoint**
   
   The webhook endpoint must be:
   - Publicly accessible from the internet
   - Served over HTTPS (required by Microsoft Graph)
   - Able to respond within 10 seconds
   
   For local development, use a tunneling service like:
   - ngrok: `ngrok http 8000`
   - Azure Web App (already has public URL)

3. **Configuration**
   
   Add to your `settings.py` or environment variables:
   ```python
   SITE_URL = 'https://yourdomain.com'  # Your public-facing URL
   ```
   
   Or for Azure App Service, the system will auto-detect the URL.

### Deployment Considerations

- **Webhook URL must be HTTPS**: Microsoft Graph will not send notifications to HTTP endpoints
- **Response time**: Endpoints must respond within 10 seconds or notifications will be dropped
- **Subscription expiration**: Max 4230 minutes (~3 days) for Teams channel messages
- **Rate limiting**: Microsoft throttles endpoints that become slow or unresponsive

## Usage

### Creating a Subscription

#### Via UI:

1. Navigate to **Teams Webhooks** page: `/graph/webhooks/teams/` (or click "Teams Webhooks" in the main navigation)
2. Fill in the form:
   - **Team ID**: The GUID of the Teams team
   - **Channel ID**: The GUID of the channel within that team
   - **Description**: Optional human-readable description
   - **Expiration**: Minutes until subscription expires (max 4230)
3. Click **Create Subscription**

#### Via API:

```python
import requests

url = "https://yourdomain.com/api/msgraph/api/subscriptions/create/"
payload = {
    "team_id": "your-team-id",
    "channel_id": "your-channel-id",
    "description": "Main Team - General channel",
    "expiration_minutes": 60
}

response = requests.post(url, json=payload, headers={
    'Authorization': 'Bearer YOUR_SESSION_TOKEN',
    'Content-Type': 'application/json'
})

print(response.json())
```

### Finding Team and Channel IDs

#### Team Id = 19%3A9T-mYfQRqgAOqz2zBGVpXOchZq3GSWO4z5R9-YQ3-Jc1%40thread.tacv2
#### Foundations channel id = 19:cedb5b3e12ef4358a9668550c0667991@thread.tacv2

#### Method 1: Microsoft Graph Explorer
1. Go to https://developer.microsoft.com/graph/graph-explorer
2. Sign in and consent to permissions
3. Query: `GET https://graph.microsoft.com/v1.0/me/joinedTeams`
4. Find your team, copy the `id`
5. Query: `GET https://graph.microsoft.com/v1.0/teams/{team-id}/channels`
6. Find your channel, copy the `id`

#### Method 2: Teams URL
From a Teams channel URL like:
```
https://teams.microsoft.com/l/channel/19%3aABCD1234...%40thread.tacv2/General?groupId=12345678-1234-1234-1234-123456789abc&tenantId=...
```
- `groupId` = Team ID
- First part after `/channel/` (URL decoded) = Channel ID

### Receiving Notifications

When a message is created/updated in the subscribed channel, Microsoft Graph sends a notification to your webhook endpoint. The notification is automatically:

1. **Validated**: Client state is checked against stored value
2. **Parsed**: Team ID, Channel ID, and Message ID are extracted
3. **Stored**: Full notification payload saved to `TeamsWebhookNotification` table
4. **Logged**: Event is logged for debugging

Access notifications:
- **UI**: Real-time updates on the Teams Webhooks page (`/graph/webhooks/teams/`)
- **API**: `GET /graph/api/notifications/?limit=50`
- **Django Admin**: Navigate to `msgraph_integration > Teams Webhook Notifications`

### Notification Payload Example

```json
{
  "id": "...",
  "subscriptionId": "your-subscription-id",
  "changeType": "created",
  "clientState": "secret-token",
  "tenantId": "...",
  "resource": "teams('team-id')/channels('channel-id')/messages('message-id')",
  "resourceData": {
    "id": "message-id",
    "@odata.type": "#Microsoft.Graph.chatMessage",
    "@odata.id": "..."
  }
}
```

### Subscription Lifecycle

#### Expiration
- Subscriptions expire after the specified time (max 4230 minutes)
- Microsoft Graph stops sending notifications after expiration
- Expired subscriptions are marked with status `expired` in the UI

#### Renewal
Currently manual via API:
```python
from msgraph_integration.services import GraphService

service = GraphService()
service.renew_subscription(subscription_id, expiration_minutes=60)
```

#### Deletion
- Via UI: Click **Delete** button on subscription card
- Via API: `DELETE /api/msgraph/api/subscriptions/{id}/delete/`
- Deletes from both Microsoft Graph and local database

## Workflow Integration

### Processing Notifications

To trigger workflows when notifications arrive, add processing logic in the webhook handler:

```python
# In msgraph_integration/api_views.py - TeamsWebhookView.post()

# After creating webhook_notification record:
if change_type == 'created' and message_id:
    # Launch your workflow here
    from your_workflow_module import process_teams_message
    process_teams_message(
        team_id=team_id,
        channel_id=channel_id,
        message_id=message_id,
        notification_payload=notification
    )
```

### Example: RAG Pipeline Trigger

```python
# Example workflow integration
def process_teams_message(team_id, channel_id, message_id, notification_payload):
    """
    Process a new Teams message through RAG pipeline
    """
    # 1. Fetch full message content via Graph API
    from msgraph_integration.services_delegated import GraphServiceDelegated
    graph = GraphServiceDelegated()
    message = graph.get_channel_message(team_id, channel_id, message_id)
    
    # 2. Extract content
    content = message.get('body', {}).get('content', '')
    
    # 3. Send to RAG API for processing
    import requests
    rag_response = requests.post(
        'https://your-rag-api/process',
        json={'content': content, 'source': 'teams'}
    )
    
    # 4. Post response back to Teams channel
    reply = rag_response.json().get('response')
    graph.post_channel_message(team_id, channel_id, reply)
```

## Security

### Client State Validation
Every notification includes a `clientState` token that must match the one stored during subscription creation. This prevents:
- Unauthorized webhook calls
- Cross-site request forgery
- Spoofed notifications

### Endpoint Security
The webhook endpoint is intentionally public (no authentication) because:
- Microsoft Graph needs to POST notifications without authentication
- Security is provided by client state validation
- The endpoint only creates database records, no sensitive operations

## Monitoring

### Health Checks
Monitor webhook endpoint health:
```bash
curl https://yourdomain.com/graph/api/webhooks/teams/
# Response: "Webhook endpoint is active"
```

### Logs
Application logs include:
- Subscription creation/deletion events
- Notification receipt and processing
- Client state validation failures
- Errors during notification handling

### Django Admin
Access full notification history and subscription details:
- Navigate to `/admin/`
- `msgraph_integration > Graph Subscriptions`
- `msgraph_integration > Teams Webhook Notifications`

## Troubleshooting

### Subscription Creation Fails

**Error**: `Failed to create subscription: Invalid notificationUrl`
- **Cause**: URL is not publicly accessible or not HTTPS
- **Fix**: Deploy to Azure or use ngrok for local testing

**Error**: `Insufficient privileges to complete the operation`
- **Cause**: Missing `ChannelMessage.Read.All` permission
- **Fix**: Add permission in Azure AD app registration and grant admin consent

### Not Receiving Notifications

1. **Check subscription status**: Should be "Active" in UI
2. **Check expiration**: Subscriptions expire after configured time
3. **Test endpoint**: `GET https://yourdomain.com/graph/api/webhooks/teams/`
4. **Check logs**: Look for validation errors or timeouts
5. **Verify client state**: Check database for correct token

### Notification Processing Errors

Check logs for:
- JSON parsing errors
- Database write failures
- Client state mismatches

View raw notifications in Django admin to debug payload structure.

## API Reference

### POST /graph/api/subscriptions/create/
Create a new subscription.

**Request**:
```json
{
  "team_id": "string",
  "channel_id": "string",
  "description": "string (optional)",
  "expiration_minutes": 60
}
```

**Response**:
```json
{
  "success": true,
  "subscription": {
    "id": "subscription-id",
    "resource": "/teams/.../channels/.../messages",
    "expires": "2024-01-01T12:00:00Z",
    "team_id": "...",
    "channel_id": "..."
  }
}
```

### GET /graph/api/subscriptions/
List all active subscriptions.

**Response**:
```json
{
  "subscriptions": [
    {
      "id": "subscription-id",
      "resource": "...",
      "team_id": "...",
      "channel_id": "...",
      "description": "...",
      "expires": "2024-01-01T12:00:00Z",
      "is_expired": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 1
}
```

### DELETE /graph/api/subscriptions/{id}/delete/
Delete a subscription.

**Response**:
```json
{
  "success": true,
  "message": "Subscription deleted"
}
```

### GET /graph/api/notifications/?limit=50
List recent notifications.

**Response**:
```json
{
  "notifications": [
    {
      "id": 1,
      "change_type": "created",
      "resource": "...",
      "team_id": "...",
      "channel_id": "...",
      "message_id": "...",
      "received_at": "2024-01-01T12:00:00Z",
      "processed": false,
      "payload": {...}
    }
  ],
  "count": 1
}
```

## Limitations

- **Subscription duration**: Max 4230 minutes (~3 days) for Teams messages
- **Organization limit**: 10,000 total Teams subscriptions per tenant
- **Endpoint performance**: Must respond within 10 seconds
- **Throttling**: Slow endpoints (>10s for >10% of requests) will be marked as "slow" or "drop"
- **Licensing**: May have licensing requirements depending on API usage pattern

## Next Steps

1. **Add automatic renewal**: Implement background task to renew subscriptions before expiry
2. **Lifecycle notifications**: Handle subscription lifecycle events (reauthorization, expiration warnings)
3. **Resource data encryption**: Enable `includeResourceData: true` for encrypted message content
4. **Workflow triggers**: Connect notifications to your business logic/RAG pipeline
5. **Error handling**: Add retry logic for failed notification processing

## Resources

- [Microsoft Graph Change Notifications](https://learn.microsoft.com/en-us/graph/webhooks)
- [Teams Channel Messages Subscriptions](https://learn.microsoft.com/en-us/graph/teams-changenotifications-chatmessage)
- [Subscription API Reference](https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions)
