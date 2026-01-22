from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('health/', views.health_status, name='health_status'),
    path('search/', views.search_documents, name='search_documents'),
]
