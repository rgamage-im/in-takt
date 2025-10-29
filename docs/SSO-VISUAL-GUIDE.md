# Azure AD SSO Configuration - Visual Guide

## What You'll See in Your Browser

### Before Adding Redirect URI
When you click "Sign in with Microsoft", you'll see this error:
```
AADSTS50011: The redirect URI 'http://localhost:8000/complete/azuread-tenant-oauth2/' 
specified in the request does not match the redirect URIs configured for the application
```

### After Adding Redirect URI
1. Click "Sign in with Microsoft"
2. Redirected to Microsoft login page
3. Log in with your credentials (if not already)
4. Consent screen (first time only):
   ```
   In-Takt wants to:
   - Sign you in
   - Read your profile info
   - Read your email address
   ```
5. Click "Accept"
6. Redirected back to In-Takt
7. You're logged in! 🎉

## Azure Portal Configuration Screenshots Guide

### Step 1: Navigate to App Registrations
```
Azure Portal (portal.azure.com)
├── Azure Active Directory
│   ├── App registrations
│   │   ├── All applications
│   │   │   └── Search: "In-Takt" or Client ID: 70810155-f32c-46f6-8159-1618ea380966
```

### Step 2: Authentication Settings
```
Your App Registration
├── Overview
├── Authentication ← Click here
│   ├── Platform configurations
│   │   ├── Web
│   │   │   ├── Redirect URIs
│   │   │   │   ├── http://localhost:8000/graph/callback/ (existing)
│   │   │   │   └── http://localhost:8000/complete/azuread-tenant-oauth2/ (ADD THIS)
```

### Step 3: Verify Settings

#### Supported account types
Should be: **"Accounts in this organizational directory only (Single tenant)"**
- ✅ This allows any user in your organization to log in
- ❌ Don't use "Personal Microsoft accounts" - that's for consumer apps

#### Implicit grant and hybrid flows
Can be unchecked - not needed for OAuth 2.0 with PKCE

#### Allow public client flows
Should be: **No**
- We're using confidential client (server-side) flow

## Django Application Flow

### User Journey
```
User clicks "Sign in with Microsoft"
    ↓
Django redirects to: /login/azuread-tenant-oauth2/
    ↓
social-auth-app-django builds authorization URL
    ↓
Redirects to Microsoft login.microsoftonline.com
    ↓
User logs in with Microsoft credentials
    ↓
Microsoft redirects back to: /complete/azuread-tenant-oauth2/
    ↓
social-auth-app-django exchanges code for access token
    ↓
Fetches user profile from Microsoft Graph
    ↓
Creates or updates Django user:
    - email: from Azure AD
    - first_name: from Azure AD
    - last_name: from Azure AD
    - username: generated from email
    ↓
Logs user into Django session
    ↓
Redirects to: / (home page)
    ↓
User sees: "Hello, First Last" in navigation
```

### Database Tables Created
```
social_auth_usersocialauth
├── id (primary key)
├── user_id (foreign key to auth_user)
├── provider (e.g., 'azuread-tenant-oauth2')
├── uid (user's Azure AD object ID)
├── extra_data (JSON with tokens and profile)
└── created, modified timestamps

social_auth_association
├── Links social accounts to Django users

social_auth_nonce
└── Security: prevents replay attacks

social_auth_code
└── Security: one-time authorization codes

social_auth_partial
└── Stores partial pipeline state
```

## URL Patterns Available

After configuration, these URLs are available:

| URL | Purpose |
|-----|---------|
| `/login/azuread-tenant-oauth2/` | Initiates SSO login |
| `/complete/azuread-tenant-oauth2/` | OAuth callback (Microsoft redirects here) |
| `/disconnect/azuread-tenant-oauth2/` | Unlink Microsoft account |
| `/logout/` | Django logout |

## Settings Configuration

### In config/settings.py
```python
# Authentication URLs
LOGIN_URL = '/login/azuread-tenant-oauth2/'  # ← SSO login
LOGIN_REDIRECT_URL = '/'  # ← After successful login
LOGOUT_REDIRECT_URL = '/'  # ← After logout

# Authentication Backends (order matters!)
AUTHENTICATION_BACKENDS = [
    'social_core.backends.azuread_tenant.AzureADTenantOAuth2',  # ← Try SSO first
    'django.contrib.auth.backends.ModelBackend',  # ← Fallback for admin
]

# Azure AD Configuration
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY = os.getenv('MICROSOFT_GRAPH_CLIENT_ID')
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = os.getenv('MICROSOFT_GRAPH_CLIENT_SECRET')
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = os.getenv('MICROSOFT_GRAPH_TENANT_ID')
```

## Testing Checklist

### ✅ Pre-Login Tests
- [ ] Navigate to http://localhost:8000
- [ ] See "Sign in with Microsoft" button (red, with Microsoft logo)
- [ ] Button is in top-right navigation
- [ ] Home page loads without errors

### ✅ Login Flow Tests
- [ ] Click "Sign in with Microsoft"
- [ ] Redirected to Microsoft login page (login.microsoftonline.com)
- [ ] URL contains your tenant ID: `66f459cf-d8c4-49ee-a087-43b80e9c8176`
- [ ] Log in with your Microsoft credentials
- [ ] Consent screen appears (first time only)
- [ ] Accept permissions
- [ ] Redirected back to http://localhost:8000
- [ ] See "Hello, [Your Name]" in navigation
- [ ] See "Logout" button

