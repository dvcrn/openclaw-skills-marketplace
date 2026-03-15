# Sell Execution (XAUT → USDT)

## 0. Pre-execution Declaration

- Current stage must be `Ready to Execute`
- Quote and explicit user confirmation must already be complete
- Full command must be displayed before execution

## 1. Input Validation

User provides XAUT amount (e.g. `0.01`); convert to on-chain integer:

```bash
AMOUNT_IN=$(echo "0.01 * 1000000" | bc | xargs printf "%.0f")
# 0.01 XAUT → 10000
```

**Precision check**: if the input has more than 6 decimal places (e.g. `0.0000001`), hard-stop:

> XAUT supports a maximum of 6 decimal places. The minimum tradeable unit is 0.000001 XAUT. Please adjust the input amount.

## 2. Quote (QuoterV2)

```bash
QUOTE_RAW=$(cast call "$QUOTER" \
  "quoteExactInputSingle((address,address,uint256,uint24,uint160))" \
  "($XAUT,$USDT,$AMOUNT_IN,$FEE,0)" \
  --rpc-url "$ETH_RPC_URL")
```

Parse return value:

```bash
AMOUNT_OUT=$(cast abi-decode \
  "f()(uint256,uint160,uint32,uint256)" \
  "$QUOTE_RAW" | head -1 | awk '{print $1}')
# USDT has 6 decimals: human-readable = AMOUNT_OUT / 1_000_000
```

Calculate `minAmountOut` (default slippage 50 bps):

```bash
# Use python3 to avoid bash integer overflow on large trades
MIN_AMOUNT_OUT=$(python3 -c \
  "print(int($AMOUNT_OUT * (10000 - $DEFAULT_SLIPPAGE_BPS) // 10000))")
```

Reference rate (for Preview display; both tokens have 6 decimals so divide directly):

```
Reference rate = amountOut / AMOUNT_IN  (USDT/XAUT, human-readable)
```

## 3. Preview Output

Must include at minimum:

- Input amount (user-provided form + on-chain unit)
- Estimated USDT received (`amountOut`, human-readable)
- Reference rate: `1 XAUT ≈ X USDT`
- Slippage setting and `minAmountOut`
- Risk indicators (large trade / slippage / gas)

**Large-trade check**: convert `amountOut` (USDT) to USD value; if it exceeds `risk.large_trade_usd`, require double confirmation.

## 4. Explicit Confirmation Gate

Do not execute any `cast send` unless the user has explicitly confirmed.

Accepted confirmation phrases:
- "confirm approve"
- "confirm swap"

## 5. allowance Check

```bash
cast call "$XAUT" "allowance(address,address)" "$WALLET_ADDRESS" "$ROUTER" --rpc-url "$ETH_RPC_URL"
```

If allowance < `AMOUNT_IN`, approve first.

## 6. approve (XAUT is standard ERC-20)

**XAUT does not require a prior reset** — approve directly:

```bash
TX_HASH=$(cast send "$XAUT" "approve(address,uint256)" "$ROUTER" "$AMOUNT_IN" \
  --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE" \
  --rpc-url "$ETH_RPC_URL" --json | python3 -c "import sys,json; print(json.load(sys.stdin)['transactionHash'])")
echo "Approve tx: https://etherscan.io/tx/$TX_HASH"
```

> ⚠️ Note: Unlike USDT, XAUT does not require `approve(0)` to reset before approving.

## 7. Swap Execution

Calculate `deadline` and encode `exactInputSingle`:

```bash
# DEADLINE_SECONDS from risk.deadline_seconds in config.yaml
DEADLINE=$(cast --to-uint256 $(($(date +%s) + $DEADLINE_SECONDS)))

SWAP_DATA=$(cast calldata \
  "exactInputSingle((address,address,uint24,address,uint256,uint256,uint160))" \
  "($XAUT,$USDT,$FEE,$WALLET_ADDRESS,$AMOUNT_IN,$MIN_AMOUNT_OUT,0)")
```

Dry-run before execution (hard-stop on failure — no gas consumed):

```bash
cast call "$ROUTER" \
  "multicall(uint256,bytes[])" \
  "$DEADLINE" "[$SWAP_DATA]" \
  --from "$WALLET_ADDRESS" \
  --rpc-url "$ETH_RPC_URL"
# On network/policy errors (timeout/429/-32603/403 whitelist), retry dry-run on fallback read RPCs.
# Hard-stop only if all read-capable RPCs fail, or if revert/invalid-params persists.
```

Execute multicall:

```bash
TX_HASH=$(cast send "$ROUTER" "multicall(uint256,bytes[])" "$DEADLINE" "[$SWAP_DATA]" \
  --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE" \
  --rpc-url "$ETH_RPC_URL" --json | python3 -c "import sys,json; print(json.load(sys.stdin)['transactionHash'])")
echo "Swap tx: https://etherscan.io/tx/$TX_HASH"
# Balance may take a few seconds to update; Etherscan is authoritative
```

## 8. Result Verification

Pre-swap snapshot (fetch before executing swap):

```bash
cast call "$XAUT" "balanceOf(address)" "$WALLET_ADDRESS" --rpc-url "$ETH_RPC_URL"
```

Post-swap USDT balance:

```bash
cast call "$USDT" "balanceOf(address)" "$WALLET_ADDRESS" --rpc-url "$ETH_RPC_URL"
```

Return:
- tx hash
- XAUT balance before and after (comparison)
- post-trade USDT balance
- on failure, return retry suggestions (reduce sell amount / increase slippage tolerance / check nonce and gas)

## 9. Mandatory Rules

- Before every `cast send`, remind the user: "About to execute an on-chain write"
- Trade execution confirmation follows:
  - `< risk.confirm_trade_usd`: show full preview, then execute without blocking confirmation
  - `>= risk.confirm_trade_usd` and `< risk.large_trade_usd`: single confirmation
  - `>= risk.large_trade_usd` or estimated slippage exceeds `risk.max_slippage_bps_warn`: double confirmation
- Approval confirmation follows `risk.approve_confirmation_mode` with force override:
  - If approve amount `> risk.approve_force_confirm_multiple * AMOUNT_IN`, require explicit approval confirmation
- Hard-stop if input precision exceeds 6 decimal places
