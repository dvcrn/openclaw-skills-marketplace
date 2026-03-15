---
name: prisma-sase-claw
description: "How to interact with the Palo Alto Networks Prisma SASE API, including Prisma Access, Prisma SD-WAN, and Prisma Access Browser. Use this skill whenever the user wants to query, configure, monitor, or automate anything related to Prisma SASE, Prisma Access, Prisma SD-WAN, Prisma Access Browser, Palo Alto SASE, PANW SASE, or network security policies managed through the SASE platform. Also trigger when the user mentions tenant service groups (TSGs), SASE API tokens, security policy rules, SD-WAN sites, remote networks, GlobalProtect, or aggregate monitoring via the SASE platform."
---

# Prisma SASE API Integration

This skill generates working curl commands and Python scripts to interact with the Palo Alto Networks Prisma SASE platform API. It covers three main products:

- **Prisma Access** — Cloud-delivered network security (security policies, remote networks, GlobalProtect, service connections)
- **Prisma SD-WAN** — Software-defined WAN (site configs, routing, path policies, performance monitoring)
- **Prisma Access Browser** — Secure enterprise browser management

## Quick Reference

| Component | Base URL |
|-----------|----------|
| **API Gateway** | `https://api.sase.paloaltonetworks.com` |
| **Auth Endpoint** | `https://auth.apps.paloaltonetworks.com/oauth2/access_token` |

| Product | URL Prefix |
|---------|-----------|
| Prisma Access Config | `/sse/config/v1/...` |
| SD-WAN | `/sdwan/v2.1/api/...` |
| Aggregate Monitoring | `/mt/monitor/v1/...` |
| IAM | `/iam/v1/...` |
| Tenancy | `/tenancy/v1/...` |
| Subscription | `/subscription/v1/...` |

## Authentication

All API calls use OAuth2 client credentials flow. The user needs three values:
- `client_id` and `client_secret` — from a service account created in the Prisma SASE UI
- `tsg_id` — the Tenant Service Group ID scoping the token

### Get an access token

```bash
curl -s -X POST "https://auth.apps.paloaltonetworks.com/oauth2/access_token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "${CLIENT_ID}:${CLIENT_SECRET}" \
  -d "grant_type=client_credentials&scope=tsg_id:${TSG_ID}"
```

The response returns a JWT access token valid for **15 minutes**. There is no refresh token — request a new one when it expires.

### Python authentication helper

When generating Python scripts, use the helper at `scripts/sase_auth.py` (relative to this skill directory). Read it for the implementation — it handles token caching and auto-renewal.

### Required headers for all API calls

```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

Some services also require a **regional header**:
```
x-panw-region: <region_code>
```
Required for: Aggregate Monitoring, ZTNA Connector, Autonomous DEM.
Valid regions: `americas`, `au`, `ca`, `de`, `europe`, `in`, `jp`, `sg`, `uk`.

**Important:** Including `x-panw-region` on services that don't need it causes errors. Only add it when the endpoint requires it.

## Product-Specific Guides

Depending on what the user needs, read the relevant reference file for detailed endpoint documentation:

| User wants to... | Read this file |
|-------------------|---------------|
| Manage security policies, remote networks, GlobalProtect, service connections, decryption rules, or any Prisma Access configuration | `references/prisma-access.md` |
| Configure SD-WAN sites, routing, path policies, NAT, QoS, or query SD-WAN metrics/events | `references/prisma-sdwan.md` |
| Manage Prisma Access Browser settings, policies, or deployments | `references/prisma-browser.md` |
| Set up authentication, manage tokens, or troubleshoot auth issues | `references/authentication.md` |
| Query aggregate monitoring data, alerts, or multi-tenant reports | `references/monitoring.md` |

Read the appropriate reference file before generating API calls for that product area.

## Common API Patterns

### Prisma Access Configuration: Candidate/Running Config Model

Prisma Access uses a two-stage configuration model. Changes go to a "candidate" config first, then must be pushed to become the "running" config:

1. **Make changes** — POST/PUT/DELETE to config endpoints (creates candidate changes)
2. **Push candidate config:**
   ```bash
   curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/config-versions/candidate:push" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"folders": ["All"]}'
   ```
3. **Monitor the push job** until it completes
4. The candidate becomes the running configuration

Always remind the user that config changes won't take effect until pushed.

### SD-WAN: Profile Initialization

After obtaining a token, the first SD-WAN API call must be:
```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sdwan/v2.1/api/profile" \
  -H "Authorization: Bearer ${TOKEN}"
```
Skipping this causes 403 errors on subsequent SD-WAN calls.

### Aggregate Monitoring: POST-based Filtering

Monitoring queries use POST with structured filter bodies, not query parameters:

```json
{
  "filter": {
    "operator": "AND",
    "rules": [
      {"property": "severity", "operator": "in", "values": ["Critical", "High"]},
      {"property": "event_time", "operator": "last_n_days", "values": [7]}
    ]
  },
  "properties": [
    {"property": "total_count"},
    {"property": "severity"}
  ]
}
```

Filter operators: `in`, `gt`, `lt`, `last_n_minutes`, `last_n_hours`, `last_n_days`.

### Multi-tenant Aggregation

Add `?agg_by=tenant` to aggregate responses across a parent tenant and all child tenants.

### Common Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Check request body/params |
| 401 | Unauthorized | Token expired or invalid — re-authenticate |
| 403 | Forbidden | Insufficient role permissions (or SD-WAN profile not initialized) |
| 409 | Conflict | Resource already exists or version conflict |

## Script Generation Guidelines

When generating scripts for the user:

1. **Always parameterize credentials** — never hardcode `client_id`, `client_secret`, or `tsg_id`. Use environment variables or prompt the user.
2. **Handle token expiry** — tokens last 15 minutes. For long-running scripts, implement token refresh logic.
3. **Include error handling** — check HTTP status codes and print meaningful error messages.
4. **Use the auth helper** — for Python scripts, reference `scripts/sase_auth.py` for a reusable auth class.
5. **Remind about config push** — when generating Prisma Access config changes, always include the push step or remind the user it's needed.
6. **Initialize SD-WAN profile** — when generating SD-WAN scripts, include the profile initialization call.

## Tenant Service Groups (TSGs)

TSGs are the organizational hierarchy for multi-tenancy:
- A TSG contains tenants and/or child TSGs
- OAuth tokens are scoped to a specific TSG and its children
- The root TSG must be created via UI; child TSGs can be created via API
- Key endpoints:
  - `GET /tenancy/v1/tenant_service_groups` — list all TSGs
  - TSG children and ancestors are also queryable

## IAM and Roles

Service accounts need appropriate roles assigned to perform API operations. Key roles:
- **Superuser** — full read/write
- **Security Admin** — security policy management
- **Network Admin** — network policy and logs
- **View Only Administrator** — read-only across all
- **SOC Analyst** — read-only for logs, reports, alerts

If the user gets 403 errors, suggest checking their service account's role assignments.
