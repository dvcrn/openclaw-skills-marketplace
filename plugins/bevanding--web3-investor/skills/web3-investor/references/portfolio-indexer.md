# Portfolio Indexer Module

> **Purpose**: Query on-chain balances for specified addresses.

---

## What It Does

Queries on-chain balances for specified addresses.

## Supported Chains

- Ethereum mainnet
- Base
- Arbitrum (partial)

## Usage

```bash
# Query portfolio
python3 scripts/portfolio/indexer.py \
  --address 0x... \
  --chain ethereum \
  --output json
```

## Output Format

### JSON Output

```json
{
  "address": "0x...",
  "chain": "ethereum",
  "timestamp": "2026-03-05T15:00:00Z",
  "balances": [
    {
      "token": "USDC",
      "symbol": "USDC",
      "balance": "1000.50",
      "balance_usd": 1000.50,
      "contract": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    },
    {
      "token": "WETH",
      "symbol": "WETH",
      "balance": "0.5",
      "balance_usd": 1500.00,
      "contract": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    }
  ],
  "total_usd": 2500.50
}
```

## Environment Variables

```bash
# Optional: Alchemy for better RPC
ALCHEMY_API_KEY=your_key_here

# Optional: Debank for portfolio tracking
WEB3_INVESTOR_DEBANK_API_KEY=your_key_here
```

## Troubleshooting

### No Balances Found
- Verify the address is correct
- Check if the chain is supported
- Ensure RPC endpoint is accessible

### Slow Response
- Alchemy API provides faster responses than public RPC
- Debank API provides aggregated portfolio data across chains