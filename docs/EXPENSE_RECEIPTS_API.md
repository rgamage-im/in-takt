# Expense Receipts API

## Overview

This API endpoint provides quick access to all expense receipt files stored in your designated SharePoint folder.

**Endpoint:** `GET /graph/api/receipts/expense/`

## Default Configuration

The API is pre-configured to access:

- **SharePoint Site:** Integral Methods
- **Document Library:** Documents
- **Folder:** Expense Receipts
- **Drive ID:** `b!0F05pe1C2kK-wpKqi5Zc48axM_lpIdFNjnrGDD3PSm5M87XCUZy6TIbJKPIgDtH7`
- **Folder ID:** `01FUFIEDFYM6C7J3SLSBDZCH3NDO7KCVRK`

## Usage

### Basic Usage (Default Folder)

```bash
GET http://localhost:8000/graph/api/receipts/expense/
```

**Response:**
```json
{
  "value": [
    {
      "id": "01ABCDEF123456",
      "name": "receipt-2024-11-10.pdf",
      "size": 245678,
      "createdDateTime": "2024-11-10T10:30:00Z",
      "lastModifiedDateTime": "2024-11-10T10:30:00Z",
      "webUrl": "https://integralmethods.sharepoint.com/sites/IntegralMethods9/Shared%20Documents/...",
      "downloadUrl": "https://integralmethods.sharepoint.com/...",
      "mimeType": "application/pdf",
      "createdBy": "Randy Gamage",
      "lastModifiedBy": "Randy Gamage"
    },
    {
      "id": "01FEDCBA654321",
      "name": "expense-receipt-001.jpg",
      "size": 123456,
      "createdDateTime": "2024-11-09T15:20:00Z",
      "lastModifiedDateTime": "2024-11-09T15:20:00Z",
      "webUrl": "https://integralmethods.sharepoint.com/...",
      "downloadUrl": "https://integralmethods.sharepoint.com/...",
      "mimeType": "image/jpeg",
      "createdBy": "Matthew Thompson",
      "lastModifiedBy": "Matthew Thompson"
    }
  ],
  "totalFiles": 2,
  "folderInfo": {
    "folderId": "01FUFIEDFYM6C7J3SLSBDZCH3NDO7KCVRK",
    "driveId": "b!0F05pe1C2kK-wpKqi5Zc48axM_lpIdFNjnrGDD3PSm5M87XCUZy6TIbJKPIgDtH7",
    "location": "Integral Methods > Documents > Expense Receipts"
  }
}
```

### Custom Folder (Override Defaults)

You can specify a different folder if needed:

```bash
# Use a different folder in the same drive
GET /graph/api/receipts/expense/?folder_id=01XYZNEW123456

# Use a completely different drive and folder
GET /graph/api/receipts/expense/?folder_id=01ABC123&drive_id=b!xyz789...
```

## Response Fields

Each file in the `value` array includes:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique file ID |
| `name` | string | File name with extension |
| `size` | number | File size in bytes |
| `createdDateTime` | string | ISO 8601 timestamp |
| `lastModifiedDateTime` | string | ISO 8601 timestamp |
| `webUrl` | string | Browser URL to view/download |
| `downloadUrl` | string | Direct download URL (temporary, expires) |
| `mimeType` | string | File MIME type (e.g., `application/pdf`) |
| `createdBy` | string | User display name |
| `lastModifiedBy` | string | User display name |

## Features

✅ **Files Only:** Returns only files, filters out subfolders  
✅ **Download URLs:** Includes direct download links for automation  
✅ **Metadata:** Full file metadata including creator, modified date, size  
✅ **Fast:** Direct folder access, no searching required  
✅ **Configurable:** Can override folder/drive IDs if needed  

## Use Cases

### 1. List All Receipts

```python
import requests

cookies = {'sessionid': 'your-session-id'}

response = requests.get(
    'http://localhost:8000/graph/api/receipts/expense/',
    cookies=cookies
)

receipts = response.json()
print(f"Found {receipts['totalFiles']} receipt files")

for file in receipts['value']:
    print(f"{file['name']} - {file['size']} bytes - by {file['createdBy']}")
```

### 2. Download a Specific Receipt

```python
import requests

# Get all receipts
response = requests.get(
    'http://localhost:8000/graph/api/receipts/expense/',
    cookies=cookies
)

# Find specific receipt
receipts = response.json()['value']
target = next(r for r in receipts if 'invoice-12345' in r['name'])

# Download it
file_response = requests.get(target['downloadUrl'])
with open(target['name'], 'wb') as f:
    f.write(file_response.content)
```

