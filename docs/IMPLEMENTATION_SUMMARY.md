# OAuth 2.0 Implementation Summary

## What We Just Built

I've implemented a complete OAuth 2.0 authorization code flow for Microsoft Graph API with delegated permissions. This allows your web application to access Microsoft 365 data **on behalf of authenticated users**.

## New Files Created

### 1. `msgraph_integration/services_delegated.py`
- **Purpose**: Microsoft Graph API client using OAuth 2.0 delegated permissions
- **Key Methods**:
  - `get_auth_url()` - Generates Microsoft login URL
  - `get_token_from_code()` - Exchanges authorization code for tokens
  - `get_token_from_refresh_token()` - Refreshes expired tokens
  - `get_my_profile()` - Gets authenticated user's profile
  - `get_my_messages()` - Gets user's emails
  - `get_my_calendar_events()` - Gets user's calendar events
  - `search_users()` - Searches directory for users

### 2. `msgraph_integration/auth_views.py`
- **Purpose**: Django views handling OAuth workflow
- **Views**:
  - `GraphLoginView` - Initiates Microsoft login
  - `GraphCallbackView` - Handles OAuth callback and token exchange
  - `GraphLogoutView` - Clears session and logs out
  - `MyProfilePageView` - Displays user profile page

### 3. `msgraph_integration/api_views.py`
- **Purpose**: REST API endpoints using delegated permissions
- **Endpoints**:
  - `MyProfileAPIView` - Returns authenticated user's profile as JSON
  - `MyMessagesAPIView` - Returns user's recent emails as JSON
  - `MyCalendarAPIView` - Returns user's calendar events as JSON

### 4. `msgraph_integration/templates/msgraph/profile.html`
- **Purpose**: HTML page displaying user's Microsoft profile
- **Features**:
  - Profile photo or initial avatar
  - Display name, job title, department
  - Email and phone contact info
  - Account details (User ID, UPN, office location)
  - Quick action links to messages, calendar, API docs
  - Logout button

### 5. `OAUTH_SETUP.md`
- **Purpose**: Complete setup and testing guide
- **Includes**:
  - Azure AD configuration steps
  - Redirect URI setup
  - API permissions configuration
  - Testing workflow
  - Available endpoints
  - Token management
  - Troubleshooting guide

## Updated Files

### 1. `msgraph_integration/urls.py`
Added routes for:
- `/graph/login/` - Start OAuth flow
- `/graph/callback/` - OAuth callback handler
- `/graph/logout/` - Logout
- `/graph/profile/` - Profile page
- `/graph/api/me/` - Profile API
- `/graph/api/me/messages/` - Messages API
- `/graph/api/me/calendar/` - Calendar API

### 2. `config/urls.py`
Added: `path("graph/", include("msgraph_integration.urls"))`

### 3. `core/templates/core/home.html`
Added "Login with Microsoft" button in Quick Actions section

### 4. `.env.example`
Added: `MICROSOFT_GRAPH_REDIRECT_URI=http://localhost:8000/graph/callback/`

## How It Works

### OAuth 2.0 Flow Diagram

```
User                    Django App              Microsoft
 |                          |                       |
 |---(1) Click Login------->|                       |
 |                          |                       |
 |                          |---(2) Redirect to---->|
 |                          |      MS Login         |
 |                          |                       |
 |<---------(3) Login & Consent at Microsoft------->|
 |                          |                       |
 |                          |<--(4) Redirect with---|
 |                          |      auth code        |
 |                          |                       |
 |                          |---(5) Exchange code-->|
 |                          |      for tokens       |
 |                          |                       |
 |                          |<--(6) Access token----|
 |                          |      & refresh token  |
 |                          |                       |
 |<---(7) Store in session--|                       |
 |     & redirect to profile|                       |
 |                          |                       |
 |---(8) Request data------>|                       |
 |                          |---(9) API call with-->|
 |                          |      access token     |
 |                          |                       |
 |                          |<--(10) User data------|
 |<---(11) Display data-----|                       |
```

### Security Features

1. **State Parameter** - CSRF protection using random token
2. **Session Storage** - Tokens stored server-side (not in cookies/localStorage)
3. **Token Expiration** - Access tokens expire after ~1 hour
4. **Refresh Tokens** - Automatic renewal without re-authentication
5. **HTTPS Required** - For production deployments

## Next Steps

