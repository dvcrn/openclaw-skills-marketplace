---
name: agentstead-deploy
description: "Deploy OpenClaw AI agents to AgentStead cloud hosting. Use when a user wants to deploy a sub-agent on AgentStead, connect Telegram/Discord, and launch quickly with AgentStead-provided AI models."
---

# AgentStead Deploy

Deploy an OpenClaw agent to AgentStead's cloud hosting in minutes.

**API Base URL:** `https://www.agentstead.com/api/v1`

## Quick Deploy Flow

1. Register/login → 2. Create agent → 3. Add channel → 4. Set up billing → 5. Start agent → 6. Verify

## Conversation Guide

Before calling any APIs, gather from the user:

1. **Agent name** — What should the agent be called?
2. **Personality/instructions** — System prompt or personality description
3. **Channel** — Telegram (need bot token from @BotFather) or Discord (need bot token from Discord Developer Portal)
4. **AI credit plan** — Pay-as-you-go ($0 base), 1K ($10/mo), 3K ($30/mo), 5K ($50/mo), or 10K ($100/mo) ASTD/mo
5. **AI model** — Claude 3.5 Haiku (fast), Claude Sonnet 4 (balanced), or Claude Opus 4.6 (most capable)
6. **Hosting plan** — Starter $9/mo, Pro $19/mo, Business $39/mo, Enterprise $79/mo
7. **Payment method** — ASTD Balance, Crypto (USDC on Base/Polygon), or Card (Stripe)

## Step-by-Step Workflow

### Step 1: Register

```bash
curl -X POST https://www.agentstead.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

Response includes `token` — use as `Authorization: Bearer <token>` for all subsequent requests.

If user already has an account, use login instead:

```bash
curl -X POST https://www.agentstead.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

### Step 2: Create Agent

```bash
curl -X POST https://www.agentstead.com/api/v1/agents \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyAgent",
    "personality": "You are a helpful assistant...",
    "plan": "pro",
    "aiPlan": "ASTD_5000",
    "defaultModel": "anthropic/claude-sonnet-4-20250514"
  }'
```

**Valid `aiPlan` values:**
| Plan | Price | Description |
|------|-------|-------------|
| `PAYG` | $0 base | Pay-as-you-go, deducts from ASTD balance per use |
| `ASTD_1000` | $10/mo | 1,000 ASTD monthly credits |
| `ASTD_3000` | $30/mo | 3,000 ASTD monthly credits |
| `ASTD_5000` | $50/mo | 5,000 ASTD monthly credits |
| `ASTD_10000` | $100/mo | 10,000 ASTD monthly credits |

**Valid `defaultModel` values:**
| Model | ID | Best For |
|-------|----|----------|
| Claude 3.5 Haiku | `anthropic/claude-haiku-3-5` | Fast, efficient responses |
| Claude Sonnet 4 | `anthropic/claude-sonnet-4-20250514` | Balanced performance |
| Claude Opus 4.6 | `anthropic/claude-opus-4-6` | Most capable reasoning |

Response includes the agent `id` — save it for subsequent steps.

### Step 3: Add Channel

**Telegram:**
```bash
curl -X POST https://www.agentstead.com/api/v1/agents/<agent_id>/channels \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"type": "telegram", "botToken": "123456:ABC-DEF..."}'
```

**Discord:**
```bash
curl -X POST https://www.agentstead.com/api/v1/agents/<agent_id>/channels \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"type": "discord", "botToken": "MTIz..."}'
```

### Step 4: Set Up Billing

**Crypto (USDC):**
```bash
curl -X POST https://www.agentstead.com/api/v1/billing/crypto/create-invoice \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "<agent_id>", "plan": "pro", "aiPlan": "ASTD_5000"}'
```

Returns a deposit address. Guide user to send USDC on Base or Polygon chain.

**Stripe (card):**
```bash
curl -X POST https://www.agentstead.com/api/v1/billing/checkout \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "<agent_id>", "plan": "pro", "aiPlan": "ASTD_5000"}'
```

Returns a Stripe checkout URL. Send to user to complete payment.

### Step 5: Start Agent

```bash
curl -X POST https://www.agentstead.com/api/v1/agents/<agent_id>/start \
  -H "Authorization: Bearer <token>"
```

### Step 6: Verify

```bash
curl -X GET https://www.agentstead.com/api/v1/agents/<agent_id> \
  -H "Authorization: Bearer <token>"
```

Check that `status` is `"RUNNING"`. If not, wait a few seconds and retry.

## Pricing Reference

### Hardware Plans (per agent)
| Plan | Price | Specs |
|------|-------|-------|
| Starter | $9/mo | t3.micro · 1 vCPU · 1GB RAM · 5GB storage |
| Pro | $19/mo | t3.small · 2 vCPU · 2GB RAM · 20GB storage |
| Business | $39/mo | t3.medium · 2 vCPU · 4GB RAM · 50GB storage |
| Enterprise | $79/mo | t3.large · 2 vCPU · 8GB RAM · 100GB storage |

### AI Credit Plans
| Plan | Price | Description |
|------|-------|-------------|
| PAYG | $0 base | Pay-as-you-go from ASTD balance |
| ASTD_1000 | $10/mo | 1,000 ASTD monthly credits |
| ASTD_3000 | $30/mo | 3,000 ASTD monthly credits |
| ASTD_5000 | $50/mo | 5,000 ASTD monthly credits |
| ASTD_10000 | $100/mo | 10,000 ASTD monthly credits |

All plans include access to Claude 3.5 Haiku, Claude Sonnet 4, and Claude Opus 4.6.

**ASTD conversion:** 100 ASTD = $1 USD. Platform fee: 4% on top of AI provider cost.

## Notes

- Telegram bot tokens come from [@BotFather](https://t.me/BotFather)
- Discord bot tokens come from the [Discord Developer Portal](https://discord.com/developers/applications)
- Agents can be stopped with `POST /agents/:id/stop` and restarted anytime
- Top up ASTD balance via the web dashboard or iOS app
- See `references/api-reference.md` for full API documentation
