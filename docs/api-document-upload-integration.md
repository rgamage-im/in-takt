# Document Upload API Integration Guide

## Overview
New endpoint for uploading documents (PDF, DOCX, XLSX, TXT) with automatic parsing, table extraction, chunking, and indexing.

## Endpoint

**POST** `/api/v1/ingest/document/upload`

- **Content-Type**: `multipart/form-data`
- **Authentication**: Required via `X-API-Key` header

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | Document file (PDF, DOCX, XLSX, TXT) |
| `metadata` | JSON string | Yes | Document metadata (see structure below) |
| `acl` | JSON string | No | Access control list |

### Metadata JSON Structure
```json
{
  "source": "string",
  "source_type": "string",
  "file_path": "string (optional)",
  "file_name": "string (optional)",
  "file_type": "string (optional)",
  "author": "string (optional)",
  "title": "string (optional)",
  "created_at": "ISO datetime (optional)",
  "modified_at": "ISO datetime (optional)"
}
```

**Required fields**: `source`, `source_type`

**Source Type Values**: `sharepoint`, `onedrive`, `teams`, `local`, etc.

### ACL JSON Structure (Optional)
```json
{
  "allowed_users": ["user1@domain.com", "user2@domain.com"],
  "allowed_groups": ["group1", "group2"]
}
```

## Response

**Success (201 Created)**
```json
{
  "document_id": "uuid",
  "chunks_indexed": 7,
  "status": "success"
}
```

**Error (400/500)**
```json
{
  "detail": "Error description"
}
```

## Supported File Formats

| Format | Extension | Special Handling |
|--------|-----------|------------------|
| Text | `.txt` | Plain text |
| PDF | `.pdf` | Text + table extraction |
| Word | `.docx` | Text + table extraction |
| Excel | `.xlsx`, `.xls` | Multiple sheets, tables preserved with column context |

**Table Handling**: Tables are converted to markdown format and semantic row representations for optimal search results.

## Example Usage

### JavaScript (Fetch API)
```javascript
const uploadDocument = async (file, metadata) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('metadata', JSON.stringify({
    source: 'sharepoint',
    source_type: 'sharepoint',
    title: file.name,
    author: 'current.user@domain.com'
  }));

  const response = await fetch('https://rag-api.politesea-1108f270.westus2.azurecontainerapps.io/api/v1/ingest/document/upload', {
    method: 'POST',
    headers: {
      'X-API-Key': 'your-api-key'
    },
    body: formData
  });

  return response.json();
};
```

### C# (.NET)
```csharp
using var client = new HttpClient();
client.DefaultRequestHeaders.Add("X-API-Key", "your-api-key");

using var content = new MultipartFormDataContent();
using var fileStream = File.OpenRead(filePath);
content.Add(new StreamContent(fileStream), "file", Path.GetFileName(filePath));
content.Add(new StringContent(JsonSerializer.Serialize(new {
    source = "sharepoint",
    source_type = "sharepoint",
    title = Path.GetFileName(filePath)
})), "metadata");

var response = await client.PostAsync(
    "https://rag-api.politesea-1108f270.westus2.azurecontainerapps.io/api/v1/ingest/document/upload",
    content
);
```

### Python
```python
import requests

def upload_document(file_path, api_key):
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {
            'metadata': json.dumps({
                'source': 'sharepoint',
                'source_type': 'sharepoint',
                'title': os.path.basename(file_path)
            })
        }
        headers = {'X-API-Key': api_key}
        
        response = requests.post(
            'https://rag-api.politesea-1108f270.westus2.azurecontainerapps.io/api/v1/ingest/document/upload',
            files=files,
            data=data,
            headers=headers
        )
        return response.json()
```

## Implementation Notes

1. **File Size**: No explicit limit documented; recommend implementing client-side validation (e.g., 50MB max)

2. **Async Processing**: Upload is synchronous but includes parsing/chunking/indexing, expect ~5-15 seconds for typical documents

3. **Progress Indication**: Recommend showing loading indicator during upload

4. **Error Handling**: Handle 400 (validation errors), 401 (auth), 500 (server errors)

5. **Metadata Best Practices**:
   - Include `title` for better user experience in search results
   - Use consistent `source_type` values across your app
   - Populate `author` for audit trails

6. **ACL Integration**: If implementing access control, ensure ACL data matches your authentication system

## Migration from Text-Only Endpoint

**Old Endpoint**: `POST /api/v1/ingest/document` (still available)
- Accepts JSON with `content` field as plain text string
- Use for programmatically generated content

**New Endpoint**: `POST /api/v1/ingest/document/upload`
- Accepts file uploads with automatic parsing
- Recommended for user-uploaded documents

## Search Integration

Documents indexed via upload are searchable using existing search endpoints:

**GET** `/api/v1/retrieve/search?q={query}&top_k=10`

Search results include metadata for identifying source documents by `document_id`.

## Questions?

Contact: [Your contact information]
