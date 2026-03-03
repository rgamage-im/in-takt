"""
Notion Integration URLs
"""
from django.urls import path

from .api_views import NotionSearchAPIView, NotionPageContentAPIView, NotionPageDetailAPIView, NotionSyncAPIView

app_name = "notion"

urlpatterns = [
    path("api/search/", NotionSearchAPIView.as_view(), name="api-search"),
    path("api/pages/<str:page_id>/", NotionPageDetailAPIView.as_view(), name="api-page-detail"),
    path("api/pages/<str:page_id>/content/", NotionPageContentAPIView.as_view(), name="api-page-content"),
    path("api/sync/", NotionSyncAPIView.as_view(), name="api-sync"),
]
