---
name: web3-investor
description: "AI-friendly Web3 investment infrastructure for autonomous agents. Use when (1) discovering and analyzing DeFi/NFT investment opportunities, (2) executing secure transactions via local keystore signer REST API with preview-approve-execute state machine, (3) managing portfolio with dashboards and expiry alerts. Supports base and ethereum chains, configurable security constraints including whitelist protection, transaction limits, and mandatory simulation before execution."
---

# Web3 Investor Skill

> **Purpose**: Enable AI agents to safely discover, analyze, and execute DeFi investments.
> 
> **Core Philosophy**: Data-driven decisions. No generic advice without real-time discovery.

---

## ⚠️ Critical Rules (MUST FOLLOW)

### Rule 1: Discovery First
**When user asks for investment advice:**
```
❌ WRONG: Give generic advice immediately (e.g., "I recommend Aave")
✅ CORRECT: 
   1. Collect investment preferences (chain, token, risk tolerance)
   2. Run discovery to get real-time data
   3. Analyze data
   4. Provide data-backed recommendations
```

### Rule 2: User's LLM Makes Decisions
- This skill provides **raw data only**
- Investment analysis and recommendations are the responsibility of the user's LLM/agent
- This skill is NOT responsible for investment outcomes

### Rule 3: Risk Acknowledgment
- APY data comes from third-party APIs and may be delayed or inaccurate
- Investment decisions are made at the user's own risk
- Always DYOR (Do Your Own Research)

### Rule 4: Verify Execution Capability Before Trading
**Before attempting any transaction, the agent MUST check signer availability:**
```
❌ WRONG: Directly call preview/execute without checking API
✅ CORRECT:
   1. Check if signer API is reachable (call balances endpoint)
   2. If unreachable → inform user: "Signer service unavailable, please check SETUP.md"
   3. Never proceed with preview if signer is unavailable
```

**Health Check Command**:
```bash
python3 scripts/trading/trade_executor.py balances --network base
# If success → signer is available
# If error E010 → signer unavailable, stop and inform user
```

### Rule 5: Check Payment Capability FIRST (NEW in v0.5.0)
**Before asking user for transaction details, ALWAYS check execution readiness:**
```
❌ WRONG: Ask "How much do you want to invest?" without checking payment capability
✅ CORRECT:
   1. Run: python3 scripts/trading/preflight.py check --network <chain>
   2. Inform user of available payment methods
   3. Then ask for transaction details
```

**Preflight Check Output**:
```json
{
  "recommended": "eip681_payment_link",
  "methods": [
    {"method": "keystore_signer", "status": "unavailable"},
    {"method": "eip681_payment_link", "status": "available"}
  ],
  "message": "⚠️ No local signer. Use EIP-681 payment link."
}
```

**Payment Method Flow**:
| Recommended Method | Action |
|-------------------|--------|
| `keystore_signer` | Use `preview → approve → execute` flow |
| `eip681_payment_link` | Generate EIP-681 link with `eip681_payment.py` |

---

## 🎯 Quick Start for Agents

### Step 1: Collect Investment Preferences (REQUIRED)

Before running discovery, ask the user:

| Preference | Key | Options | Why It Matters |
|------------|-----|---------|----------------|
| **Chain** | `chain` | ethereum, base, arbitrum, optimism | Determines which blockchain to search |
| **Capital Token** | `capital_token` | USDC, USDT, ETH, WBTC, etc. | The token they want to invest |
| **Reward Preference** | `reward_preference` | single / multi / any | Single token rewards vs multiple tokens |
| **Accept IL** | `accept_il` | true / false / any | Impermanent loss tolerance |
| **Underlying Type** | `underlying_preference` | rwa / onchain / mixed / any | Real-world assets vs on-chain |

### Step 2: Run Discovery

```bash
# Basic search
python3 scripts/discovery/find_opportunities.py \
  --chain ethereum \
  --min-apy 5 \
  --limit 20

# With LLM-ready output
python3 scripts/discovery/find_opportunities.py \
  --chain ethereum \
  --llm-ready \
  --output json
```

### Step 3: Filter by Preferences

```python
from scripts.discovery.investment_profile import InvestmentProfile

profile = InvestmentProfile()
profile.set_preferences(
    chain="ethereum",
    capital_token="USDC",
    accept_il=False,
    reward_preference="single"
)
filtered = profile.filter_opportunities(opportunities)
```

### Step 4: Execute Transaction (Choose Payment Method)

#### Option A: Keystore Signer (Production)
```bash
# Preview → Approve → Execute
python3 scripts/trading/trade_executor.py preview \
  --type deposit --protocol aave --asset USDC --amount 1000 --network base

python3 scripts/trading/trade_executor.py approve --preview-id <uuid>

python3 scripts/trading/trade_executor.py execute --approval-id <uuid>
```

#### Option B: EIP-681 Payment Link (Mobile)
```bash
python3 scripts/trading/eip681_payment.py generate \
  --token USDC --to 0x... --amount 10 --network base \
  --qr-output /tmp/payment_qr.png
```

---

## 📁 Project Structure

```
web3-investor/
├── scripts/
│   ├── discovery/           # Opportunity discovery tools
│   ├── trading/             # Transaction execution modules
│   └── portfolio/           # Balance queries
├── config/
│   ├── config.json          # Execution model & security settings
│   └── protocols.json       # Protocol registry
├── references/              # Detailed module documentation
│   ├── discovery.md
│   ├── investment-profile.md
│   ├── trade-executor.md
│   ├── portfolio-indexer.md
│   ├── protocols.md
│   └── risk-framework.md
└── SKILL.md
```

