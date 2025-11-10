# SharePoint Drives Missing - SOLUTION

## Problem

When calling `/graph/api/me/drives/`, you only see:
- Your personal OneDrive for Business
- A PersonalCacheLibrary

**Missing:** All your SharePoint team site document libraries

## Root Cause

The Microsoft Graph API endpoint `/me/drives` only returns drives where you are the **owner**. SharePoint team sites are owned by the organization/team, not individual users, so they don't appear in this list.

## Solution

I've added **3 new endpoints** that properly access SharePoint:

### 1. Get ALL Accessible Drives (RECOMMENDED)

**Endpoint:** `GET /graph/api/drives/all/`

This returns:
- ✅ Your personal OneDrive for Business
- ✅ ALL SharePoint team site document libraries you have access to
- ✅ Metadata showing which are personal vs SharePoint

**Example Response:**
```json
{
  "value": [
    {
      "id": "b!abc123...",
      "name": "OneDrive",
      "driveType": "business",
      "_source": "personal"
    },
    {
      "id": "b!xyz789...",
      "name": "Documents",
      "driveType": "documentLibrary",
      "_source": "sharepoint",
      "_siteName": "Finance Team Site",
      "_siteId": "contoso.sharepoint.com,abc..."
    },
    {
      "id": "b!def456...",
      "name": "Shared Documents",
      "driveType": "documentLibrary",
      "_source": "sharepoint",
      "_siteName": "HR Team Site"
    }
  ],
  "totalDrives": 8
}
```

### 2. List SharePoint Sites

**Endpoint:** `GET /graph/api/sharepoint/sites/`

List all SharePoint team sites you have access to.

**Optional parameter:** `?search=Finance` to filter by name

### 3. Search ALL Drives Including SharePoint

**Endpoint:** `GET /graph/api/drives/search-all/`

**This is the most comprehensive search** - searches:
- Your personal OneDrive
- ALL SharePoint team sites
- All document libraries

**Example:**
```bash
GET /graph/api/drives/search-all/?q=receipt

# Response includes source info:
{
  "value": [
    {
      "name": "receipt-001.pdf",
      "_driveInfo": {
        "source": "sharepoint",
        "siteName": "Finance Team Site",
        "name": "Documents"
      }
    }
  ],
  "totalDrivesSearched": 8,
  "totalResults": 15
}
```

## Required Permission

I've added the `Sites.Read.All` permission to your app. You need to:

### Step 1: Add Permission in Azure AD

1. Go to Azure Portal → Azure Active Directory → App Registrations
2. Select your app
3. Go to "API Permissions"
4. Click "Add a permission" → Microsoft Graph → Delegated permissions
5. Search for and add: **Sites.Read.All**
6. Click "Grant admin consent" (if you're an admin)

### Step 2: Users Must Re-authenticate

**IMPORTANT:** Users who already logged in won't have this permission. They must:

1. **Log out:** Visit `http://localhost:8000/graph/logout/`
2. **Log back in:** Visit `http://localhost:8000/graph/login/`
3. **Accept new permission:** They'll see a consent screen asking for permission to "Read items in all site collections"

## Testing

### Quick Test (Python)

```python
import requests

cookies = {'sessionid': 'your-session-id'}

# Get ALL drives including SharePoint
r = requests.get('http://localhost:8000/graph/api/drives/all/', cookies=cookies)
drives = r.json()

print(f"Total drives: {drives['totalDrives']}")
for drive in drives['value']:
    source = drive.get('_source', 'unknown')
    site = drive.get('_siteName', 'N/A')
    print(f"[{source}] {drive['name']} - Site: {site}")
```

### Expected Output

```
Total drives: 8
[personal] OneDrive - Site: N/A
[personal] PersonalCacheLibrary - Site: N/A
[sharepoint] Documents - Site: Finance Team Site
[sharepoint] Shared Documents - Site: HR Team Site
[sharepoint] Documents - Site: Engineering Site
...
```

## Updated Endpoints Summary

| Old Endpoint | Issue | New Endpoint | Benefit |
|-------------|-------|--------------|---------|
| `/graph/api/me/drives/` | Only shows owned drives | `/graph/api/drives/all/` | Shows OneDrive + SharePoint |
| `/graph/api/me/drive/search-all/` | Only searches owned drives | `/graph/api/drives/search-all/` | Searches everywhere including SharePoint |
| N/A | No way to list sites | `/graph/api/sharepoint/sites/` | Lists all accessible SharePoint sites |

## Next Steps

1. ✅ **Add `Sites.Read.All` permission in Azure AD** (see Step 1 above)
2. ✅ **Log out and log back in** to grant the new permission
3. ✅ **Test:** Call `/graph/api/drives/all/` to see all your drives
4. ✅ **Use:** Switch to `/graph/api/drives/search-all/` for comprehensive searches

## Why This Matters for Your Receipt Workflow

Now when you search for receipts, the search will include:
- ✅ Receipts in your personal OneDrive
- ✅ Receipts in the Finance SharePoint site
- ✅ Receipts in any team site document library
- ✅ Shared folders synced from SharePoint to your PC

You'll be able to find receipts stored anywhere in your organization!
