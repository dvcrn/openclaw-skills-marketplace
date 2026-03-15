# Prisma SASE Authentication Reference

## OAuth2 Client Credentials Flow

### Prerequisites

Before you can authenticate:

1. **Create a Tenant Service Group (TSG)** — the root TSG must be created through the Prisma SASE UI at `https://app.prismaaccess.com`
2. **Create a Service Account** — generates a `client_id` and `client_secret`. The secret is shown only once and cannot be retrieved later.
3. **Assign Roles** — without roles, even a valid token won't authorize any operations.

### Token Request

```bash
curl -s -X POST "https://auth.apps.paloaltonetworks.com/oauth2/access_token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "${CLIENT_ID}:${CLIENT_SECRET}" \
  -d "grant_type=client_credentials&scope=tsg_id:${TSG_ID}"
```

**Parameters:**

| Parameter | Location | Value |
|-----------|----------|-------|
| Authorization | Header | `Basic base64(client_id:client_secret)` |
| grant_type | Body | `client_credentials` |
| scope | Body | `tsg_id:<your_tsg_id>` |
| Content-Type | Header | `application/x-www-form-urlencoded` |

### Token Response

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "scope": "tsg_id:1234567890",
  "token_type": "Bearer",
  "expires_in": 899
}
```

- **Format:** JWT (can be decoded at jwt.io to verify claims)
- **Lifetime:** 899 seconds (~15 minutes)
- **No refresh token** — request a new token when it expires

### Using the Token

Include in all API requests:
```
Authorization: Bearer <access_token>
```

### Python Token Request

```python
import requests
import base64

def get_sase_token(client_id, client_secret, tsg_id):
    url = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"

    auth_string = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_string}"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": f"tsg_id:{tsg_id}"
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()

    return response.json()["access_token"]
```

## Token Scoping

- A token is scoped to the TSG specified in the `scope` parameter
- The token grants access to that TSG and all its child TSGs
- To access a different part of the tenant hierarchy, request a new token with a different `tsg_id`

## Troubleshooting Authentication

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid or expired token | Re-authenticate with valid credentials |
| 401 + "invalid_client" | Wrong client_id or client_secret | Verify credentials; regenerate if lost |
| 401 + "invalid_scope" | TSG ID doesn't exist or not accessible | Verify TSG ID in the UI |
| 403 Forbidden | Token valid but insufficient permissions | Check service account role assignments |
| 403 on SD-WAN calls | Profile not initialized | Call `GET /sdwan/v2.1/api/profile` first |

## Security Best Practices

1. **Never hardcode credentials** — use environment variables or a secrets manager
2. **Rotate secrets regularly** — create new service account credentials periodically
3. **Least privilege** — assign only the roles needed for the API operations you'll perform
4. **Token caching** — cache tokens and reuse until near expiry rather than requesting a new one per call
5. **Secure storage** — store client_secret encrypted; it cannot be retrieved from the UI after creation

## Service Account Management via API

Once authenticated, you can manage service accounts programmatically:

```bash
# List service accounts
curl -s -X GET "https://api.sase.paloaltonetworks.com/iam/v1/service_accounts" \
  -H "Authorization: Bearer ${TOKEN}"

# Create a service account
curl -s -X POST "https://api.sase.paloaltonetworks.com/iam/v1/service_accounts" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "automation-account",
    "description": "Account for CI/CD pipeline"
  }'

# Assign a role to a service account
curl -s -X POST "https://api.sase.paloaltonetworks.com/iam/v1/access_policies" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "principal": "<service_account_id>",
    "role": "security_admin",
    "resource": "tsg:<tsg_id>"
  }'
```
