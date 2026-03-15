# Quote & Slippage Protection

## 1. Fetch Quote (QuoterV2)

Example: 100 USDT (6 decimals)

```bash
AMOUNT_IN=100000000
QUOTE_RAW=$(cast call "$QUOTER" \
  "quoteExactInputSingle((address,address,uint256,uint24,uint160))" \
  "($USDT,$XAUT,$AMOUNT_IN,$FEE,0)" \
  --rpc-url "$ETH_RPC_URL")
```

Parse the return value (QuoterV2 returns a tuple: amountOut, sqrtPriceX96After, initializedTicksCrossed, gasEstimate):

```bash
# Use cast abi-decode to parse — avoids fragile manual hex slicing
AMOUNT_OUT=$(cast abi-decode \
  "f()(uint256,uint160,uint32,uint256)" \
  "$QUOTE_RAW" | head -1)

# XAUT has 6 decimals: human-readable = AMOUNT_OUT / 1_000_000
# USDT also has 6 decimals; sell direction works the same way
```

## 2. Calculate minAmountOut

Default slippage `default_slippage_bps` (e.g. 50 bps = 0.5%):

```bash
# Use python3 to avoid bash integer overflow on large trades
MIN_AMOUNT_OUT=$(python3 -c \
  "print(int($AMOUNT_OUT * (10000 - $DEFAULT_SLIPPAGE_BPS) // 10000))")
```

## 3. Preview Output

Must include at minimum:
- Input amount (human-readable and raw unit)
- Estimated XAUT received (`amountOut`)
- Slippage setting and `minAmountOut`
- Risk indicators (large trade / slippage / gas)

## 4. Execution Confirmation Gate

Determine confirmation level by USD notional and risk:

- `< risk.confirm_trade_usd`: show full preview, then execute without blocking confirmation
- `>= risk.confirm_trade_usd` and `< risk.large_trade_usd`: single confirmation
- `>= risk.large_trade_usd` or estimated slippage exceeds `risk.max_slippage_bps_warn`: double confirmation

Accepted confirmation phrases:
- "confirm approve"
- "confirm swap"
