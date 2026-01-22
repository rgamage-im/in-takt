# RAG Search Integration - Phase 1

## Overview
This Django app integrates the In-Takt Company Data Portal with the RAG (Retrieval-Augmented Generation) Pipeline Backend API for intelligent document search and management.

## Phase 1: Health Monitoring ✅

### Features Implemented
- **Health Check Dashboard** at `/search/`
  - Real-time connection status to RAG API
  - Health status monitoring (healthy/degraded/unhealthy)
  - Readiness status (ready/not_ready)
  - OpenSearch cluster status (green/yellow/red)
  - Auto-refresh every 30 seconds via HTMX
  - Manual refresh button
  - Graceful error handling when RAG API is offline

### Configuration
Add to your `.env` file:
```bash
RAG_API_BASE_URL=http://localhost:8000
RAG_API_KEY=your-api-key-here
```

### Access
- **URL**: http://localhost:8080/search/
- **Authentication**: Requires login (all authenticated users can access)

### Architecture
- **Views**: `search_integration/views.py`
  - `dashboard()` - Main dashboard page
  - `health_status()` - HTMX partial for status updates
- **Templates**: `search_integration/templates/search/`
  - `dashboard.html` - Main dashboard layout
  - `health_status_partial.html` - Status cards partial (HTMX target)
- **URL Routing**: `/search/` prefix
- **Styling**: Tailwind CSS matching existing In-Takt theme

### Error Handling
The integration gracefully handles:
- ✅ RAG API not running (connection errors)
- ✅ Request timeouts
- ✅ HTTP errors (400, 401, 404, 500, etc.)
- ✅ Network issues

When RAG API is offline, the dashboard shows:
- Clear error message
- Troubleshooting guidance
- Placeholder status cards

### Testing Phase 1
1. **Start RAG API** (if available):
   ```bash
   cd c:\github\search-engine  # Or your RAG API location
   docker-compose up -d
   ```

2. **Start Django Server**:
   ```bash
   source venv/bin/activate
   python manage.py runserver 8080
   ```

3. **Visit Dashboard**:
   - Navigate to: http://localhost:8080/search/
   - Login if not authenticated
   - Observe status indicators

4. **Test Offline Handling**:
   - Stop RAG API: `docker-compose down`
   - Refresh dashboard - should show error state
   - Restart RAG API - status should recover automatically

## Phase 2: Document Management (Coming Soon)

Planned features:
- [ ] Ingest Document - Text input with metadata
- [ ] Delete Document - Remove indexed documents
- [ ] Search Documents - Hybrid vector/keyword search
- [ ] SharePoint/OneDrive link ingestion
- [ ] File upload support
- [ ] Microsoft Entra ID ACL integration

## Technical Notes

### HTMX Integration
- Dashboard uses HTMX for dynamic status updates
- Automatic polling every 30 seconds
- Manual refresh without page reload
- Loading indicators during requests

### Authentication
All views use `@login_required` decorator:
```python
@login_required
@require_http_methods(["GET"])
def dashboard(request):
    ...
```

### API Client Pattern
Error handling wrapper example from views.py:
```python
try:
    response = requests.get(
        f"{settings.RAG_API_BASE_URL}/health",
        headers={"X-API-Key": settings.RAG_API_KEY},
        timeout=5
    )
    response.raise_for_status()
    # Process success...
except requests.exceptions.ConnectionError:
    # Handle offline...
```

### Styling
Uses In-Takt color scheme:
- Deep Navy: `#1A2A3A`
- Warm Brick: `#C14E32`
- Soft Sky Blue: `#7BB6E0`
- Light Sand: `#E8E2D0`
- Olive Gray: `#808870`

Status badges:
- Green: Healthy/Ready
- Yellow: Degraded
- Red: Unhealthy/Not Ready
- Gray: Offline/Error

## Development

### Project Structure
```
search_integration/
├── __init__.py
├── apps.py
├── views.py
├── urls.py
└── templates/
    └── search/
        ├── dashboard.html
        └── health_status_partial.html
```

### Adding New Features
1. Create view in `views.py`
2. Add URL pattern in `urls.py`
3. Create template in `templates/search/`
4. Update dashboard.html if needed

### Future Enhancements
- Document count metric
- Recent activity log
- Document list/browse interface
- Advanced search filters
- Batch operations
- Azure production configuration

## Support
See `docs/rag-pipeline-integration-guide.md` for complete API reference and integration details.
