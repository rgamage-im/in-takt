# REST API & Microsoft Graph Setup - Complete! ✅

## What Was Created

### 1. REST Framework Configuration (`config/settings.py`)
- ✅ Django REST Framework installed and configured
- ✅ drf-spectacular for OpenAPI/Swagger documentation
- ✅ Session authentication enabled
- ✅ API pagination set to 20 items per page

### 2. API Structure (`api/`)
- ✅ `api/urls.py` - Main API routing with versioning
- ✅ OpenAPI schema at `/api/schema/`
- ✅ Swagger UI at `/api/docs/`
- ✅ ReDoc alternative at `/api/redoc/`

### 3. Microsoft Graph Integration (`msgraph_integration/`)
- ✅ `services.py` - GraphService class for MS Graph API calls
- ✅ `serializers.py` - Data serialization for API responses
- ✅ `views.py` - Three API endpoints:
  - Get user profile (me or by ID)
  - List users
  - Search users
- ✅ `urls.py` - URL routing for MS Graph endpoints

### 4. Documentation
- ✅ `API_DOCS.md` - Complete API documentation
- ✅ `test_graph.py` - Testing script for MS Graph connection

## API Endpoints Available

### Base URL: `http://localhost:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/docs/` | GET | Interactive Swagger UI |
| `/api/redoc/` | GET | Alternative API documentation |
| `/api/schema/` | GET | OpenAPI 3.0 schema (JSON) |
| `/api/v1/graph/me/` | GET | Get current user's profile |
| `/api/v1/graph/users/` | GET | List users (with pagination) |
| `/api/v1/graph/users/{id}/` | GET | Get specific user profile |
| `/api/v1/graph/users/search/` | GET | Search users by name/email |

## How to Use

### Step 1: Configure Microsoft Graph Credentials

Edit your `.env` file and add:

```bash
MICROSOFT_GRAPH_CLIENT_ID=your-app-client-id
MICROSOFT_GRAPH_CLIENT_SECRET=your-app-client-secret
MICROSOFT_GRAPH_TENANT_ID=your-tenant-id
```

**To get these credentials:**
1. Go to Azure Portal → Azure Active Directory → App registrations
2. Create a new app registration or use existing
3. Copy the Application (client) ID → `MICROSOFT_GRAPH_CLIENT_ID`
4. Copy the Directory (tenant) ID → `MICROSOFT_GRAPH_TENANT_ID`
5. Go to Certificates & secrets → New client secret → Copy value → `MICROSOFT_GRAPH_CLIENT_SECRET`
6. Go to API permissions → Add `User.Read.All` (Application permission)
7. Click "Grant admin consent"

### Step 2: Test the Connection

```bash
# Windows
venv\Scripts\python test_graph.py

# WSL
wsl bash -c "source venv/bin/activate && python test_graph.py"
```

This will verify:
- ✅ Environment variables are set
- ✅ Can authenticate with Microsoft Graph
- ✅ Can retrieve user data

### Step 3: Start the Server

```bash
# Windows
venv\Scripts\python manage.py runserver

# WSL
wsl bash -c "source venv/bin/activate && python manage.py runserver"
```

### Step 4: Explore the API

1. **Visit Swagger UI**: http://localhost:8000/api/docs/
   - Interactive documentation
   - Try out endpoints directly
   - See request/response examples

2. **Test from Home Page**: http://localhost:8000
   - Click "View My Profile →" on the Microsoft 365 card
   - This will call `/api/v1/graph/me/`

## Code Examples

### Python
```python
import requests

# Create session and login
session = requests.Session()
session.post('http://localhost:8000/admin/login/', 
    data={'username': 'admin', 'password': 'yourpassword'})

# Get my profile
response = session.get('http://localhost:8000/api/v1/graph/me/')
profile = response.json()
print(f"Hello {profile['displayName']}!")

# List users
response = session.get('http://localhost:8000/api/v1/graph/users/?top=10')
users = response.json()
for user in users['value']:
    print(f"- {user['displayName']} ({user['mail']})")
```

### JavaScript/Fetch
```javascript
// Get my profile
fetch('/api/v1/graph/me/', {
    credentials: 'same-origin'
})
.then(response => response.json())
.then(data => console.log('My profile:', data));

// Search users
fetch('/api/v1/graph/users/search/?q=john', {
    credentials: 'same-origin'
})
.then(response => response.json())
.then(data => console.log('Search results:', data));
```

### HTMX (for your templates)
```html
<!-- Load user profile dynamically -->
<div hx-get="/api/v1/graph/me/" 
     hx-trigger="load"
     hx-swap="innerHTML">
    Loading profile...
</div>
```

## Features

✅ **OpenAPI 3.0 Compliant** - Industry standard API documentation  
✅ **Interactive Testing** - Try endpoints directly in Swagger UI  
✅ **Type Validation** - Request/response validation with serializers  
✅ **Error Handling** - Proper error responses with meaningful messages  
✅ **Authentication** - Session-based auth (can add JWT/OAuth later)  
✅ **Pagination** - Built-in pagination for list endpoints  
✅ **Versioning** - API versioned at `/api/v1/`  

## Next Steps

1. ✅ **Test MS Graph connection** - Run `test_graph.py`
2. ✅ **Explore API docs** - Visit `/api/docs/`
3. ⏳ **Add more endpoints** - Calendar, emails, SharePoint
4. ⏳ **Add QuickBooks integration** - Similar structure
5. ⏳ **Build dashboard UI** - Use HTMX to display data
6. ⏳ **Add JWT authentication** - For external API consumers

## Troubleshooting

**Q: Getting "Authentication failed" error?**  
A: Check your MS Graph credentials in `.env` file

**Q: "Permission denied" error?**  
A: Make sure you've granted admin consent for User.Read.All permission

**Q: API returns 403 Forbidden?**  
A: Make sure you're logged in. Visit `/admin/` first to authenticate

**Q: Changes not showing up?**  
A: Refresh browser (F5). Django auto-reloads Python code but not static files.

## Architecture Notes

**Service Layer Pattern** (following your requirements):
- `services.py` - Business logic and external API calls
- `views.py` - HTTP request/response handling  
- `serializers.py` - Data validation and transformation
- `models.py` - Database models (none needed yet, using external APIs)

This keeps MS Graph logic separate from the API layer, making it easy to:
- Test independently
- Reuse in other parts of the app
- Switch implementations if needed
- Add caching later

---

**Great work! Your REST API and MS Graph integration are now ready! 🎉**
