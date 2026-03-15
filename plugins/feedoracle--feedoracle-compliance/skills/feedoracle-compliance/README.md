<div align="center">

# 🛡️ FeedOracle Compliance Intelligence

**Verifiable compliance evidence for AI agents in regulated tokenized markets**

[![License: MIT-0](https://img.shields.io/badge/License-MIT--0-brightgreen.svg)](https://spdx.org/licenses/MIT-0.html)
[![API Status](https://img.shields.io/badge/API-Live-success.svg)](https://api.feedoracle.io/health)
[![MCP Tools](https://img.shields.io/badge/MCP_Tools-48-blue.svg)](https://feedoracle.io/mcp)
[![ClawHub](https://img.shields.io/badge/ClawHub-feedoracle--compliance-orange.svg)](https://clawhub.ai/feedoracle/feedoracle-compliance)
[![Endpoints](https://img.shields.io/badge/API_Endpoints-43+-purple.svg)](https://feedoracle.io/docs)

ECDSA-signed responses · On-chain anchored (Polygon + XRPL) · Replayable proof
Designed for MiCA, DORA, and AMLR compliance workflows.

[Get Free API Key](https://feedoracle.io/dashboard) · [API Docs](https://feedoracle.io/docs) · [MCP Servers](https://feedoracle.io/mcp) · [Website](https://feedoracle.io)

</div>

---

## ⚡ Quick Start — Verify in 30 Seconds

No login, no funnel — just copy-paste:

```bash
# Health check (no API key needed)
curl -s https://api.feedoracle.io/health | jq .

# With your free API key (100 calls/day):
export FEEDORACLE_API_KEY="your_key_here"

# Stablecoin risk score with reserve backing and peg monitoring
curl -s -H "Authorization: Bearer $FEEDORACLE_API_KEY" \
  https://api.feedoracle.io/v1/stablecoin/risk/USDC | jq .

# MiCA compliance status and issuer registry check
curl -s -H "Authorization: Bearer $FEEDORACLE_API_KEY" \
  https://api.feedoracle.io/v1/mica/status/USDC | jq .
```

### Example Response — Stablecoin Risk Score

```json
{
  "symbol": "USDC",
  "risk_score": 22,
  "risk_level": "LOW",
  "mica_status": "COMPLIANT",
  "peg_stability": 0.9998,
  "reserve_backing": "FULL",
  "issuer": "Circle Internet Financial",
  "issuer_registered": true,
  "polygon_tx": "0x8a3f...verified",
  "ecdsa_signature": "0x304502...",
  "timestamp": "2025-03-11T14:30:00Z"
}
```

> Every response includes an ECDSA signature and Polygon TX hash — independently verifiable on-chain.

---

## 📦 Install as OpenClaw / ClawHub Skill

```bash
npx clawhub@latest install feedoracle-compliance
```

Or add manually to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "feedoracle-compliance": {
        "enabled": true,
        "env": {
          "FEEDORACLE_API_KEY": "your_key_here"
        }
      }
    }
  }
}
```

API keys available at → [feedoracle.io/dashboard](https://feedoracle.io/dashboard)

---

## 🤖 What This Skill Does

Your agent **automatically** uses FeedOracle whenever a conversation involves:

| Trigger | Examples |
|---------|----------|
| 🪙 **Stablecoin names** | USDT, USDC, EURC, EURI, PYUSD, DAI |
| 📋 **Regulatory keywords** | MiCA, DORA, AMLR, ESMA, EBA, BaFin |
| 🏦 **Issuer due diligence** | Issuer registration, licensing, reserve backing |
| 📊 **Peg monitoring** | Peg stability, collateral, reserve assessment |
| 🔍 **Evidence requests** | "Show proof", "audit trail", "compliance verification" |
| 🏛️ **Tokenized asset compliance** | RWA, regulated DeFi, digital asset issuer intelligence |

The agent retrieves signed compliance data, cites the Polygon TX hash for audit trail, and references the relevant MiCA enforcement timeline where applicable.

---

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/stablecoin/risk/{symbol}` | Risk score (0-100), peg stability, reserve backing, issuer status |
| `GET` | `/v1/mica/status/{symbol}` | ESMA/EBA register check, EMT/ART classification, enforcement timeline |
| `GET` | `/v1/macro/{indicator}` | 86 FRED + 20 ECB macro economic series |
| `POST` | `/v1/evidence/bundle` | ECDSA-signed evidence bundle with Polygon TX hash |
| `GET` | `/v1/registry/issuer/{name}` | Issuer license and registration lookup |

### Full Platform (43+ Endpoints)

Beyond this skill, FeedOracle offers **43+ API endpoints** across 9 categories, including:

- **Macro Economic Oracle** — FRED (86 series) + ECB (20 series) real-time data
- **On-chain Verification** — Polygon + XRPL multi-chain anchoring
- **Evidence Infrastructure** — JWS signing, versioned schemas, deterministic replay
- **Issuer Registry** — ESMA + EBA register cross-referencing for issuer due diligence

### MCP Servers (48 Tools)

FeedOracle provides **3 MCP servers** for direct AI agent integration:

| Server | Tools | Focus |
|--------|-------|-------|
| Compliance MCP | 22 | MiCA status, stablecoin risk, issuer registry |
| Macro MCP | 13 | FRED/ECB data, economic indicators |
| Risk MCP | 13 | Risk scoring, evidence bundles, on-chain verification |

---

## 🔐 Evidence Architecture

```
┌─────────────────────────────────────────────┐
│         FeedOracle Evidence Flow             │
├─────────────────────────────────────────────┤
│                                             │
│  Agent Query → API Response                 │
│       ↓              ↓                      │
│  ECDSA Signed    Polygon TX Hash            │
│       ↓              ↓                      │
│  Independently   On-chain                   │
│  Verifiable      Anchored                   │
│       ↓              ↓                      │
│  Verifiable compliance evidence             │
│  suitable for audit and review workflows    │
│                                             │
│  Every claim independently checkable.       │
│  Every proof replayable.                    │
└─────────────────────────────────────────────┘
```

---

## 💰 Pricing

| Tier | Calls/day | Price | Best for |
|------|-----------|-------|----------|
| **Free** | 100 | $0 | Evaluation & testing |
| **Pro** | 10,000 | $49/mo | Compliance teams |
| **Agent** | Unlimited | $299/mo | AI agents in production |
| **Enterprise** | Custom | Custom | Regulated institutions |

All tiers include ECDSA-signed responses and on-chain anchoring.
Payments via Stripe or USDC (Polygon).

→ [feedoracle.io/pricing](https://feedoracle.io/pricing)

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| 🌐 Website | [feedoracle.io](https://feedoracle.io) |
| 📖 API Docs | [feedoracle.io/docs](https://feedoracle.io/docs) |
| 🤖 MCP Servers | [feedoracle.io/mcp](https://feedoracle.io/mcp) |
| 🔑 Get API Key | [feedoracle.io/dashboard](https://feedoracle.io/dashboard) |
| 📊 API Status | [uptime.feedoracle.io](https://uptime.feedoracle.io) |
| 🦞 ClawHub Skill | [clawhub.ai/feedoracle/feedoracle-compliance](https://clawhub.ai/feedoracle/feedoracle-compliance) |

---

## 📄 License

[MIT-0](https://spdx.org/licenses/MIT-0.html) — use freely in any agent or application. No attribution required.
