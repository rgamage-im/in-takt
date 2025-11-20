# Azure Deployment Quick Checklist

## Pre-Deployment
- [x] Azure App Service created
- [x] GitHub Actions CI/CD configured
- [x] Code updated for production settings
- [ ] Generate new DJANGO_SECRET_KEY
- [ ] PostgreSQL database ready (optional)

## Azure Portal Configuration

### App Service > Configuration > Application Settings
Add these environment variables:

**Required:**
- [ ] DJANGO_SECRET_KEY=`<generate-new>`
- [ ] DJANGO_DEBUG=False
- [ ] DJANGO_ALLOWED_HOSTS=in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net
- [ ] MICROSOFT_GRAPH_CLIENT_ID=`<your-client-id>`
- [ ] MICROSOFT_GRAPH_CLIENT_SECRET=`<your-client-secret>`
- [ ] MICROSOFT_GRAPH_TENANT_ID=`<your-tenant-id>`
- [ ] MICROSOFT_GRAPH_REDIRECT_URI=https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/graph/callback/
- [ ] QUICKBOOKS_CLIENT_ID=`<your-quickbooks-client-id>`
- [ ] QUICKBOOKS_CLIENT_SECRET=`<your-quickbooks-client-secret>`
- [ ] QUICKBOOKS_REALM_ID=`<your-realm-id>`
- [ ] QUICKBOOKS_ENVIRONMENT=sandbox
- [ ] QUICKBOOKS_REDIRECT_URI=https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/quickbooks/callback/

**Optional:**
- [ ] DATABASE_URL=`<postgresql-connection-string>` (if using PostgreSQL)
- [ ] DJANGO_LOG_LEVEL=INFO

### App Service > Configuration > General Settings
- [ ] Startup Command: `/home/site/wwwroot/startup.sh`

## Azure AD App Registration
- [ ] Add redirect URI: https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/graph/callback/
- [ ] Add redirect URI: https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/complete/azuread-tenant-oauth2/

## Deploy
- [ ] Commit changes to GitHub
- [ ] Push to `main` branch
- [ ] Monitor GitHub Actions workflow
- [ ] Wait for deployment to complete (~5-10 min)

## Post-Deployment
- [ ] SSH into Azure App Service
- [ ] Run: `python manage.py migrate`
- [ ] Run: `python manage.py createsuperuser`
- [ ] Test: Home page loads
- [ ] Test: SSO login works
- [ ] Test: Static files display
- [ ] Test: Microsoft 365 integration
- [ ] Test: QuickBooks integration
- [ ] Test: Admin panel access

## Commands to Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Production URL
https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/

## Documentation
See: docs/AZURE-DEPLOYMENT.md for detailed instructions
