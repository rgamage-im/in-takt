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
    TeamsMessagesTableView
)
from .api_views import (
    MyProfileAPIView, 
    MyMessagesAPIView, 
    MyCalendarAPIView,
    MyTeamsAPIView,
    MyTeamsChannelMessagesAPIView
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
    
    # API Routes - Delegated Permissions (uses session token)
    path('api/me/', MyProfileAPIView.as_view(), name='api-my-profile'),
    path('api/me/messages/', MyMessagesAPIView.as_view(), name='api-my-messages'),
    path('api/me/calendar/', MyCalendarAPIView.as_view(), name='api-my-calendar'),
    path('api/me/teams/', MyTeamsAPIView.as_view(), name='api-my-teams'),
    path('api/me/teams/messages/', MyTeamsChannelMessagesAPIView.as_view(), name='api-my-teams-messages'),
]
