# Development Session Notes - January 26, 2026

## Summary
Session focused on improving the RAG search dashboard UI/UX and resolving port conflicts between the Django portal and RAG API.

---

## Changes Implemented

### 1. Port Configuration Updates
**Issue**: Both Django portal and RAG API were trying to use port 8000, causing conflicts.

**Solution**:
- Updated `startup.sh` to run Gunicorn on port 8080 instead of 8000
- Created `devstart.sh` script for easy development server startup on port 8080
  ```bash
  ./devstart.sh  # Runs: python manage.py runserver 8080
  ```
- Updated Microsoft Graph API redirect URI from `http://localhost:8000/graph/callback/` to `http://localhost:8080/graph/callback/`

**Files Modified**:
- `startup.sh`
- `devstart.sh` (new file)
- `.env`

---

### 2. Document Ingestion UX Improvement
**Issue**: No visual feedback during document ingestion, leaving users uncertain if the process was working.

**Solution**:
- Added full-page loading overlay with spinner during document ingestion
- Overlay displays:
  - Large spinning loader
  - "Ingesting Document..." message
  - "This may take a moment" subtext
- Uses HTMX's built-in indicator mechanism for automatic show/hide

**Files Modified**:
- `search_integration/templates/search/ingest_document.html`

**Technical Details**:
```html
<div id="ingest-loading" class="htmx-indicator absolute inset-0 bg-white bg-opacity-90...">
  <!-- Spinner and text -->
</div>
```

---

### 3. Document Count Metric Removal
**Issue**: The "Indexed Chunks" metric on the dashboard was showing incorrect values (always 1 or dash).

**Root Cause Analysis**:
1. Initially tried using search with `query: "*"` - resulted in showing 1
2. Attempted empty string query - caused 500 error from RAG API
3. Attempted using `/api/v1/ingest/initialize` endpoint - only returns index status, not count
4. Discovered that:
   - RAG API has no dedicated stats endpoint
   - Search `total_results` only reflects matches for that specific query
   - OpenSearch index contains **chunks**, not complete documents
   - Example: 4 documents ingested = 1010 chunks indexed

**Understanding Chunks vs Documents**:
- When documents are ingested, they're split into smaller chunks (~few hundred words each)
- Each chunk is stored as a separate entry in OpenSearch
- This enables better semantic search and works within embedding token limits
- In testing: 4 documents → 1010 chunks (~252 chunks/document average)

**Solution**:
- Removed the "Indexed Chunks" card from dashboard
- Changed grid layout from 4 columns to 3 columns
- Removed document count fetching logic from `views.py`
- Dashboard now shows only: Health Status, Readiness, OpenSearch Cluster

**Files Modified**:
- `search_integration/templates/search/health_status_partial.html`
- `search_integration/views.py`

**Future Recommendation**:
Request RAG API team to add a dedicated stats endpoint:
```python
GET /api/v1/stats

Response:
{
  "total_chunks": 1010,
  "unique_documents": 4,
  "index_size_bytes": 12345678,
  "last_indexed": "2026-01-26T21:30:00Z"
}
```

---

### 4. OpenSearch Dashboards Investigation
**Objective**: Explore alternative ways to view document counts and create custom dashboards.

**Key Findings**:

**Getting Unique Document Count** (via Dev Tools):
```http
GET /documents/_search
{
  "size": 0,
  "aggs": {
    "unique_docs": {
      "cardinality": {
        "field": "document_id"
      }
    }
  }
}
```

**Useful OpenSearch Queries**:
```http
# Get total count
GET /documents/_count

# View all documents
GET /documents/_search
{
  "query": {"match_all": {}},
  "size": 100
}

# List all indices
GET /_cat/indices?v
```

**Document Structure** (from OpenSearch):
```json
{
  "document_id": "e138dbcb-d641-42aa-a129-d4ab72a2f0bb",
  "chunk_id": "e138dbcb-d641-42aa-a129-d4ab72a2f0bb_0",
  "content": "...",
  "embedding": [...],
  "metadata": {
    "source": "test",
    "source_type": "local",
    "file_name": "test.txt",
    "title": "Test Document on AI",
    ...
  },
  "chunk_metadata": {
    "chunk_index": 0,
    "total_chunks": 1
  },
  "indexed_at": "2026-01-21T05:41:10.271743"
}
```

**Custom Dashboard Creation** (attempted but encountered issues):
- Tried creating Metric visualization with Unique Count (Cardinality) on `document_id`
- Field aggregation issues prevented successful visualization
- Alternative: Create Data Table with Terms aggregation to list all document IDs

**Why Not Query OpenSearch Directly from Portal?**
1. Wrong service - port 5601 is Dashboards UI, not OpenSearch API
2. Architecture violation - RAG API is designed as single point of access
3. Production issues - OpenSearch won't be accessible in production
4. Authentication complexity - would need separate credentials
5. Missing business logic - bypasses ACL and other RAG API features

---

## Testing Performed
- ✅ Port 8080 configuration working for both startup.sh and devstart.sh
- ✅ Document ingestion spinner displays correctly during submission
- ✅ Dashboard displays 3 status cards correctly
- ✅ OpenSearch queries verified document count and structure
- ✅ Changes committed and pushed to GitHub

---

## Git Commit
**Commit**: `afa5d29`  
**Message**: "feat: RAG search dashboard improvements"

**Files Changed**:
- `devstart.sh` (new file)
- `startup.sh`
- `msgraph_integration/auth_views.py`
- `search_integration/templates/search/health_status_partial.html`
- `search_integration/templates/search/ingest_document.html`
- `search_integration/views.py`

---

## Known Issues & Future Work

### Immediate
- None - all known issues addressed

### Future Enhancements
1. **Stats Endpoint**: Request RAG API team to add `/api/v1/stats` endpoint for proper metrics
2. **OpenSearch Dashboard**: Complete custom dashboard creation with proper visualizations
3. **Document Management**: Add ability to list and manage ingested documents via portal UI
4. **Batch Operations**: Support for bulk document ingestion

---

## Architecture Notes

### Port Allocation
- **Django Portal**: Port 8080 (development and production)
- **RAG API**: Port 8000 (FastAPI)
- **OpenSearch**: Port 9200 (internal only)
- **OpenSearch Dashboards**: Port 5601 (development only)

### Data Flow
```
Portal (8080) → RAG API (8000) → OpenSearch (9200)
                                      ↑
                       OpenSearch Dashboards (5601) [dev only]
```

---

## Developer Notes
- Use `./devstart.sh` for local development instead of `python manage.py runserver`
- RAG API must be running for dashboard to function
- OpenSearch Dashboards available at http://localhost:5601 for direct database inspection
- Document ingestion creates multiple chunks per document - this is expected behavior
