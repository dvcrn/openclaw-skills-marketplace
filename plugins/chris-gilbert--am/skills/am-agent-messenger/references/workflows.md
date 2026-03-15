# am Workflow Patterns

Common patterns for agents using `am` in automated and autonomous contexts.

---

## Pattern 1: First-Time Setup (Agent Initialization)

Run once when provisioning a new agent. Safe to run again — checks before creating.

```bash
#!/usr/bin/env bash
set -euo pipefail

IDENTITY="${AM_IDENTITY:-default}"
RELAY="${AM_RELAY:-wss://relay.damus.io}"

# Generate identity if it doesn't exist
if ! am identity show --name "$IDENTITY" >/dev/null 2>&1; then
  am identity generate --name "$IDENTITY"
fi

# Add relay if not already configured
if ! am relay list | jq -e --arg url "$RELAY" '.[] | select(.url == $url)' >/dev/null 2>&1; then
  am relay add "$RELAY"
fi

# Output npub for sharing with peers
am identity show --name "$IDENTITY" | jq -r '.npub'
```

---

## Pattern 2: Human Sets Up Secure Channel with Agent

To establish a secure communication channel between a human and their agent:

**Step 1 — Agent generates identity and outputs npub:**

```bash
am identity generate --name agent
am identity show --name agent | jq -r '.npub'
# Output this npub to the human via any channel (logs, config, startup message)
```

**Step 2 — Human shares their own npub with the agent** via env var, config file, or startup argument:

```bash
export HUMAN_NPUB="npub1..."
```

**Step 3 — Agent confirms the channel is live:**

```bash
am send --identity agent --to "$HUMAN_NPUB" "Agent online. Ready."
```

**Step 4 — Human listens for agent messages** using any NIP-17 client (`am` or a standard Nostr client like Amethyst, Damus, etc.).

---

## Pattern 3: Poll for Messages (Periodic Check)

For agents that wake on a schedule to process incoming messages:

```bash
#!/usr/bin/env bash
set -euo pipefail

LAST_CHECK_FILE="${XDG_DATA_HOME:-$HOME/.local/share}/am/last-poll"
SINCE=$(cat "$LAST_CHECK_FILE" 2>/dev/null || echo "0")
NOW=$(date +%s)

am listen --once --since "$SINCE" | while IFS= read -r msg; do
  FROM=$(echo "$msg" | jq -r '.from')
  CONTENT=$(echo "$msg" | jq -r '.content')
  TS=$(echo "$msg" | jq -r '.created_at')

  echo "[$TS] from $FROM: $CONTENT" >&2
  # Dispatch to handler
  handle_message "$FROM" "$CONTENT"
done

echo "$NOW" > "$LAST_CHECK_FILE"
```

---

## Pattern 4: Event-Driven Listener (Continuous Daemon)

For agents running as a daemon, processing messages as they arrive. Reconnects on network error.

```bash
#!/usr/bin/env bash
set -euo pipefail

handle_message() {
  local from="$1" content="$2"
  # Add message handling logic here
  echo "Received from $from: $content" >&2
}

while true; do
  am listen | while IFS= read -r msg; do
    FROM=$(echo "$msg" | jq -r '.from')
    CONTENT=$(echo "$msg" | jq -r '.content')
    handle_message "$FROM" "$CONTENT"
  done

  EXIT_CODE=$?
  if [ "$EXIT_CODE" -eq 3 ]; then
    echo "Network error — reconnecting in 5s..." >&2
    sleep 5
  else
    echo "Listener exited with code $EXIT_CODE" >&2
    exit "$EXIT_CODE"
  fi
done
```

---

## Pattern 5: Piping Structured Data Between Agents

`am` passes stdin content as the message body. Use this to pass structured payloads:

