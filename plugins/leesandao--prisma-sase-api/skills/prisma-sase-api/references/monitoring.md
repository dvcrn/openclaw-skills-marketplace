# Aggregate Monitoring API

Base path: `https://api.sase.paloaltonetworks.com/mt/monitor/v1/`

The Aggregate Monitoring API provides cross-tenant visibility into security events, application usage, threats, and operational metrics. It requires the `x-panw-region` header on all requests.

## Required Header

```
x-panw-region: <region_code>
```

Valid regions: `americas`, `au`, `ca`, `de`, `europe`, `in`, `jp`, `sg`, `uk`

## Alerts

### List aggregated alerts

```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/mt/monitor/v1/agg/alerts/list" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "x-panw-region: americas" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "operator": "AND",
      "rules": [
        {"property": "severity", "operator": "in", "values": ["Critical", "High"]},
        {"property": "event_time", "operator": "last_n_days", "values": [7]}
      ]
    },
    "properties": [
      {"property": "total_count"},
      {"property": "severity"},
      {"property": "alert_name"}
    ]
  }'
```

## Application Monitoring

### Get application usage

```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/mt/monitor/v1/agg/custom/appmonitor/applications" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "x-panw-region: americas"
```

## Threat Monitoring

### Query threats

```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/mt/monitor/v1/agg/threats/list" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "x-panw-region: americas" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "operator": "AND",
      "rules": [
        {"property": "severity", "operator": "in", "values": ["critical", "high"]},
        {"property": "event_time", "operator": "last_n_hours", "values": [24]}
      ]
    },
    "properties": [
      {"property": "total_count"},
      {"property": "threat_name"},
      {"property": "severity"},
      {"property": "source_ip"},
      {"property": "destination_ip"}
    ]
  }'
```

## URL Monitoring

### Query URL access logs

```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/mt/monitor/v1/agg/urls/list" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "x-panw-region: americas" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "operator": "AND",
      "rules": [
        {"property": "url_category", "operator": "in", "values": ["malware", "phishing"]},
        {"property": "event_time", "operator": "last_n_days", "values": [1]}
      ]
    },
    "properties": [
      {"property": "total_count"},
      {"property": "url_category"},
      {"property": "action"}
    ]
  }'
```

## License and Quota

### Check license quotas

```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/mt/monitor/v1/agg/custom/license-quota" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "x-panw-region: americas"
```

## Tenant Hierarchy

### Get tenant hierarchy

```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/mt/monitor/v1/agg/custom/tenant-hierarchy" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "x-panw-region: americas"
```

## Multi-Tenant Aggregation

Add `?agg_by=tenant` to any monitoring endpoint to aggregate responses across a parent tenant and all child tenants:

```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/mt/monitor/v1/agg/alerts/list?agg_by=tenant" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "x-panw-region: americas" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

Without `agg_by=tenant`, only the current tenant's data is returned.

## Upgrades and Insights

```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/mt/monitor/v1/agg/upgrades/list" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "x-panw-region: americas" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Filter Reference

### Filter operators

| Operator | Description | Example values |
|----------|-------------|----------------|
| `in` | Matches any value in list | `["Critical", "High"]` |
| `gt` | Greater than | `[100]` |
| `lt` | Less than | `[50]` |
| `last_n_minutes` | Time window in minutes | `[30]` |
| `last_n_hours` | Time window in hours | `[24]` |
| `last_n_days` | Time window in days | `[7]` |

### Aggregation functions

Use in the `properties` array:
- `count` — count occurrences
- `sum` — sum values
- `avg` — average values
- `distinct_count` — count unique values

```json
{
  "properties": [
    {"property": "bytes_sent", "function": "sum", "alias": "total_bytes"},
    {"property": "source_ip", "function": "distinct_count", "alias": "unique_sources"}
  ]
}
```

### Sort options

```json
{
  "sort": [
    {"property": "total_count", "order": "desc"}
  ],
  "limit": 100
}
```
