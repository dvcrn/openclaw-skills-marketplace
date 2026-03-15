---
name: agentfuel-api
description: "Use AgentFuel to call Replicate, Anthropic, and ElevenLabs APIs using a single crypto-funded key. Generate a free af_ key, create an invoice to get a unique USDT deposit address, then proxy all AI API calls through the AgentFuel gateway. No per-service accounts required."
---

# AgentFuel API

AgentFuel is a crypto-funded API credit broker for AI agents. One `af_` key gives you access to Replicate, Anthropic (Claude), and ElevenLabs — funded with USDT on Ethereum. No credit cards. No per-service accounts.

**Base URL:** `https://agentfuel.dev/v1`
**Auth header:** `Authorization: Bearer $AGENTFUEL_KEY`
**Pricing:** 1,000 credits = $1 USD

---

## Startup: Get a Key and Check Balance

If you don't have an `af_` key yet, generate one for free:

```bash
curl -X POST https://agentfuel.dev/v1/new-key \
  -H "Content-Type: application/json" \
  -d '{"label": "my-agent"}'
```

Response:
```json
{
  "key": "af_abc123...",
  "credits": 0,
  "message": "Key created. Use POST /v1/invoice to get a deposit address and add credits."
}
```

Save your key. Then check your balance before making API calls:

```bash
curl https://agentfuel.dev/v1/balance \
  -H "Authorization: Bearer $AGENTFUEL_KEY"
```

Response:
```json
{
  "credits_remaining": 500,
  "credits_used": 0,
  "credits_total": 500,
  "usd_value": "0.50",
  "usage_by_service": {
    "replicate": 0,
    "anthropic": 0,
    "elevenlabs": 0
  }
}
```

If `credits_remaining` is 0, create an invoice to deposit USDT.

---

## How to Get Credits (USDT Invoice)

AgentFuel uses a secure invoice system. Each invoice gives you a **unique deposit address** — no need to submit transaction IDs. Credits are applied automatically after 6 confirmations (~2 minutes).

### Step 1 — Create an invoice

During alpha, invoices are fixed at **$5 USD** (5,000 credits). Set `amount_usd: 5`.

```bash
curl -X POST https://agentfuel.dev/v1/invoice \
  -H "Authorization: Bearer $AGENTFUEL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"amount_usd": 5}'
```

Response:
```json
{
  "invoice_id": 42,
  "pay_to_address": "0xCc4343235BC4B3C1415DA4A106fdC55B3519fDe8",
  "network": "ERC-20 (Ethereum mainnet)",
  "token": "USDT",
  "amount_usdt": "5.00",
  "credits": 5000,
  "expires_at": "2026-01-01 12:30:00",
  "note": "Send exactly this amount of USDT to the address above. Credits are applied automatically after 6 confirmations (~2 min)."
}
```

### Step 2 — Send USDT

Send **exactly** the `amount_usdt` of USDT (ERC-20, Ethereum mainnet) to `pay_to_address`. Each invoice has its own unique address — do not reuse addresses across invoices.

Invoice expires in **30 minutes**.

### Step 3 — Poll for confirmation

```bash
curl https://agentfuel.dev/v1/invoice/42 \
  -H "Authorization: Bearer $AGENTFUEL_KEY"
```

Response when paid:
```json
{
  "invoice_id": 42,
  "status": "paid",
  "amount_usdt": 10,
  "credits": 10000,
  "paid_at": "2026-01-01 12:05:33",
  "sweep_txid": "0xabc..."
}
```

Poll every 30 seconds until `status` is `"paid"`. Once paid, your balance increases immediately.

---

## Calling Replicate

Route Replicate calls through `/v1/replicate/`. Same request format as `api.replicate.com/v1/`.

### Submit a prediction

```bash
curl -X POST https://agentfuel.dev/v1/replicate/predictions \
  -H "Authorization: Bearer $AGENTFUEL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "MODEL_VERSION_HASH",
    "input": { }
  }'
```

### Poll for result

```bash
curl https://agentfuel.dev/v1/replicate/predictions/PREDICTION_ID \
  -H "Authorization: Bearer $AGENTFUEL_KEY"
```

Poll every 2–3 seconds until `status` is `"succeeded"`. Credits are deducted on success.

### FLUX Schnell (4 credits/run)

```bash
curl -X POST https://agentfuel.dev/v1/replicate/predictions \
  -H "Authorization: Bearer $AGENTFUEL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "black-forest-labs/flux-schnell",
    "input": {
      "prompt": "a photorealistic cat sitting on a rooftop at sunset",
      "num_outputs": 1
    }
  }'
```

---

## Calling Anthropic (Claude)

Route calls through `/v1/anthropic/messages`. Identical to `api.anthropic.com/v1/messages`.

### Text message

```bash
curl -X POST https://agentfuel.dev/v1/anthropic/messages \
  -H "Authorization: Bearer $AGENTFUEL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Your prompt here"}]
  }'
```

### Vision (image analysis)

```bash
curl -X POST https://agentfuel.dev/v1/anthropic/messages \
  -H "Authorization: Bearer $AGENTFUEL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 512,
    "messages": [{
      "role": "user",
      "content": [
        {"type": "image", "source": {"type": "url", "url": "https://example.com/image.jpg"}},
        {"type": "text", "text": "Describe this image."}
      ]
    }]
  }'
```

---

## Calling ElevenLabs

Route calls through `/v1/elevenlabs/`. Returns `audio/mpeg`.

```bash
curl -X POST \
  "https://agentfuel.dev/v1/elevenlabs/text-to-speech/21m00Tcm4TlvDq8ikWAM" \
  -H "Authorization: Bearer $AGENTFUEL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your design is ready.",
    "model_id": "eleven_turbo_v2_5"
  }' \
  --output speech.mp3
```

---

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Invalid key | Check `AGENTFUEL_KEY` starts with `af_` |
| 402 | Insufficient credits | Create an invoice and deposit USDT |
| 429 | Rate limited | Wait 60s, then retry |
| 502 | Upstream API error | Retry once after 10s |

On `402`, the response includes `credits_required`, `credits_available`, and a `next_step` field with the exact action to take (create an invoice). Follow `next_step` to self-heal without human intervention.

---

## Pricing Reference

| Service | Model | Unit | Credits |
|---------|-------|------|---------|
| Replicate | FLUX Schnell | per run | 4 |
| Replicate | FLUX Dev | per run | 40 |
| Replicate | SDXL ControlNet | per run | 28 |
| Anthropic | claude-haiku-4-5 input | per 1K tokens | 1 |
| Anthropic | claude-haiku-4-5 output | per 1K tokens | 5 |
| Anthropic | claude-sonnet-4-6 input | per 1K tokens | 4 |
| Anthropic | claude-sonnet-4-6 output | per 1K tokens | 20 |
| ElevenLabs | Turbo v2.5 | per 1K chars | 220 |
| ElevenLabs | Multilingual v2 | per 1K chars | 280 |

**1,000 credits = $1 USD**

---

## About AgentFuel

AI-native API access, funded by crypto. Visit [agentfuel.dev](https://agentfuel.dev).
Skill hosted at: `https://agentfuel.dev/skill.md`