---

## 📚 Module Overview

| Module | Purpose | Details |
|--------|---------|---------|
| **Discovery** | Search DeFi yield opportunities | See [references/discovery.md](references/discovery.md) |
| **Investment Profile** | Preference collection & filtering | See [references/investment-profile.md](references/investment-profile.md) |
| **Trade Executor** | Transaction execution REST API | See [references/trade-executor.md](references/trade-executor.md) |
| **Portfolio Indexer** | On-chain balance queries | See [references/portfolio-indexer.md](references/portfolio-indexer.md) |

---

## 🔍 Discovery Data Sources

### Primary Data Sources

| Source | Type | Use Case |
|--------|------|----------|
| **MCP (AntAlpha)** | Real-time yields | Primary source for DeFi opportunities |
| **DefiLlama** | Protocol TVL/Yields | Fallback and cross-validation |
| **Dune** | On-chain analytics | Custom queries, advanced analysis |

### Dune MCP Integration

Dune provides powerful on-chain analytics through MCP (Model Context Protocol). Use Dune for:
- Custom on-chain data queries
- Protocol-specific analytics
- Historical trend analysis
- Whale wallet tracking

**Configuration** (`config/config.json`):
```json
{
  "discovery": {
    "data_sources": ["mcp", "dune", "defillama"],
    "dune": {
      "mcp_endpoint": "https://api.dune.com/mcp/v1",
      "auth": {
        "header": { "name": "x-dune-api-key", "env_var": "DUNE_API_KEY" },
        "query_param": { "name": "api_key", "env_var": "DUNE_API_KEY" }
      }
    }
  }
}
```

**Environment Setup**:
```bash
# Required for Dune integration
export DUNE_API_KEY="your_dune_api_key"
```

**Authentication Methods**:
1. **Header Auth** (Recommended): `x-dune-api-key: <DUNE_API_KEY>`
2. **Query Param**: `?api_key=<DUNE_API_KEY>`

**Usage Example**:
```bash
# Query Dune for protocol analytics
curl -H "x-dune-api-key: $DUNE_API_KEY" \
  "https://api.dune.com/mcp/v1/query/<query_id>/results"
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Optional: Alchemy for better RPC
ALCHEMY_API_KEY=your_key_here

# Optional: Debank for portfolio tracking
WEB3_INVESTOR_DEBANK_API_KEY=your_key_here

# Trade Executor: Local API endpoint
WEB3_INVESTOR_API_URL=http://localhost:3000/api
```

### Security Configuration (`config/config.json`)

```json
{
  "security": {
    "max_trade_usd": 10000,
    "max_slippage_percent": 3.0,
    "whitelist_enabled": false,
    "whitelist_tokens": ["USDC", "USDT", "DAI", "WETH", "ETH", "stETH", "rETH"],
    "whitelist_protocols": ["uniswap", "aave", "compound", "lido", "0x"],
    "double_confirm": {
      "enabled": true,
      "large_trade_threshold_usd": 5000
    }
  }
}
```

#### Whitelist Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `whitelist_enabled` | `false` | Enable/disable whitelist filtering in trade execution |
| `whitelist_tokens` | [...] | Allowed tokens for trading |
| `whitelist_protocols` | [...] | Allowed protocols for interaction |

**Note**: When `whitelist_enabled` is `false` (default), trade execution skips whitelist checks, allowing broader protocol/token access. Set to `true` to enforce strict whitelist validation.

### Whitelist Setup

```bash
python3 scripts/trading/whitelist.py \
  --add 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2 \
  --name "Aave V3 Pool" \
  --limit 10000
```

---

## 📝 Skill Author Template (MUST INCLUDE IN PROMPTS)

When using this skill for transaction generation, include this template:

```
Output structured transaction request (JSON), do not execute directly.
All transactions must go through preview -> approve -> execute.
If transaction parameters cannot be determined, return clarification, do not guess.
```

### Required Output Format

```json
{
  "request_id": "uuid",
  "timestamp": "ISO8601", 
  "network": "base|ethereum",
  "chain_id": 8453|1,
  "type": "transfer|swap|deposit|contract_call",
  "description": "human readable description",
  "transaction": {
    "to": "0x...",
    "value": "0x0",
    "data": "0x...",
    "gas_limit": 250000
  },
  "metadata": {
    "protocol": "uniswap|aave|compound|...",
    "from_token": "USDC",
    "to_token": "WETH", 
    "amount": "5"
  }
}
```

---

## 🆘 Troubleshooting

### Import Errors
Run from workspace root:
```bash
cd /home/admin/.openclaw/workspace
python3 skills/web3-investor/scripts/discovery/find_opportunities.py ...
```

### No Opportunities Found
- Check chain name spelling
- Try lowering `--min-apy` threshold
- Ensure `--max-apy` isn't too restrictive

### Rate Limiting
- DefiLlama has generous limits but can occasionally rate limit
- Add delays between requests if batch processing

---

## 🤝 Contributing

Test donations welcome:
- **Network**: Base Chain
- **Address**: `0x1F3A9A450428BbF161C4C33f10bd7AA1b2599a3e`

---

**Maintainer**: Web3 Investor Skill Team  
**Registry**: https://clawhub.com/skills/web3-investor  
**License**: MIT