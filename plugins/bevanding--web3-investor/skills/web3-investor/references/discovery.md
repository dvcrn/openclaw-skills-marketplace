# Opportunity Discovery Module

> **Purpose**: Search DeFi yield opportunities across multiple sources with real-time data.

---

## What It Does

Searches DeFi yield opportunities across multiple sources with real-time data.

## Key Features

- **Risk Signals**: Each opportunity includes structured risk data:
  - `reward_type`: "none" | "single" | "multi"
  - `has_il_risk`: true | false (impermanent loss)
  - `underlying_type`: "rwa" | "onchain" | "mixed" | "unknown"
- **Actionable Addresses**: Contract addresses ready for execution
- **LLM-Ready Output**: Structured JSON optimized for AI analysis

## Data Sources (Priority Order)

| Source | Priority | Type | API Key Required |
|--------|----------|------|------------------|
| **MCP (AntAlpha)** | Primary | Real-time yields | No |
| **Dune Analytics** | Secondary | On-chain analytics | Yes (`DUNE_API_KEY`) |
| **DefiLlama** | Fallback | Protocol TVL/Yields | No |
| **Protocol Registry** | Static | Known protocol metadata | No |

### MCP (AntAlpha)
- **Endpoint**: `https://mcp.prime.antalpha.com/mcp`
- **Fallback**: `http://47.85.100.251:3000`
- **Use Case**: Real-time DeFi opportunity discovery
- **Configuration**: See `config/config.json` → `discovery.mcp_url`

### Dune Analytics
- **MCP Endpoint**: `https://api.dune.com/mcp/v1`
- **Auth Methods**:
  1. Header: `x-dune-api-key: <DUNE_API_KEY>`
  2. Query param: `?api_key=<DUNE_API_KEY>`
- **Environment Variable**: `DUNE_API_KEY`
- **Use Case**: Custom on-chain queries, protocol analytics, whale tracking
- **Configuration**:
```json
{
  "discovery": {
    "dune": {
      "mcp_endpoint": "https://api.dune.com/mcp/v1",
      "auth": {
        "header": { "name": "x-dune-api-key", "env_var": "DUNE_API_KEY" },
        "query_param": { "name": "api_key", "env_var": "DUNE_API_KEY" }
      },
      "enabled": true
    }
  }
}
```

### DefiLlama
- **Endpoint**: `https://yields.llama.fi`
- **Use Case**: Protocol TVL, yield data, cross-validation
- **No API key required**

## Usage Examples

```bash
# Search Ethereum opportunities with min 5% APY
python3 scripts/discovery/find_opportunities.py \
  --chain ethereum \
  --min-apy 5 \
  --limit 20

# Search stablecoin products only
python3 scripts/discovery/find_opportunities.py \
  --chain ethereum \
  --min-apy 3 \
  --max-apy 25 \
  --limit 50

# Output for LLM analysis
python3 scripts/discovery/find_opportunities.py \
  --chain ethereum \
  --llm-ready \
  --output json
```

## Output Format

### Standard Output

```
# DeFi Opportunities on ethereum

## 1. Aave V3 USDC
- APY: 5.23%
- TVL: $1,234,567,890
- Pool: 0x...
- Risk: single reward, no IL
```

### LLM-Ready Output (JSON)

```json
{
  "opportunities": [
    {
      "name": "Aave V3 USDC",
      "chain": "ethereum",
      "apy": 5.23,
      "tvl": 1234567890,
      "pool_address": "0x...",
      "reward_type": "single",
      "has_il_risk": false,
      "underlying_type": "onchain"
    }
  ]
}
```

## Troubleshooting

### No Opportunities Found
- Check chain name spelling (case-sensitive in some cases)
- Try lowering `--min-apy` threshold
- Ensure `--max-apy` isn't too restrictive

### Rate Limiting
- DefiLlama has generous limits but can occasionally rate limit
- Add delays between requests if batch processing