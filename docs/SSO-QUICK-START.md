# SSO Quick Start Guide

## ✅ What's Been Configured

Your In-Takt application now has **Azure AD Single Sign-On** enabled! Here's what's set up:

### Authentication
- ✅ Social Auth Django package installed
- ✅ Azure AD OAuth 2.0 backend configured
- ✅ Using your existing Microsoft Graph credentials (no extra cost!)
- ✅ Automatic user creation on first login
- ✅ Login button added to navigation bar
- ✅ Database tables created (migrations run)

### User Experience
- ✅ "Sign in with Microsoft" button on home page
- ✅ Automatic redirect to Microsoft login
- ✅ User profile synced from Azure AD (name, email)
- ✅ Single logout functionality
- ✅ Session management

## 🔧 One Required Step: Update Azure AD Redirect URI

Before users can log in, you need to add the SSO redirect URI to your Azure AD app:

### Steps:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: **Azure Active Directory** → **App registrations**
3. Find your app: **In-Takt** (Client ID: `70810155-f32c-46f6-8159-1618ea380966`)
4. Click **Authentication** in the left menu
5. Under **Platform configurations** → **Web** → **Redirect URIs**, click **Add URI**
6. Add this exact URI:
   ```
   http://localhost:8000/complete/azuread-tenant-oauth2/
   ```
7. Click **Save**

**Note**: Keep your existing redirect URI (`http://localhost:8000/graph/callback/`) - you need both!

## 🧪 Testing SSO

### Step 1: Verify Server is Running
The server should already be running at: http://localhost:8000

### Step 2: Access Home Page
1. Open your browser
2. Go to: http://localhost:8000
3. You should see the "Sign in with Microsoft" button (red button with Microsoft logo)

### Step 3: Test Login
1. Click "Sign in with Microsoft"
2. You'll be redirected to Microsoft login
3. Log in with your Microsoft account (if not already logged in)
4. You may see a consent screen (first time only) - click Accept
5. You'll be redirected back to In-Takt
6. You should now be logged in! (Navigation shows "Hello, Your Name")

### Step 4: Verify User Creation
Open a new terminal and run:
```bash
# WSL / Linux / macOS
cd /home/rgamage/projects/in-takt
source venv/bin/activate
python manage.py shell

# Windows
cd C:\github\in-takt
venv\Scripts\Activate.ps1
python manage.py shell
```

Then in the Python shell:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.all()
# Should show your user account
```

## 🎯 What Works Now

### For All Users
- ✅ Single Sign-On with Microsoft
- ✅ Automatic account creation
- ✅ Access to QuickBooks integration (after connecting)
- ✅ Access to Microsoft Graph integration (after connecting)

### For Admins (You)
To make yourself an admin:
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email='your-email@yourdomain.com')
user.is_staff = True
user.is_superuser = True
user.save()
```

Then access Django Admin at: http://localhost:8000/admin/

## 🔒 Access Control Options

### Option 1: Open to All Organization Users (Default)
Any user in your Azure AD tenant can log in.
- ✅ Simple setup
- ✅ Good for small organizations
- ✅ No additional configuration needed

### Option 2: Restrict to Specific Users
1. Go to Azure Portal
2. **Azure Active Directory** → **Enterprise Applications**
3. Find your app: **In-Takt**
4. **Properties** → Set "User assignment required?" to **Yes**
5. **Users and groups** → Click **Add user/group**
6. Select specific users or security groups
7. Click **Assign**

Now only assigned users can log in!

## 📋 Files Modified

Here's what was changed in your project:

### Configuration Files
- `config/settings.py` - Added social auth configuration
- `config/urls.py` - Added social auth URLs
- `requirements.txt` - Added social-auth-app-django
- `.env` - Added social auth redirect URI (documentation only)

### Templates
- `templates/base.html` - Updated login button to use SSO

### Database
- Ran migrations to create social auth tables

## 🚀 Production Deployment

When you're ready to deploy to production:

### 1. Update Settings
In `config/settings.py` or production settings file:
```python
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
```

### 2. Add Production Redirect URI
In Azure AD app → Authentication → Add URI:
```
https://yourdomain.com/complete/azuread-tenant-oauth2/
```

### 3. Update Environment Variables
In production `.env`:
```bash
SOCIAL_AUTH_REDIRECT_URI=https://yourdomain.com/complete/azuread-tenant-oauth2/
```

### 4. Enable Security Features
- Enable HTTPS/SSL on your domain
- Set `DEBUG = False`
- Use strong `SECRET_KEY`
- Enable Azure AD Conditional Access policies (if available)
- Require MFA for users

## 💰 Cost Breakdown

| Item | Cost |
|------|------|
| Azure AD Basic SSO | $0 |
| OAuth 2.0 Authentication | $0 |
| social-auth-app-django | $0 |
| User Accounts (up to 50k) | $0 |
| **TOTAL** | **$0** |

**No extra costs!** You're using the free tier of Azure AD that comes with Microsoft 365.

## 🆘 Troubleshooting

### "Redirect URI mismatch" error
- ✅ Verify you added `http://localhost:8000/complete/azuread-tenant-oauth2/` to Azure AD
- ✅ Check the URI is exact (case-sensitive)

### Login button doesn't work
- ✅ Check Django server is running
- ✅ Check browser console for JavaScript errors
- ✅ Try clearing browser cookies

### User not created after login
- ✅ Check Django logs for errors
- ✅ Verify `social_django` is in INSTALLED_APPS
- ✅ Verify migrations were run: `python manage.py migrate`

### "User is not authenticated" after login
- ✅ Check session middleware is enabled
- ✅ Clear browser cookies and try again
- ✅ Check `LOGIN_REDIRECT_URL` is set to `/`

## 📚 Documentation

For detailed information, see:
- [Full SSO Setup Guide](./SSO-SETUP.md) - Complete documentation
- [Django Social Auth Docs](https://python-social-auth.readthedocs.io/)
- [Azure AD OAuth 2.0](https://learn.microsoft.com/en-us/azure/active-directory/develop/)

## ✨ Next Steps

1. **Add the redirect URI to Azure AD** (see above)
2. **Test the login flow** (see Testing SSO above)
3. **Make yourself an admin** (see What Works Now above)
4. **Invite your team** - They can now log in with Microsoft!
5. **Configure permissions** - Set up Django groups and permissions as needed

## 🎉 That's It!

Your SSO is now configured! Users from your organization can log in with their Microsoft credentials - no passwords to remember, no separate accounts to manage.

Questions? Check the [Full SSO Setup Guide](./SSO-SETUP.md) for detailed information.
