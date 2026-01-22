import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET"])
def dashboard(request):
    """Main RAG search dashboard"""
    return render(request, "search/dashboard.html")


@login_required
@require_http_methods(["GET"])
def health_status(request):
    """HTMX endpoint to fetch and render RAG API health status"""
    try:
        # Call RAG API health endpoint
        response = requests.get(
            f"{settings.RAG_API_BASE_URL}/health",
            headers={"X-API-Key": settings.RAG_API_KEY},
            timeout=5
        )
        response.raise_for_status()
        health_data = response.json()
        
        # Call readiness endpoint
        readiness_response = requests.get(
            f"{settings.RAG_API_BASE_URL}/ready",
            headers={"X-API-Key": settings.RAG_API_KEY},
            timeout=5
        )
        readiness_response.raise_for_status()
        readiness_data = readiness_response.json()
        
        context = {
            "health": health_data,
            "readiness": readiness_data,
            "error": None,
            "connected": True
        }
        
    except requests.exceptions.Timeout:
        context = {
            "error": "RAG API timeout - request took too long to respond",
            "error_type": "timeout",
            "connected": False
        }
    except requests.exceptions.ConnectionError:
        context = {
            "error": "Cannot connect to RAG API - is it running?",
            "error_type": "connection",
            "connected": False
        }
    except requests.exceptions.HTTPError as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        context = {
            "error": f"RAG API returned error: {error_detail}",
            "error_type": "http_error",
            "status_code": e.response.status_code,
            "connected": False
        }
    except Exception as e:
        context = {
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown",
            "connected": False
        }
    
    return render(request, "search/health_status_partial.html", context)
