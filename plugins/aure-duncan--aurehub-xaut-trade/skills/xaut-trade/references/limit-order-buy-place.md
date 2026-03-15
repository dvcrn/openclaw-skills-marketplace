# Limit Order Placement (USDT → XAUT via UniswapX)

## 0. Pre-execution Declaration

- Current stage must be `Ready to Execute`
- Parameters must be confirmed and user must have explicitly confirmed
- Full command must be displayed before execution

## 1. Pre-flight Checks

```bash
node --version     # If not found, hard-stop and prompt to install https://nodejs.org (market orders unaffected)
cast --version
cast block-number --rpc-url "$ETH_RPC_URL"
# ETH balance check (same as balance.md)
# tokenIn (USDT) balance check
```

## 2. Parameter Confirmation (Preview)

Display at minimum:
- Pair: USDT → XAUT
- Limit price: `1 XAUT = X USDT` (i.e. amountIn / minAmountOut, human-readable)
- Amount: `amountIn` USDT → at least `minAmountOut` XAUT
- Expiry: `expiry` seconds / deadline in local time
- UniswapX Filler risk notice: XAUT is a low-liquidity token; if no Filler fills the order, it expires automatically after the deadline with no loss of funds

## 3. Large-Trade Double Confirmation

If amountIn (USDT converted to USD) > `risk.large_trade_usd`, double confirmation is required.

## 4. Approve Permit2 (if allowance is insufficient)

Check USDT allowance for Permit2:

```bash
cast call "$USDT" "allowance(address,address)" \
  "$WALLET_ADDRESS" "$PERMIT2" \
  --rpc-url "$ETH_RPC_URL"
```

If insufficient, approve (USDT requires reset then approve):

```bash
# Reset
cast send "$USDT" "approve(address,uint256)" "$PERMIT2" 0 \
  --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE" \
  --rpc-url "$ETH_RPC_URL"

# Approve
cast send "$USDT" "approve(address,uint256)" "$PERMIT2" "$AMOUNT_IN" \
  --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE" \
  --rpc-url "$ETH_RPC_URL"
```

## 5. Place Order

```bash
# EXPIRY_SECONDS: use the user-specified expiry, or fall back to
# limit_order.default_expiry_seconds in config.yaml (default: 86400 = 1 day).
# The script uses the provided value directly (no min/max clamping in code).
RESULT=$(node skills/xaut-trade/scripts/limit-order.js place \
  --token-in       "$USDT" \
  --token-out      "$XAUT" \
  --amount-in      "$AMOUNT_IN" \
  --min-amount-out "$MIN_AMOUNT_OUT" \
  --expiry         "$EXPIRY_SECONDS" \
  --wallet         "$WALLET_ADDRESS" \
  --chain-id       1 \
  --api-url        "$UNISWAPX_API")
```

Parse result:

```bash
ORDER_HASH=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['orderHash'])")
DEADLINE=$(echo "$RESULT"   | python3 -c "import sys,json; print(json.load(sys.stdin)['deadline'])")
NONCE=$(echo "$RESULT"      | python3 -c "import sys,json; print(json.load(sys.stdin)['nonce'])")
```

## 6. Output

Return to user:
- `orderHash`: for querying / cancelling the order
- `deadline`: order expiry in local time
- nonce (needed for cancellation)
- Reminder: order has been submitted to UniswapX; the computer does not need to stay online — the Filler network fills automatically when the price is reached

## 7. Error Handling

| Error | Action |
|-------|--------|
| `node` not found | Hard-stop, prompt to install, note market orders are unaffected |
| UniswapX API returns 4xx | Hard-stop, note XAUT may not be in the supported list, suggest market order |
| Limit price deviates > 50% from current market | Warn + double confirmation (prevent price typos) |
| Approve failed | Return failure reason, suggest retry |
