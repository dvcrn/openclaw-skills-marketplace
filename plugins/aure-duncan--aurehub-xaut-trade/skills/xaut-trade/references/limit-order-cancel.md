# Limit Order Cancellation

## 0. Pre-confirmation

Cancelling a limit order is an on-chain operation (gas required). Confirm before cancelling:
- orderHash
- Current order status (recommended: query first to avoid cancelling an already-filled or expired order)

## 1. Fetch Cancellation Parameters

```bash
CANCEL_PARAMS=$(node skills/xaut-trade/scripts/limit-order.js cancel \
  --nonce "$NONCE")

WORD_POS=$(echo "$CANCEL_PARAMS" | python3 -c "import sys,json; print(json.load(sys.stdin)['wordPos'])")
MASK=$(echo "$CANCEL_PARAMS"     | python3 -c "import sys,json; print(json.load(sys.stdin)['mask'])")
PERMIT2=$(echo "$CANCEL_PARAMS"  | python3 -c "import sys,json; print(json.load(sys.stdin)['permit2'])")
```

## 2. Execute Cancellation

Display the command and wait for user confirmation:

```bash
TX_HASH=$(cast send "$PERMIT2" \
  "invalidateUnorderedNonces(uint256,uint256)" \
  "$WORD_POS" "$MASK" \
  --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE" \
  --rpc-url "$ETH_RPC_URL" --json | python3 -c "import sys,json; print(json.load(sys.stdin)['transactionHash'])")
echo "Cancel tx: https://etherscan.io/tx/$TX_HASH"
```

## 3. Output

- tx hash
- Note: No assets were locked — Permit2 uses signature-based authorization, not asset custody. Cancellation revokes the signature on-chain; no token return operation is needed.

## 4. Special Cases

| Case | Action |
|------|--------|
| Order already filled | No cancellation needed; inform the user |
| Order already expired | Nonce has auto-invalidated; no on-chain cancellation needed |
| Cancel succeeds but Filler is still processing | Very low probability; the Filler transaction will revert once the nonce is invalidated on-chain |
