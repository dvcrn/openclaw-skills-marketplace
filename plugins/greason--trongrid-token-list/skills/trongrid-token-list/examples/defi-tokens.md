# Example: DeFi Tokens on TRON

## User Prompt

```
Show me all the DeFi tokens on TRON — which ones are trending?
```

## Expected Workflow

1. **Web Search** → Search "TRON DeFi tokens trending 2026" → Identify DeFi projects
2. **Token Info** → `getTrc20Info(contractList)` → Metadata for each DeFi token
3. **Holders** → `getTrc20TokenHolders(address)` × each → Distribution data
4. **Events** → `getEventsByContractAddress(address, limit=50)` × top 3 → Recent activity
5. **Contract Info** → `getContractInfo(address)` × each → Deployment and settings

## Expected Output (Sample)

```
## DeFi Tokens on TRON

TRON's DeFi ecosystem is anchored by the SUN.io platform, with multiple
governance and utility tokens supporting DEX, lending, and stablecoin protocols.

### DeFi Token Rankings

| Token    | Symbol | Price   | Market Cap | TVL/Usage        | Category    |
|----------|--------|---------|-----------|-----------------|-------------|
| SUN      | SUN    | $0.025  | $480M     | SunSwap TVL $2B | Governance  |
| JUST     | JST    | $0.038  | $360M     | JustLend TVL $5B| Lending     |
| WINkLink | WIN    | $0.0001 | $95M      | Oracle feeds    | Oracle      |
| USDJ     | USDJ   | $1.00   | $180M     | JustStable mint | Stablecoin  |

### Trending DeFi Activity
- **SUN**: Governance vote active — staking APY increased to 12%
- **JST**: JustLend TVL growing, new collateral types added
- **WINkLink**: New price feed integrations with 3 protocols

### DeFi Protocol Comparison
| Protocol   | TVL     | Daily Txs | Active Users (est.) |
|-----------|---------|-----------|-------------------|
| SunSwap V2 | $2.1B  | ~15,000   | ~5,000            |
| JustLend  | $5.2B   | ~8,000    | ~2,500            |
| SUN.io    | $800M   | ~4,000    | ~1,200            |
```

## MCP Tools Used

| Tool | Call Count | Purpose |
|------|-----------|---------|
| `getTrc20Info` | 1 | Token metadata (batch) |
| `getTrc20TokenHolders` | 4 | Holder distribution |
| `getEventsByContractAddress` | 3 | Activity analysis |
| `getContractInfo` | 4 | Contract details |
