# OneDrive API Documentation

## Overview

The OneDrive integration provides REST API endpoints for accessing and searching OneDrive files and folders using Microsoft Graph API with delegated permissions.

## Prerequisites

### Azure AD App Registration Permissions

Add the following Microsoft Graph **delegated permissions** to your Azure AD app:

- `Files.Read` - Read user files
- `Files.Read.All` - Read all files user can access
- `Sites.Read.All` - **Required for SharePoint sites** - Read items in all site collections

### User Authentication

All endpoints require the user to be authenticated with Microsoft Graph. The API uses session-based tokens from the OAuth flow.

## API Endpoints

### 1. Get My OneDrive Info

**GET** `/graph/api/me/drive/`

Get information about the authenticated user's default OneDrive.

**Response:**
```json
{
  "id": "drive-id",
  "driveType": "personal",
  "owner": {
    "user": {
      "displayName": "User Name",
      "email": "user@example.com"
    }
  },
  "quota": {
    "total": 1099511627776,
    "used": 123456789,
    "remaining": 1099388170987,
    "state": "normal"
  }
}
```

### 2. List All Drives

**GET** `/graph/api/me/drives/`

List all drives available to the user (OneDrive, SharePoint sites, etc.).

**⚠️ IMPORTANT:** This endpoint only returns drives where the user is the **owner** (typically just your personal OneDrive). For SharePoint team sites, use `/graph/api/drives/all/` instead.

**Response:**
```json
{
  "value": [
    {
      "id": "drive-id-1",
      "name": "OneDrive",
      "driveType": "personal"
    }
  ]
}
```

### 2b. List ALL Accessible Drives (Including SharePoint)

**GET** `/graph/api/drives/all/`

**⭐ RECOMMENDED:** List ALL drives accessible to the user, including SharePoint team sites.

This endpoint returns:
- Personal OneDrive for Business
- SharePoint site document libraries  
- All team sites you have access to

