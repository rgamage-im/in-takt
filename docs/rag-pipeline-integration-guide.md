# RAG Pipeline Backend Integration Guide

**Document Purpose**: Technical specification for integrating the In-Takt Company Data Portal (Django/HTMX) with the RAG (Retrieval-Augmented Generation) Pipeline Backend API.

**Target Audience**: Portal Architect/Developer  
**Date**: January 21, 2026  
**Version**: 1.0 - Development Environment

---

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Development Environment Configuration](#development-environment-configuration)
4. [API Authentication](#api-authentication)
5. [Dashboard Requirements](#dashboard-requirements)
6. [API Endpoints Reference](#api-endpoints-reference)
7. [Integration Examples](#integration-examples)
8. [Error Handling](#error-handling)
9. [Future Production Considerations](#future-production-considerations)

---

## Overview

### What is the RAG Pipeline?
The RAG Pipeline is a Python FastAPI service that provides:
- **Document Ingestion**: Chunks documents, generates embeddings, and indexes them in OpenSearch
- **Hybrid Search**: Vector similarity + BM25 keyword search for document retrieval
- **Health Monitoring**: System health and readiness checks

### Technology Stack
- **Framework**: FastAPI (Python)
- **Vector Database**: OpenSearch 2.12.0
- **Embeddings**: Azure OpenAI (text-embedding-ada-002)
- **Deployment**: Docker Compose (dev), Azure (production TBD)

---

## System Architecture

### Development Environment
```
┌─────────────────────────┐         ┌─────────────────────────┐
│  Company Data Portal    │         │   RAG Pipeline API      │
│  (Django/HTMX)          │◄────────┤   (FastAPI)             │
│  Port: TBD              │  HTTP   │   Port: 8000            │
│  (may need to avoid     │         │   http://localhost:8000 │
│   port 8000 conflict)   │         │                         │
└─────────────────────────┘         └───────────┬─────────────┘
                                                 │
                                    ┌────────────▼─────────────┐
                                    │   OpenSearch Cluster     │
                                    │   Port: 9200             │
                                    │   (Internal Only)        │
                                    └──────────────────────────┘
```

### Component Relationships
- **Portal**: Consumes RAG API, displays dashboard, triggers actions
- **RAG API**: Processes requests, manages document lifecycle
- **OpenSearch**: Stores document chunks, vectors, and metadata (not directly accessed by portal)

---

## Development Environment Configuration

### Base URL
```
http://localhost:8000
```

### Port Conflict Consideration
⚠️ **Important**: The RAG API runs on port 8000 by default. If your Django portal also uses port 8000, you have two options:

**Option 1: Change Django Port** (Recommended)
```bash
# Run Django on port 8080 instead
python manage.py runserver 8080
```

**Option 2: Change RAG API Port**
Modify `docker-compose.yml`:
```yaml
rag-api:
  ports:
    - "8001:8000"  # External:Internal
```
Then use `http://localhost:8001` as base URL.

### Starting the RAG API
```bash
cd c:\github\search-engine
docker-compose up -d
```

The API will be available at `http://localhost:8000` once all containers are healthy (~30-60 seconds after startup).

### API Documentation
Interactive Swagger UI available at:
```
http://localhost:8000/docs
```

---

## API Authentication

### Authentication Method: API Key
All requests to the RAG API must include an API key in the request header.

**Header Format**:
```http
X-API-Key: your-api-key-here
```

### Implementation Notes for Django
```python
# In your Django settings or environment
RAG_API_BASE_URL = "http://localhost:8000"
RAG_API_KEY = "your-secure-api-key"  # To be provided separately

# Example request header
headers = {
    "X-API-Key": settings.RAG_API_KEY,
    "Content-Type": "application/json"
}
```

🔒 **Security Notes**:
- API key will be provided separately via secure channel
- Store in environment variables, not in code
- CORS is disabled for development (same-machine access)

---

## Dashboard Requirements

### 5.1 Status Indicators

#### Health Status
**Endpoint**: `GET /health`

**Display Requirements**:
- **Overall Status**: `healthy` | `degraded` | `unhealthy`
- **OpenSearch Status**: Show cluster health status
- **Color Coding**:
  - Green: `healthy`
  - Yellow: `degraded`
  - Red: `unhealthy`
- **Last Check Timestamp**: Display in user's local timezone

**Response Structure**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-21T10:30:00.000Z",
  "services": {
    "opensearch": {
      "status": "healthy",
      "cluster_status": "green"
    }
  }
}
```

#### Readiness Status
**Endpoint**: `GET /ready`

**Display Requirements**:
- **Status**: `ready` | `not_ready`
- **Color Coding**:
  - Green: `ready`
  - Red: `not_ready`

**Response Structure**:
```json
{
  "status": "ready"
}
```

#### Document Count Metric
**Endpoint**: `GET /api/v1/ingest/initialize`  
(Returns index stats if already exists)

**Display Requirements**:
- Show total number of document chunks indexed
- Refresh via manual button click

**How to Get Count**:
Since there's no dedicated stats endpoint yet, use OpenSearch count API:
```http
POST /api/v1/retrieve/search
Content-Type: application/json

{
  "query": "*",
  "top_k": 1
}
```
The `total_results` field approximates document count (note: this is chunks, not unique documents).

**Recommended**: Request a dedicated `/stats` endpoint from backend team for accurate metrics.

---

### 5.2 Action Buttons

#### Button 1: Ingest Document
**Purpose**: Submit a document for indexing in the RAG system

**Endpoint**: `POST /api/v1/ingest/document`

**UI Requirements**:
- Button label: "Ingest Document"
- Opens modal/form to input:
  - Document content (textarea or file upload that extracts text)
  - Source type (dropdown: `sharepoint`, `onedrive`, `teams`, `notion`, `quickbooks`, `local`, `other`)
  - Source identifier (text input)
  - Optional metadata fields

**Request Payload**:
```json
{
  "content": "Full text content of the document...",
  "metadata": {
    "source": "company-portal-manual",
    "source_type": "local",
    "file_name": "Q4-2025-Report.pdf",
    "file_type": "pdf",
    "author": "John Doe",
    "title": "Q4 2025 Financial Report",
    "created_at": "2025-10-15T10:00:00Z",
    "modified_at": "2025-12-20T15:30:00Z"
  },
  "acl": {
    "allowed_users": ["user123", "user456"],
    "allowed_groups": ["finance-team", "executives"]
  }
}
```

**Response Handling**:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks_indexed": 42,
  "status": "success"
}
```

**UI Feedback**:
- Show success message with document_id and chunks count
- Display error message if ingestion fails
- Disable button during processing (loading state)

---

#### Button 2: Delete Document
**Purpose**: Remove a document and all its chunks from the index

**Endpoint**: `DELETE /api/v1/ingest/document/{document_id}`

**UI Requirements**:
- Button label: "Delete Document"
- Requires document_id input (text field or search)
- Confirmation dialog: "Are you sure you want to delete document {document_id}?"

**Request**: 
```http
DELETE /api/v1/ingest/document/550e8400-e29b-41d4-a716-446655440000
X-API-Key: your-api-key-here
```

**Response Handling**:
```json
{
  "status": "success",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks_deleted": 42
}
```

**UI Feedback**:
- Show success message with chunks deleted count
- Update document count metric
- Display error if document not found or deletion fails

---

#### Button 3: Search Documents
**Purpose**: Test search functionality and preview results

**Endpoint**: `POST /api/v1/retrieve/search`

**UI Requirements**:
- Search input field
- Optional settings:
  - Results count (default: 10, max: 100)
  - Vector weight slider (0.0 to 1.0, default: 0.5)
    - 0.0 = Pure keyword search (BM25)
    - 1.0 = Pure semantic search (vector)
    - 0.5 = Balanced hybrid
- Display results with:
  - Relevance score
  - Content snippet
  - Metadata (source, file name, etc.)

**Request Payload**:
```json
{
  "query": "financial reports from Q4",
  "top_k": 10,
  "vector_weight": 0.5,
  "filters": {
    "source_type": "sharepoint"
  },
  "acl_users": ["current-user-id"],
  "acl_groups": ["user-group-ids"]
}
```

**Response Handling**:
```json
{
  "query": "financial reports from Q4",
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000_0",
      "score": 0.87,
      "content": "Q4 financial results show...",
      "metadata": {
        "source": "sharepoint-site-abc",
        "source_type": "sharepoint",
        "file_name": "Q4-Report.pdf",
        "author": "Jane Smith",
        "title": "Q4 2025 Report"
      },
      "chunk_metadata": {
        "chunk_index": 0,
        "start_char": 0,
        "end_char": 512
      }
    }
  ],
  "total_results": 25
}
```

**UI Display**:
- List results with relevance score (show as percentage or bar)
- Highlight matching content
- Show metadata in collapsible section
- "No results found" message if empty

---

### 5.3 Dashboard Layout Recommendation

```
┌─────────────────────────────────────────────────────────────┐
│  RAG Pipeline Dashboard                              [Refresh]│
├─────────────────────────────────────────────────────────────┤
│  System Status                                               │
│  ┌─────────────┬──────────────┬──────────────────────────┐ │
│  │ Health      │ Readiness    │ Indexed Chunks           │ │
│  │ ● Healthy   │ ● Ready      │ 1,234 chunks             │ │
│  │             │              │ (Manual refresh)         │ │
│  └─────────────┴──────────────┴──────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Actions                                                     │
│  [Ingest Document]  [Delete Document]  [Search Documents]   │
├─────────────────────────────────────────────────────────────┤
│  Recent Activity (optional)                                  │
│  • Document abc-123 ingested (42 chunks) - 2 mins ago      │
│  • Search: "quarterly reports" - 1 hour ago                 │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints Reference

### Base URL
```
http://localhost:8000
```

### Full Endpoint List

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/health` | System health check | Yes |
| GET | `/ready` | Readiness check | Yes |
| POST | `/api/v1/ingest/initialize` | Initialize index (setup) | Yes |
| POST | `/api/v1/ingest/document` | Ingest a document | Yes |
| DELETE | `/api/v1/ingest/document/{document_id}` | Delete a document | Yes |
| POST | `/api/v1/retrieve/search` | Hybrid search | Yes |
| GET | `/api/v1/retrieve/search?q=...` | Simple search (GET) | Yes |
| POST | `/api/v1/retrieve/vector-search` | Pure vector search | Yes |
| POST | `/api/v1/retrieve/bm25-search` | Pure keyword search | Yes |

### Common Headers
```http
X-API-Key: your-api-key-here
Content-Type: application/json
Accept: application/json
```

---

## Integration Examples

### 7.1 Django View Example (Health Check)

```python
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views import View

class RAGHealthView(View):
    def get(self, request):
        """Fetch health status from RAG API"""
        try:
            response = requests.get(
                f"{settings.RAG_API_BASE_URL}/health",
                headers={
                    "X-API-Key": settings.RAG_API_KEY
                },
                timeout=5
            )
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                "status": "error",
                "error": str(e)
            }, status=503)
```

### 7.2 HTMX Integration Example

**HTML Template**:
```html
<!-- Dashboard Status Section -->
<div id="rag-status" hx-get="/portal/rag/status" hx-trigger="load, every 30s">
  <p>Loading status...</p>
</div>

<!-- Ingest Button -->
<button 
  hx-post="/portal/rag/ingest" 
  hx-target="#ingest-result"
  hx-indicator="#loading-spinner">
  Ingest Document
</button>
<div id="ingest-result"></div>
<div id="loading-spinner" class="htmx-indicator">Processing...</div>
```

**Django View for HTMX**:
```python
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import requests

@require_http_methods(["GET"])
def rag_status(request):
    """HTMX endpoint to fetch and render status"""
    try:
        health_response = requests.get(
            f"{settings.RAG_API_BASE_URL}/health",
            headers={"X-API-Key": settings.RAG_API_KEY},
            timeout=5
        )
        readiness_response = requests.get(
            f"{settings.RAG_API_BASE_URL}/ready",
            headers={"X-API-Key": settings.RAG_API_KEY},
            timeout=5
        )
        
        context = {
            "health": health_response.json(),
            "readiness": readiness_response.json()
        }
        return render(request, "rag/status_partial.html", context)
    except Exception as e:
        context = {"error": str(e)}
        return render(request, "rag/status_error.html", context)
```

**Status Partial Template** (`status_partial.html`):
```html
<div class="status-grid">
  <div class="status-card">
    <h3>Health</h3>
    <span class="badge badge-{{ health.status }}">
      {{ health.status|upper }}
    </span>
  </div>
  <div class="status-card">
    <h3>Readiness</h3>
    <span class="badge badge-{{ readiness.status }}">
      {{ readiness.status|upper }}
    </span>
  </div>
  <div class="status-card">
    <h3>OpenSearch</h3>
    <span class="badge badge-{{ health.services.opensearch.cluster_status }}">
      {{ health.services.opensearch.cluster_status|upper }}
    </span>
  </div>
</div>
<p class="text-muted">Last updated: {{ health.timestamp|date:"Y-m-d H:i:s" }}</p>
```

### 7.3 Ingest Document Example

```python
@require_http_methods(["POST"])
def ingest_document(request):
    """Handle document ingestion"""
    try:
        # Get form data
        content = request.POST.get("content")
        source_type = request.POST.get("source_type", "local")
        file_name = request.POST.get("file_name")
        
        # Prepare payload
        payload = {
            "content": content,
            "metadata": {
                "source": "company-portal",
                "source_type": source_type,
                "file_name": file_name,
                "author": request.user.username,
                "title": request.POST.get("title", file_name),
            }
        }
        
        # Call RAG API
        response = requests.post(
            f"{settings.RAG_API_BASE_URL}/api/v1/ingest/document",
            headers={
                "X-API-Key": settings.RAG_API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return render(request, "rag/ingest_success.html", {
            "document_id": result["document_id"],
            "chunks_indexed": result["chunks_indexed"]
        })
        
    except requests.exceptions.RequestException as e:
        return render(request, "rag/ingest_error.html", {
            "error": str(e)
        })
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Portal Response |
|------|---------|-----------------|
| 200 | Success | Display result |
| 201 | Created | Show success message |
| 400 | Bad Request | Show validation errors |
| 401 | Unauthorized | Check API key configuration |
| 404 | Not Found | Document/resource doesn't exist |
| 500 | Server Error | Show error, suggest retry |
| 503 | Service Unavailable | RAG API or OpenSearch is down |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Recommended Error Handling Strategy

```python
def call_rag_api(endpoint, method="GET", **kwargs):
    """
    Wrapper for RAG API calls with error handling
    """
    try:
        url = f"{settings.RAG_API_BASE_URL}{endpoint}"
        headers = {
            "X-API-Key": settings.RAG_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            timeout=kwargs.get("timeout", 30),
            **kwargs
        )
        
        response.raise_for_status()
        return {"success": True, "data": response.json()}
        
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out", "code": "timeout"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to RAG API", "code": "connection"}
    except requests.exceptions.HTTPError as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        return {
            "success": False,
            "error": error_detail,
            "code": "http_error",
            "status_code": e.response.status_code
        }
    except Exception as e:
        return {"success": False, "error": str(e), "code": "unknown"}
```

### User-Facing Error Messages

```python
ERROR_MESSAGES = {
    "timeout": "The RAG system is taking too long to respond. Please try again.",
    "connection": "Cannot connect to the RAG system. Please check if it's running.",
    "http_error": "The RAG system returned an error: {detail}",
    "unknown": "An unexpected error occurred: {detail}"
}
```

---

## Future Production Considerations

### 9.1 Production Environment (Azure)

**Known**:
- Both services will be deployed to Azure
- Services will run on separate VMs/Web Apps
- URLs will be different from development

**To Be Determined**:
- Production RAG API URL (TBD by DevOps/Infrastructure)
- Azure authentication method (may switch to Azure AD/Managed Identity)
- SSL/TLS certificate configuration
- CORS policies for cross-origin requests
- API Gateway or Azure API Management integration

### 9.2 Configuration Management

**Recommendation**: Use environment-based configuration

```python
# Django settings.py
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    RAG_API_BASE_URL = "http://localhost:8000"
    RAG_API_KEY = os.getenv("RAG_API_KEY_DEV")
elif ENVIRONMENT == "production":
    RAG_API_BASE_URL = os.getenv("RAG_API_BASE_URL_PROD")  # Azure URL (TBD)
    RAG_API_KEY = os.getenv("RAG_API_KEY_PROD")
```

### 9.3 Monitoring & Logging

**Recommended**:
- Log all RAG API calls (success/failure)
- Track response times
- Alert on repeated failures
- Monitor rate limits (if implemented)

### 9.4 Security Enhancements for Production

- Store API keys in Azure Key Vault
- Implement request signing
- Add rate limiting on portal side
- Use Azure Managed Identity if both services in Azure
- Enable HTTPS only
- Implement request/response validation

---

## Appendix: Quick Reference

### Minimum Viable Integration Checklist

- [ ] Configure RAG API base URL in Django settings
- [ ] Store API key securely
- [ ] Create health status view/partial
- [ ] Create readiness status view/partial
- [ ] Implement document count display
- [ ] Create ingest document form and handler
- [ ] Create delete document handler
- [ ] Create search interface
- [ ] Implement error handling wrapper
- [ ] Add loading indicators for async operations
- [ ] Test all endpoints in development
- [ ] Document production URL requirements

### Environment Variables Required

```bash
# Development (.env)
RAG_API_BASE_URL=http://localhost:8000
RAG_API_KEY=your-development-api-key

# Production (Azure App Settings)
RAG_API_BASE_URL=https://rag-api.azurewebsites.net  # TBD
RAG_API_KEY=your-production-api-key  # From Key Vault
ENVIRONMENT=production
```

### Support Contacts

- **RAG API Issues**: [Your contact info]
- **API Documentation**: http://localhost:8000/docs (dev)
- **OpenAPI Spec**: Available at `/swagger.json`

---

**Document Version**: 1.0  
**Last Updated**: January 21, 2026  
**Next Review**: Upon production URL availability
