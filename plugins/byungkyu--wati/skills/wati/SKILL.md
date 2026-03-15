---
name: wati
description: "WATI (WhatsApp Team Inbox) API integration with managed authentication. Send WhatsApp messages, manage contacts, and handle templates.\n Use this skill when users want to send WhatsApp messages, manage WhatsApp contacts, or work with message templates via WATI.\n For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway)."
---

# WATI

Access the WATI (WhatsApp Team Inbox) API with managed authentication. Send WhatsApp messages, manage contacts, and work with message templates.

## Quick Start

```bash
# Get contacts list
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/wati/api/v1/getContacts?pageSize=10&pageNumber=1')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/wati/{native-api-path}
```

Replace `{native-api-path}` with the actual WATI API endpoint path. The gateway proxies requests to your WATI instance and automatically injects your API token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your WATI connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=wati&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'wati'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "wati",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple WATI connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/wati/api/v1/getContacts?pageSize=10&pageNumber=1')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Contacts

#### Get Contacts

```bash
GET /wati/api/v1/getContacts?pageSize=10&pageNumber=1
```

**Query Parameters:**
- `pageSize` - Number of results per page
- `pageNumber` - Page number (1-indexed)
- `name` (optional) - Filter by contact name
- `attribute` (optional) - Filter by attribute (format: `[{"name": "name", "operator": "contain", "value": "test"}]`)
- `createdDate` (optional) - Filter by created date (YYYY-MM-DD)

**Attribute operators:** `contain`, `notContain`, `exist`, `notExist`, `==`, `!=`, `valid`, `invalid`

#### Add Contact

```bash
POST /wati/api/v1/addContact/{whatsappNumber}
Content-Type: application/json

{
  "name": "John Doe",
  "customParams": [
    {
      "name": "member",
      "value": "VIP"
    }
  ]
}
```

#### Update Contact Attributes

```bash
POST /wati/api/v1/updateContactAttributes/{whatsappNumber}
Content-Type: application/json

{
  "customParams": [
    {
      "name": "member",
      "value": "VIP"
    }
  ]
}
```

### Messages

#### Get Messages

```bash
GET /wati/api/v1/getMessages/{whatsappNumber}?pageSize=10&pageNumber=1
```

**Query Parameters:**
- `pageSize` - Number of results per page
- `pageNumber` - Page number (1-indexed)

#### Send Session Message

Send a text message within an active session (24-hour window):

```bash
POST /wati/api/v1/sendSessionMessage/{whatsappNumber}
Content-Type: application/x-www-form-urlencoded

messageText=Hello%20from%20WATI!
```

#### Send Session File

Send a file within an active session:

```bash
POST /wati/api/v1/sendSessionFile/{whatsappNumber}?caption=Check%20this%20out
Content-Type: multipart/form-data

file=@document.pdf
```

### Message Templates

#### Get Message Templates

```bash
GET /wati/api/v1/getMessageTemplates?pageSize=10&pageNumber=1
```

#### Send Template Message

Send a pre-approved template message to a single contact:

```bash
POST /wati/api/v1/sendTemplateMessage?whatsappNumber={whatsappNumber}
Content-Type: application/json

{
  "template_name": "order_update",
  "broadcast_name": "order_update",
  "parameters": [
    {
      "name": "name",
      "value": "John"
    },
    {
      "name": "ordernumber",
      "value": "12345"
    }
  ]
}
```

#### Send Template Messages (Bulk)

Send template messages to multiple contacts:

```bash
POST /wati/api/v1/sendTemplateMessages
Content-Type: application/json

{
  "template_name": "order_update",
  "broadcast_name": "order_update",
  "receivers": [
    {
      "whatsappNumber": "14155551234",
      "customParams": [
        {
          "name": "name",
          "value": "John"
        },
        {
          "name": "ordernumber",
          "value": "12345"
        }
      ]
    },
    {
      "whatsappNumber": "14155555678",
      "customParams": [
        {
          "name": "name",
          "value": "Jane"
        },
        {
          "name": "ordernumber",
          "value": "67890"
        }
      ]
    }
  ]
}
```

#### Send Template Message via CSV

```bash
POST /wati/api/v1/sendTemplateMessageCSV?template_name=order_update&broadcast_name=order_update
Content-Type: multipart/form-data

whatsapp_numbers_csv=@contacts.csv
```

### Message Templates (v2 API)

