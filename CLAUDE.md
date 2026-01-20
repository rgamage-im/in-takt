# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

In-Takt is an internal data access portal for Takt Homes that integrates Microsoft Graph API, QuickBooks API, and Notion API to provide unified access to company data through a web interface and RESTful API.

**Tech Stack:** Django 5.2.7, Django REST Framework, HTMX, Tailwind CSS, PostgreSQL (production), SQLite (dev)

## Common Commands

```bash
# Development server
python manage.py runserver

# Run all tests
pytest

# Run tests for a specific app
pytest msgraph_integration/tests/

# Run tests with coverage
pytest --cov

# Database migrations
python manage.py migrate
python manage.py makemigrations <app_name>

# Code formatting and linting
black .
isort .
flake8 .
mypy .

# Collect static files (production)
python manage.py collectstatic --noinput
```

## Architecture

### App Structure

Each integration is a separate Django app with a consistent pattern:

```
<integration>_integration/
├── services.py         # Business logic and API calls
├── services_delegated.py  # OAuth delegated flow (if applicable)
├── auth_views.py       # OAuth login/callback handlers
├── api_views.py        # REST API endpoints (JSON)
├── views.py            # HTML views (web UI)
├── serializers.py      # DRF serializers
├── urls.py             # App routes
└── templates/          # App-specific templates
```

### Key Apps

- **msgraph_integration/** - Microsoft Graph API (emails, calendar, OneDrive, SharePoint, Teams)
- **quickbooks_integration/** - QuickBooks Online API (customers, invoices, expenses)
- **notion_integration/** - Notion API (search, page retrieval)
- **core/** - Shared functionality, home page, custom management commands
- **api/** - API documentation routes (Swagger/ReDoc at `/api/docs/`)
- **config/** - Django settings, root URL routing, auth pipeline

### Authentication Patterns

**OAuth 2.0 Delegated (Primary):** Used for user-specific data access
- Tokens stored server-side in Django session
- Flow: `/graph/login/` → Microsoft login → `/graph/callback/` → tokens in session

**Client Credentials (Secondary):** Used for app-level directory access
- `GraphService` in `services.py` uses client credentials
- `GraphServiceDelegated` in `services_delegated.py` uses OAuth tokens

### Service Layer Pattern

Business logic is in service classes, not views:
```python
# In api_views.py
class MyMessagesAPIView(APIView):
    def get(self, request):
        access_token = request.session.get('graph_access_token')
        service = GraphServiceDelegated()
        messages = service.get_my_messages(access_token)
        return Response(MessageSerializer(messages, many=True).data)
```

## URL Structure

```
/                          # Home page
/admin/                    # Django admin
/graph/login/              # Start MS Graph OAuth
/graph/callback/           # OAuth callback
/graph/api/me/             # User profile API
/graph/api/me/messages/    # Emails API
/graph/api/me/calendar/    # Calendar API
/graph/api/me/drive/       # OneDrive API
/quickbooks/login/         # Start QuickBooks OAuth
/quickbooks/api/...        # QuickBooks endpoints
/notion/api/search/        # Notion search API
/api/docs/                 # Swagger UI
/api/redoc/                # ReDoc UI
/login/azuread-tenant-oauth2/  # Azure AD SSO
```

## Adding New Features

**New API endpoint in existing integration:**
1. Add service method in `services.py` or `services_delegated.py`
2. Create APIView in `api_views.py`
3. Add URL route in `urls.py`
4. Add DRF serializer if needed
5. Update drf-spectacular decorators for API docs

**New integration:**
1. Create new Django app: `python manage.py startapp <name>_integration`
2. Add to `INSTALLED_APPS` in `config/settings.py`
3. Follow the app structure pattern above
4. Include URLs in `config/urls.py`

## Environment Variables

Key variables needed in `.env` (see `.env.example`):
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- `MICROSOFT_GRAPH_CLIENT_ID`, `MICROSOFT_GRAPH_CLIENT_SECRET`, `MICROSOFT_GRAPH_TENANT_ID`, `MICROSOFT_GRAPH_REDIRECT_URI`
- `QUICKBOOKS_CLIENT_ID`, `QUICKBOOKS_CLIENT_SECRET`, `QUICKBOOKS_REALM_ID`, `QUICKBOOKS_REDIRECT_URI`
- `NOTION_INTERNAL_TOKEN` or `NOTION_API_TOKEN`
- `DATABASE_URL` (production PostgreSQL)

## Deployment

- GitHub Actions auto-deploys to Azure App Service on push to `main`
- Production uses Azure PostgreSQL, configured via `DATABASE_URL`
- `startup.sh` runs migrations, collects static files, and starts Gunicorn
- Static files served via WhiteNoise
