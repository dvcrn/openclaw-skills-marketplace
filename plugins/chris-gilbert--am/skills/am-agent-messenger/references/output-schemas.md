# am Output Schemas

All `am` commands output JSON to stdout by default. Stderr receives error messages. This document defines exact output structures for every command.

## identity generate / identity import

```json
{
  "name": "string",   // identity name
  "npub": "string"    // bech32 public key (npub1...)
}
```

## identity show

Without `--secret`:

```json
{
  "name": "string",
  "npub": "string",
  "nsec": null
}
```

With `--secret`:

```json
{
  "name": "string",
  "npub": "string",
  "nsec": "string"    // bech32 secret key (nsec1...) — handle with care, never log
}
```

## identity list

Array of identity summaries (nsec is never included):

```json
[
  {"name": "default", "npub": "npub1..."},
  {"name": "private", "npub": "npub1..."}
]
```

Empty array if no identities exist:

```json
[]
```

## relay add

```json
{"added": "wss://relay.damus.io"}
```

## relay remove

```json
{"removed": "wss://relay.damus.io"}
```

## relay list

```json
[
  {"url": "wss://relay.damus.io"},
  {"url": "wss://nos.lol"}
]
```

Empty array if no relays configured:

```json
[]
```

## send

```json
{
  "to": "npub1...",       // recipient bech32 public key
  "event_id": "string"    // Nostr event ID (64-char hex)
}
```

## listen

Each received message is a single JSON object. Both `--once` (batch) and streaming output use NDJSON — one JSON object per line, no array wrapper.

```json
{
  "from": "npub1...",         // sender bech32 public key
  "content": "string",        // decrypted message content
  "created_at": 1700000000,   // Unix timestamp (seconds)
  "event_id": "string"        // Nostr event ID (64-char hex)
}
```

### Parsing streaming output

```bash
# Process each message as it arrives
am listen | while IFS= read -r line; do
  echo "$line" | jq -r '"[\(.created_at)] from \(.from): \(.content)"'
done

# Collect batch into a JSON array
messages=$(am listen --once | jq -s '.')
count=$(echo "$messages" | jq 'length')
```

### Distinguishing batch vs. streaming

Both use the same per-line JSON format. The difference is termination: `--once` exits after fetching, streaming blocks indefinitely. Use `--once` in scripts; use streaming for daemon processes.

## config show

```json
{
  "default_identity": "default",      // null if not set
  "relays": ["wss://relay.damus.io"],
  "format": null                       // null if not set; "json" or "text" if configured
}
```

## config set

No stdout output. Exit code 0 on success, 2 on invalid key, 5 on write failure.

## Error Output

Errors are written to stderr. Stdout is empty (or contains partial output if the error occurred mid-operation).

```
Error: <description>
```

Exit codes are the authoritative signal — do not parse error message text, as its format is not guaranteed stable across versions.

### Common error scenarios

| Exit code | Common causes |
|-----------|--------------|
| 2 | Malformed npub, unknown identity name |
| 3 | Relay unreachable, WebSocket failure, no relays configured |
| 4 | Corrupted nsec file, invalid key format |
| 5 | Config file missing or malformed TOML |

### Detecting no messages

`am listen --once` with no messages available exits 0 and produces no output (empty stdout). Check for empty output rather than a non-zero exit code:

```bash
output=$(am listen --once --since "$SINCE")
if [ -z "$output" ]; then
  echo "No new messages"
else
  echo "$output" | while IFS= read -r msg; do
    # process msg
    :
  done
fi
```
