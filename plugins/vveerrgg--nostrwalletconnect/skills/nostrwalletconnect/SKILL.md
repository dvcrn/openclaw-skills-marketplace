---
name: nostrwalletconnect
description: "Nostr Wallet Connect (NIP-47) SDK for AI agents — pay Lightning invoices, check balance, create invoices via any NWC-compatible wallet."
---

# NostrWalletConnect — Lightning Wallet Access for AI Agents

You are an AI agent that needs to send and receive Lightning payments. Use the `nostrwalletconnect` Python SDK to connect to any NWC-compatible wallet and pay invoices, check your balance, create invoices, and list transactions — all over the Nostr protocol.

## Install

```bash
pip install nostrwalletconnect
```

This also installs `nostrkey` (the Nostr identity SDK) as a dependency.

## Prerequisites

You need an **NWC connection string** from a wallet that supports NIP-47. This looks like:

```
nostr+walletconnect://<wallet_pubkey>?relay=wss://...&secret=<hex_secret>
```

Compatible wallets include Alby, Mutiny, Coinos, and others that support NWC.

## Core Capabilities

### Connect to a Wallet

```python
from nostrwalletconnect import NWCClient

async with NWCClient("nostr+walletconnect://...") as nwc:
    balance = await nwc.get_balance()
    print(f"Balance: {balance.balance} msats")
```

### Pay a Lightning Invoice

```python
async with NWCClient(connection_string) as nwc:
    result = await nwc.pay_invoice("lnbc10u1p...")
    print(f"Paid! Preimage: {result.preimage}")
```

### Create a Lightning Invoice

```python
async with NWCClient(connection_string) as nwc:
    invoice = await nwc.make_invoice(
        amount=50_000,  # millisatoshis
        description="Payment for AI service"
    )
    print(f"Invoice: {invoice.invoice}")
    print(f"Payment hash: {invoice.payment_hash}")
```

### Check Invoice Status

```python
async with NWCClient(connection_string) as nwc:
    status = await nwc.lookup_invoice(payment_hash="abc123...")
    print(f"Paid: {status.paid}")
```

### List Transactions

```python
async with NWCClient(connection_string) as nwc:
    history = await nwc.list_transactions(limit=10)
    for tx in history.transactions:
        print(f"{tx.type}: {tx.amount} msats")
```

### Get Wallet Info

```python
async with NWCClient(connection_string) as nwc:
    info = await nwc.get_info()
    print(f"Wallet: {info.alias}")
    print(f"Methods: {info.methods}")
```

## When to Use Each Method

| Task | Method | Returns |
|------|--------|---------|
| Check wallet balance | `get_balance()` | `BalanceResponse` (millisatoshis) |
| Pay a Lightning invoice | `pay_invoice(bolt11)` | `PayResponse` (preimage) |
| Create an invoice to receive | `make_invoice(amount, desc)` | `MakeInvoiceResponse` (bolt11 + hash) |
| Check if an invoice was paid | `lookup_invoice(hash)` | `LookupInvoiceResponse` (paid status) |
| View transaction history | `list_transactions()` | `ListTransactionsResponse` |
| Check wallet capabilities | `get_info()` | `GetInfoResponse` (alias, methods) |

## Important Notes

- **Never expose the NWC connection string.** It contains the secret key that authorizes payments. Treat it like a password.
- **Async-first.** All client methods are async. Use `async with` for the connection.
- **All communication is encrypted.** Requests and responses use NIP-44 encryption over Nostr relays. The relay operator cannot read payment details.
- **Amounts are in millisatoshis.** 1 sat = 1000 msats. Divide by 1000 for sats.
- **Timeout is configurable.** Default is 30 seconds. Pass `timeout=60` to the client constructor for slower wallets.
- **Depends on nostrkey.** The `nostrkey` package handles all cryptographic operations (signing, encryption, relay communication).
