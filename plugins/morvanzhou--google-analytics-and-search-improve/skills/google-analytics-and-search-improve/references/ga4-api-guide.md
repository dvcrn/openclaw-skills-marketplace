# Google Analytics 4 Data API Reference

## Authentication Setup

GA4 and GSC share the same Service Account. If you haven't created one yet, first follow Steps 1-2 in [gsc-api-guide.md](gsc-api-guide.md) to create the Google Cloud project, enable APIs, and download the Service Account key (GA4 API enablement is already included there).

### Authorize Service Account in GA4

1. Open [Google Analytics](https://analytics.google.com/)
2. Click the gear icon (Admin) in the bottom-left
3. Under "Property", click "Property Access Management"
4. Click "+" (top-right) → "Add users"
5. Paste the Service Account email (format: `xxx@xxx.iam.gserviceaccount.com`) → set role to "Viewer" → "Add"

### Get GA4 Property ID

1. In the Google Analytics Admin page, click "Property Settings" (or "Property Details") under "Property"
2. The "Property ID" is displayed in the top-right — a numeric string (e.g., `123456789`, no "UA-" prefix)

### Write to .env

Write the following value to `$DATA_DIR/.env` (scripts will auto-load):

```
GA4_PROPERTY_ID=123456789
```

`GOOGLE_APPLICATION_CREDENTIALS` was already written during GSC configuration. GA4 shares the same key file — no need to repeat it.

## Script Usage

Scripts auto-read `GOOGLE_APPLICATION_CREDENTIALS` and `GA4_PROPERTY_ID` from `$DATA_DIR/.env`. Once `.env` is configured, you don't need to pass these values on the command line.

### Preset Query Templates

```bash
python scripts/ga4_query.py --preset traffic_overview       # Daily traffic trends
python scripts/ga4_query.py --preset top_pages --limit 50   # Top pages
python scripts/ga4_query.py --preset user_acquisition       # User acquisition sources
python scripts/ga4_query.py --preset device_breakdown        # Device distribution
python scripts/ga4_query.py --preset geo_distribution        # Geographic distribution
python scripts/ga4_query.py --preset landing_pages           # Landing pages
python scripts/ga4_query.py --preset user_behavior           # User behavior
python scripts/ga4_query.py --preset conversion_events       # Conversion events
```

The `--property-id` CLI flag overrides `GA4_PROPERTY_ID` from `.env`.

### Custom Queries

```bash
python scripts/ga4_query.py \
    --dimensions pagePath,deviceCategory \
    --metrics sessions,bounceRate,averageSessionDuration \
    --start-date 2025-01-01 --end-date 2025-03-01 \
    --order-by -sessions --limit 200
```

### Date Formats

Both absolute and relative dates are supported:
- Absolute: `2025-01-01`
- Relative: `today`, `yesterday`, `NdaysAgo` (e.g., `28daysAgo`)

## Common Dimensions

| Dimension | Description |
|-----------|-------------|
| `date` | Date |
| `pagePath` | Page path |
| `pageTitle` | Page title |
| `landingPage` | Landing page |
| `sessionDefaultChannelGroup` | Channel grouping |
| `sessionSource` / `sessionMedium` | Source / Medium |
| `deviceCategory` | Device category |
| `operatingSystem` / `browser` | Operating system / Browser |
| `country` / `city` | Country / City |
| `eventName` | Event name |

## Common Metrics

| Metric | Description |
|--------|-------------|
| `sessions` | Session count |
| `totalUsers` / `newUsers` | Total users / New users |
| `screenPageViews` | Page views |
| `bounceRate` | Bounce rate |
| `averageSessionDuration` | Average session duration (seconds) |
| `engagementRate` / `engagedSessions` | Engagement rate / Engaged sessions |
| `eventCount` | Event count |
| `conversions` | Conversion count |

## Preset Template Reference

| Template | Purpose |
|----------|---------|
| `traffic_overview` | Daily traffic trends; detect traffic anomalies |
| `top_pages` | Find most popular and underperforming pages |
| `user_acquisition` | Analyze user source channel effectiveness |
| `device_breakdown` | Device and browser distribution; detect compatibility issues |
| `geo_distribution` | Geographic distribution; optimize internationalization |
| `landing_pages` | Landing page performance; optimize entry experience |
| `user_behavior` | User behavior paths and engagement depth |
| `conversion_events` | Conversion event tracking and funnel analysis |
