# Quick Start: Testing Teams Webhook Feature

## What Was Built

A complete Microsoft Graph webhook subscription system for Microsoft Teams channel messages:

1. ✅ **Database Models**: Store subscriptions and notifications
2. ✅ **Webhook Endpoint**: Receive notifications from Microsoft Graph
3. ✅ **Subscription API**: Create, list, and delete subscriptions programmatically
4. ✅ **Web UI**: User-friendly interface to manage subscriptions and view notifications
5. ✅ **Service Methods**: Backend logic for subscription lifecycle management

## Access the Feature

**URL**: https://in-takt.azurewebsites.net/api/msgraph/webhooks/teams/

## Testing Steps

### 1. Get Team and Channel IDs

#### Option A: Microsoft Graph Explorer
1. Go to https://developer.microsoft.com/graph/graph-explorer
2. Sign in with your Microsoft account
3. Run: `GET https://graph.microsoft.com/v1.0/me/joinedTeams`
4. Copy a team `id`
5. Run: `GET https://graph.microsoft.com/v1.0/teams/{team-id}/channels`
6. Copy a channel `id`

#### Option B: Teams URL
From a Teams channel URL, extract:
- `groupId` parameter = Team ID  
- Channel ID is in the path (URL decode it)

### 2. Create a Subscription

1. Navigate to the webhooks page
2. Fill in the form:
   - **Team ID**: Paste the team GUID
   - **Channel ID**: Paste the channel GUID
   - **Description**: "Test subscription for General channel"
   - **Expiration**: 60 minutes
3. Click **Create Subscription**
4. You should see a success message with the subscription ID

### 3. Trigger a Notification

1. Go to the Teams channel you subscribed to
2. Post a new message or edit an existing one
3. Microsoft Graph will send a notification to your webhook endpoint

### 4. View the Notification

**In the Web UI:**
- The "Recent Notifications" section will auto-refresh every 30 seconds
- You should see your notification appear with:
  - Change type (created/updated)
  - Message ID
  - Team and Channel IDs
  - Timestamp
  - Raw payload (expandable)

**In Django Admin:**
1. Navigate to: https://in-takt.azurewebsites.net/admin/
2. Go to: `msgraph_integration > Teams Webhook Notifications`
3. View full notification details and payloads

### 5. Verify Subscription is Active

**In the Web UI:**
- Check the "Active Subscriptions" section
- Your subscription should show status: **Active**
- Expiration time should be displayed

**Via API:**
```bash
curl https://in-takt.azurewebsites.net/api/msgraph/api/subscriptions/
```

## Testing the Webhook Endpoint Directly

### Check if endpoint is accessible:
```bash
curl https://in-takt.azurewebsites.net/api/msgraph/api/webhooks/teams/
```
Expected response: `Webhook endpoint is active`

### Test validation token (simulating Microsoft Graph):
```bash
curl "https://in-takt.azurewebsites.net/api/msgraph/api/webhooks/teams/?validationToken=test123"
```
Expected response: `test123` (in plain text)

## Common Issues and Solutions

### Issue: Subscription creation fails with "Invalid notificationUrl"
**Cause**: The app is not accessible via HTTPS from the internet  
**Solution**: Already deployed to Azure, should work. If testing locally, use ngrok.

### Issue: Subscription created but no notifications received
**Possible causes:**
1. **Subscription expired**: Check expiration time in UI
2. **Wrong IDs**: Verify Team/Channel IDs are correct
3. **Permissions**: Ensure `ChannelMessage.Read.All` permission is granted
4. **Endpoint not responding**: Check Azure App Service logs

**Debug steps:**
1. Check subscription status in UI (should be "Active")
2. Post a message in the Teams channel
3. Check Django admin for new notifications within 30 seconds
4. Check application logs for errors

### Issue: Client state validation errors in logs
**Cause**: Mismatch between stored client_state and notification clientState  
**Solution**: This shouldn't happen. If it does, delete and recreate the subscription.

## What Happens Behind the Scenes

1. **You create subscription** → App calls Microsoft Graph API `/subscriptions`
2. **Microsoft validates webhook** → Sends GET request with validation token
3. **App responds** → Returns validation token in plain text
4. **Microsoft confirms** → Returns subscription ID
5. **App stores subscription** → Saves to database with client_state secret
6. **Message posted in Teams** → Microsoft detects change
7. **Microsoft sends notification** → POST to webhook endpoint
8. **App validates** → Checks client_state matches
9. **App stores notification** → Saves to database with full payload
10. **UI updates** → Shows notification in real-time (30s refresh)

## Next Steps for Workflow Integration

To trigger workflows when notifications arrive, edit:
`msgraph_integration/api_views.py` - `TeamsWebhookView.post()` method

Add your workflow logic after line where `webhook_notification` is created:

```python
# After creating webhook_notification record:
if change_type == 'created' and message_id:
    # Your workflow trigger here
    from your_module import launch_workflow
    launch_workflow(
        team_id=team_id,
        channel_id=channel_id,
        message_id=message_id
    )
    
    # Mark as processed
    webhook_notification.processed = True
    webhook_notification.save()
```

## Expected Behavior

✅ **Successful subscription creation**:
- Green success message in UI
- Subscription appears in "Active Subscriptions" list
- Expiration time is displayed
- Can delete subscription via Delete button

✅ **Successful notification receipt**:
- Notification appears in "Recent Notifications" within 30 seconds of posting message
- Shows: change type, message ID, team/channel IDs, timestamp
- Full payload viewable by expanding details
- Django admin shows full notification record

✅ **Subscription expiration**:
- After expiration time, subscription shows status: "Expired"
- No new notifications received
- Old subscription record remains in database for history

## Monitoring

**Real-time UI**: 
- https://in-takt.azurewebsites.net/api/msgraph/webhooks/teams/
- Auto-refreshes notifications every 30 seconds

**Django Admin**:
- Subscriptions: /admin/msgraph_integration/graphsubscription/
- Notifications: /admin/msgraph_integration/teamswebhooknotification/

**API Endpoints**:
- List subscriptions: `GET /api/msgraph/api/subscriptions/`
- List notifications: `GET /api/msgraph/api/notifications/?limit=50`

## Files Modified/Created

```
msgraph_integration/
├── models.py                 # Added GraphSubscription, TeamsWebhookNotification
├── admin.py                  # Registered models in Django admin
├── api_views.py             # Added TeamsWebhookView, subscription API views
├── auth_views.py            # Added TeamsWebhooksView
├── services.py              # Added subscription methods
├── urls.py                  # Added webhook and management routes
├── templates/msgraph/
│   └── teams_webhooks.html  # New management UI
└── migrations/
    └── 0001_initial.py      # Database migrations

docs/
└── TEAMS_WEBHOOKS.md        # Comprehensive documentation
```

## Ready to Test!

Everything is committed, pushed to GitHub, and will deploy automatically via GitHub Actions. Once deployment completes:

1. Visit the webhooks page
2. Create a test subscription
3. Post a message in the Teams channel
4. Watch the notification appear!

🎉 The feature is now live and ready to trigger workflows!
