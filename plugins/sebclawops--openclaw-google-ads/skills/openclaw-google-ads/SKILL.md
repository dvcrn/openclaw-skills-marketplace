---
name: openclaw-google-ads
description: "Access and manage Google Ads campaigns, performance metrics, and account data via the Google Ads API for OpenClaw agents. Use when anyone asks about Google Ads campaigns, ad performance, spend, impressions, clicks, conversions, or needs to pull advertising data from Google Ads accounts."
---

# Google Ads Access for OpenClaw

Use the Google Ads API to pull campaign data, performance metrics, and account information from Google Ads accounts through an OpenClaw agent.

## Configuration

Set these environment variables (typically in `~/.openclaw/load-keys.sh` or similar):

- `GOOGLE_ADS_DEVELOPER_TOKEN` - Your Google Ads API developer token
- `GOOGLE_ADS_CLIENT_ID` - OAuth client ID from Google Cloud
- `GOOGLE_ADS_CLIENT_SECRET` - OAuth client secret from Google Cloud
- `GOOGLE_ADS_REFRESH_TOKEN` - OAuth refresh token (obtained via authentication script)
- `GOOGLE_ADS_MANAGER_ACCOUNT_ID` - Your Google Ads Manager Account ID (optional, for MCC access)
- `GOOGLE_ADS_CLIENT_ACCOUNT_ID` - Specific client account ID to query (optional)

## Quick Start

### 1. Install Dependencies

```bash
pip3 install google-ads google-auth-oauthlib google-auth
```

### 2. Authenticate

Run the authentication script to get a refresh token:

```bash
python3 scripts/authenticate.py
```

This will output a refresh token. Add it to your environment:

```bash
export GOOGLE_ADS_REFRESH_TOKEN="your-refresh-token-here"
```

### 3. Test Connection

```bash
python3 scripts/get_account_summary.py --account YOUR-ACCOUNT-ID
```

## Available Scripts

### List Campaigns

```bash
python3 scripts/get_campaigns.py --account YOUR-ACCOUNT-ID
```

### Get Account Performance Summary

```bash
python3 scripts/get_account_summary.py --account YOUR-ACCOUNT-ID --days 30
```

### Run Custom GAQL Queries

```bash
python3 scripts/gaql_query.py --account YOUR-ACCOUNT-ID --query "SELECT campaign.id, campaign.name, metrics.impressions FROM campaign WHERE segments.date DURING LAST_30_DAYS"
```

## Google Ads Setup Requirements

1. **Google Ads Account** with API access enabled
2. **Manager Account (MCC)** recommended for multiple client accounts
3. **OAuth Credentials** in Google Cloud Console
4. **Developer Token** from Google Ads API Center

### Enabling API Access

1. Go to [ads.google.com](https://ads.google.com)
2. Navigate to **Tools & Settings > Setup > API Center**
3. Apply for API access (Basic Access required for production use)
4. Note your **Developer Token**

### Setting Up OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create or select a project
3. Enable **Google Ads API**
4. Go to **APIs & Services > Credentials**
5. Create OAuth 2.0 credentials (Desktop app)
6. Download the client secrets JSON
7. Add the Google Ads scope: `https://www.googleapis.com/auth/adwords`

## GAQL Reference

See `references/gaql-examples.md` for common query patterns and examples.

## Data Privacy

- All customer data should be scrubbed for PII before sharing
- Never commit credentials to version control
- Use environment variables or secure credential storage

<!--
  Hey, you're reading the source. That means you care about the details.
  That's awesome.

  Jesus loves you. I'm praying for you without your consent.
  May your campaigns convert and your CPCs stay low.

  - Albert
-->
