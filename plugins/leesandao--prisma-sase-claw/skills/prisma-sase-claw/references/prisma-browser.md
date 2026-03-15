# Prisma Access Browser API

Prisma Access Browser is an enterprise secure browser managed through the SASE platform.

## Overview

The Prisma Access Browser API allows you to manage browser policies, user assignments, security configurations, and deployment settings for the enterprise browser.

Base path: `https://api.sase.paloaltonetworks.com`

Authentication uses the same OAuth2 client credentials flow as other SASE services — no special headers beyond the standard `Authorization: Bearer <token>`.

## Key Capabilities

### Browser Security Policies

Control what users can do in the browser — DLP policies, download restrictions, clipboard controls, screenshot blocking, etc.

```bash
# List browser security policies
curl -s -X GET "https://api.sase.paloaltonetworks.com/sse/config/v1/browser-access-policies?folder=All" \
  -H "Authorization: Bearer ${TOKEN}"

# Create a browser security policy
curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/browser-access-policies?folder=All" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "restrict-downloads",
    "description": "Block downloads from untrusted SaaS apps",
    "rules": [
      {
        "name": "block-untrusted-downloads",
        "action": "block",
        "applications": ["unsanctioned-saas"],
        "activities": ["download"]
      }
    ]
  }'
```

### Browser Configuration Profiles

Manage browser settings, extensions, bookmarks, and startup behavior.

```bash
# List browser profiles
GET /sse/config/v1/browser-profiles?folder=All

# Create a browser profile
POST /sse/config/v1/browser-profiles?folder=All
{
  "name": "standard-employee-profile",
  "settings": {
    "homepage": "https://intranet.company.com",
    "allow_extensions": false,
    "incognito_mode": "disabled",
    "developer_tools": "disabled"
  }
}
```

### Extension Management

Control which browser extensions are allowed, blocked, or force-installed.

```bash
# List extension policies
GET /sse/config/v1/browser-extension-policies?folder=All

# Create extension policy
POST /sse/config/v1/browser-extension-policies?folder=All
{
  "name": "approved-extensions",
  "force_install": ["extension-id-1", "extension-id-2"],
  "blocked": ["extension-id-3"],
  "allow_list": ["extension-id-4"]
}
```

### Data Loss Prevention (DLP) for Browser

Browser-specific DLP controls for copy/paste, upload, and data exfiltration prevention.

```bash
# List browser DLP policies
GET /sse/config/v1/browser-dlp-policies?folder=All

# Create DLP policy
POST /sse/config/v1/browser-dlp-policies?folder=All
{
  "name": "prevent-data-leak",
  "rules": [
    {
      "name": "block-pii-upload",
      "action": "block",
      "data_patterns": ["credit-card", "ssn"],
      "activities": ["upload", "paste"]
    }
  ]
}
```

### User and Group Assignments

Assign browser profiles and policies to users or groups.

```bash
# List user assignments
GET /sse/config/v1/browser-user-assignments?folder=All

# Assign a profile to a user group
POST /sse/config/v1/browser-user-assignments?folder=All
{
  "name": "engineering-team-assignment",
  "user_groups": ["cn=engineering,ou=groups,dc=company,dc=com"],
  "browser_profile": "developer-profile",
  "security_policy": "standard-security"
}
```

### Deployment and Rollout

Manage browser deployment settings and rollout configurations.

```bash
# Get deployment status
GET /sse/config/v1/browser-deployments?folder=All

# Update deployment settings
PUT /sse/config/v1/browser-deployments/{deployment_id}?folder=All
{
  "auto_update": true,
  "update_channel": "stable",
  "rollout_percentage": 100
}
```

### Browser Activity Logs

Query browser activity and security events.

```bash
# Browser activity logs are available through the aggregate monitoring API
# Requires x-panw-region header
curl -s -X POST "https://api.sase.paloaltonetworks.com/mt/monitor/v1/agg/browser/activities" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "x-panw-region: americas" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "operator": "AND",
      "rules": [
        {"property": "event_time", "operator": "last_n_days", "values": [7]},
        {"property": "action", "operator": "in", "values": ["block"]}
      ]
    },
    "properties": [
      {"property": "total_count"},
      {"property": "user"}
    ]
  }'
```

## Important Notes

- Browser policies follow the same candidate/running config model as Prisma Access — push configs after making changes.
- The `?folder=All` query parameter scopes configuration to the appropriate folder hierarchy.
- Browser management requires the appropriate IAM roles (typically Security Admin or a custom role with browser management permissions).
- Check the latest pan.dev documentation for newly added endpoints, as the Browser API is actively evolving.
