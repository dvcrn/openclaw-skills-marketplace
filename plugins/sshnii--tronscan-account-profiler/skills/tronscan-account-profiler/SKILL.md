---
name: tronscan-account-profiler
description: "Query TRON wallet-type address total assets, token holdings, DeFi participation, energy/bandwidth, votes, tx/transfer count.\n Use when user asks \"what assets does this address have\", \"address balance\", \"recent activity\", or provides a TRON address for profiling.\n If the core question is contract identification, verification status, or popular methods, immediately switch to tronscan-contract-analysis.\n Do NOT use for single token details or holder distribution (use tronscan-token-scanner); tx hash details (use tronscan-transaction-info)."
---

# Account Profiler

## Overview

| Tool | Function | Use Case |
|------|----------|----------|
| getAccountDetail | Account detail | Balance, tx count, bandwidth/energy, votes |
| getAccountTokens | Account tokens | Tokens held by address |
| getTokenAssetOverview | Asset overview | Holdings and total value |
| getParticipatedProjects | Participated projects | DeFi participation |

## Workflow: Wallet Address Profiling

> User: "What assets does this address have? Any recent activity?"

1. **tronscan-account-profiler** — `getAccountDetail` → balance, tx count, bandwidth/energy, votes.
2. **tronscan-account-profiler** — `getAccountTokens` + `getTokenAssetOverview` for holdings and total value; optionally `getParticipatedProjects` for DeFi participation.
3. If **recent transactions** needed: **tronscan-transaction-info** — call `getTransactionList` with the address.

**Data handoff**: Same TRON address used as account parameter across all steps.

## MCP Server

- **Prerequisite**: [TronScan MCP Guide](https://mcpdoc.tronscan.org)

## Troubleshooting

- **MCP connection failed**: If you see "Connection refused", verify TronScan MCP is connected in Settings > Extensions.
- **API rate limit / 429**: TronScan API has call count and frequency limits when no API key is used. If you encounter rate limiting or 429 errors, go to [TronScan Developer API](https://tronscan.org/#/developer/api) to apply for an API key, then add it to your MCP configuration and retry.

### Invalid address
Ensure the address is a valid TRON base58 format (starts with T). For contract analysis, use **tronscan-contract-analysis** skill instead.