The v2 API provides enhanced response format with message tracking IDs.

#### Send Template Message (v2)

```bash
POST /wati/api/v2/sendTemplateMessage?whatsappNumber={whatsappNumber}
Content-Type: application/json

{
  "template_name": "order_update",
  "broadcast_name": "order_update",
  "parameters": [
    {
      "name": "name",
      "value": "John"
    }
  ]
}
```

**Response:**
```json
{
  "result": true,
  "error": null,
  "templateName": "order_update",
  "receivers": [
    {
      "localMessageId": "38aca0c0-f80a-409c-81ed-607fa5206529",
      "waId": "14155551234",
      "isValidWhatsAppNumber": true,
      "errors": []
    }
  ],
  "parameters": [
    {"name": "name", "value": "John"}
  ]
}
```

#### Send Template Messages (v2 - Bulk)

```bash
POST /wati/api/v2/sendTemplateMessages
Content-Type: application/json

{
  "template_name": "order_update",
  "broadcast_name": "order_update",
  "receivers": [
    {
      "whatsappNumber": "14155551234",
      "customParams": [
        {"name": "name", "value": "John"}
      ]
    },
    {
      "whatsappNumber": "14155555678",
      "customParams": [
        {"name": "name", "value": "Jane"}
      ]
    }
  ]
}
```

**Response:**
```json
{
  "result": true,
  "error": null,
  "templateName": "order_update",
  "receivers": [
    {
      "localMessageId": "c486f386-d86d-431d-aa3b-fb1b6c494e58",
      "waId": "14155551234",
      "isValidWhatsAppNumber": true,
      "errors": []
    },
    {
      "localMessageId": "d597f497-e97e-542e-bb4c-718gb6d5a069",
      "waId": "14155555678",
      "isValidWhatsAppNumber": true,
      "errors": []
    }
  ]
}
```

### Interactive Messages

#### Send Interactive Buttons Message

```bash
POST /wati/api/v1/sendInteractiveButtonsMessage?whatsappNumber={whatsappNumber}
Content-Type: application/json

{
  "header": {
    "type": "text",
    "text": "Order Status"
  },
  "body": "Your order #12345 is ready. What would you like to do?",
  "footer": "Reply within 24 hours",
  "buttons": [
    {
      "text": "Track Order"
    },
    {
      "text": "Contact Support"
    }
  ]
}
```

#### Send Interactive List Message

```bash
POST /wati/api/v1/sendInteractiveListMessage?whatsappNumber={whatsappNumber}
Content-Type: application/json

{
  "header": "Choose an option",
  "body": "Please select from the menu below",
  "footer": "Powered by WATI",
  "buttonText": "View Options",
  "sections": [
    {
      "title": "Products",
      "rows": [
        {
          "title": "Product A",
          "description": "Best seller item"
        },
        {
          "title": "Product B",
          "description": "New arrival"
        }
      ]
    }
  ]
}
```

### Operators

#### Assign Operator

```bash
POST /wati/api/v1/assignOperator?email=agent@example.com&whatsappNumber={whatsappNumber}
```

### Media

#### Get Media

```bash
GET /wati/api/v1/getMedia?fileName={fileName}
```

## Pagination

WATI uses page-based pagination:

```bash
GET /wati/api/v1/getContacts?pageSize=50&pageNumber=1
```

**Parameters:**
- `pageSize` - Results per page
- `pageNumber` - Page number (1-indexed)

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/wati/api/v1/getContacts?pageSize=10&pageNumber=1',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/wati/api/v1/getContacts',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'pageSize': 10, 'pageNumber': 1}
)
data = response.json()
```

### Send Template Message

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/wati/api/v1/sendTemplateMessage',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    params={'whatsappNumber': '14155551234'},
    json={
        'template_name': 'order_update',
        'broadcast_name': 'order_update',
        'parameters': [
            {'name': 'name', 'value': 'John'},
            {'name': 'ordernumber', 'value': '12345'}
        ]
    }
)
```

## Notes

- WhatsApp numbers should include country code without + or spaces (e.g., `14155551234`)
- Session messages can only be sent within 24 hours of the last customer message
- Template messages require pre-approved templates from WhatsApp
- Interactive messages (buttons/lists) have specific character limits set by WhatsApp
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing WATI connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from WATI API |

## Resources

- [WATI API Documentation](https://docs.wati.io/reference/introduction)
- [WATI Help Center](https://docs.wati.io/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
