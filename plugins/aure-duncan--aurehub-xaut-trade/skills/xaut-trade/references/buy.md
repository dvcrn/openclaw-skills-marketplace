# Buy Execution (USDT → XAUT)

## 0. Pre-execution Declaration

- Current stage must be `Ready to Execute`
- Quote and explicit user confirmation must already be complete
- Full command must be displayed before execution

## 1. allowance Check

```bash
cast call "$TOKEN_IN" "allowance(address,address)" "$WALLET_ADDRESS" "$ROUTER" --rpc-url "$ETH_RPC_URL"
```

If allowance < `AMOUNT_IN`, approve first.

## 2. approve (per token)

USDT (non-standard — `token_rules.USDT.requires_reset_approve: true` in config — must reset to zero before approving):

```bash
TX_HASH=$(cast send "$USDT" "approve(address,uint256)" "$ROUTER" 0 \
  --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE" \
  --rpc-url "$ETH_RPC_URL" --json | python3 -c "import sys,json; print(json.load(sys.stdin)['transactionHash'])")
echo "Approve(0) tx: https://etherscan.io/tx/$TX_HASH"
```

```bash
TX_HASH=$(cast send "$USDT" "approve(address,uint256)" "$ROUTER" "$AMOUNT_IN" \
  --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE" \
  --rpc-url "$ETH_RPC_URL" --json | python3 -c "import sys,json; print(json.load(sys.stdin)['transactionHash'])")
echo "Approve tx: https://etherscan.io/tx/$TX_HASH"
```

## 3. Swap Execution

Calculate `deadline` and encode `exactInputSingle`:

```bash
# DEADLINE_SECONDS from risk.deadline_seconds in config.yaml
DEADLINE=$(cast --to-uint256 $(($(date +%s) + $DEADLINE_SECONDS)))

SWAP_DATA=$(cast calldata \
  "exactInputSingle((address,address,uint24,address,uint256,uint256,uint160))" \
  "($TOKEN_IN,$XAUT,$FEE,$WALLET_ADDRESS,$AMOUNT_IN,$MIN_AMOUNT_OUT,0)")
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

## 4. Result Verification

```bash
cast call "$XAUT" "balanceOf(address)" "$WALLET_ADDRESS" --rpc-url "$ETH_RPC_URL"
```

Return:
- tx hash
- post-trade XAUT balance
- on failure, return retry suggestions

## 5. Mandatory Rules

- Before every `cast send`, remind the user: "About to execute an on-chain write"
- Trade execution confirmation follows:
  - `< risk.confirm_trade_usd`: show full preview, then execute without blocking confirmation
  - `>= risk.confirm_trade_usd` and `< risk.large_trade_usd`: single confirmation
  - `>= risk.large_trade_usd` or estimated slippage exceeds `risk.max_slippage_bps_warn`: double confirmation
- Approval confirmation follows `risk.approve_confirmation_mode` with force override:
  - If approve amount `> risk.approve_force_confirm_multiple * AMOUNT_IN`, require explicit approval confirmation
