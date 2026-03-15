---
name: nostrsocial
description: "Social graph manager — contacts, trust tiers, and identity verification over Nostr"
---

# NostrSocial — Social Graph for AI Agents

Give your AI agent the ability to manage contacts, enforce trust tiers, and track identity verification — all anchored to Nostr npub identity.

## Install

```bash
pip install nostrsocial
```

## Core Capabilities

### 1. Manage Contacts

Add contacts to friends, block, or gray lists with capacity enforcement.

```python
from nostrsocial import SocialEnclave, Tier

enclave = SocialEnclave.create()
enclave.add("alice@example.com", "email", Tier.CLOSE, display_name="Alice")
enclave.block("spam@bad.com", "email")
enclave.gray("meh@example.com", "email")
```

### 2. Query Behavioral Rules

Get tier-based behavioral parameters for any contact.

```python
rules = enclave.get_behavior("alice@example.com", "email")
# rules.token_budget, rules.warmth, rules.can_interrupt, etc.

# Unknown contacts get neutral behavior
rules = enclave.get_behavior("stranger@example.com", "email")
# warmth=0.5, token_budget=500
```

### 3. Identity Verification

Track identity state from proxy to claimed to verified.

```python
# See who needs verification
for contact in enclave.get_upgradeable():
    print(f"{contact.display_name}: {contact.upgrade_hint}")

# Create a challenge for a claimed npub
challenge = enclave.create_challenge("npub1alice...")
```

### 4. Persistence

Save and load the social graph.

```python
from nostrsocial import FileStorage

storage = FileStorage("~/.agent/social.json")
enclave = SocialEnclave.create(storage)
enclave.add("alice@example.com", "email", Tier.CLOSE)
enclave.save()

# Later
enclave = SocialEnclave.load(storage)
```

## When to Use Each Module

| Task | Module | Function |
|------|--------|----------|
| Add/remove contacts | `enclave` | `SocialEnclave.add`, `block`, `gray`, `remove` |
| Change trust tier | `enclave` | `promote`, `demote` |
| Get behavioral rules | `enclave` / `behavior` | `get_behavior` |
| Check remaining slots | `enclave` | `slots_remaining` |
| Find unverified contacts | `enclave` | `get_unverified_contacts`, `get_upgradeable` |
| Create verification challenge | `enclave` / `verify` | `create_challenge` |
| Derive proxy npub | `proxy` | `derive_proxy_npub` |
| Decay stale contacts | `enclave` | `decay` |
| Persist social graph | `enclave` | `save` / `load` |

## Important Notes

- Friends list is capped at 150 (Dunbar's number): 5 intimate + 15 close + 50 familiar + 80 known
- Block list holds 50. Gray list holds 100 with auto-decay.
- Proxy npubs are deterministic — same identifier always maps to same npub
- Identity state: proxy → claimed → verified. Verified contacts get warmer behavior.
- Challenge verification requires relay interaction — stub only in 0.1.0
- Depends on `nostrkey` for npub derivation