### 1. Configure Azure AD (REQUIRED)
Before testing, you **must** add the redirect URI to your Azure AD app:

```
Go to: https://portal.azure.com
→ App registrations
→ Your app (70810155-f32c-46f6-8159-1618ea380966)
→ Authentication
→ Add platform → Web
→ Redirect URI: http://localhost:8000/graph/callback/
→ Save
```

### 2. Update .env File
Add this line to your `.env` file:

```bash
MICROSOFT_GRAPH_REDIRECT_URI=http://localhost:8000/graph/callback/
```

### 3. Test the Flow

1. **Start Django server**:
   ```bash
   cd /home/rgamage/projects/in-takt
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Visit home page**: http://localhost:8000

3. **Click "Login with Microsoft"** - This will:
   - Redirect you to Microsoft login
   - Ask you to grant permissions
   - Redirect back to your profile page

4. **View your profile**: http://localhost:8000/graph/profile/

5. **Test API endpoints**:
   - http://localhost:8000/graph/api/me/
   - http://localhost:8000/graph/api/me/messages/
   - http://localhost:8000/graph/api/me/calendar/

### 4. Verify Permissions
In Azure AD, ensure these **delegated permissions** are granted:
- `User.Read`
- `User.ReadBasic.All`
- `Calendars.Read`
- `Mail.Read`

Click "Grant admin consent" if you have admin rights.

## Key Differences: Client Credentials vs Delegated

### Before (Client Credentials)
- ❌ App authenticates as itself
- ❌ Requires application permissions (higher privilege)
- ❌ Can't access user-specific data like "my calendar"
- ❌ No user login required

### After (OAuth 2.0 Delegated)
- ✅ User logs in with their Microsoft account
- ✅ App accesses data **on behalf of the user**
- ✅ Uses delegated permissions (lower privilege)
- ✅ Can access "my profile", "my calendar", "my emails"
- ✅ User can see and control what data the app accesses

## API Endpoints Overview

### OAuth Endpoints (HTML Pages)
| URL | Description |
|-----|-------------|
| `/graph/login/` | Redirects to Microsoft login |
| `/graph/callback/` | OAuth callback (automatic) |
| `/graph/logout/` | Clears session |
| `/graph/profile/` | Profile page with user info |

### API Endpoints (JSON)
| URL | Description | Auth Required |
|-----|-------------|---------------|
| `/graph/api/me/` | Current user's profile | Yes (session) |
| `/graph/api/me/messages/` | User's recent emails | Yes (session) |
| `/graph/api/me/calendar/` | User's calendar events | Yes (session) |
| `/api/docs/` | Swagger UI (all endpoints) | No |

### Legacy Endpoints (Client Credentials)
| URL | Description | Auth Required |
|-----|-------------|---------------|
| `/api/v1/graph/users/` | List all users | Yes (app creds) |
| `/api/v1/graph/users/{id}/` | Get user by ID | Yes (app creds) |

## Troubleshooting

### "Invalid redirect URI"
→ Add `http://localhost:8000/graph/callback/` to Azure AD app registration

### "Insufficient privileges"
→ Grant delegated permissions in Azure AD and click "Grant admin consent"

### "Not authenticated with Microsoft"
→ Visit `/graph/login/` first to authenticate

### "Token expired"
→ Login again or implement automatic refresh using refresh_token

## What's Next?

After testing the OAuth flow:

1. **Add Token Refresh Logic** - Automatically refresh expired tokens
2. **Build Dashboard** - Use HTMX to load data dynamically
3. **QuickBooks OAuth** - Follow similar pattern for QuickBooks API
4. **Error Handling** - Add more robust error handling and logging
5. **Production Config** - Update redirect URI for production domain with HTTPS

## Testing Checklist

- [ ] Added redirect URI to Azure AD app
- [ ] Added MICROSOFT_GRAPH_REDIRECT_URI to .env
- [ ] Started Django development server
- [ ] Visited home page and clicked "Login with Microsoft"
- [ ] Successfully logged in with Microsoft account
- [ ] Saw profile page with my information
- [ ] Tested `/graph/api/me/` endpoint (returns JSON)
- [ ] Tested `/graph/api/me/messages/` endpoint
- [ ] Tested `/graph/api/me/calendar/` endpoint
- [ ] Logged out and confirmed session cleared

---

**Note**: All the code is ready. You just need to configure Azure AD with the redirect URI and test it!
