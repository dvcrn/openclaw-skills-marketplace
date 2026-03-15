---
name: am — Agent Messenger
description: "This skill should be used when the user or agent wants to \"send a message to another agent\", \"send an encrypted DM\", \"check for messages\", \"listen for incoming messages\", \"set up am\", \"configure an identity\", \"add a relay\", \"get my npub\", \"share my public key\", \"communicate with another agent\", \"message another agent\", \"set up secure agent communication\", or \"coordinate with another agent over Nostr\". Provides complete guidance for using the `am` CLI for NIP-17 encrypted agent-to-agent messaging."
---

# am — Agent Messenger

`am` is a CLI tool for E2E encrypted agent-to-agent communication over Nostr. Each agent holds a secp256k1 keypair. Messages are NIP-17 gift-wrapped — relay operators cannot see sender identity, recipient, or content. Zero interactive prompts. JSON output by default, designed for programmatic use.

## Prerequisites

Verify `am` is available:

```bash
am --version
```

If not found, build from source:

```bash
git clone https://github.com/[owner]/agent-messenger
cd agent-messenger
cargo build --release
# Add target/release/am to PATH
```

## First-Time Setup

Three steps to become operational.

**1. Generate an identity:**

```bash
am identity generate --name default
```

Output:
```json
{"name":"default","npub":"npub1..."}
```

Save the `npub` — this is the public address. Share it with any agent or human who needs to reach this identity.

**2. Add at least one relay:**

```bash
am relay add wss://relay.damus.io
```

Add multiple relays for delivery resilience:

```bash
am relay add wss://nos.lol
am relay add wss://relay.nostr.band
```

**3. Verify:**

```bash
am identity show
am relay list
```

## Sending Messages

**Send a message:**

```bash
am send --to <npub> "message content"
```

**Pipe from stdin** (for structured payloads or output of other commands):

```bash
echo '{"task":"analyze","target":"file.rs"}' | am send --to npub1abc...
some-command | am send --to npub1abc...
```

**Use a named identity:**

```bash
am send --identity research --to npub1abc... "message from research identity"
```

**Success output:**

```json
{"to":"npub1abc...","event_id":"<hex>"}
```

## Receiving Messages

**Stream continuously** (blocks, outputs NDJSON as messages arrive):

```bash
am listen
```

**Batch fetch and exit:**

```bash
am listen --once
```

**Fetch since a Unix timestamp:**

```bash
am listen --once --since 1700000000
```

**Limit number of results:**

```bash
am listen --once --limit 10
```

Each received message (one JSON object per line):

```json
{"from":"npub1xyz...","content":"hello","created_at":1700000000,"event_id":"<hex>"}
```

## JSON Output and Parsing

All commands output JSON by default. Use `--format text` for human-readable output.

```bash
# Get own npub
NPUB=$(am identity show | jq -r '.npub')

# Get content of latest message
am listen --once --limit 1 | jq -r '.content'

# Send result of a command
some-command | am send --to npub1abc...

# Collect batch messages into an array
messages=$(am listen --once | jq -s '.')
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General / IO / JSON error |
| 2 | Invalid arguments |
| 3 | Network / relay error |
| 4 | Crypto / key error |
| 5 | Config / TOML error |

Always check exit codes in automated workflows:

```bash
am send --to npub1abc... "ping" || echo "Send failed with exit $?"
```

## Multiple Identities

Hold multiple identities for compartmentalization (e.g., public-facing vs. private coordination):

```bash
am identity generate --name public
am identity generate --name private
am identity list

am send --identity private --to npub1abc... "sensitive coordination"
```

## Config Management

```bash
am config show                          # Dump full config
am config set default_identity private  # Set default identity
am config set format text               # Change default output format
```

Config lives at `$XDG_CONFIG_HOME/am/config.toml`. Identities at `$XDG_DATA_HOME/am/identities/<name>.nsec` (0600 permissions).

## Privacy Guarantees

- **Protocol**: NIP-17 with NIP-59 gift wrapping
- **What relays see**: A Kind:1059 event from a random ephemeral key to the recipient's key. Sender identity is concealed from relay operators.
- **What relays don't see**: Sender npub, message content, or relationship between parties
- **Key storage**: Plaintext nsec files at 0600 permissions — safe in isolated environments; passphrase protection is v0.2

**Group messaging is not available in v0.1.** Multi-recipient encrypted messages are planned for v0.2 as `am send --to npub1 --to npub2 ...`.

## Additional Resources

### Reference Files

- **`${CLAUDE_PLUGIN_ROOT}/skills/am/references/output-schemas.md`** — Full JSON schemas for every command and output type, including NDJSON streaming format and error output
- **`${CLAUDE_PLUGIN_ROOT}/skills/am/references/workflows.md`** — Seven common agent workflow patterns: first-time setup, human-agent key exchange, polling, continuous listening, piping structured data, request/response, and multi-identity compartmentalization

### Examples

- **`${CLAUDE_PLUGIN_ROOT}/skills/am/examples/setup.sh`** — Idempotent first-time setup script for agent provisioning
- **`${CLAUDE_PLUGIN_ROOT}/skills/am/examples/messaging.sh`** — Send and receive examples including structured JSON payloads