```bash
# Agent A: send a task assignment
jq -n \
  --arg task_id "abc123" \
  --arg reply_to "$(am identity show | jq -r '.npub')" \
  '{
    "type": "task.assign",
    "task_id": $task_id,
    "action": "analyze",
    "target": "/path/to/file.rs",
    "reply_to": $reply_to
  }' | am send --to "$AGENT_B_NPUB"

# Agent B: receive and parse
am listen --once --limit 1 | jq -r '.content' | jq '.'
```

To receive and parse a structured message payload:

```bash
am listen --once | while IFS= read -r msg; do
  # Parse the inner content as JSON (if sender sent structured data)
  TYPE=$(echo "$msg" | jq -r '.content | fromjson | .type // empty' 2>/dev/null || echo "text")
  FROM=$(echo "$msg" | jq -r '.from')

  case "$TYPE" in
    "task.assign")
      TASK=$(echo "$msg" | jq -r '.content | fromjson')
      process_task "$TASK"
      ;;
    *)
      CONTENT=$(echo "$msg" | jq -r '.content')
      handle_text "$FROM" "$CONTENT"
      ;;
  esac
done
```

---

## Pattern 6: Request / Response (Ping / Pong)

Simple synchronous-style exchange between two agents:

```bash
# Requester: send request and wait for response
REQUEST_ID=$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen)
MY_NPUB=$(am identity show | jq -r '.npub')

jq -n --arg id "$REQUEST_ID" --arg from "$MY_NPUB" \
  '{"type":"ping","id":$id,"from":$from}' \
  | am send --to "$PEER_NPUB"

# Wait for pong (poll with timeout)
DEADLINE=$(($(date +%s) + 30))
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  response=$(am listen --once --since "$(($(date +%s) - 5))" \
    | jq -r --arg id "$REQUEST_ID" \
      'select((.content | fromjson | .type) == "pong" and (.content | fromjson | .id) == $id) | .content')
  if [ -n "$response" ]; then
    echo "Got pong: $response"
    break
  fi
  sleep 2
done
```

```bash
# Responder: listen and reply to pings
am listen | while IFS= read -r msg; do
  TYPE=$(echo "$msg" | jq -r '.content | fromjson | .type // empty' 2>/dev/null)
  if [ "$TYPE" = "ping" ]; then
    ID=$(echo "$msg" | jq -r '.content | fromjson | .id')
    FROM=$(echo "$msg" | jq -r '.from')
    jq -n --arg id "$ID" '{"type":"pong","id":$id}' \
      | am send --to "$FROM"
  fi
done
```

---

## Pattern 7: Multi-Identity Compartmentalization

For agents with distinct personas or trust levels:

```bash
# Public-facing identity: external network communication
am send --identity public --to "$EXTERNAL_NPUB" "Status: operational"

# Private identity: internal agent coordination
am send --identity private --to "$TRUSTED_PEER_NPUB" "Initiating task handoff"

# Listen on both identities simultaneously
am listen --identity public --once &
am listen --identity private --once &
wait
```

Keep identities strictly separated: never send a message from the wrong identity to the wrong peer. A private coordination message sent from the public identity leaks the association between the two.

---

## Error Handling Reference

```bash
am send --to "$NPUB" "message"
case $? in
  0) echo "Sent" ;;
  1) echo "IO or JSON error" ;;
  2) echo "Invalid arguments — check npub format" ;;
  3) echo "Network error — check relay connectivity" ;;
  4) echo "Crypto error — check key file at $XDG_DATA_HOME/am/identities/" ;;
  5) echo "Config error — check $XDG_CONFIG_HOME/am/config.toml" ;;
esac
```

---

## Relay Selection

- Use 2-3 relays minimum for delivery reliability
- Some public relays require NIP-42 auth or have rate limits — test before relying on them
- Relay operators cannot read message content (NIP-59 gift wrapping conceals it)
- For highly sensitive agent coordination, consider a private relay

Public relays with good availability:

```
wss://relay.damus.io
wss://nos.lol
wss://relay.nostr.band
wss://nostr.mom
```