**Response:**
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
      "_siteId": "finance.sharepoint.com,abc123..."
    }
  ],
  "totalDrives": 5
}
```

### 3. List Folder Contents

**GET** `/graph/api/me/drive/contents/`

List files and folders in a OneDrive location.

**Query Parameters:**
- `path` (optional) - Folder path, e.g., `Documents/Receipts`
- `item_id` (optional) - Folder item ID
- `drive_id` (optional) - Specific drive ID (uses default OneDrive if not specified)

**Priority:** If multiple parameters provided: `item_id` > `path` > root folder

**Examples:**

Get root folder contents:
```
GET /graph/api/me/drive/contents/
```

Get folder by path:
```
GET /graph/api/me/drive/contents/?path=Documents/Receipts
```

Get folder by ID:
```
GET /graph/api/me/drive/contents/?item_id=01ABCDEF123456
```

Get folder from specific drive:
```
GET /graph/api/me/drive/contents/?path=Invoices&drive_id=b!xyz123
```

**Response:**
```json
{
  "value": [
    {
      "id": "01ABCDEF123456",
      "name": "receipt-001.pdf",
      "size": 245678,
      "createdDateTime": "2024-01-15T10:30:00Z",
      "lastModifiedDateTime": "2024-01-15T10:30:00Z",
      "file": {
        "mimeType": "application/pdf"
      },
      "webUrl": "https://onedrive.live.com/..."
    },
    {
      "id": "01FEDCBA654321",
      "name": "2024",
      "folder": {
        "childCount": 12
      },
      "createdDateTime": "2024-01-01T00:00:00Z",
      "lastModifiedDateTime": "2024-01-20T15:45:00Z"
    }
  ]
}
```

### 4. Search OneDrive

**GET** `/graph/api/me/drive/search/`

Search for files and folders in a **single drive** (OneDrive or SharePoint).

**Query Parameters:**
- `q` (required) - Search query (matches file names, folder names, and content)
- `drive_id` (optional) - Specific drive ID to search
- `top` (optional) - Maximum results (default: 50)

**Examples:**

Search for receipts:
```
GET /graph/api/me/drive/search/?q=receipt
```

Search with result limit:
```
GET /graph/api/me/drive/search/?q=invoice&top=10
```

Search in specific drive:
```
GET /graph/api/me/drive/search/?q=budget&drive_id=b!xyz123
```

**Response:**
```json
{
  "value": [
    {
      "id": "01ABCDEF123456",
      "name": "receipt-2024-01-15.pdf",
      "size": 245678,
      "webUrl": "https://onedrive.live.com/...",
      "parentReference": {
        "path": "/drive/root:/Documents/Receipts"
      }
    }
  ]
}
```

### 5. Search ALL Drives (OneDrive + SharePoint)

**GET** `/graph/api/me/drive/search-all/`

Search for files and folders across **ALL drives** the user has access to (personal OneDrive + all SharePoint sites).

**Query Parameters:**
- `q` (required) - Search query (matches file names, folder names, and content)
- `top` (optional) - Maximum results **per drive** (default: 50)

**Examples:**

Search all drives for receipts:
```
GET /graph/api/me/drive/search-all/?q=receipt
```

Limit results per drive:
```
GET /graph/api/me/drive/search-all/?q=invoice&top=20
```

**Response:**
```json
{
  "value": [
    {
      "id": "01ABCDEF123456",
      "name": "receipt-2024-01-15.pdf",
      "size": 245678,
      "webUrl": "https://onedrive.live.com/...",
      "parentReference": {
        "path": "/drive/root:/Documents/Receipts"
      },
      "_driveInfo": {
        "id": "personal-drive-id",
        "name": "OneDrive",
        "type": "personal"
      }
    },
    {
      "id": "01FEDCBA654321",
      "name": "receipt-vendor-abc.pdf",
      "size": 123456,
      "webUrl": "https://sharepoint.com/...",
      "parentReference": {
        "path": "/drive/root:/Shared Documents/Finance"
      },
      "_driveInfo": {
        "id": "b!xyz789",
        "name": "Finance Team Site",
        "type": "documentLibrary"
      }
    }
  ],
  "totalDrivesSearched": 3,
  "totalResults": 2
}
```

**Note:** This endpoint may be slower than single-drive search as it queries multiple drives. Each result includes `_driveInfo` metadata showing which drive (OneDrive or SharePoint) the file came from.

### 6. Search ALL Drives + SharePoint (Comprehensive)

**GET** `/graph/api/drives/search-all/`

**⭐ RECOMMENDED FOR SHAREPOINT:** Search across ALL accessible drives including SharePoint team sites.

This is the most comprehensive search that includes:
- Personal OneDrive for Business
- All SharePoint team site document libraries
- Shared drives

**Query Parameters:**
- `q` (required) - Search query (matches file names, folder names, and content)
- `top` (optional) - Maximum results **per drive** (default: 50)

**Example:**

```
GET /graph/api/drives/search-all/?q=receipt
```

**Response includes SharePoint site info:**
```json
{
  "value": [
    {
      "id": "01ABCDEF...",
      "name": "receipt-2024-11-10.pdf",
      "_driveInfo": {
        "id": "b!xyz789...",
        "name": "Documents",
        "type": "documentLibrary",
        "source": "sharepoint",
        "siteName": "Finance Team Site"
      }
    }
  ],
  "totalDrivesSearched": 8,
  "totalResults": 15
}
```

### 7. List SharePoint Sites

**GET** `/graph/api/sharepoint/sites/`

List all SharePoint sites you have access to.

**Query Parameters:**
- `search` (optional) - Filter sites by name

**Example:**

```
GET /graph/api/sharepoint/sites/?search=Finance
```

**Response:**
```json
{
  "value": [
    {
      "id": "contoso.sharepoint.com,abc123...",
      "displayName": "Finance Team Site",
      "name": "finance",
      "webUrl": "https://contoso.sharepoint.com/sites/finance"
    }
  ]
}
```

## Authentication Flow

1. User must first authenticate via OAuth:
   - Navigate to `/graph/login/`
   - Complete Microsoft login flow
   - Consent to permissions (if first time)

2. After authentication, session token is stored and used automatically for API calls

3. If not authenticated, API returns:
   ```json
   {
     "error": "Not authenticated with Microsoft",
     "login_url": "/graph/login/"
   }
   ```

## Common Use Cases

### Automation: Search All Locations for Receipt Files

```python
import requests

# Search across personal OneDrive AND SharePoint for receipt files
response = requests.get(
    'http://localhost:8000/graph/api/me/drive/search-all/',
    params={'q': 'receipt .pdf', 'top': 100},
    cookies=session_cookies
)

