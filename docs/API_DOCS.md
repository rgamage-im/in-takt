# API Documentation

## Overview

The In-Takt API provides RESTful access to Microsoft Graph and QuickBooks data.

## Interactive Documentation

When the development server is running, you can access:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Authentication

All API endpoints require authentication. Use your Django session authentication (login via /admin/).

## Microsoft Graph Endpoints

### Get My Profile
```
GET /api/v1/graph/me/
```
Returns the current authenticated user's profile from Microsoft Graph.

### Get User Profile
```
GET /api/v1/graph/users/{user_id}/
```
Returns a specific user's profile by ID.

### List Users
```
GET /api/v1/graph/users/?top=10&select=displayName,mail
```
Returns a list of users. Query parameters:
- `top`: Number of users to return (default: 10, max: 999)
- `select`: Comma-separated list of properties to return

### Search Users
```
GET /api/v1/graph/users/search/?q=john&top=10
```
Search for users by display name or email.
- `q`: Search query (required)
- `top`: Number of results (default: 10)

## Environment Variables

Configure these in your `.env` file:

```bash
# Microsoft Graph API
MICROSOFT_GRAPH_CLIENT_ID=your-client-id
MICROSOFT_GRAPH_CLIENT_SECRET=your-client-secret
MICROSOFT_GRAPH_TENANT_ID=your-tenant-id
```

## Testing the API

### Using curl:
```bash
# Login first to get session cookie
curl -X POST http://localhost:8000/admin/login/ \
  -d "username=admin&password=yourpassword"

# Then make API calls
curl -X GET http://localhost:8000/api/v1/graph/me/ \
  --cookie "sessionid=your-session-id"
```

### Using Python requests:
```python
import requests

# Create session
session = requests.Session()

# Login
session.post('http://localhost:8000/admin/login/', 
    data={'username': 'admin', 'password': 'yourpassword'})

# Get my profile
response = session.get('http://localhost:8000/api/v1/graph/me/')
print(response.json())
```

## Response Format

All successful responses follow this structure:

```json
{
  "id": "user-id",
  "displayName": "John Doe",
  "mail": "john.doe@takthomes.com",
  "jobTitle": "Developer",
  "department": "IT"
}
```

Error responses:

```json
{
  "error": "Error message description"
}
```

## Next Steps

1. Configure your Microsoft Graph API credentials in `.env`
2. Run the development server: `python manage.py runserver`
3. Visit http://localhost:8000/api/docs/ to explore the API
4. Test endpoints using the Swagger UI "Try it out" feature
