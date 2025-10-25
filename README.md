# In-Takt Web Portal

**Your window into Takt Homes**

An internal data access portal that integrates Microsoft Graph API and QuickBooks API to provide unified access to company data through a modern web interface and RESTful API.

## 🚀 Project Status

**Current Phase:** Foundation Setup ✅  
**Version:** 0.1.0  
**Last Updated:** October 24, 2025

## 📋 Overview

In-Takt is an internal-facing web application that centralizes access to company data from multiple sources:
- **Microsoft 365** (via Microsoft Graph API)
- **QuickBooks** (financial data)
- **Unified API** for programmatic access
- **Interactive Documentation** via Swagger/OpenAPI

## 🛠️ Technology Stack

- **Backend:** Django 5.2.7 (LTS), Django REST Framework
- **Frontend:** HTMX, Tailwind CSS, HTML5/CSS3
- **APIs:** Microsoft Graph SDK, QuickBooks Python SDK
- **Database:** Azure PostgreSQL
- **Caching:** Redis
- **Task Queue:** Celery
- **Documentation:** drf-spectacular (OpenAPI 3.0)
- **Hosting:** Azure App Service

## 📁 Project Structure

```
in-takt/
├── config/                 # Django project settings
├── core/                   # Core functionality and shared utilities
├── msgraph_integration/    # Microsoft Graph API integration
├── quickbooks_integration/ # QuickBooks API integration
├── api/                    # RESTful API endpoints
├── web_ui/                 # HTMX-based web interface
├── branding/               # Brand assets and theme
├── venv/                   # Virtual environment (not in Git)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
└── manage.py              # Django management script
```

## 🔧 Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL (or Azure PostgreSQL)
- Redis (for caching and Celery)
- Git
- WSL/Ubuntu (for Windows development)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rgamage-im/in-takt.git
   cd in-takt
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs/
   - Admin: http://localhost:8000/admin/

## 🔑 Environment Variables

Copy `.env.example` to `.env` and configure the following:

### Required Variables
- `DJANGO_SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `AZURE_CLIENT_ID` - Azure AD client ID
- `AZURE_CLIENT_SECRET` - Azure AD client secret
- `AZURE_TENANT_ID` - Azure AD tenant ID
- `MICROSOFT_GRAPH_CLIENT_ID` - MS Graph client ID
- `MICROSOFT_GRAPH_CLIENT_SECRET` - MS Graph client secret
- `QUICKBOOKS_CLIENT_ID` - QuickBooks client ID
- `QUICKBOOKS_CLIENT_SECRET` - QuickBooks client secret
- `QUICKBOOKS_REALM_ID` - QuickBooks company ID

### Optional Variables
- `REDIS_URL` - Redis connection string
- `CELERY_BROKER_URL` - Celery broker URL
- `AZURE_KEY_VAULT_URL` - Azure Key Vault URL
- `APPLICATIONINSIGHTS_CONNECTION_STRING` - App Insights

## 📚 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use Black for code formatting: `black .`
- Use isort for import sorting: `isort .`
- Run flake8 for linting: `flake8 .`
- Type hints with mypy: `mypy .`

### Testing
- Write tests for all new features
- Run tests: `pytest`
- Check coverage: `pytest --cov`
- Target: 80% minimum code coverage

### Git Workflow
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes

### Architecture Principles
- **Modular design** - Separate apps for different concerns
- **API-first** - Backend API separate from UI
- **Service layer** - Business logic in service classes
- **Integration layer** - External APIs in dedicated modules

## 🔌 API Integrations

### Microsoft Graph API
Located in `msgraph_integration/`:
- User directory and profiles
- Calendar and scheduling
- Email and communications
- SharePoint and OneDrive
- Teams data

### QuickBooks API
Located in `quickbooks_integration/`:
- Invoices and billing
- Customers and vendors
- Expenses and payments
- Financial reports
- Time tracking

## 📖 API Documentation

Interactive API documentation is available at `/api/docs/` when running the development server.

Features:
- OpenAPI 3.0 specification
- Swagger UI interface
- Try-it-out functionality
- Authentication testing
- Schema validation

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific app tests
pytest msgraph_integration/tests/

# Run with verbose output
pytest -v
```

## 🚀 Deployment

### Azure Deployment

1. **Configure Azure resources:**
   - App Service (Python 3.12)
   - PostgreSQL Database
   - Key Vault
   - Application Insights
   - Redis Cache

2. **Set environment variables in Azure:**
   - Configure App Service settings
   - Reference Key Vault secrets

3. **Deploy application:**
   ```bash
   az webapp up --name in-takt --resource-group your-rg
   ```

## 📊 Project Phases

- ✅ **Phase 1:** Foundation Setup (Weeks 1-3)
- ⏳ **Phase 2:** API Development (Weeks 4-7)
- ⏳ **Phase 3:** Web Interface (Weeks 8-10)
- ⏳ **Phase 4:** Testing & Optimization (Weeks 11-12)
- ⏳ **Phase 5:** Documentation & Deployment (Weeks 13-14)

## 🤝 Contributing

This is an internal project. For contributions:
1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request
5. Code review required

## 📝 Documentation

- [Requirements Document](InTakt%20Web%20Portal%20Requirements.md)
- [Development Guidelines](development-guidlines.md)
- [API Documentation](http://localhost:8000/api/docs/) (when running)

## 🔒 Security

- All secrets in Azure Key Vault
- HTTPS/TLS 1.3 for all communications
- Azure AD authentication
- Role-based access control (RBAC)
- No sensitive data in logs

## 📞 Support

For issues or questions:
- Check documentation first
- Review existing issues
- Contact the development team

## 📄 License

Internal use only - Takt Homes

---

**Built with ❤️ for Takt Homes**
