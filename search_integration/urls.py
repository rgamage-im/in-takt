from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('health/', views.health_status, name='health_status'),
    path('search/', views.search_documents, name='search_documents'),    path('ingest/', views.ingest_document, name='ingest_document'),
    path('delete/', views.delete_document, name='delete_document'),]
