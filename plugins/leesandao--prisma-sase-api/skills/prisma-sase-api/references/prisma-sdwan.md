# Prisma SD-WAN API

Base path: `https://api.sase.paloaltonetworks.com/sdwan/v2.1/api/`

Prisma SD-WAN provides software-defined WAN capabilities. Before making any SD-WAN API calls, you must initialize the profile (see below).

## Table of Contents

1. [Profile Initialization](#profile-initialization)
2. [Sites](#sites)
3. [Site Templates](#site-templates)
4. [Network Constructs](#network-constructs)
5. [Routing (OSPF)](#routing-ospf)
6. [Security Policy](#security-policy)
7. [NAT Policy](#nat-policy)
8. [Path Policy](#path-policy)
9. [Performance Policy](#performance-policy)
10. [QoS Policy](#qos-policy)
11. [Applications](#applications)
12. [DHCP and DNS](#dhcp-and-dns)
13. [Device Management](#device-management)
14. [Metrics and Events](#metrics-and-events)
15. [Reports and Audit Logs](#reports-and-audit-logs)
16. [Software Management](#software-management)
17. [Topology and Fabric](#topology-and-fabric)
18. [Bulk Operations](#bulk-operations)

---

## Profile Initialization

**This must be the first SD-WAN API call after obtaining a token.** Skipping it causes 403 errors on all subsequent calls.

```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sdwan/v2.1/api/profile" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## Sites

Sites represent physical locations with SD-WAN appliances.

### List all sites
```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sdwan/v2.1/api/sites" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Get a specific site
```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sdwan/v2.1/api/sites/${SITE_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create a site
```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/sdwan/v2.1/api/sites" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "branch-chicago",
    "description": "Chicago branch office",
    "address": {
      "street": "123 Main St",
      "city": "Chicago",
      "state": "IL",
      "country": "US"
    },
    "location": {
      "latitude": 41.8781,
      "longitude": -87.6298
    },
    "policy_set_id": "<policy_set_id>",
    "element_cluster_role": "SPOKE"
  }'
```

### Update a site
```bash
curl -s -X PUT "https://api.sase.paloaltonetworks.com/sdwan/v2.1/api/sites/${SITE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

### Delete a site
```bash
curl -s -X DELETE "https://api.sase.paloaltonetworks.com/sdwan/v2.1/api/sites/${SITE_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## Site Templates

Templates for standardized site configuration.

```bash
# List templates
GET /sdwan/v2.1/api/sites/site_templates

# Get template
GET /sdwan/v2.1/api/sites/site_templates/${TEMPLATE_ID}

# Create template
POST /sdwan/v2.1/api/sites/site_templates

# Apply template to site
POST /sdwan/v2.1/api/sites/${SITE_ID}/site_template_apply
```

---

## Network Constructs

Network constructs define the WAN and LAN interfaces, circuits, and paths.

```bash
# WAN interfaces for a site
GET  /sdwan/v2.1/api/sites/${SITE_ID}/wannetworks
POST /sdwan/v2.1/api/sites/${SITE_ID}/wannetworks

# LAN networks
GET  /sdwan/v2.1/api/sites/${SITE_ID}/lannetworks
POST /sdwan/v2.1/api/sites/${SITE_ID}/lannetworks

# WAN interface labels (global)
GET  /sdwan/v2.1/api/waninterfacelabels
POST /sdwan/v2.1/api/waninterfacelabels
```

---

## Routing (OSPF)

```bash
# OSPF configuration for a site element
GET  /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/ospfconfigs
POST /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/ospfconfigs
PUT  /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/ospfconfigs/${CONFIG_ID}

# BGP configuration
GET  /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/bgpconfigs
POST /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/bgpconfigs
```

---

## Security Policy

SD-WAN security policies at the global or site level.

```bash
# Global security policy sets
GET  /sdwan/v2.1/api/securitypolicysets
POST /sdwan/v2.1/api/securitypolicysets

# Security policy rules within a set
GET  /sdwan/v2.1/api/securitypolicysets/${SET_ID}/securitypolicyrules
POST /sdwan/v2.1/api/securitypolicysets/${SET_ID}/securitypolicyrules
PUT  /sdwan/v2.1/api/securitypolicysets/${SET_ID}/securitypolicyrules/${RULE_ID}
DELETE /sdwan/v2.1/api/securitypolicysets/${SET_ID}/securitypolicyrules/${RULE_ID}

# Security zones
GET  /sdwan/v2.1/api/securityzones
POST /sdwan/v2.1/api/securityzones
```

---

## NAT Policy

```bash
# NAT policy sets
GET  /sdwan/v2.1/api/natpolicysets
POST /sdwan/v2.1/api/natpolicysets

# NAT rules
GET  /sdwan/v2.1/api/natpolicysets/${SET_ID}/natpolicyrules
POST /sdwan/v2.1/api/natpolicysets/${SET_ID}/natpolicyrules
```

---

## Path Policy

Path policies control WAN path selection and traffic steering.

```bash
# Path policy sets
GET  /sdwan/v2.1/api/pathpolicysets

# Path policy rules
GET  /sdwan/v2.1/api/pathpolicysets/${SET_ID}/pathpolicyrules
POST /sdwan/v2.1/api/pathpolicysets/${SET_ID}/pathpolicyrules
```

---

## Performance Policy

```bash
GET  /sdwan/v2.1/api/performancepolicysets
GET  /sdwan/v2.1/api/performancepolicysets/${SET_ID}/performancepolicyrules
POST /sdwan/v2.1/api/performancepolicysets/${SET_ID}/performancepolicyrules
```

---

## QoS Policy

```bash
GET  /sdwan/v2.1/api/prioritypolicysets
GET  /sdwan/v2.1/api/prioritypolicysets/${SET_ID}/prioritypolicyrules
POST /sdwan/v2.1/api/prioritypolicysets/${SET_ID}/prioritypolicyrules
```

---

## Applications

Application definitions for policy matching.

```bash
# List all applications
GET /sdwan/v2.1/api/appdefs

# Custom applications
POST /sdwan/v2.1/api/appdefs
PUT  /sdwan/v2.1/api/appdefs/${APP_ID}
DELETE /sdwan/v2.1/api/appdefs/${APP_ID}
```

---

## DHCP and DNS

```bash
# DHCP server configuration per site
GET  /sdwan/v2.1/api/sites/${SITE_ID}/dhcpservers
POST /sdwan/v2.1/api/sites/${SITE_ID}/dhcpservers

# DNS services
GET  /sdwan/v2.1/api/dnsserviceprofiles
POST /sdwan/v2.1/api/dnsserviceprofiles
```

---

## Device Management

```bash
# List elements (devices/appliances)
GET /sdwan/v2.1/api/elements

# Get element details
GET /sdwan/v2.1/api/elements/${ELEMENT_ID}

# Site-specific elements
GET /sdwan/v2.1/api/sites/${SITE_ID}/elements

# Element interfaces
GET  /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/interfaces
POST /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/interfaces
PUT  /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/interfaces/${INTF_ID}

# Switch configuration
GET  /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/elementshellconfigs
```

---

## Metrics and Events

### Query metrics
```bash
# Topn metrics (aggregated)
POST /sdwan/v2.1/api/monitor/topn
{
  "topn_basis": "traffic_volume",
  "type": "app",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-02T00:00:00Z",
  "filter": {
    "site": ["<site_id>"]
  },
  "limit": 10
}
```

### Query events
```bash
POST /sdwan/v2.1/api/monitor/events
{
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-02T00:00:00Z",
  "filter": {
    "site": ["<site_id>"]
  }
}
```

### Flows and statistics
```bash
POST /sdwan/v2.1/api/monitor/flows
POST /sdwan/v2.1/api/monitor/sys_metrics
POST /sdwan/v2.1/api/monitor/sys_point_metrics
```

---

## Reports and Audit Logs

```bash
# Audit logs
GET /sdwan/v2.1/api/auditlog

# Reports
POST /sdwan/v2.1/api/reports
GET  /sdwan/v2.1/api/reports/${REPORT_ID}
```

---

## Software Management

```bash
# List available software
GET /sdwan/v2.1/api/element_images

# Upgrade an element
POST /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/software_upgrade
{
  "image_id": "<image_id>",
  "scheduled_upgrade": false
}

# Check upgrade status
GET /sdwan/v2.1/api/sites/${SITE_ID}/elements/${ELEMENT_ID}/software_state
```

---

## Topology and Fabric

```bash
# Topology
GET /sdwan/v2.1/api/topology

# SASE fabric links
GET /sdwan/v2.1/api/sasefabriclinks
```

---

## Bulk Operations

For large-scale operations:
```bash
POST /sdwan/v2.1/api/sites/bulk_operations
{
  "action": "claim",
  "sites": [...]
}
```

---

## Common Patterns

- **Site-scoped resources:** Most SD-WAN resources are scoped to a site: `/sites/${SITE_ID}/...`
- **Element-scoped resources:** Interface and routing configs are per-element within a site: `/sites/${SITE_ID}/elements/${ELEMENT_ID}/...`
- **Policy hierarchy:** Policies are organized as sets containing rules. CRUD the set first, then manage rules within it.
- **Pagination:** Use `?limit=N&offset=M` query parameters for paginated endpoints.