results = response.json()
print(f"Found {results['totalResults']} files across {results['totalDrivesSearched']} drives")

for item in results['value']:
    drive_info = item['_driveInfo']
    print(f"{item['name']} - in {drive_info['name']} ({drive_info['type']})")
```

### Automation: Upload Receipt to QuickBooks

```python
import requests

# Step 1: Search all drives for a specific receipt
search_response = requests.get(
    'http://localhost:8000/graph/api/me/drive/search-all/',
    params={'q': 'receipt-2024-11-10.pdf'},
    cookies=session_cookies
)
receipt = search_response.json()['value'][0]

# Step 2: Upload receipt to QuickBooks
# (You would download the file first using receipt['@microsoft.graph.downloadUrl'])
upload_response = requests.post(
    'http://localhost:8000/quickbooks/api/upload-receipt/',
    files={'file': open('receipt.pdf', 'rb')},
    cookies=session_cookies
)
```

### List All Files in Receipts Folder

```python
response = requests.get(
    'http://localhost:8000/graph/api/me/drive/contents/',
    params={'path': 'Documents/Receipts'},
    cookies=session_cookies
)

files = [item for item in response.json()['value'] if 'file' in item]
for file in files:
    print(f"{file['name']}: {file['size']} bytes")
```

### Find All PDFs Modified This Month

```python
# First search for PDFs
response = requests.get(
    'http://localhost:8000/graph/api/me/drive/search/',
    params={'q': '.pdf', 'top': 100},
    cookies=session_cookies
)

# Filter by date in your code
from datetime import datetime, timedelta
current_month = datetime.now().replace(day=1)

recent_pdfs = [
    item for item in response.json()['value']
    if datetime.fromisoformat(item['lastModifiedDateTime'].replace('Z', '+00:00')) >= current_month
]
```

## Error Handling

### Common Errors

**401 Unauthorized**
- User not authenticated with Microsoft
- Solution: Direct user to `/graph/login/`

**400 Bad Request**
- Missing required parameter (e.g., `q` for search)
- Check error message for specific parameter

**403 Forbidden**
- Insufficient permissions
- Solution: Add required scopes to Azure AD app and have user re-consent

**404 Not Found**
- Folder path or item_id doesn't exist
- Check path syntax and verify folder exists

**500 Internal Server Error**
- Microsoft Graph API error
- Check error message for Graph API details

## Troubleshooting Search Issues

### Problem: Search Returns Unrelated Files

Microsoft Graph search matches multiple fields (filename, content, metadata), which can return unexpected results.

**Solutions:**

1. **Use more specific search terms:**
   ```
   # Instead of just "receipts"
   GET /graph/api/me/drive/search/?q=receipt.pdf
   
   # Or combine terms
   GET /graph/api/me/drive/search/?q=receipt 2024
   ```

2. **Search by file extension:**
   ```
   GET /graph/api/me/drive/search/?q=.pdf receipt
   ```

3. **Use exact filename (with extension):**
   ```
   GET /graph/api/me/drive/search/?q=invoice-12345.pdf
   ```

4. **Filter results in your code:**
   ```python
   results = response.json()['value']
   pdf_only = [f for f in results if f['name'].endswith('.pdf')]
   receipts_only = [f for f in pdf_only if 'receipt' in f['name'].lower()]
   ```

### Problem: Search Finds 0 Results for Known File

**Possible causes and solutions:**

1. **File is in a different drive (SharePoint vs OneDrive)**
   
   **Solution:** Use search-all to search everywhere:
   ```bash
   GET /graph/api/me/drive/search-all/?q=your-filename.pdf
   ```

2. **Search index hasn't updated yet**
   
   **Solution:** Recently uploaded files may not be indexed. Try browsing by folder instead:
   ```bash
   # List folder contents directly
   GET /graph/api/me/drive/contents/?path=Documents/Receipts
   ```

3. **File name has special characters**
   
   **Solution:** Search for partial filename without special characters:
   ```bash
   # Instead of searching for "Receipt-2024-11-10.pdf"
   GET /graph/api/me/drive/search/?q=Receipt 2024 11
   ```

### How to Find Drive IDs

**⚠️ IMPORTANT:** The `/graph/api/me/drives/` endpoint only shows drives you OWN (your personal OneDrive). To see SharePoint team sites, use `/graph/api/drives/all/` instead.

**Method 1: List ALL drives including SharePoint (RECOMMENDED)**

```bash
GET /graph/api/drives/all/

