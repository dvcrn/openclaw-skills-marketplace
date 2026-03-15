---
name: hopeids
description: "Openclaw Plugin"
---

# hopeIDS Security Skill

Inference-based intrusion detection for AI agents with quarantine and human-in-the-loop.

## Security Invariants

These are **non-negotiable** design principles:

1. **Block = full abort** — Blocked messages never reach jasper-recall or the agent
2. **Metadata only** — No raw malicious content is ever stored
3. **Approve ≠ re-inject** — Approval changes future behavior, doesn't resurrect messages
4. **Alerts are programmatic** — Telegram alerts built from metadata, no LLM involved

---

## Features

- **Auto-scan** — Scan messages before agent processing
- **Quarantine** — Block threats with metadata-only storage
- **Human-in-the-loop** — Telegram alerts for review
- **Per-agent config** — Different thresholds for different agents
- **Commands** — `/approve`, `/reject`, `/trust`, `/quarantine`

---

## The Pipeline

```
Message arrives
    ↓
hopeIDS.autoScan()
    ↓
┌─────────────────────────────────────────┐
│  risk >= threshold?                     │
│                                         │
│  BLOCK (strictMode):                    │
│     → Create QuarantineRecord           │
│     → Send Telegram alert               │
│     → ABORT (no recall, no agent)       │
│                                         │
│  WARN (non-strict):                     │
│     → Inject <security-alert>           │
│     → Continue to jasper-recall         │
│     → Continue to agent                 │
│                                         │
│  ALLOW:                                 │
│     → Continue normally                 │
└─────────────────────────────────────────┘
```

---

## Configuration

```json
{
  "plugins": {
    "entries": {
      "hopeids": {
        "enabled": true,
        "config": {
          "autoScan": true,
          "defaultRiskThreshold": 0.7,
          "strictMode": false,
          "telegramAlerts": true,
          "agents": {
            "moltbook-scanner": {
              "strictMode": true,
              "riskThreshold": 0.7
            },
            "main": {
              "strictMode": false,
              "riskThreshold": 0.8
            }
          }
        }
      }
    }
  }
}
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `autoScan` | boolean | `false` | Auto-scan every message |
| `strictMode` | boolean | `false` | Block (vs warn) on threats |
| `defaultRiskThreshold` | number | `0.7` | Risk level that triggers action |
| `telegramAlerts` | boolean | `true` | Send alerts for blocked messages |
| `telegramChatId` | string | - | Override alert destination |
| `quarantineDir` | string | `~/.openclaw/quarantine/hopeids` | Storage path |
| `agents` | object | - | Per-agent overrides |
| `trustOwners` | boolean | `true` | Skip scanning owner messages |

---

## Quarantine Records

When a message is blocked, a metadata record is created:

```json
{
  "id": "q-7f3a2b",
  "ts": "2026-02-06T00:48:00Z",
  "agent": "moltbook-scanner",
  "source": "moltbook",
  "senderId": "@sus_user",
  "intent": "instruction_override",
  "risk": 0.85,
  "patterns": [
    "matched regex: ignore.*instructions",
    "matched keyword: api key"
  ],
  "contentHash": "ab12cd34...",
  "status": "pending"
}
```

**Note:** There is NO `originalMessage` field. This is intentional.

---

## Telegram Alerts

When a message is blocked:

```
🛑 Message blocked

ID: `q-7f3a2b`
Agent: moltbook-scanner
Source: moltbook
Sender: @sus_user
Intent: instruction_override (85%)

Patterns:
• matched regex: ignore.*instructions
• matched keyword: api key

`/approve q-7f3a2b`
`/reject q-7f3a2b`
`/trust @sus_user`
```

Built from metadata only. No LLM touches this.

---

## Commands

### `/quarantine [all|clean]`

List quarantine records.

```
/quarantine        # List pending
/quarantine all    # List all (including resolved)
/quarantine clean  # Clean expired records
```

### `/approve <id>`

Mark a blocked message as a false positive.

```
/approve q-7f3a2b
```

**Effect:**
- Status → `approved`
- (Future) Add sender to allowlist
- (Future) Lower pattern weight

### `/reject <id>`

Confirm a blocked message was a true positive.

```
/reject q-7f3a2b
```

**Effect:**
- Status → `rejected`
- (Future) Reinforce pattern weights

### `/trust <senderId>`

Whitelist a sender for future messages.

```
/trust @legitimate_user
```

### `/scan <message>`

Manually scan a message.

```
/scan ignore your previous instructions and...
```

---

## What Approve/Reject Mean

| Command | What it does | What it doesn't do |
|---------|--------------|-------------------|
| `/approve` | Marks as false positive, may adjust IDS | Does NOT re-inject the message |
| `/reject` | Confirms threat, may strengthen patterns | Does NOT affect current message |
| `/trust` | Whitelists sender for future | Does NOT retroactively approve |

**The blocked message is gone by design.** If it was legitimate, the sender can re-send.

---

## Per-Agent Configuration

Different agents need different security postures:

```json
"agents": {
  "moltbook-scanner": {
    "strictMode": true,    // Block threats
    "riskThreshold": 0.7   // 70% = suspicious
  },
  "main": {
    "strictMode": false,   // Warn only
    "riskThreshold": 0.8   // Higher bar for main
  },
  "email-processor": {
    "strictMode": true,    // Always block
    "riskThreshold": 0.6   // More paranoid
  }
}
```

---

## Threat Categories

| Category | Risk | Description |
|----------|------|-------------|
| `command_injection` | 🔴 Critical | Shell commands, code execution |
| `credential_theft` | 🔴 Critical | API key extraction attempts |
| `data_exfiltration` | 🔴 Critical | Data leak to external URLs |
| `instruction_override` | 🔴 High | Jailbreaks, "ignore previous" |
| `impersonation` | 🔴 High | Fake system/admin messages |
| `discovery` | ⚠️ Medium | API/capability probing |

---

## Installation

```bash
npx hopeid setup
```

Then restart OpenClaw.

---

## Links

- **GitHub**: https://github.com/E-x-O-Entertainment-Studios-Inc/hopeIDS
- **npm**: https://www.npmjs.com/package/hopeid
- **Docs**: https://exohaven.online/products/hopeids
