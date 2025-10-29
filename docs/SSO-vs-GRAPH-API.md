# Understanding SSO vs Microsoft Graph API Authentication# SSO Authentication vs Microsoft Graph API



## Two Separate Authentication Systems## Important: Two Separate Authentications



Your In-Takt application now has **two independent authentication systems**:Your In-Takt application now has **two different Microsoft integrations**:



### 1. Azure AD SSO (Single Sign-On) ✅ WORKING### 1. Azure AD SSO (Single Sign-On) ✅ WORKING

**Purpose**: Authenticate users to access the Django application**Purpose**: Log users into the Django application

**URL**: "Sign in with Microsoft" button

**What it does**:**What it does**:

- Allows users to log in with their Microsoft account- Authenticates users via Azure AD

- Creates Django user accounts automatically- Creates Django user accounts automatically

- Provides access to the In-Takt web portal- Allows access to the application

- Uses scopes: `openid`, `email`, `profile`- Uses user's email, first name, last name



**Tokens**: Stored in Django session, used ONLY for user authentication**Token Scopes**:

- `openid` - Basic authentication

**Login URL**: Click "Sign in with Microsoft" button (red button in nav)- `email` - User's email address

- `profile` - User's basic profile

**Status**: ✅ Working! You're logged in as Randy Gamage

**What you CAN do after SSO login**:

---- ✅ Access the In-Takt application

- ✅ Use QuickBooks integration

### 2. Microsoft Graph API Access ⚠️ SEPARATE FLOW- ✅ Access Django admin (if staff/superuser)

**Purpose**: Access Microsoft 365 data (emails, calendar, OneDrive, etc.)- ✅ Use any app features



**What it does**:**What you CANNOT do**:

- Separate OAuth flow for Microsoft Graph API- ❌ Access Microsoft Graph API (requires separate login)

- Requests different scopes: `User.Read`, `Mail.Read`, `Calendars.Read`, etc.- ❌ Read user's calendar, emails, files

- Uses different tokens stored separately in session- ❌ Access Office 365 data



**Tokens**: Stored separately in `request.session['graph_access_token']`### 2. Microsoft Graph API Integration 🔄 REQUIRES SEPARATE LOGIN

**Purpose**: Access Office 365 data (calendar, email, files, etc.)

**Login URL**: Navigate to `/graph/login/` or click "Login with Microsoft" on the Graph profile page**URL**: `/graph/login/` (separate from SSO login)

**What it does**:

**Status**: ⚠️ Not connected yet - you need to do this separately- Requests additional permissions to access Office 365 data

- Stores Graph API access tokens

---- Allows reading/writing to Microsoft services



## Why Two Separate Logins?**Token Scopes**:

- `User.Read` - Read user profile

**Security & Permissions**: - `Calendars.Read` - Read calendar events

- SSO only needs basic info (name, email) to log you into the app- `Mail.Read` - Read emails

- Graph API requires additional permissions to access your Microsoft 365 data- (More scopes as needed)

- Users should explicitly consent to giving the app access to their emails/calendar

**Important**: Even if you're logged in via SSO, you still need to separately authorize the Microsoft Graph API integration to access your Office 365 data.

**Best Practice**:

- Don't request Graph API permissions unless actually needed## Why Two Separate Logins?

- Keep authentication simple (SSO) separate from data access (Graph API)

This is a **security and privacy best practice**:

---

1. **Separation of Concerns**: 

## How to Fix the 403 Error   - SSO only needs basic identity info (who you are)

   - Graph API needs access to personal data (calendar, email, files)

The `/api/v1/graph/me/` endpoint is trying to call Microsoft Graph API, but you're only logged in via SSO (which doesn't have Graph API tokens).

2. **User Control**:

### Solution: Log in to Microsoft Graph   - Users can log into the app without giving access to their personal data

1. Navigate to http://localhost:8000/graph/login/   - Users explicitly consent to data access

2. Click "Login with Microsoft"

3. Consent to the Graph API permissions3. **Principle of Least Privilege**:

4. You'll be redirected to the profile page with your data   - Application only requests what it needs

   - Reduces security risk

---

## User Experience

## Current Status

### First Time Using In-Takt

```

✅ SSO Authentication: WORKING**Step 1: Log in with SSO**

   - User: Randy Gamage (randy1)1. Click "Sign in with Microsoft"

   - Email: randy@integral-methods.com2. Log in with Microsoft credentials

   - Can access: Django app, QuickBooks integration3. ✅ You're now logged into In-Takt

4. You can access most features

⚠️ Microsoft Graph API: NOT CONNECTED

   - Need to: Navigate to /graph/login/**Step 2: (Optional) Connect Microsoft Graph**

   - Will grant: Access to Microsoft 365 data1. Navigate to Microsoft Graph section

   - Required for: Profile page, email/calendar features2. Click "Login with Microsoft" in the Graph section

```3. Consent to additional permissions

