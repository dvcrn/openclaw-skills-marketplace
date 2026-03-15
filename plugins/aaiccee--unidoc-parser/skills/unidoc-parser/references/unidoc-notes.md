# UniDoc API Notes

## API Endpoints

### Environment
- **Base URL**: `http://unidoc.uat.hivoice.cn`
- **Environment**: UAT (User Acceptance Testing)
- **Note**: This is a testing environment. Production endpoints may differ.

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/syncUploadFile` | POST | Synchronous file upload and conversion |
| `/asyncUploadFile` | POST | Asynchronous file upload (returns file ID) |
| `/exportFile` | GET | Download converted file |
| `/getFileStatus` | GET | Check async task status |

## Request Parameters

### Upload (Sync/Async)

**Form Data:**
- `uid` (string): Unique user identifier
- `func` (string): Conversion method (default: "unisound")
- `file` (file): The document file to convert

**Example:**
```python
body = {"uid": "user123", "func": "unisound"}
files = {'file': open('document.pdf', 'rb')}
response = requests.post(url, data=body, files=files)
```

### Export File

**Query Parameters:**
- `fileId` (string): File identifier from upload response
- `targetType` (string): Output format ("md" or "json")

**Example:**
```python
params = {"fileId": "abc123", "targetType": "md"}
response = requests.get(url, params=params)
```

### Check Status

**Query Parameters:**
- `fileId` (string): File identifier

**Response:**
```json
{
  "result": {
    "status": "SUCCESS" | "FAILED" | "PROCESSING"
  }
}
```

## Response Format

### Success Response
```json
{
  "result": "file-id-string"  // async mode
  // or
  {
    "fileId": "file-id-string"  // sync mode
  }
}
```

### Error Response
```json
{
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

## Status Polling Behavior

### Async Mode Polling
- Default polling interval: 1 second
- Maximum attempts: 300 (5 minutes timeout)
- Status values:
  - `PROCESSING`: Conversion in progress
  - `SUCCESS`: Conversion completed successfully
  - `FAILED`: Conversion failed

### Polling Strategy
```python
task_status = None
while task_status not in ["SUCCESS", "FAILED"]:
    # Check status
    # Wait 1 second
    # Continue
```

## Common Error Codes

| Error | Description | Solution |
|-------|-------------|----------|
| Network Error | Cannot reach API server | Check internet connection |
| Timeout | Request timed out | Retry or use async mode |
| Invalid File | Unsupported file format | Check file format |
| File Too Large | Exceeds size limit | Compress or split file |
| Rate Limit | Too many requests | Wait and retry |

## Supported File Formats

Based on the original `api_test_demo.py`:

- **Documents**: PDF, DOC, DOCX
- **Images**: PNG, JPG, JPEG
- **Other formats**: Check API documentation for full list

## Output Formats

### Markdown (`.md`)
- Plain text with markdown formatting
- Preserves document structure
- Suitable for further processing

### JSON (`.json`)
- Structured data format
- Includes metadata
- Easier programmatic parsing

## Network Requirements

### Connectivity
- Requires active internet connection
- API server: `unidoc.uat.hivoice.cn`
- Port: 80 (HTTP) or 443 (HTTPS)

### Firewall Considerations
If behind a firewall, ensure:
- Outbound connections to API domain are allowed
- No proxy configuration issues
- SSL/TLS certificates are valid (if using HTTPS)

## Performance Considerations

### Synchronous Mode
- **Pros**: Simpler, immediate result
- **Cons**: Blocks until complete, may timeout on large files
- **Use when**: Small files, quick results needed

### Asynchronous Mode
- **Pros**: Handles large files, non-blocking
- **Cons**: Requires polling, more complex
- **Use when**: Large files, batch processing

## Troubleshooting

### Connection Errors
```python
# Test connectivity
import requests
try:
    response = requests.get("http://unidoc.uat.hivoice.cn")
    print(f"Status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("Cannot connect to API server")
```

### File Not Found
```python
# Verify file exists before upload
import os
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")
```

### Invalid Response
```python
# Check API response structure
res = response.json()
if "result" not in res:
    print(f"API Error: {res.get('message', 'Unknown error')}")
```

## Best Practices

1. **Error Handling**: Always wrap API calls in try-except blocks
2. **File Validation**: Check file exists and is readable before upload
3. **Timeout Management**: Set appropriate timeouts for requests
4. **Output Directory**: Create output directories before writing
5. **Resource Cleanup**: Close file handles properly

## Example Usage

```python
from scripts.unidoc_parse import parse_document

# Parse a document
output_path = parse_document(
    file_path="document.pdf",
    output_dir="./output",
    format_type="md",
    mode="sync"
)
print(f"Output: {output_path}")
```

## Migration from api_test_demo.py

### Key Changes
1. Added command-line argument parsing
2. Organized output into per-document directories
3. Enhanced error handling and validation
4. Added class-based parser structure
5. Improved async polling with timeout protection

### Compatibility
The core API logic remains compatible with `api_test_demo.py`:
- Same endpoints
- Same request/response format
- Same conversion behavior
