# RAG Pipeline Integration - Phase 3 Complete

## Overview
Phase 3 adds full document management capabilities and Microsoft Entra ID ACL integration to the RAG search system.

## Features Implemented

### 1. Document Ingestion Form (`/search/ingest/`)
- **Manual Text Input**: Submit document content directly through a web form
- **Metadata Fields**:
  - Source Type (dropdown: local, sharepoint, onedrive, teams, notion, quickbooks, other)
  - File Name (optional)
  - Document Title (optional)
  - Author (optional)
- **Automatic ACL Assignment**: Documents are automatically secured with:
  - Current user's email (from `request.user.email`)
  - User's Microsoft Entra ID groups (from Azure AD SSO `extra_data`)
- **HTMX Integration**: Real-time form submission without page reload
- **Success Feedback**: Shows document ID and number of chunks indexed
- **Error Handling**: Graceful error messages for timeout, connection, and API errors

**API Endpoint Used**: `POST /api/v1/ingest/document`

**Template Files**:
- `search_integration/templates/search/ingest_document.html` - Main form
- `search_integration/templates/search/ingest_result_partial.html` - HTMX response

---

### 2. Document Deletion Interface (`/search/delete/`)
- **Document ID Input**: UUID format validation with pattern matching
- **Confirmation Dialog**: HTMX `hx-confirm` attribute prevents accidental deletion
- **Guidance Section**: Helps users find document IDs via search results
- **Success Feedback**: Shows document ID and number of chunks deleted
- **Error Handling**: 
  - 404 errors for non-existent documents
  - Connection errors for RAG API downtime
  - Timeout handling for long operations

**API Endpoint Used**: `DELETE /api/v1/ingest/document/{document_id}`

**Template Files**:
- `search_integration/templates/search/delete_document.html` - Main form
- `search_integration/templates/search/delete_result_partial.html` - HTMX response

---

### 3. Microsoft Entra ID ACL Integration
Enhanced search functionality with access control:

**Search Filtering** (`search_documents` view):
- Automatically adds `acl_users` parameter with current user's email
- Automatically adds `acl_groups` parameter with user's Azure AD groups
- Groups are extracted from `social_auth.extra_data['groups']` via `social_django`

**Document Ingestion** (`ingest_document` view):
- Sets ACL on ingested documents to current user and their groups
- Ensures users can only find documents they have permission to access

**Implementation**:
```python
# In search_documents view
if request.user.is_authenticated:
    user_email = request.user.email
    social = request.user.social_auth.filter(provider='azuread-tenant-oauth2').first()
    if social and social.extra_data:
        user_groups = social.extra_data.get('groups', [])
    
    payload["acl_users"] = [user_email]
    payload["acl_groups"] = user_groups
```

---

### 4. Dashboard Updates
- **Document Management Section**: Added working buttons for Ingest and Delete
- **Phase 3 Notice**: Updated info box to indicate Phase 3 completion
- **Document ID Display**: Search results now show document IDs with copy button for easy deletion

---

## File Changes

### New Files Created
1. `search_integration/templates/search/ingest_document.html` - Ingestion form
2. `search_integration/templates/search/ingest_result_partial.html` - Ingestion result
3. `search_integration/templates/search/delete_document.html` - Deletion form
4. `search_integration/templates/search/delete_result_partial.html` - Deletion result
5. `search_integration/README_PHASE3.md` - This documentation

### Modified Files
1. `search_integration/views.py`:
   - Added `ingest_document()` view (GET/POST)
   - Added `delete_document()` view (GET/POST)
   - Updated `search_documents()` to include ACL filtering
   - Added `import json` and `from django.http import JsonResponse`

2. `search_integration/urls.py`:
   - Added path for `ingest/` → `ingest_document`
   - Added path for `delete/` → `delete_document`

3. `search_integration/templates/search/dashboard.html`:
   - Replaced disabled buttons with working links to ingest/delete forms
   - Updated Phase 2 notice to Phase 3 notice
   - Added icons to action buttons

4. `search_integration/templates/search/search_results_partial.html`:
   - Added document ID display with truncation
   - Added "Copy" button for document IDs
   - Moved ID tag to first position in metadata section

---

## User Workflow

