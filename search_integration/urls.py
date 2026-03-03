from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('health/', views.health_status, name='health_status'),
    path('stats-json/', views.rag_stats_json, name='stats_json'),
    path('search/', views.search_documents, name='search_documents'),    
    path('ingest/', views.ingest_document, name='ingest_document'),
    path('ingest/upload/', views.ingest_document_upload, name='ingest_document_upload'),
    path('delete/', views.delete_document, name='delete_document'),
    path('delete-index/', views.delete_index, name='delete_index'),
]
