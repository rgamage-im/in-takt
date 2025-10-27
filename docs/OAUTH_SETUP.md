# Microsoft Graph OAuth 2.0 Setup Guide

## Overview
This application uses OAuth 2.0 authorization code flow with delegated permissions to access Microsoft Graph API on behalf of authenticated users.

## Azure AD App Registration Configuration

### 1. Redirect URI
Add the following redirect URI to your Azure AD app registration:
```
http://localhost:8000/graph/callback/
```

**Steps:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "App registrations"
3. Select your app (Client ID: `70810155-f32c-46f6-8159-1618ea380966`)
4. Go to "Authentication" → "Add a platform" → "Web"
5. Enter redirect URI: `http://localhost:8000/graph/callback/`
6. Save changes

### 2. API Permissions (Delegated)
Ensure the following Microsoft Graph **delegated permissions** are granted:

- `User.Read` - Read signed-in user's profile
- `User.ReadBasic.All` - Read basic profiles of all users
- `Calendars.Read` - Read user's calendars
- `Mail.Read` - Read user's mail

**Steps:**
1. In your app registration, go to "API permissions"
2. Click "Add a permission" → "Microsoft Graph" → "Delegated permissions"
3. Search for and select each permission above
4. Click "Add permissions"
5. Click "Grant admin consent" (requires admin privileges)

### 3. Environment Variables
Add to your `.env` file:
```bash
MICROSOFT_GRAPH_REDIRECT_URI=http://localhost:8000/graph/callback/
```

## Testing the OAuth Flow

### Step 1: Start Django Server
```bash
cd /home/rgamage/projects/in-takt
source venv/bin/activate
python manage.py runserver
```

### Step 2: Initiate Login
Visit: http://localhost:8000/graph/login/

This will:
1. Generate a secure state token (CSRF protection)
2. Store state in session
3. Redirect you to Microsoft login page

### Step 3: Microsoft Login & Consent
You'll be redirected to Microsoft's login page where you will:
1. Enter your Microsoft credentials
2. Review requested permissions
3. Grant consent to the application

### Step 4: Callback & Token Exchange
After successful authentication, Microsoft redirects back to:
```
http://localhost:8000/graph/callback/?code=<authorization_code>&state=<state_token>
```

The callback handler will:
1. Verify the state token (CSRF protection)
2. Exchange authorization code for access token
3. Store tokens in Django session
4. Redirect to your profile page

### Step 5: View Profile
You should now see your Microsoft profile at:
http://localhost:8000/graph/profile/

## Available Endpoints

### OAuth Endpoints
- `/graph/login/` - Initiate Microsoft login
- `/graph/callback/` - OAuth callback (configured in Azure AD)
- `/graph/logout/` - Clear session and logout
- `/graph/profile/` - View your Microsoft profile (HTML page)

### API Endpoints (JSON responses)
- `/graph/api/me/` - Get your profile (JSON)
- `/graph/api/me/messages/` - Get your recent emails (JSON)
- `/graph/api/me/calendar/` - Get your calendar events (JSON)

### Legacy Endpoints (Client Credentials - requires Application permissions)
- `/api/v1/graph/users/` - List all users
- `/api/v1/graph/users/{id}/` - Get specific user profile
- `/api/v1/graph/users/search/?q=query` - Search users

## API Documentation
Interactive API docs with Swagger UI:
http://localhost:8000/api/docs/

## Token Management

### Access Token
- Stored in session: `request.session['graph_access_token']`
- Valid for ~1 hour
- Used to make API calls on behalf of the user

### Refresh Token
- Stored in session: `request.session['graph_refresh_token']`
- Valid for ~90 days
- Used to obtain new access tokens without re-authentication

### Token Refresh (Automatic)
The `GraphServiceDelegated` class includes a `get_token_from_refresh_token()` method that can automatically refresh expired tokens. You can implement this in your API views:

```python
access_token = request.session.get('graph_access_token')
refresh_token = request.session.get('graph_refresh_token')

try:
    # Make API call
    data = graph_service.get_my_profile(access_token)
except Exception as e:
    if '401' in str(e):  # Token expired
        # Refresh token
        token_response = graph_service.get_token_from_refresh_token(refresh_token)
        request.session['graph_access_token'] = token_response['access_token']
        request.session['graph_refresh_token'] = token_response['refresh_token']
        # Retry API call
        data = graph_service.get_my_profile(token_response['access_token'])
```

## Troubleshooting

### Error: "Invalid redirect URI"
- Ensure `http://localhost:8000/graph/callback/` is added to Azure AD app registration
- Check that MICROSOFT_GRAPH_REDIRECT_URI in .env matches exactly

### Error: "Insufficient privileges"
- Verify delegated permissions are granted in Azure AD
- Ensure admin consent is granted (click "Grant admin consent" button)
- Make sure you're using delegated permissions, not application permissions

### Error: "CSRF verification failed"
- Clear your browser cookies and try again
- Ensure state parameter is being stored and verified correctly

### Error: "Token expired"
- Click "Login with Microsoft" again to get a new token
- Implement automatic token refresh using refresh_token

### Error: "Not authenticated with Microsoft"
- You need to login first by visiting `/graph/login/`
- Session may have expired - login again

## Security Best Practices

1. **CSRF Protection**: State parameter is used to prevent CSRF attacks
2. **Session Security**: Tokens are stored in Django sessions (server-side)
3. **HTTPS in Production**: Always use HTTPS for redirect URIs in production
4. **Token Expiration**: Access tokens expire after ~1 hour
5. **Refresh Tokens**: Refresh tokens should be used to obtain new access tokens
6. **Scope Limitation**: Only request the permissions you actually need

## Next Steps

1. Configure Azure AD app registration with redirect URI
2. Test the OAuth flow by visiting `/graph/login/`
3. Verify profile page displays your Microsoft account information
4. Test API endpoints at `/graph/api/me/`, `/graph/api/me/messages/`, etc.
5. Implement automatic token refresh in API views
6. Add QuickBooks OAuth integration following similar pattern
7. Build dashboard with HTMX for dynamic data loading

## Production Considerations

For production deployment:
1. Update redirect URI to use your production domain with HTTPS
2. Store secrets in Azure Key Vault instead of .env file
3. Enable Django session security settings (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
4. Implement proper logging and error handling
5. Add rate limiting to API endpoints
6. Configure Azure Application Insights for monitoring