### Ingesting a Document
1. Navigate to RAG Search Dashboard (`/search/`)
2. Click "Ingest Document" button
3. Fill in document content (required) and metadata (optional)
4. Click "Ingest Document" button
5. Wait for processing (HTMX loading indicator)
6. View success message with document ID and chunk count
7. Document is now searchable (ACL-protected to your user/groups)

### Deleting a Document
1. First, search for the document to get its ID
2. Copy the document ID from search results
3. Navigate to "Delete Document" page
4. Paste the document ID
5. Click "Delete Document" button
6. Confirm deletion in dialog
7. View success message with chunks deleted count

### Searching with ACL
1. Search as normal from the dashboard
2. Results are automatically filtered to:
   - Documents you created (your email in ACL)
   - Documents shared with your groups (Azure AD groups)
3. Other users' private documents won't appear in your results

---

## Security Features

### ACL Enforcement
- **Search**: Only returns documents where user email or groups match ACL
- **Ingestion**: Automatically sets ACL to current user's email and groups
- **No Bypass**: ACL filtering happens server-side in RAG API (not client-side)

### Authentication Required
- All endpoints require `@login_required` decorator
- Users must authenticate via Azure AD SSO before accessing

### API Key Protection
- RAG API key stored in environment variables (`.env` file)
- Never exposed to client-side code
- All API calls made server-side from Django views

---

## Technical Notes

### HTMX Integration
- All forms use `hx-post` for submissions
- Results rendered with `hx-target` partials
- Loading indicators with `hx-indicator`
- Confirmation dialogs with `hx-confirm` attribute

### Error Handling
Views handle multiple error types:
- `requests.exceptions.Timeout` - RAG API too slow
- `requests.exceptions.ConnectionError` - RAG API offline
- `requests.exceptions.HTTPError` - API returned error status
- Generic `Exception` - Unexpected errors

### Azure AD Integration
Uses `social_django` (already configured in project):
- `request.user.email` - User's email address
- `request.user.social_auth.filter(provider='azuread-tenant-oauth2').first()` - Social auth record
- `social.extra_data.get('groups', [])` - User's Azure AD groups

---

## Testing Checklist

- [x] Ingest document with all metadata fields
- [ ] Ingest document with minimal fields (content + source_type only)
- [ ] Verify document appears in search results
- [ ] Copy document ID from search results
- [ ] Delete document using copied ID
- [ ] Verify document no longer appears in search
- [ ] Test deletion with invalid document ID (should show 404 error)
- [ ] Test ingestion/deletion with RAG API offline (should show connection error)
- [ ] Verify ACL filtering (user can only see their own documents)
- [ ] Test with different Azure AD users/groups

---

## Next Steps / Future Enhancements

### Potential Phase 4 Features
1. **Bulk Operations**:
   - Upload multiple documents from file
   - Bulk delete by source or date range

2. **Document Browser**:
   - List all documents user has access to
   - Filter by source type, author, date
   - Preview document metadata before deletion

3. **File Upload**:
   - Accept PDF, DOCX, TXT files
   - Server-side text extraction
   - Automatic metadata parsing

4. **ACL Management**:
   - View/edit ACL for existing documents
   - Share documents with specific users/groups
   - Revoke access from documents

5. **Analytics Dashboard**:
   - Most searched queries
   - Document access logs
   - Ingestion/deletion history
   - Storage usage metrics

---

## Deployment Notes

### Environment Variables
Ensure `.env` contains:
```bash
RAG_API_BASE_URL=http://172.28.144.1:8000  # WSL gateway IP for Docker
RAG_API_KEY=your-api-key-here
```

### Django Settings
Verify `config/settings.py` includes:
- `django.contrib.humanize` in `INSTALLED_APPS`
- `search_integration` in `INSTALLED_APPS`
- RAG API configuration at end of file

### Static Files
No new static files required (uses inline styles and Tailwind CDN).

### Database Migrations
No new models added - no migrations needed for Phase 3.

---

## Phase Summary

**Phase 1**: Health monitoring dashboard (4 status cards, auto-refresh)  
**Phase 2**: Document search with hybrid vector/keyword search  
**Phase 3**: Document ingestion, deletion, and Microsoft Entra ID ACL integration  

**Status**: ✅ Phase 3 Complete - All features implemented and ready for testing
