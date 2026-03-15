# Limit Order Query

## 1. Query a Single Order (by orderHash)

```bash
RESULT=$(node skills/xaut-trade/scripts/limit-order.js status \
  --order-hash "$ORDER_HASH" \
  --chain-id   1 \
  --api-url    "$UNISWAPX_API")

STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
```

## 2. List All Open Orders (by wallet address)

```bash
RESULT=$(node skills/xaut-trade/scripts/limit-order.js list \
  --wallet       "$WALLET_ADDRESS" \
  --chain-id     1 \
  --api-url      "$UNISWAPX_API" \
  --order-status open)   # Optional: open / filled / expired / cancelled — omit to return all
```

Returns JSON: `{ total, orders: [{ orderHash, status, inputToken, inputAmount, outputToken, outputAmount, txHash, createdAt }] }`

## 3. Status Display

| status | Display |
|--------|---------|
| `open` | Order active; remaining time = deadline - current time |
| `filled` | Filled: show txHash and actual settled amounts (settledAmounts) |
| `expired` | Expired; can re-place the order |
| `cancelled` | Cancelled |
| `not_found` | orderHash does not exist or has been purged from the API (may be cleared after expiry) |

## 3. Error Handling

- API unreachable: prompt to check network, suggest retrying later
- `not_found`: suggest the orderHash may be wrong, or the order has expired and been purged
