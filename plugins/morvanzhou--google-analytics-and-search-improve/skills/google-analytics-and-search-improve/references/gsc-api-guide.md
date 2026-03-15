# Google Search Console API Reference

## Authentication Setup

GSC and GA4 share the same Service Account. Create it once to use for both.

### Step 1: Create a Google Cloud Project and Enable APIs

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project selector (top-left) → "New Project" → name it (e.g., "my-site-analytics") → "Create"
3. Confirm you've switched to the new project, then open the [API Library](https://console.cloud.google.com/apis/library)
4. Search for **"Google Search Console API"** → click into it → click "Enable"
5. Search for **"Google Analytics Data API"** → click into it → click "Enable" (this enables GA4 as well)
6. Search for **"PageSpeed Insights API"** → click into it → click "Enable" (used for site performance auditing; without it you'll get 429 quota errors)

### Step 2: Create a Service Account and Download JSON Key

1. Open the [Service Accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "+ Create Service Account" at the top
3. Enter a name (e.g., "analytics-reader") → click "Create and Continue"
4. Skip role selection (no project-level role needed) → "Continue" → "Done"
5. Find the newly created Service Account in the list, click its email address to enter the details page
6. Click the "Keys" tab → "Add Key" → "Create new key" → select **JSON** → "Create"
7. Your browser will automatically download a `.json` file (e.g., `my-site-analytics-xxxx.json`) — this is the key file
8. Remember the file path on your machine (e.g., `/Users/yourname/Downloads/my-site-analytics-xxxx.json`)

**Important**: Also note the Service Account email address (format: `analytics-reader@my-site-analytics.iam.gserviceaccount.com`) — you'll need it for authorization below.

### Step 3: Authorize in Search Console

1. Open [Google Search Console](https://search.google.com/search-console/)
2. Select your site property
3. Click "Settings" at the bottom of the left menu → "Users and permissions"
4. Click "Add user" → paste the Service Account email → set permission to "Restricted" (read-only) → "Add"

### Step 4: Confirm GSC Property Type

GSC has two property types, and the `GSC_SITE_URL` value must match the actual type:

- **Domain property**: Shows a bare domain in the GSC top-left selector → use `sc-domain:example.com`
- **URL-prefix property**: Shows a full URL → use `https://example.com`

Using the wrong format will cause the API to return a 403 permission error.

### Step 5: Write to .env

Write the following values to `$DATA_DIR/.env` (scripts will auto-load):

```
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/on/your/machine/my-site-analytics-xxxx.json
GSC_SITE_URL=sc-domain:example.com
```

> **Note**: `GOOGLE_APPLICATION_CREDENTIALS` should use an **absolute path**. Relative paths may fail to locate the key file when running from different working directories.

## Script Usage

Scripts auto-read `GOOGLE_APPLICATION_CREDENTIALS` and `GSC_SITE_URL` from `$DATA_DIR/.env`. Once `.env` is configured, you don't need to pass these values on the command line.

### Search Analytics Queries

```bash
# Last 28 days grouped by query and page (default)
python scripts/gsc_query.py

# Specify dimensions and date range
python scripts/gsc_query.py --dimensions query --limit 500 \
    --start-date 2025-01-01 --end-date 2025-03-01

# Group by device and country
python scripts/gsc_query.py --dimensions device,country --limit 100

# View trends by date
python scripts/gsc_query.py --dimensions date

# Output to file
python scripts/gsc_query.py --dimensions query -o gsc_data.json
```

The `--site-url` CLI flag overrides `GSC_SITE_URL` from `.env`.

### Available Dimensions

| Dimension | Description |
|-----------|-------------|
| `query` | Search query term |
| `page` | Page URL |
| `country` | Country code |
| `device` | Device type (DESKTOP/MOBILE/TABLET) |
| `date` | Date |
| `searchAppearance` | Search result appearance type |

### Returned Metrics

Each row contains:
- `clicks` — Click count
- `impressions` — Impression count
- `ctr` — Click-through rate (clicks / impressions)
- `position` — Average ranking position

### Sitemap Query

```bash
python scripts/gsc_query.py --mode sitemaps
```

### URL Inspection

```bash
python scripts/gsc_query.py --mode inspect --inspect-url "https://example.com/some-page"
```

Returns indexing status, crawl info, mobile usability, etc.

## Common Analysis Scenarios

### Find High-Impression Low-Click Keywords (CTR Optimization Opportunities)

Query `search_analytics` grouped by query; find rows with high `impressions` but low `ctr`.

### Find Pages with Declining Rankings

Group by `date,page`; compare `position` changes across different time periods.

### Find Unindexed Pages

Use `inspect` mode to check the indexing status of key pages one by one.
