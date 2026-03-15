---
name: skill-amazon-ads-reporter
description: "Amazon Ads Reporter"
---

# skill-amazon-ads-reporter

## Description
Fetch Amazon Ads Sponsored Products campaign performance reports using a decoupled async pattern. Avoids timeout issues with the v3 Reporting API (2–10 min generation time) by splitting request and poll into separate steps.

## Why two steps?
Amazon's Reporting API v3 is async — you request a report, get a `reportId`, and poll until it's ready. Doing this inline in a cron causes timeouts. The correct pattern:

```
request → save reportId → (wait 1-2 min) → poll + download
```

## Usage

### Step-by-step (recommended for crons)
```bash
# Step 1: Request report — exits immediately with reportId
node scripts/request-report.js --days 7

# Step 2: Poll + download (run 1-2 min later, or from a separate cron)
node scripts/poll-report.js
```

### All-in-one (for manual runs or long-timeout jobs)
```bash
node scripts/get-report.js --days 7
```

## Arguments
| Arg | Default | Description |
|-----|---------|-------------|
| `--days N` | `7` | Number of days to include in report |

## Configuration
Reads credentials from `AMAZON_ADS_PATH` env var, defaulting to `~/amazon-ads-api.json`.

### `amazon-ads-api.json` format
```json
{
  "accessToken": "...",
  "clientId": "...",
  "profileId": "...",
  "region": "EU"
}
```

Regions: `EU` (default, includes UAE), `NA` (North America), `FE` (Far East).

## Output
- `~/.openclaw/workspace/tmp/amazon-report-pending.json` — created by request-report.js
- `~/.openclaw/workspace/tmp/amazon-report-latest.json` — created by poll-report.js after success
- Console table: Campaign | Impressions | Clicks | CTR% | Spend | Sales | ACOS%

## Report columns
`campaignName`, `campaignId`, `impressions`, `clicks`, `spend`, `purchases7d`, `sales7d`

Paused campaigns are automatically filtered out by cross-referencing `GET /sp/campaigns/list`.

## Dependencies
Node.js built-ins only (`https`, `zlib`, `fs`, `path`). No npm install required.

## Notes
- Access tokens expire — refresh via Amazon Login with Advertising if needed
- The `GZIP_JSON` format is gunzipped automatically by poll-report.js
- Reports are only available for the previous day and earlier (endDate = yesterday)
