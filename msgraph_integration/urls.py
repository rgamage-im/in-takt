"""
Microsoft Graph Integration URLs
"""
from django.urls import path
from .auth_views import (
    GraphLoginView,
    GraphCallbackView,
    GraphLogoutView,
    MyProfilePageView,
    GraphExploreView,
    TeamsMessagesTableView,
    ExpenseReceiptsTableView,
    TeamsWebhooksView,
    CompanyAssistantView
)
from .api_views import (
    MyProfileAPIView,
    MyMessagesAPIView,
    MyCalendarAPIView,
    MyTeamsAPIView,
    MyTeamsChannelMessagesAPIView,
    MyOneDriveAPIView,
    MyDrivesListAPIView,
    OneDriveFolderContentsAPIView,
    OneDriveSearchAPIView,
    OneDriveSearchAllAPIView,
    SharePointSitesAPIView,
    AllAccessibleDrivesAPIView,
    SearchAllDrivesIncludingSharePointAPIView,
    GlobalSearchAPIView,
    TeamsSearchAPIView,
    EmailSearchAPIView,
    AssistantChatAPIView,
    ExpenseReceiptsAPIView,
    DownloadFileAPIView,
    UploadReceiptToQuickBooksAPIView,
    # Webhook and subscription views
    TeamsWebhookView,
    CreateTeamsChannelSubscriptionAPIView,
    ListSubscriptionsAPIView,
    DeleteSubscriptionAPIView,
    ListNotificationsAPIView
)

app_name = 'msgraph'

urlpatterns = [
    # OAuth Authentication Routes
    path('login/', GraphLoginView.as_view(), name='graph-login'),
    path('callback/', GraphCallbackView.as_view(), name='graph-callback'),
    path('logout/', GraphLogoutView.as_view(), name='graph-logout'),
    
    # Explore - Auto-login if needed
    path('explore/', GraphExploreView.as_view(), name='graph-explore'),
    
    # Profile Page (HTML)
    path('profile/', MyProfilePageView.as_view(), name='my-profile-page'),
    
    # Teams Messages Table (HTML)
    path('teams/messages/', TeamsMessagesTableView.as_view(), name='teams-messages-table'),

    # Expense Receipts Table (HTML)
    path('receipts/expense/', ExpenseReceiptsTableView.as_view(), name='expense-receipts-table'),
    
    # Teams Webhooks Management (HTML)
    path('webhooks/teams/', TeamsWebhooksView.as_view(), name='teams-webhooks'),
    
    # Company Assistant (HTML)
    path('assistant/', CompanyAssistantView.as_view(), name='company-assistant'),

    # API Routes - Delegated Permissions (uses session token)
    path('api/me/', MyProfileAPIView.as_view(), name='api-my-profile'),
    path('api/me/messages/', MyMessagesAPIView.as_view(), name='api-my-messages'),
    path('api/me/calendar/', MyCalendarAPIView.as_view(), name='api-my-calendar'),
    path('api/me/teams/', MyTeamsAPIView.as_view(), name='api-my-teams'),
    path('api/me/teams/messages/', MyTeamsChannelMessagesAPIView.as_view(), name='api-my-teams-messages'),
    
    # OneDrive API Routes
    path('api/me/drive/', MyOneDriveAPIView.as_view(), name='api-my-drive'),
    path('api/me/drives/', MyDrivesListAPIView.as_view(), name='api-my-drives-list'),
    path('api/me/drive/contents/', OneDriveFolderContentsAPIView.as_view(), name='api-drive-folder-contents'),
    path('api/me/drive/search/', OneDriveSearchAPIView.as_view(), name='api-drive-search'),
    path('api/me/drive/search-all/', OneDriveSearchAllAPIView.as_view(), name='api-drive-search-all'),
    path('api/me/drive/download/', DownloadFileAPIView.as_view(), name='api-download-file'),
    
    # SharePoint API Routes
    path('api/sharepoint/sites/', SharePointSitesAPIView.as_view(), name='api-sharepoint-sites'),
    path('api/drives/all/', AllAccessibleDrivesAPIView.as_view(), name='api-all-drives'),
    path('api/drives/search-all/', SearchAllDrivesIncludingSharePointAPIView.as_view(), name='api-search-all-drives'),
    
    # Global Search API
    path('api/search/global/', GlobalSearchAPIView.as_view(), name='api-global-search'),
    path('api/search/teams/', TeamsSearchAPIView.as_view(), name='api-teams-search'),
    path('api/search/email/', EmailSearchAPIView.as_view(), name='api-email-search'),
    path('api/assistant/chat/', AssistantChatAPIView.as_view(), name='api-assistant-chat'),
    
    # Expense Receipts API
    path('api/receipts/expense/', ExpenseReceiptsAPIView.as_view(), name='api-expense-receipts'),
    path('api/receipts/upload-to-quickbooks/', UploadReceiptToQuickBooksAPIView.as_view(), name='api-upload-receipt-to-qb'),
    
    # Webhook endpoints (public - no auth required)
    path('api/webhooks/teams/', TeamsWebhookView.as_view(), name='teams-webhook'),
    
    # Subscription management API (authenticated)
    path('api/subscriptions/create/', CreateTeamsChannelSubscriptionAPIView.as_view(), name='create-subscription'),
    path('api/subscriptions/', ListSubscriptionsAPIView.as_view(), name='list-subscriptions'),
    path('api/subscriptions/<str:subscription_id>/delete/', DeleteSubscriptionAPIView.as_view(), name='delete-subscription'),
    path('api/notifications/', ListNotificationsAPIView.as_view(), name='list-notifications'),
]
