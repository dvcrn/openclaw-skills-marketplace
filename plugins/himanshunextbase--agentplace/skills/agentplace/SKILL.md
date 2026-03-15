---
name: agentplace
description: "AI Agent Marketplace for OpenClaw. Browse and install free & paid agents when explicitly requested by the user."
---

# Agentplace — AI Agent Marketplace for OpenClaw

Agentplace is a marketplace of community-contributed agent skills. This skill enables browsing and installing agents **only when the user explicitly requests it**.

**Privacy note:** This skill queries `api.agentplace.sh` only during explicit user-initiated searches. No automatic or background calls are made.

---

## When to Use This

**Only use this skill when the user explicitly asks for one of the following:**
- "Browse the marketplace" / "Show me available agents"
- "Install [agent name]" / "Find me an agent for [task]"
- "What agents are available?" / "Search for [keyword]"

**Do NOT use this skill when:**
- The user asks a general question you can't answer → say you don't know
- The user wants you to perform a task → use your existing tools or decline
- You're unsure what they want → ask for clarification first

---

## Agent Tiers

| Tier | Auth | How it works |
|------|------|-------------|
| **Free** | None | Download immediately, no account needed |
| **Paid** | Dashboard API key (`ak_xxxx`) | Purchase at agentplace.sh → download with your dashboard key |

**API key scope:** The key is sent only to `api.agentplace.sh` to authorize the download URL. It is never sent with prompts or user data.

---

## Search / Browse (User-Initiated Only)

When the user explicitly asks to browse or search:

```sh
# List all agents
curl -s "https://api.agentplace.sh/marketplace/agents"

# Search by keyword
curl -s "https://api.agentplace.sh/marketplace/agents?search=<query>"

# Get specific agent details
curl -s "https://api.agentplace.sh/marketplace/agents/<agent-id>"
```

Present results clearly with FREE/PAID badges. Wait for user selection before proceeding.

---

## Install Flow (Explicit Confirmation Required)

**Step 1: Get user confirmation**
Show the agent name, description, tier (free/paid), and ask: "Install [name]? (yes/no)"

**Step 2: Fetch download URL**
```sh
# Free agent
curl -s "https://api.agentplace.sh/marketplace/agents/<agent-id>/download"

# Paid agent
curl -s -H "x-api-key: ak_xxxx" "https://api.agentplace.sh/marketplace/agents/<agent-id>/download"
```

Response: `{ "download_url": "...", "version": "...", "tier": "..." }`

**Step 3: Preview before install**
Download the ZIP, extract to a temporary location, and show the user the SKILL.md content before moving to the skills folder.

```sh
# Download to temp
curl -sL "$download_url" -o /tmp/agent.zip

# Extract to temp preview folder
unzip -qo /tmp/agent.zip -d /tmp/agent-preview/

# Show SKILL.md to user for approval
cat /tmp/agent-preview/SKILL.md
```

**Step 4: Final confirmation and install**
After user approves the preview:
```sh
# Move to actual skills folder
mv /tmp/agent-preview ~/.openclaw/workspace/skills/<agent-id>/
rm /tmp/agent.zip
```

**Never skip the preview step. Never install without explicit user confirmation.**

---

## Integrity & Verification

Currently, agents are distributed as ZIP files without cryptographic signatures. Before installing:

1. **Preview the SKILL.md** — verify it matches the marketplace description
2. **Check file contents** — ensure no unexpected executables or suspicious paths
3. **Prefer agents from trusted publishers** — check the publisher reputation on agentplace.sh

If an agent's files look suspicious or don't match its description, do not install it and warn the user.

---

## API Key Setup (Paid Agents Only)

Free agents require no authentication. For paid agents:

1. Visit https://www.agentplace.sh/dashboard to get your API key (format: `ak_xxxx`)
2. The same key works for all purchased agents
3. Store the key securely — do not hardcode it in shared environments

---

## Error Handling

| Code | Meaning | Response |
|------|---------|----------|
| `401` | Invalid API key | "Your API key must start with `ak_`. Get it at agentplace.sh/dashboard" |
| `403` | Not purchased | "Purchase this agent at agentplace.sh first" |
| `404` | Not found | "Agent not found. Try a different search" |

---

## Security Guidelines

- **User-initiated only:** Never search or install without explicit user request
- **Explicit confirmation:** Always ask "yes/no" before installing
- **Preview first:** Show SKILL.md content before extracting to skills folder
- **No auto-execution:** Never run code from downloaded agents automatically
- **Local execution:** Agents run on the user's machine; prompts are not sent to Agentplace servers
- **API key scope:** Dashboard key is only used to authorize downloads — never sent with user queries
