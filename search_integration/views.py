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
        
        # Get document count via search with wildcard
        try:
            count_response = requests.post(
                f"{settings.RAG_API_BASE_URL}/api/v1/retrieve/search",
                headers={
                    "X-API-Key": settings.RAG_API_KEY,
                    "Content-Type": "application/json"
                },
                json={"query": "*", "top_k": 1},
                timeout=5
            )
            count_response.raise_for_status()
            count_data = count_response.json()
            document_count = count_data.get("total_results", 0)
        except:
            document_count = None
        
        context = {
            "health": health_data,
            "readiness": readiness_data,
            "document_count": document_count,
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


@login_required
@require_http_methods(["POST"])
def search_documents(request):
    """HTMX endpoint to search documents"""
    query = request.POST.get("query", "").strip()
    top_k = int(request.POST.get("top_k", 10))
    vector_weight = float(request.POST.get("vector_weight", 0.5))
    
    if not query:
        context = {
            "error": "Search query is required",
            "results": []
        }
        return render(request, "search/search_results_partial.html", context)
    
    try:
        # Prepare search payload
        payload = {
            "query": query,
            "top_k": top_k,
            "vector_weight": vector_weight
        }
        
        # Call RAG API search endpoint
        response = requests.post(
            f"{settings.RAG_API_BASE_URL}/api/v1/retrieve/search",
            headers={
                "X-API-Key": settings.RAG_API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        context = {
            "query": query,
            "results": data.get("results", []),
            "total_results": data.get("total_results", 0),
            "vector_weight": vector_weight,
            "error": None
        }
        
    except requests.exceptions.Timeout:
        context = {
            "error": "Search request timed out. Try a simpler query or reduce the number of results.",
            "query": query,
            "results": []
        }
    except requests.exceptions.ConnectionError:
        context = {
            "error": "Cannot connect to RAG API. Please check if the service is running.",
            "query": query,
            "results": []
        }
    except requests.exceptions.HTTPError as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        context = {
            "error": f"Search failed: {error_detail}",
            "query": query,
            "results": []
        }
    except Exception as e:
        context = {
            "error": f"Unexpected error: {str(e)}",
            "query": query,
            "results": []
        }
    
    return render(request, "search/search_results_partial.html", context)
