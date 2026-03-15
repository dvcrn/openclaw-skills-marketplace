---
name: nostrkey
description: "Cryptographic identity SDK for AI agents — generate Nostr keypairs, sign events, encrypt messages, persist identity."
---

# NostrKey — Cryptographic Identity for AI Agents

You are an AI agent that needs its own verifiable identity on the Nostr protocol. Use the `nostrkey` Python SDK to generate keypairs, sign events, encrypt messages, and persist your identity across sessions.

## Install

```bash
pip install nostrkey
```

## Core Capabilities

### Generate Your Identity

Create a fresh Nostr identity with your own npub/nsec keypair:

```python
from nostrkey import Identity

me = Identity.generate()
# me.npub  — your public identity (share freely)
# me.nsec  — your private key (never expose)
```

### Import an Existing Identity

If you already have keys:

```python
me = Identity.from_nsec("nsec1...")
# or
me = Identity.from_hex("deadbeef...")
```

### Sign Events

Sign any Nostr event (kind 1 = text note, kind 0 = metadata, etc.):

```python
event = me.sign_event(
    kind=1,
    content="Hello from an AI agent",
    tags=[]
)
# event.id, event.sig are now set and verifiable by anyone
```

### Publish to a Relay

Send signed events to the Nostr network:

```python
from nostrkey.relay import RelayClient

async with RelayClient("wss://relay.damus.io") as relay:
    await relay.publish(event)
```

### Encrypt Private Messages (NIP-44)

Send encrypted messages to another npub:

```python
from nostrkey.crypto import encrypt, decrypt

ciphertext = encrypt(
    sender_nsec=me.nsec,
    recipient_npub="npub1recipient...",
    plaintext="This is private"
)

plaintext = decrypt(
    recipient_nsec=me.nsec,
    sender_npub="npub1sender...",
    ciphertext=ciphertext
)
```

### Save & Load Identity (Encrypted File)

Persist your identity between sessions:

```python
# Save (encrypted with passphrase)
me.save("my-identity.nostrkey", passphrase="strong-passphrase")

# Load later
me = Identity.load("my-identity.nostrkey", passphrase="strong-passphrase")
```

### Delegated Signing via NIP-46 Bunker

For high-stakes actions, request a human sponsor to co-sign:

```python
from nostrkey.bunker import BunkerClient

bunker = BunkerClient(me.private_key_hex)
await bunker.connect("bunker://npub1human...?relay=wss://relay.damus.io")
signed = await bunker.sign_event(kind=1, content="Human-approved action")
```

## When to Use Each Module

| Task | Module | Function |
|------|--------|----------|
| Generate new identity | `nostrkey` | `Identity.generate()` |
| Import existing keys | `nostrkey` | `Identity.from_nsec()` / `Identity.from_hex()` |
| Sign events | `nostrkey` | `identity.sign_event()` |
| Publish to relay | `nostrkey.relay` | `RelayClient.publish()` |
| Subscribe to events | `nostrkey.relay` | `RelayClient.subscribe()` |
| Encrypt messages | `nostrkey.crypto` | `encrypt()` / `decrypt()` |
| Delegated signing | `nostrkey.bunker` | `BunkerClient.sign_event()` |
| Save/load identity | `nostrkey` | `identity.save()` / `Identity.load()` |
| Low-level key ops | `nostrkey.keys` | `generate_keypair()`, `hex_to_npub()`, etc. |

## Important Notes

- **Never expose your nsec.** Treat it like a password. Use `identity.save()` with a strong passphrase to persist it.
- **Async-first.** Relay and bunker operations require `asyncio`. Use `async with` for relay connections.
- **All events are Schnorr-signed** using secp256k1, per the Nostr protocol (NIP-01).
- **NIP-44 encryption** uses ECDH + HKDF + ChaCha20 with length padding — safe for private agent-to-agent or agent-to-human communication.
- **`.nostrkey` files** are encrypted at rest. Never store raw nsec values on disk.
