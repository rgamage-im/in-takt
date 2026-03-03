"""
Notion Integration URLs
"""
from django.urls import path

from .api_views import (
    NotionSearchAPIView,
    NotionPageContentAPIView,
    NotionPageDetailAPIView,
    NotionSyncAPIView,
    NotionSyncAsyncAPIView,
    NotionSyncJobStatusAPIView,
    NotionSyncJobCancelAPIView,
    NotionSyncActiveJobAPIView,
    NotionSyncLatestJobAPIView,
    NotionIngestToRAGAPIView,
)

app_name = "notion"

urlpatterns = [
    path("api/search/", NotionSearchAPIView.as_view(), name="api-search"),
    path("api/pages/<str:page_id>/", NotionPageDetailAPIView.as_view(), name="api-page-detail"),
    path("api/pages/<str:page_id>/content/", NotionPageContentAPIView.as_view(), name="api-page-content"),
    path("api/sync/", NotionSyncAPIView.as_view(), name="api-sync"),
    path("api/sync/async/", NotionSyncAsyncAPIView.as_view(), name="api-sync-async"),
    path("api/sync/jobs/active/", NotionSyncActiveJobAPIView.as_view(), name="api-sync-jobs-active"),
    path("api/sync/jobs/latest/", NotionSyncLatestJobAPIView.as_view(), name="api-sync-jobs-latest"),
    path("api/sync/jobs/<str:job_id>/", NotionSyncJobStatusAPIView.as_view(), name="api-sync-job-status"),
    path("api/sync/jobs/<str:job_id>/cancel/", NotionSyncJobCancelAPIView.as_view(), name="api-sync-job-cancel"),
    path("api/ingest-rag/", NotionIngestToRAGAPIView.as_view(), name="api-ingest-rag"),
]
