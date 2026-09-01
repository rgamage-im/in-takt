# Quick Reference - In-Takt OAuth Testing

## 🚀 Quick Start (3 Steps)

### Step 1: Azure AD Setup
1. Go to https://portal.azure.com → App registrations
2. Select app: **70810155-f32c-46f6-8159-1618ea380966**
3. Go to **Authentication** → **Add platform** → **Web**
4. Add redirect URI: **`http://localhost:8000/graph/callback/`**
5. Save

### Step 2: Update .env
Add this line to `.env`:
```bash
MICROSOFT_GRAPH_REDIRECT_URI=http://localhost:8000/graph/callback/
```

### Step 3: Test
```bash
# WSL / Linux / macOS
cd /home/rgamage/projects/in-takt
source venv/bin/activate
python manage.py runserver
```

```powershell
# Windows
cd C:\github\in-takt
venv\Scripts\Activate.ps1
python manage.py runserver
```

Then visit: **http://localhost:8000** → Click **"Login with Microsoft"**

---

## 📍 Important URLs

| URL | What It Does |
|-----|--------------|
| http://localhost:8000 | Home page |
| http://localhost:8000/graph/login/ | Start Microsoft login |
| http://localhost:8000/graph/profile/ | Your profile page |
| http://localhost:8000/graph/api/me/ | Your profile (JSON) |
| http://localhost:8000/api/docs/ | API documentation |

---

## 🔑 Required Azure AD Permissions

These **delegated permissions** must be granted in Azure AD:
- ✅ User.Read
- ✅ User.ReadBasic.All
- ✅ Calendars.Read
- ✅ Mail.Read

Don't forget to click **"Grant admin consent"**!

---

## 🧪 Testing Workflow

1. **Click "Login with Microsoft"** on home page
2. **Enter your Microsoft credentials**
3. **Grant consent** to requested permissions
4. **View your profile** at `/graph/profile/`
5. **Test API endpoints**:
   - `/graph/api/me/` - Your profile as JSON
   - `/graph/api/me/messages/` - Your recent emails
   - `/graph/api/me/calendar/` - Your calendar events

---

## 📚 Documentation Files

- **`IMPLEMENTATION_SUMMARY.md`** - Complete overview of what was built
- **`OAUTH_SETUP.md`** - Detailed setup and troubleshooting guide
- **`development-guidelines.md`** - Original development guidelines

---

## 🆘 Common Issues

| Error | Solution |
|-------|----------|
| "Invalid redirect URI" | Add `http://localhost:8000/graph/callback/` to Azure AD |
| "Insufficient privileges" | Grant delegated permissions and admin consent |
| "Not authenticated" | Visit `/graph/login/` first |
| "Token expired" | Login again (will auto-redirect) |

---

## 🎯 What Changed

**Before**: App used client credentials flow (app authenticates as itself)
**After**: App uses OAuth 2.0 flow (users login with their Microsoft account)

This means:
- ✅ Users authenticate with their own credentials
- ✅ App accesses data **on behalf of the user**
- ✅ Can access "my calendar", "my emails", etc.
- ✅ Lower privilege requirements (delegated vs application)

---

## ⚡ Quick Commands

### Start Server
```bash
# Windows
venv\Scripts\python manage.py runserver

# WSL
wsl bash -c "cd /home/rgamage/projects/in-takt && source venv/bin/activate && python manage.py runserver"
```

### Check for Errors
```bash
# Windows
venv\Scripts\python manage.py check

# WSL
wsl bash -c "cd /home/rgamage/projects/in-takt && source venv/bin/activate && python manage.py check"
```

### View Logs
Watch terminal for OAuth flow logs and any errors

---

**Ready to test? Follow the 3 steps above and you're good to go!** 🚀
