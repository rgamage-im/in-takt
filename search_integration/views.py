import requests
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse


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
            # Check if there are actual results, not just total_results field
            if count_data.get("results") and len(count_data.get("results", [])) > 0:
                document_count = count_data.get("total_results", 0)
            else:
                # No actual results, so count is 0 even if total_results says otherwise
                document_count = 0
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
        # Prepare search payload with ACL filtering
        payload = {
            "query": query,
            "top_k": top_k,
            "vector_weight": vector_weight
        }
        
        # Add ACL filters using current user's email from Azure AD SSO
        if request.user.is_authenticated:
            user_email = request.user.email
            # Get user groups from social auth extra_data if available
            user_groups = []
            try:
                social = request.user.social_auth.filter(provider='azuread-tenant-oauth2').first()
                if social and social.extra_data:
                    # Azure AD groups are typically in extra_data
                    user_groups = social.extra_data.get('groups', [])
            except:
                pass
            
            if user_email:
                payload["acl_users"] = [user_email]
            if user_groups:
                payload["acl_groups"] = user_groups
        
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


@login_required
@require_http_methods(["GET", "POST"])
def ingest_document(request):
    """Document ingestion form and handler"""
    if request.method == "GET":
        return render(request, "search/ingest_document.html")
    
    # Handle POST - submit document for ingestion
    content = request.POST.get("content", "").strip()
    source_type = request.POST.get("source_type", "local")
    file_name = request.POST.get("file_name", "").strip()
    title = request.POST.get("title", "").strip()
    author = request.POST.get("author", "").strip()
    
    if not content:
        context = {
            "error": "Document content is required",
            "success": False
        }
        return render(request, "search/ingest_result_partial.html", context)
    
    try:
        # Build metadata
        # Use file_name as source identifier, or generate a generic one
        source_identifier = file_name if file_name else f"portal-upload-{request.user.username}"
        
        metadata = {
            "source": source_identifier,
            "source_type": source_type,
            "file_type": "text"
        }
        
        if file_name:
            metadata["file_name"] = file_name
        if title:
            metadata["title"] = title
        else:
            # If no title provided, use file_name as fallback
            if file_name:
                metadata["title"] = file_name
        if author:
            metadata["author"] = author
        
        # Add ACL - default to current user
        acl = {}
        if request.user.is_authenticated and request.user.email:
            acl["allowed_users"] = [request.user.email]
            
            # Try to get user's groups from Azure AD
            try:
                social = request.user.social_auth.filter(provider='azuread-tenant-oauth2').first()
                if social and social.extra_data:
                    user_groups = social.extra_data.get('groups', [])
                    if user_groups:
                        acl["allowed_groups"] = user_groups
            except:
                pass
        
        # Prepare payload
        payload = {
            "content": content,
            "metadata": metadata
        }
        if acl:
            payload["acl"] = acl
        
        # Call RAG API ingest endpoint
        response = requests.post(
            f"{settings.RAG_API_BASE_URL}/api/v1/ingest/document",
            headers={
                "X-API-Key": settings.RAG_API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        context = {
            "success": True,
            "document_id": data.get("document_id"),
            "chunks_indexed": data.get("chunks_indexed", 0),
            "error": None
        }
        
    except requests.exceptions.Timeout:
        context = {
            "error": "Ingestion request timed out. The document may be too large.",
            "success": False
        }
    except requests.exceptions.ConnectionError:
        context = {
            "error": "Cannot connect to RAG API. Please check if the service is running.",
            "success": False
        }
    except requests.exceptions.HTTPError as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        context = {
            "error": f"Ingestion failed: {error_detail}",
            "success": False
        }
    except Exception as e:
        context = {
            "error": f"Unexpected error: {str(e)}",
            "success": False
        }
    
    return render(request, "search/ingest_result_partial.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def delete_document(request):
    """Document deletion form and handler"""
    if request.method == "GET":
        return render(request, "search/delete_document.html")
    
    # Handle POST - delete document
    document_id = request.POST.get("document_id", "").strip()
    
    if not document_id:
        context = {
            "error": "Document ID is required",
            "success": False
        }
        return render(request, "search/delete_result_partial.html", context)
    
    try:
        # Call RAG API delete endpoint
        response = requests.delete(
            f"{settings.RAG_API_BASE_URL}/api/v1/ingest/document/{document_id}",
            headers={
                "X-API-Key": settings.RAG_API_KEY
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        context = {
            "success": True,
            "document_id": document_id,
            "chunks_deleted": data.get("chunks_deleted", 0),
            "error": None
        }
        
    except requests.exceptions.Timeout:
        context = {
            "error": "Deletion request timed out.",
            "success": False
        }
    except requests.exceptions.ConnectionError:
        context = {
            "error": "Cannot connect to RAG API. Please check if the service is running.",
            "success": False
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            context = {
                "error": f"Document '{document_id}' not found.",
                "success": False
            }
        else:
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            context = {
                "error": f"Deletion failed: {error_detail}",
                "success": False
            }
    except Exception as e:
        context = {
            "error": f"Unexpected error: {str(e)}",
            "success": False
        }
    
    return render(request, "search/delete_result_partial.html", context)

