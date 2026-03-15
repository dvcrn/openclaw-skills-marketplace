---
name: docuseal
description: "Manage DocuSeal document templates and e-signatures."
---

# DocuSeal App Skill

Manage document templates and e-signatures via the DocuSeal MCP endpoint.

## Setup

1. Enable MCP in DocuSeal settings (Settings > MCP)
2. Create an MCP token
3. Set environment variables:
   ```bash
   export DOCUSEAL_URL="https://your-docuseal-instance.com"
   export DOCUSEAL_MCP_TOKEN="your-mcp-token"
   ```

## Protocol

All requests use JSON-RPC 2.0 over HTTP POST to `$DOCUSEAL_URL/mcp`.

## Usage with scripts/cli.js

Requires Node.js 18+. No dependencies.

```bash
node scripts/cli.js init
node scripts/cli.js tools
node scripts/cli.js search-templates --q="contract" --limit=5
node scripts/cli.js create-template --url="https://example.com/document.pdf" --name="My Template"
node scripts/cli.js send-documents --template-id=1 --emails="signer@example.com,another@example.com"
node scripts/cli.js search-documents --q="john@example.com" --limit=5
```

## Commands Reference

### search-templates

Search document templates by name.

| Option | Type | Required | Description |
|---|---|---|---|
| `--q` | string | yes | Search query to filter templates by name |
| `--limit` | integer | no | The number of templates to return (default 10) |

### create-template

Create a template from a PDF URL.

| Option | Type | Required | Description |
|---|---|---|---|
| `--url` | string | yes | URL of the document file to upload |
| `--name` | string | no | Template name (defaults to filename) |

### send-documents

Send a document template for signing to specified submitters.

| Option | Type | Required | Description |
|---|---|---|---|
| `--template-id` | integer | yes | Template identifier |
| `--emails` | string | yes | Comma-separated list of submitter email addresses |

### search-documents

Search signed or pending documents by submitter name, email, phone, or template name.

| Option | Type | Required | Description |
|---|---|---|---|
| `--q` | string | yes | Search by submitter name, email, phone, or template name |
| `--limit` | integer | no | The number of results to return (default 10) |

## Notes

- Requires Node.js 18+ (uses built-in `fetch`, no dependencies)
- All responses follow JSON-RPC 2.0 format
- `DOCUSEAL_URL` and `DOCUSEAL_MCP_TOKEN` environment variables must be set
- MCP must be enabled in account settings before use
- Token is shown only once at creation — store it securely
