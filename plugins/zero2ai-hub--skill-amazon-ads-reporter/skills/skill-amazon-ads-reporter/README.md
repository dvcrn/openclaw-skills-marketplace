# skill-amazon-ads-reporter — Amazon Ads Performance Reports

Fetch Amazon Ads Sponsored Products campaign performance reports using a decoupled async pattern.

## Use When
- Pulling Sponsored Products campaign reports
- Analyzing ad spend, impressions, clicks, and ACOS
- Avoiding timeout issues with Amazon's v3 Reporting API (2–10 min generation)
- Scheduling regular performance snapshots

## Architecture
Decoupled two-step pattern:
1. **Request** — submit report job to Amazon Ads API v3
2. **Poll** — check status and download when ready

Avoids timeouts since report generation takes 2–10 minutes.

## Requirements
- Amazon Ads API credentials (Client ID, Client Secret, Refresh Token)
- Advertiser Profile ID

## Key Features
- Sponsored Products campaign reports
- Handles long generation times gracefully
- Supports filtering by date range, campaign, ad group
- Outputs structured JSON or CSV

## Quick Start
Load the SKILL.md for setup and full usage instructions.
