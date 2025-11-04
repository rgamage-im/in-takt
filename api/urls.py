"""
API URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Create a router for ViewSets
router = DefaultRouter()
# Register ViewSets here as we create them
# router.register(r'users', UserViewSet)

app_name = 'api'

urlpatterns = [
    # API Schema and Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
    
    # Router URLs (for ViewSets)
    path('', include(router.urls)),
]