4. ✅ Now you can access Office 365 data

---

### After Initial Setup

## Quick Actions

**When you return to the app**:

### 1. See your full name in navigation- SSO keeps you logged into Django (session persists)

Refresh your browser - you should now see "Hello, Randy Gamage" instead of "Hello, randy1"- Graph API tokens expire after some time (need to re-authorize)



### 2. Clean up duplicate user accounts (optional)## For Your Use Case

```bash

cd /home/rgamage/projects/in-taktSince you want **SSO for organization access**, you have two options:

source venv/bin/activate

python cleanup_users.py### Option A: SSO Only (Recommended for most users)

```- Users log in via Azure AD SSO

- They don't need Microsoft Graph API access

This will remove the duplicate "rgamage" and "randy" accounts created during testing.- They use QuickBooks and other features

- **No 403 errors** because they're not trying to use Graph API

### 3. Connect to Microsoft Graph API

Navigate to: http://localhost:8000/graph/login/### Option B: SSO + Graph API (For users who need Office 365 data)

- Users log in via Azure AD SSO first

---- Then separately authorize Graph API when needed

- They can access both app features AND Office 365 data

## Summary

## Fixing the 403 Error

**Your 403 error is expected behavior!** You're logged into the Django app via SSO, but haven't connected to Microsoft Graph API yet. This is by design for security and user consent reasons.

The 403 error you're seeing is because:

To use Graph API features, navigate to `/graph/login/` and complete the second OAuth flow.1. ✅ You're logged in via SSO (working)

2. ❌ You haven't authorized the Microsoft Graph API
3. The app is trying to call Graph API without proper tokens

**Solution**: Either:

**Option 1: Don't use Graph API features**
- Remove the Graph API profile link from the UI
- Users only need SSO to access the app
- No need for Graph API tokens

**Option 2: Add separate Graph API authorization**
- Keep both SSO and Graph API
- Show a message: "To access Microsoft 365 data, please authorize Graph API"
- Users click a separate button to authorize Graph API

## Recommended Home Page Updates

Update the home page to clarify:

```html
<!-- SSO Status (Django Login) -->
<div class="card">
  <h3>Application Access</h3>
  {% if user.is_authenticated %}
    <p>✅ Logged in as {{ user.email }}</p>
    <p>You can access all application features.</p>
  {% else %}
    <a href="{% url 'social:begin' 'azuread-tenant-oauth2' %}">Sign in with Microsoft</a>
  {% endif %}
</div>

<!-- Graph API Status (Optional) -->
<div class="card">
  <h3>Microsoft 365 Integration (Optional)</h3>
  {% if request.session.graph_access_token %}
    <p>✅ Microsoft Graph API authorized</p>
    <p>You can access Office 365 data.</p>
    <a href="/graph/profile/">View My Profile</a>
  {% else %}
    <p>⚠️ Not authorized</p>
    <p>To access your calendar, email, and files:</p>
    <a href="/graph/login/">Authorize Microsoft Graph</a>
  {% endif %}
</div>
```

## For Your Team

When rolling this out to your organization:

**What to tell users**:
1. "Click 'Sign in with Microsoft' to log into In-Takt"
2. "Use your work Microsoft account"
3. "If you need to access Office 365 data within the app, you'll be prompted to authorize that separately"

**What NOT to do**:
- Don't tell users they need to connect to Graph API unless they actually need those features
- Don't remove SSO in favor of Graph API (SSO is simpler and better for basic authentication)

## Technical Details

### SSO Flow (Simplified)
```
User → "Sign in with Microsoft" 
→ Azure AD OAuth (openid, email, profile) 
→ Django creates user account 
→ Django session authenticated 
→ ✅ User can access app
```

### Graph API Flow (Simplified)
```
User → "Login with Microsoft Graph" 
→ Azure AD OAuth (User.Read, Mail.Read, etc.) 
→ Store Graph access token in session 
→ ✅ Can call Graph API to read emails, calendar, etc.
```

### Combined Flow
```
User → SSO login first (Django authentication)
↓
✅ Logged into app
↓
(Optional) User → Graph API authorization
↓
✅ Can now use BOTH app features AND Office 365 data
```

## Summary

- **SSO = Logging into the app** ✅ WORKING
- **Graph API = Accessing Office 365 data** (separate authorization required)
- You need SSO for basic app access
- You only need Graph API if you want to read/write Office 365 data
- The 403 error is expected if Graph API hasn't been authorized
- This is by design for security and user privacy

## Next Steps

1. **Update home page** to clarify the two different integrations
2. **Remove Graph API links** if you don't need Office 365 data
3. **OR Add clear messaging** that Graph API is optional/separate
4. **Document for users** that they only need SSO to access the app
