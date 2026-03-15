# Example: Top TRON Tokens

## User Prompt

```
What are the top tokens on TRON?
```

## Expected Workflow

1. **Web Search** → Search "top TRC-20 tokens TRON market cap 2026" → Market rankings
2. **Token Info** → `getTrc20Info("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t,TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8,...")` → On-chain metadata
3. **Holders** → `getTrc20TokenHolders(address, limit=5)` × top tokens → Holder counts
4. **TRC-10 Assets** → `listAllAssets(limit=10)` → Top TRC-10 tokens
5. **Contract Activity** → `getContractTransactions(address, limit=20)` × top tokens → Activity levels

## Expected Output (Sample)

```
## TRON Token List

### Top TRC-20 Tokens by Market Cap

| Rank | Token       | Symbol | Price   | 24h Change | Market Cap | Holders     |
|------|-------------|--------|---------|-----------|------------|-------------|
| 1    | Tether      | USDT   | $1.00   | +0.01%    | $62.5B     | 48,500,000  |
| 2    | USD Coin    | USDC   | $1.00   | -0.02%    | $3.2B      | 1,200,000   |
| 3    | BitTorrent  | BTT    | $0.0012 | +3.5%     | $1.1B      | 3,800,000   |
| 4    | SUN         | SUN    | $0.025  | +1.2%     | $480M      | 520,000     |
| 5    | JUST        | JST    | $0.038  | -0.8%     | $360M      | 310,000     |
| 6    | WINkLink    | WIN    | $0.0001 | +0.5%     | $95M       | 890,000     |
| 7    | APENFT      | NFT    | $0.0000005 | -1.2%  | $50M       | 2,100,000   |

### Most Active (by Transaction Count, 24h)
| Token | Symbol | Est. 24h Transactions | Unique Addresses |
|-------|--------|----------------------|-----------------|
| USDT  | USDT   | ~800,000             | ~120,000        |
| USDC  | USDC   | ~45,000              | ~8,000          |
| SUN   | SUN    | ~12,000              | ~3,500          |

### TRC-10 Tokens (Top by Supply)
| Token     | ID      | Total Supply       | Precision |
|-----------|---------|--------------------|-----------|
| BitTorrent| 1002000 | 990,000,000,000,000| 6         |
| APENFT    | 1002508 | 999,990,000,000,000| 6         |
```

## MCP Tools Used

| Tool | Call Count | Purpose |
|------|-----------|---------|
| `getTrc20Info` | 1 | Token metadata (batch) |
| `getTrc20TokenHolders` | 5-7 | Holder counts |
| `listAllAssets` | 1 | TRC-10 token list |
| `getContractTransactions` | 5-7 | Activity levels |
