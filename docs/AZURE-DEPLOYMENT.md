# Azure App Service Deployment Guide

## Overview
This guide covers deploying the In-Takt Portal to Azure App Service with continuous deployment from GitHub.

**Production URL:** https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/

---

## Prerequisites

✅ Azure App Service created  
✅ GitHub Actions CI/CD configured  
✅ Azure PostgreSQL database (optional, can use SQLite initially)  
⚠️ Azure AD app registration needs redirect URI updates  
⚠️ Environment variables need to be configured  

---

## Step 1: Configure Environment Variables in Azure Portal

### 1.1 Navigate to App Service Configuration
1. Go to [Azure Portal](https://portal.azure.com)
2. Find your App Service: **in-takt-portal**
3. Click **Configuration** in the left menu
4. Click **Application settings** tab

### 1.2 Add Required Environment Variables

Click **+ New application setting** for each of these:

#### Django Settings
```
Name: DJANGO_SECRET_KEY
Value: <Generate using the command below>
```

**Generate Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```
Name: DJANGO_DEBUG
Value: False
```

```
Name: DJANGO_ALLOWED_HOSTS
Value: in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net
```

```
Name: DJANGO_LOG_LEVEL
Value: INFO
```

#### Database (if using PostgreSQL)
```
Name: DATABASE_URL
Value: postgresql://username:password@server.postgres.database.azure.com:5432/intakt?sslmode=require
```

*Note: If you skip this, the app will use SQLite (fine for testing)*

#### Microsoft Graph API
```
Name: MICROSOFT_GRAPH_CLIENT_ID
Value: <your-client-id>
```

```
Name: MICROSOFT_GRAPH_CLIENT_SECRET
Value: <your-client-secret>
```

```
Name: MICROSOFT_GRAPH_TENANT_ID
Value: <your-tenant-id>
```

```
Name: MICROSOFT_GRAPH_REDIRECT_URI
Value: https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/graph/callback/
```

#### QuickBooks API
```
Name: QUICKBOOKS_CLIENT_ID
Value: <your-quickbooks-client-id>
```

```
Name: QUICKBOOKS_CLIENT_SECRET
Value: <your-quickbooks-client-secret>
```

```
Name: QUICKBOOKS_REALM_ID
Value: <your-realm-id>
```

```
Name: QUICKBOOKS_ENVIRONMENT
Value: sandbox
```
*Change to `production` when ready to use live QuickBooks data*

```
Name: QUICKBOOKS_REDIRECT_URI
Value: https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/quickbooks/callback/
```

### 1.3 Save Configuration
- Click **Save** at the top
- Click **Continue** when prompted
- Wait for the app to restart (~30 seconds)

---

## Step 2: Configure Startup Command

### 2.1 Set Startup Script
1. In Azure Portal, go to **Configuration**
2. Click **General settings** tab
3. In **Startup Command** field, enter:
   ```bash
   bash startup.sh
   ```
4. Click **Save**

### 2.2 Alternative: Use Gunicorn Directly
If startup.sh doesn't work, use:
```bash
gunicorn config.wsgi:application --bind=0.0.0.0:8000 --workers=4 --timeout=600
```

---

## Step 3: Update Azure AD App Registration

**CRITICAL:** SSO and Microsoft Graph won't work until you add production redirect URIs.

### 3.1 Navigate to App Registration
1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **Azure Active Directory**
3. Click **App registrations**
4. Find app with ID: `70810155-f32c-46f6-8159-1618ea380966`

### 3.2 Add Redirect URIs
1. Click **Authentication** in left menu
2. Under **Web** platform, click **Add URI**
3. Add these two URIs:
   ```
   https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/graph/callback/
   https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/complete/azuread-tenant-oauth2/
   ```
4. Click **Save**

### 3.3 Keep Localhost URIs for Development
Keep these existing URIs:
```
http://localhost:8000/graph/callback/
http://localhost:8000/complete/azuread-tenant-oauth2/
```

### 4.1 Automatic Deployment
Your GitHub Actions workflow is already configured. Deployment happens automatically when you push to `main`:

```bash
git add .
git commit -m "Configure for Azure production deployment"
git push origin main
```

### 4.2 Monitor Deployment
1. Go to GitHub repository
2. Click **Actions** tab
3. Watch the "Build and deploy Python app to Azure Web App" workflow
4. Deployment takes ~5-10 minutes

### 4.3 Check Deployment Status in Azure
1. In Azure Portal, go to your App Service
2. Click **Deployment Center** in left menu
3. View deployment logs

---

## Step 5: Initialize Production Database

### 5.1 Access SSH Console
1. In Azure Portal, go to your App Service
2. Click **SSH** or **Advanced Tools** > **Go** > **SSH**
3. Wait for terminal to load

### 5.2 Run Initial Setup Commands
```bash
# Navigate to app directory
cd /home/site/wwwroot

# Verify environment
python --version
python -c "import django; print(django.VERSION)"

# Check configuration
python manage.py check

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
# Follow prompts to set username/password
```

---

## Step 6: Verify Deployment

### 6.1 Test Application
Visit: https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/

**Expected Results:**
- ✅ Home page loads
- ✅ Static files (CSS, images) display correctly
- ✅ Can click "Login with Azure AD" (SSO)
- ✅ After login, shows your name in top right

### 6.2 Test Admin Panel
Visit: https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/admin/

Login with the superuser account you created.

### 6.3 Test API Documentation
Visit: https://in-takt-portal-ezgqh2c2a2dsdyfu.westus2-01.azurewebsites.net/api/docs/

Should show Swagger UI with API documentation.

### 6.4 Test Microsoft 365 Integration
1. Click **Explore** on Microsoft 365 card
2. Should redirect to Microsoft login
3. After auth, should show your profile page
4. Try accessing messages and calendar

### 6.5 Test QuickBooks Integration
1. Click **Explore** on QuickBooks card
2. Should redirect to QuickBooks OAuth
3. After auth, should show QuickBooks dashboard

---

## Step 7: Monitoring and Troubleshooting

### 7.1 View Application Logs
**Option 1: Azure Portal**
1. Go to App Service
2. Click **Log stream** in left menu
3. Watch real-time logs

**Option 2: SSH Terminal**
```bash
tail -f /home/LogFiles/application.log
```

### 7.2 Common Issues

#### Issue: 500 Internal Server Error
**Solution:**
```bash
# Check logs for detailed error
# Common causes:
# - Missing environment variables
# - Database connection error
# - Static files not collected
```

#### Issue: Static files not loading (CSS missing)
**Solution:**
```bash
# SSH into app, run:
python manage.py collectstatic --noinput

# Or add to GitHub Actions workflow
```

#### Issue: SSO redirect not working
**Solution:**
- Verify redirect URIs in Azure AD match exactly (including trailing slash)
- Check SOCIAL_AUTH_REDIRECT_URI environment variable
- Ensure DJANGO_DEBUG=False for HTTPS redirect

#### Issue: Database migrations not applied
**Solution:**
```bash
# SSH into app, run:
python manage.py migrate
```

### 7.3 Enable Application Insights (Optional)
1. Create Application Insights resource in Azure
2. Copy connection string
3. Add to App Service configuration:
   ```
   Name: APPLICATIONINSIGHTS_CONNECTION_STRING
   Value: <your-connection-string>
   ```

---

## Step 8: Ongoing Maintenance

### 8.1 Making Changes
1. Edit code locally
2. Test thoroughly: `python manage.py runserver`
3. Commit and push to GitHub
4. GitHub Actions automatically deploys
5. Monitor deployment and test production

### 8.2 Database Backups
- Azure PostgreSQL has automated backups
- For SQLite: Manually backup db.sqlite3 file
- Schedule regular backups!

### 8.3 SSL Certificate
- Azure App Service provides free SSL certificate
- Automatically managed and renewed
- Custom domain setup available if needed

### 8.4 Scaling
Current plan:
- Check in Azure Portal > App Service > Scale up/out
- Can increase workers, memory, CPU as needed

---

## Environment Comparison

| Setting | Local Development | Azure Production |
|---------|------------------|------------------|
| DEBUG | True | False |
| Database | SQLite | PostgreSQL (recommended) |
| HTTPS | No | Yes (automatic) |
| Static Files | Served by Django | Served by WhiteNoise |
| Secret Key | Default | Unique generated |
| Logs | Console | Azure Log Stream |

---

## Quick Reference Commands

### Local Testing
```bash
# Run locally
python manage.py runserver

# Check for issues
python manage.py check --deploy

# Test production settings locally
export DJANGO_DEBUG=False
python manage.py runserver
```

### Azure SSH Commands
```bash
# Navigate to app
cd /home/site/wwwroot

# Check status
python manage.py check

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# View logs
tail -f /home/LogFiles/application.log
```

---

## Support

- **Azure Portal:** https://portal.azure.com
- **GitHub Repo:** https://github.com/rgamage-im/in-takt
- **Django Docs:** https://docs.djangoproject.com/en/5.2/howto/deployment/

---

## Next Steps

After successful deployment:

1. ✅ Test all features in production
2. ✅ Invite team members to test SSO login
3. ✅ Set up monitoring and alerts
4. ✅ Configure custom domain (optional)
5. ✅ Enable HTTPS redirect (automatic)
6. ✅ Set up database backups
7. ✅ Document any production-specific configurations
8. ✅ Update QuickBooks to production environment when ready

---

**Deployment Checklist:**

- [ ] Environment variables configured
- [ ] Startup command set
- [ ] Azure AD redirect URIs added
- [ ] Code pushed to GitHub
- [ ] Deployment successful
- [ ] Database migrations run
- [ ] Superuser created
- [ ] Home page loads
- [ ] SSO login works
- [ ] Static files display
- [ ] API documentation accessible
- [ ] Team members can log in
