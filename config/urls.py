"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    # Home page
    path("", core_views.home, name="home"),
    
    # Auth
    path("logout/", core_views.LogoutView.as_view(), name="logout"),
    
    # Social Auth (Azure AD SSO)
    path("", include("social_django.urls", namespace="social")),
    
    # Admin
    path("admin/", admin.site.urls),
    
    # Microsoft Graph OAuth and Profile
    path("graph/", include("msgraph_integration.urls")),
    
    # QuickBooks OAuth and Dashboard
    path("quickbooks/", include("quickbooks_integration.urls")),
    
    # API endpoints
    path("api/", include("api.urls")),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