### ✅ Post-Login Tests
- [ ] Click on QuickBooks or Microsoft Graph links
- [ ] Navigate to /admin/ (should work if you're staff)
- [ ] Refresh page - should stay logged in
- [ ] Click "Logout" - should redirect to home
- [ ] Verify logged out (button changes back to "Sign in")

### ✅ Database Tests
```bash
# Check user was created
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.last()
>>> print(user.email, user.first_name, user.last_name)

# Check social auth record
>>> from social_django.models import UserSocialAuth
>>> social = UserSocialAuth.objects.last()
>>> print(social.provider)  # Should be 'azuread-tenant-oauth2'
>>> print(social.uid)  # Your Azure AD object ID
```

## Common Issues and Solutions

### Issue 1: Redirect URI Mismatch
```
Error: AADSTS50011: The redirect URI does not match
```
**Solution**: 
1. Check Azure AD app → Authentication → Redirect URIs
2. Must have EXACT URI: `http://localhost:8000/complete/azuread-tenant-oauth2/`
3. No trailing slash variations
4. Case sensitive
5. Click Save in Azure portal

### Issue 2: User Not Created
```
After login, redirects to home but user not created
```
**Solution**:
1. Check Django logs for errors
2. Verify migrations ran: `python manage.py migrate`
3. Check `social_django` in INSTALLED_APPS
4. Verify environment variables are loaded

### Issue 3: Session Not Persisting
```
User appears logged in, but loses session on refresh
```
**Solution**:
1. Check `SessionMiddleware` is in MIDDLEWARE
2. Clear browser cookies
3. Check SECRET_KEY is set
4. Verify database is writable

### Issue 4: Can't Access Admin Panel
```
Logged in, but /admin/ shows "You don't have permission"
```
**Solution**:
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='your@email.com')
>>> user.is_staff = True
>>> user.is_superuser = True
>>> user.save()
```

## Security Considerations

### What's Secure ✅
- OAuth 2.0 with authorization code flow
- Client secret stored in environment variable
- Tokens stored server-side (Django session)
- CSRF protection enabled
- HTTP-only session cookies
- Single tenant (only your organization)

### What to Add for Production 🔒
- [ ] Enable HTTPS (`SOCIAL_AUTH_REDIRECT_IS_HTTPS = True`)
- [ ] Use strong SECRET_KEY (not the default)
- [ ] Set DEBUG = False
- [ ] Enable MFA requirement in Azure AD
- [ ] Add Conditional Access policies (if Azure AD Premium)
- [ ] Monitor Azure AD sign-in logs
- [ ] Regular security audits

## User Management

### Making Users Admins
```python
# Give admin access
user = User.objects.get(email='user@domain.com')
user.is_staff = True  # Can access /admin/
user.is_superuser = True  # Full permissions
user.save()
```

### Creating Permission Groups
```python
from django.contrib.auth.models import Group, Permission

# Create a group
group = Group.objects.create(name='QuickBooks Managers')

# Add permissions
perm = Permission.objects.get(codename='view_invoice')
group.permissions.add(perm)

# Add user to group
user.groups.add(group)
```

### Restricting Access by Azure AD Group (Advanced)
```python
# In config/settings.py, add to pipeline:
SOCIAL_AUTH_PIPELINE = (
    # ... existing pipeline steps ...
    'config.auth_pipeline.check_azure_group',
)

# In config/auth_pipeline.py:
def check_azure_group(backend, details, response, *args, **kwargs):
    """Only allow users in specific Azure AD group"""
    if backend.name == 'azuread-tenant-oauth2':
        groups = response.get('groups', [])
        allowed_group_id = 'your-azure-group-object-id'
        if allowed_group_id not in groups:
            raise AuthForbidden(backend)
```

## Monitoring

### Django Admin Logs
View user actions: `/admin/admin/logentry/`

### Azure AD Sign-in Logs
1. Azure Portal → Azure Active Directory
2. Monitoring → Sign-in logs
3. Filter by application: "In-Takt"
4. See login attempts, IP addresses, locations

### User Activity
```python
# Recent logins
from django.contrib.admin.models import LogEntry
recent = LogEntry.objects.all().order_by('-action_time')[:20]

# Active sessions
from django.contrib.sessions.models import Session
from django.utils import timezone
active = Session.objects.filter(expire_date__gte=timezone.now())
```

## Deployment Checklist

### Before Going to Production
- [ ] Add production redirect URI to Azure AD
- [ ] Set `SOCIAL_AUTH_REDIRECT_IS_HTTPS = True`
- [ ] Update all environment variables
- [ ] Enable HTTPS/SSL
- [ ] Set `DEBUG = False`
- [ ] Use PostgreSQL or MySQL (not SQLite)
- [ ] Configure allowed hosts
- [ ] Set up monitoring/logging
- [ ] Test login flow in production
- [ ] Document for users

### Production Environment Variables
```bash
# .env.production
DJANGO_DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SOCIAL_AUTH_REDIRECT_IS_HTTPS=True
MICROSOFT_GRAPH_CLIENT_ID=70810155-f32c-46f6-8159-1618ea380966
MICROSOFT_GRAPH_CLIENT_SECRET=your-secret
MICROSOFT_GRAPH_TENANT_ID=66f459cf-d8c4-49ee-a087-43b80e9c8176
```

## Success Criteria

Your SSO is working correctly when:
- ✅ Users click "Sign in with Microsoft" and are redirected to Microsoft
- ✅ After login, users are redirected back to your app
- ✅ Navigation shows "Hello, [User Name]"
- ✅ User account is created in Django database
- ✅ User can access protected resources
- ✅ Logout works and clears session
- ✅ Multiple login/logout cycles work correctly

## Support Resources

- **Django Social Auth**: https://python-social-auth.readthedocs.io/
- **Azure AD Docs**: https://learn.microsoft.com/en-us/azure/active-directory/
- **Django Auth**: https://docs.djangoproject.com/en/5.2/topics/auth/
- **OAuth 2.0**: https://oauth.net/2/

## Questions?

Common questions answered in [SSO-SETUP.md](./SSO-SETUP.md)