# Response shows ALL accessible drives:
{
  "value": [
    {
      "id": "b!abc123xyz...",
      "name": "OneDrive",
      "driveType": "business",
      "_source": "personal"
    },
    {
      "id": "b!def456uvw...",
      "name": "Documents",
      "driveType": "documentLibrary",
      "_source": "sharepoint",
      "_siteName": "Finance Team Site"
    }
  ],
  "totalDrives": 5
}
```

**Method 2: List SharePoint sites first, then get their drives**

```bash
# Step 1: Get SharePoint sites
GET /graph/api/sharepoint/sites/

# Step 2: For each site, get its drives
# (Not needed if using Method 1)
```

**Method 3: Find drive ID from search results**

```bash
GET /graph/api/me/drive/search-all/?q=some-file-you-know-exists

# Each result includes drive info:
{
  "value": [
    {
      "name": "found-file.pdf",
      "_driveInfo": {
        "id": "b!abc123xyz...",  # Copy this ID
        "name": "Finance Team Site",
        "type": "documentLibrary"
      }
    }
  ]
}
```

**Method 3: Get drive ID from SharePoint URL**

If you have the SharePoint site URL, you can find it in the browser:
1. Open SharePoint site in browser
2. Navigate to the document library
3. Look at URL - the drive ID is embedded in complex SharePoint URLs
4. **Easier:** Just use Method 1 or 2 above

### How to Find Correct Folder Paths

**Method 1: Browse from root**

```python
import requests

# Start at root
response = requests.get(
    'http://localhost:8000/graph/api/me/drive/contents/',
    cookies=session_cookies
)

# Print all folders at root level
for item in response.json()['value']:
    if 'folder' in item:
        print(f"Folder: {item['name']}")
        
# Then browse into a specific folder
response = requests.get(
    'http://localhost:8000/graph/api/me/drive/contents/',
    params={'path': 'Documents'},  # Folder name from above
    cookies=session_cookies
)
```

**Method 2: Use search to find the folder**

```bash
# Search for folder by name
GET /graph/api/me/drive/search-all/?q=Receipts folder

# Look at parentReference.path in results to see full path
{
  "value": [
    {
      "name": "Receipts",
      "folder": { "childCount": 25 },
      "parentReference": {
        "path": "/drive/root:/Documents/Finance"  # Full path!
      }
    }
  ]
}

# Now you know the path is: Documents/Finance/Receipts
```

**Method 3: Check file's parent path**

```bash
# Find any file you know is in the folder
GET /graph/api/me/drive/search-all/?q=some-file-in-that-folder.pdf

# Check its parentReference
{
  "name": "some-file.pdf",
  "parentReference": {
    "path": "/drive/root:/Documents/Finance/Receipts",
    "id": "01ABCDEF..."  # You can also use this parent ID
  }
}
```

### Debugging Step-by-Step

**Step 1: Verify you have access to ALL drives (including SharePoint)**
```bash
GET /graph/api/drives/all/
# Should return personal OneDrive + SharePoint sites
# If you only see 1-2 drives, you may be missing Sites.Read.All permission
```

**Step 2: List SharePoint sites separately**
```bash
GET /graph/api/sharepoint/sites/
# Should show all SharePoint team sites you have access to
# If empty, check Sites.Read.All permission
```

**Step 3: Check what's in your default drive root**
```bash
GET /graph/api/me/drive/contents/
# Lists all folders/files at the root
```

**Step 4: Try comprehensive search across everything**
```bash
GET /graph/api/drives/search-all/?q=pdf&top=10
# Should return PDFs from OneDrive AND SharePoint
# Check _driveInfo.source and _driveInfo.siteName in results
```

**Step 5: Check specific SharePoint drive**
```bash
# Use a drive_id from Step 1 where _source = "sharepoint"
GET /graph/api/me/drive/search/?q=pdf&drive_id=b!abc123...
```

### Common Path Issues

❌ **Wrong:** `/Documents/Receipts` (leading slash)
✅ **Correct:** `Documents/Receipts`

❌ **Wrong:** `Documents/Receipts/` (trailing slash)
✅ **Correct:** `Documents/Receipts`

❌ **Wrong:** `\Documents\Receipts` (backslashes)
✅ **Correct:** `Documents/Receipts`

❌ **Wrong:** `My Documents/Receipts` (space might work but try without)
✅ **Better:** Search for the folder first to get exact path

### Testing with Python Script

```python
import requests

