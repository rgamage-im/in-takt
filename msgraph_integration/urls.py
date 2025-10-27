"""
Microsoft Graph Integration URLs
"""
from django.urls import path
from .views import UserProfileView, UserListView, UserSearchView
from .auth_views import GraphLoginView, GraphCallbackView, GraphLogoutView, MyProfilePageView
from .api_views import MyProfileAPIView, MyMessagesAPIView, MyCalendarAPIView

app_name = 'msgraph'

urlpatterns = [
    # OAuth Authentication Routes
    path('login/', GraphLoginView.as_view(), name='graph-login'),
    path('callback/', GraphCallbackView.as_view(), name='graph-callback'),
    path('logout/', GraphLogoutView.as_view(), name='graph-logout'),
    
    # Profile Page (HTML)
    path('profile/', MyProfilePageView.as_view(), name='my-profile-page'),
    
    # API Routes - Delegated Permissions (uses session token)
    path('api/me/', MyProfileAPIView.as_view(), name='api-my-profile'),
    path('api/me/messages/', MyMessagesAPIView.as_view(), name='api-my-messages'),
    path('api/me/calendar/', MyCalendarAPIView.as_view(), name='api-my-calendar'),
    
    # Legacy API Routes - Client Credentials (kept for reference)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    path('users/<str:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('me/', UserProfileView.as_view(), {'user_id': 'me'}, name='my-profile'),
]