### 3. Upload Receipt to QuickBooks

```python
import requests

# Step 1: Get latest receipt
response = requests.get(
    'http://localhost:8000/graph/api/receipts/expense/',
    cookies=cookies
)
receipts = response.json()['value']

# Sort by creation date, get newest
newest = sorted(receipts, key=lambda x: x['createdDateTime'], reverse=True)[0]

# Step 2: Download the file
file_data = requests.get(newest['downloadUrl']).content

# Step 3: Upload to QuickBooks
upload_response = requests.post(
    'http://localhost:8000/quickbooks/api/upload-receipt/',
    files={'file': (newest['name'], file_data, newest['mimeType'])},
    cookies=cookies
)
```

### 4. Filter by Date Range

```python
from datetime import datetime, timedelta

# Get all receipts
response = requests.get(
    'http://localhost:8000/graph/api/receipts/expense/',
    cookies=cookies
)

# Filter to last 7 days
week_ago = datetime.now() - timedelta(days=7)
recent_receipts = [
    r for r in response.json()['value']
    if datetime.fromisoformat(r['createdDateTime'].replace('Z', '+00:00')) > week_ago
]

print(f"Found {len(recent_receipts)} receipts from the last week")
```

### 5. Find PDFs Only

```python
response = requests.get(
    'http://localhost:8000/graph/api/receipts/expense/',
    cookies=cookies
)

pdf_receipts = [
    r for r in response.json()['value']
    if r['mimeType'] == 'application/pdf'
]

print(f"Found {len(pdf_receipts)} PDF receipts")
```

## Authentication

Requires user to be authenticated via Microsoft Graph OAuth:

1. User must log in: `/graph/login/`
2. Session token is used automatically
3. If not authenticated, returns 401 with login URL

## Error Handling

**401 Unauthorized**
```json
{
  "error": "Not authenticated with Microsoft",
  "login_url": "/graph/login/"
}
```

**500 Internal Server Error**
```json
{
  "error": "Failed to get expense receipts: <details>"
}
```

## Performance

- **Fast:** Direct folder access via folder ID (no search/scan)
- **Efficient:** Only returns files, not subfolders
- **Cached:** Microsoft Graph API caches responses

## Changing the Default Folder

If you need to permanently change which folder is accessed, update the default parameters in the service method:

**File:** `msgraph_integration/services_delegated.py`

```python
def get_expense_receipts(
    self,
    access_token: str,
    folder_id: str = "YOUR_NEW_FOLDER_ID",  # Change this
    drive_id: str = "YOUR_NEW_DRIVE_ID"      # And this
) -> Dict[str, Any]:
```

### How to Find Your Folder/Drive IDs

1. **List all accessible drives:**
   ```bash
   GET /graph/api/drives/all/
   ```
   Copy the `id` of your target drive

2. **Browse to find your folder:**
   ```bash
   # Start at root
   GET /graph/api/me/drive/contents/?drive_id=YOUR_DRIVE_ID
   
   # Navigate into folders
   GET /graph/api/me/drive/contents/?path=Documents&drive_id=YOUR_DRIVE_ID
   ```
   
3. **Or search for the folder:**
   ```bash
   GET /graph/api/drives/search-all/?q=Expense%20Receipts
   ```
   Look for the `parentReference.id` in the results

## Integration with QuickBooks

This endpoint pairs perfectly with the QuickBooks receipt upload API:

```python
# Complete automation workflow
def upload_latest_receipt_to_quickbooks():
    # 1. Get latest receipt from SharePoint
    receipts = requests.get(
        'http://localhost:8000/graph/api/receipts/expense/',
        cookies=session_cookies
    ).json()
    
    latest = sorted(
        receipts['value'], 
        key=lambda x: x['createdDateTime'], 
        reverse=True
    )[0]
    
    # 2. Download file
    file_data = requests.get(latest['downloadUrl']).content
    
    # 3. Upload to QuickBooks
    result = requests.post(
        'http://localhost:8000/quickbooks/api/upload-receipt/',
        files={'file': (latest['name'], file_data, latest['mimeType'])},
        data={'Note': f'Expense receipt from {latest["createdBy"]}'},
        cookies=session_cookies
    )
    
    return result.json()
```

## API Documentation

Interactive API documentation available at:
- **Swagger UI:** `/api/schema/swagger-ui/`
- **ReDoc:** `/api/schema/redoc/`

Search for "Expense Receipts" in the documentation.