# Your session cookies after logging in via browser
cookies = {'sessionid': 'your-session-id'}

# 1. List ALL drives including SharePoint (RECOMMENDED)
print("=== All Accessible Drives (OneDrive + SharePoint) ===")
r = requests.get('http://localhost:8000/graph/api/drives/all/', cookies=cookies)
all_drives = r.json()
print(f"Total drives: {all_drives['totalDrives']}")
for drive in all_drives['value']:
    source = drive.get('_source', 'unknown')
    site = drive.get('_siteName', '')
    site_info = f" (Site: {site})" if site else ""
    print(f"  [{source}] {drive['name']} ({drive['driveType']}): {drive['id']}{site_info}")

# 2. List SharePoint sites
print("\n=== SharePoint Sites ===")
r = requests.get('http://localhost:8000/graph/api/sharepoint/sites/', cookies=cookies)
sites = r.json().get('value', [])
print(f"Found {len(sites)} SharePoint sites")
for site in sites[:5]:
    print(f"  {site.get('displayName', site.get('name'))}: {site['id']}")

# 3. Search everywhere including SharePoint
print("\n=== Search All Drives + SharePoint ===")
r = requests.get(
    'http://localhost:8000/graph/api/drives/search-all/',
    params={'q': 'receipt', 'top': 5},
    cookies=cookies
)
results = r.json()
print(f"Found {results['totalResults']} files across {results['totalDrivesSearched']} drives")
for item in results['value'][:5]:
    drive = item['_driveInfo']
    source = drive.get('source', 'unknown')
    site = drive.get('siteName', '')
    path = item.get('parentReference', {}).get('path', 'unknown')
    site_info = f" [{site}]" if site else ""
    print(f"  {item['name']}{site_info} - Source: {source}, Drive: {drive['name']}, Path: {path}")

# 4. List root folder contents (personal OneDrive)
print("\n=== Personal OneDrive Root Folder ===")
r = requests.get('http://localhost:8000/graph/api/me/drive/contents/', cookies=cookies)
items = r.json()['value']
for item in items[:10]:
    item_type = 'folder' if 'folder' in item else 'file'
    print(f"  [{item_type}] {item['name']}")
```

## Permissions Consent

When users first authenticate, they'll see a consent screen requesting:

- **View your basic profile** (User.Read)
- **Read your files** (Files.Read, Files.Read.All)
- **Read items in all site collections** (Sites.Read.All) - **Required for SharePoint**
- **Read your mail** (Mail.Read)
- **Read your calendars** (Calendars.Read)
- **Read your teams messages** (ChannelMessage.Read.All)

Users must click "Accept" to grant these permissions.

**⚠️ IMPORTANT:** If you added `Sites.Read.All` permission after users already logged in, they need to:
1. Log out: Visit `/graph/logout/`
2. Log back in: Visit `/graph/login/`
3. Accept the new permission request

## Testing

### Using the API Documentation UI

Navigate to `/api/schema/swagger-ui/` to see interactive API documentation and test endpoints.

### Using curl

```bash
# First authenticate via browser at http://localhost:8000/graph/login/
# Then extract session cookie and use it:

curl -X GET "http://localhost:8000/graph/api/me/drive/" \
  -H "Cookie: sessionid=your-session-id"

curl -X GET "http://localhost:8000/graph/api/me/drive/search/?q=receipt&top=10" \
  -H "Cookie: sessionid=your-session-id"
```

## Rate Limits

Microsoft Graph API has rate limits. The service will return 429 (Too Many Requests) if limits are exceeded.

Best practices:
- Cache results when possible
- Use specific searches instead of broad queries
- Implement exponential backoff for retries

## Next Steps

1. **Update Azure AD App Registration**: Add Files.Read and Files.Read.All permissions
2. **User Re-consent**: Users must log out and log back in to consent to new permissions
3. **Test Endpoints**: Use Swagger UI or curl to verify functionality
4. **Build Automation**: Integrate with QuickBooks receipt upload workflow
