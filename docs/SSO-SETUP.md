# Azure AD SSO Setup for In-Takt

## Overview
This application uses **Azure AD (Entra ID) Single Sign-On** for organization-wide authentication. Users from your organization can log in with their Microsoft 365 credentials.

## What's Configured

### 1. Authentication Backend
- **Library**: `social-auth-app-django` with Azure AD Tenant OAuth2
- **Cost**: $0 (uses existing Azure AD - no premium features required)
- **User Experience**: One-click Microsoft login button

### 2. Automatic User Creation
When a user from your organization logs in for the first time:
- A Django user account is automatically created
- User's email, first name, and last name are synced from Azure AD
- User remains authenticated across all apps

### 3. Security Features
- OAuth 2.0 with PKCE (industry standard)
- Tokens stored in Django session (server-side)
- Automatic token refresh
- Single logout across applications

## Azure AD App Registration Setup

### Step 1: Add Redirect URI
Go to your Azure AD app registration and add this redirect URI:
```
http://localhost:8000/complete/azuread-tenant-oauth2/
```

For production, change to:
```
https://yourdomain.com/complete/azuread-tenant-oauth2/
```

### Step 2: Configure API Permissions
Your app needs these permissions (already configured):
- `openid` - Sign in users
- `email` - Read user email
- `profile` - Read basic profile info

### Step 3: Organization Access Control
**Option A - Any user in your organization (recommended for internal apps)**
- Under "Authentication" → "Supported account types"
- Select: "Accounts in this organizational directory only (Single tenant)"

**Option B - Restrict to specific users/groups**
1. Go to "Enterprise Applications" in Azure AD
2. Find your app registration
3. Under "Properties", set "User assignment required?" to **Yes**
4. Under "Users and groups", add specific users or security groups

### Step 4: Update Production Settings
When deploying to production, update `.env`:
```bash
SOCIAL_AUTH_REDIRECT_IS_HTTPS=True
```

## How Users Log In

### First-Time Login
1. User clicks "Sign in with Microsoft" button
2. Redirected to Microsoft login (if not already logged in)
3. User consents to sharing basic profile info (one time)
4. Redirected back to In-Takt
5. Django user account automatically created
6. User is logged in

### Subsequent Logins
1. User clicks "Sign in with Microsoft"
2. If already logged into Microsoft, automatically redirected back
3. User is logged into In-Takt (no password needed)

## Role-Based Access Control (RBAC)

### Django Admin Access
To give a user admin privileges:
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@yourdomain.com')
>>> user.is_staff = True  # Can access admin panel
>>> user.is_superuser = True  # Has all permissions
>>> user.save()
```

### Custom Permissions
You can add custom permissions in Django models:
```python
class Meta:
    permissions = [
        ("view_financial_data", "Can view financial data"),
        ("manage_quickbooks", "Can manage QuickBooks integration"),
    ]
```

### Group-Based Permissions
1. Create groups in Django Admin: `/admin/auth/group/`
2. Assign permissions to groups
3. Add users to groups
4. Users inherit group permissions automatically

### Azure AD Group Integration (Optional)
To sync Azure AD groups with Django groups, add this pipeline function:
```python
# In config/settings.py
def sync_azure_groups(backend, user, response, *args, **kwargs):
    """Sync Azure AD groups to Django groups"""
    if backend.name == 'azuread-tenant-oauth2':
        azure_groups = response.get('groups', [])
        # Map Azure group IDs to Django group names
        # Implementation depends on your needs
```

## Testing SSO

### Local Testing
1. Start Django server: `python manage.py runserver`
2. Navigate to: `http://localhost:8000`
3. Click "Sign in with Microsoft"
4. Log in with your Microsoft account
5. Verify you're logged in (shows "Hello, Your Name" in navigation)

### Verify User Creation
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.all()
# Should see your user account
```

## Troubleshooting

### Error: "Redirect URI mismatch"
**Solution**: Ensure `http://localhost:8000/complete/azuread-tenant-oauth2/` is added to Azure AD app → Authentication → Redirect URIs

### Error: "User is not authenticated"
**Solution**: Check that `social_django` is in `INSTALLED_APPS` and migrations are run

### Users can't log in
**Solution**: 
1. Verify app is set to "Single tenant" mode in Azure AD
2. Check that users are in the same Azure AD tenant as the app registration
3. If "User assignment required" is enabled, verify users are assigned to the app

### Want to restrict access?
**Solution**: 
1. Azure AD → Enterprise Applications → Your App
2. Properties → "User assignment required?" = Yes
3. Users and groups → Assign specific users/groups

## Security Best Practices

### Production Checklist
- [ ] Set `SOCIAL_AUTH_REDIRECT_IS_HTTPS = True`
- [ ] Use environment variables for secrets (never commit)
- [ ] Enable SSL/HTTPS on your domain
- [ ] Update redirect URIs to production domain
- [ ] Enable Azure AD Conditional Access policies (if available)
- [ ] Enable Multi-Factor Authentication (MFA) for users
- [ ] Review and minimize API permissions
- [ ] Enable audit logging in Azure AD

### Session Security
Already configured in Django:
- Session cookies are HTTP-only
- CSRF protection enabled
- Session timeout configurable

### Monitoring
- Azure AD sign-in logs: Monitor login attempts
- Django admin logs: Track user actions
- Application Insights: Monitor app usage (optional)

## Cost Analysis

| Feature | Cost | Notes |
|---------|------|-------|
| Azure AD Basic | $0 | Included with Microsoft 365 |
| OAuth 2.0 Authentication | $0 | Standard Azure AD feature |
| User accounts (up to 50,000) | $0 | Basic tier limit |
| social-auth-app-django | $0 | Open source library |
| **Total Monthly Cost** | **$0** | For basic SSO functionality |

**Premium features** (not required for SSO):
- Azure AD Premium P1 ($6/user/month): Conditional access, group-based access
- Azure AD Premium P2 ($9/user/month): Identity protection, privileged identity management

**Recommendation**: Start with free tier. Add Premium features only if you need advanced security policies.

## Next Steps

1. **Test SSO**: Log in with your Microsoft account
2. **Configure Admin Access**: Grant admin rights to key users
3. **Set Up Groups**: Create permission groups in Django Admin
4. **Production Deploy**: Update settings for HTTPS and production domain
5. **User Training**: Send users the login URL and instructions

## Support

For issues:
1. Check Django logs for errors
2. Review Azure AD sign-in logs
3. Verify app registration settings match this guide
4. Test with different user accounts

## References

- [Django Social Auth Documentation](https://python-social-auth.readthedocs.io/)
- [Azure AD OAuth 2.0 Flow](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [Django Authentication System](https://docs.djangoproject.com/en/5.2/topics/auth/)
