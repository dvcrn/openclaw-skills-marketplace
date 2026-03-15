# 🦞 FlowClaw — LLM Usage Monitor & Load Balancer for OpenClaw

> LLM subscription usage monitoring and load balancing for OpenClaw.

```
 ███████╗██╗      ██████╗ ██╗    ██╗
 ██╔════╝██║     ██╔═══██╗██║    ██║
 █████╗  ██║     ██║   ██║██║ █╗ ██║
 ██╔══╝  ██║     ██║   ██║██║███╗██║
 ██║     ███████╗╚██████╔╝╚███╔███╔╝
 ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝
      ██████╗██╗      █████╗ ██╗    ██╗
     ██╔════╝██║     ██╔══██╗██║    ██║
     ██║     ██║     ███████║██║ █╗ ██║
     ██║     ██║     ██╔══██║██║███╗██║
     ╚██████╗███████╗██║  ██║╚███╔███╔╝
      ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝
```

**FlowClaw** is the unkillable connectivity layer for [OpenClaw](https://github.com/openclaw/openclaw). It monitors every subscription, balances every credit, and fails over to local silicon when the cloud goes dark.

It ensures your agent **never gets stuck** by intelligently routing prompts to the best available provider — whether that's a fresh Claude subscription, a free Google quota, or a local Ollama model.

**Supported Providers:**

| Provider | Auth Method | What You Get |
|----------|------------|--------------|
| **Anthropic Claude Max** | OAuth (unlimited accounts) | 5h session + 7d windows, Opus/Sonnet breakdown |
| **Google Gemini CLI** | OAuth via OpenClaw | Pro + Flash quota (24h rolling) |
| **Google Antigravity** | codexbar | Claude, Gemini Pro/Flash per-model (12h rolling) |
| **OpenAI Codex** | OAuth via OpenClaw | 3h + daily windows, plan type, credits |
| **GitHub Copilot** | OAuth via OpenClaw | Premium + Chat quota |
| **Ollama** | Local (auto-detected) | Any downloaded model (fallback) |

---

## 🎯 The Problem

Flat-rate LLM subscriptions like Claude Max and Google Gemini CLI have **usage windows that reset on a schedule**. If you don't use your credits before the window closes, they're gone. If you have multiple accounts across multiple providers, you're almost certainly leaving money on the table.

Worse, when a provider goes down or you hit a hard limit, your agent stops.

**Without FlowClaw:**
```
  ┌─────────────────────────────────────────────────────────┐
  │  Anthropic A   ████████████████████░░░░░  80% used      │  ← Resets in 30min!
  │  Anthropic B   ██░░░░░░░░░░░░░░░░░░░░░░  10% used      │  ← Resets in 11h
  │  Gemini CLI    ░░░░░░░░░░░░░░░░░░░░░░░░   0% used      │  ← Wide open
  │  Antigravity   ████░░░░░░░░░░░░░░░░░░░░  40% used      │  ← Resets in 5h
  │  Codex         ░░░░░░░░░░░░░░░░░░░░░░░░   0% used      │  ← Fresh
  │                                                         │
  │  You're using Account B... wasting 80% of Account A 💸  │
  └─────────────────────────────────────────────────────────┘
```

**With FlowClaw:**
```
  ┌─────────────────────────────────────────────────────────┐
  │  ⚡ SWITCH → Anthropic A  (score: 0.94, resets in 30m)  │
  │                                                         │
  │  "Use Account A now — 80% remaining credits expire in   │
  │   30 minutes. Account B and Google can wait."            │
  └─────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- 🦞 **Unstoppable Agents** — Automatically fails over to local Ollama models if all cloud providers are down or exhausted.
- 📈 **Real-time Metrics** — Queries provider APIs directly for accurate usage bars and reset timers.
- 👥 **Multi-account** — Juggle unlimited Anthropic accounts seamlessly.
- 🧠 **EDF Scoring** — Earliest Deadline First algorithm prioritizes credits that are about to expire.
- 🔄 **Smart Routing** — Reconfigures OpenClaw's model priority on the fly.
- 📊 **Family-aware** — Only swaps within the same capability class (Opus↔Opus, not Opus↔Gemini).
- ⏱️ **Cron-ready** — `flowclaw auto` runs silently in the background to keep your agent optimized.

---

## 📊 Dashboard

```bash
$ flowclaw status --fresh
```
```
🦞 FlowClaw — LLM Provider Dashboard

━━━ Anthropic Claude Max ━━━━━━━━━━━━━━━━━━━━

  👤 work (work@example.com) — Max 20x
     ⏱️  5h Session:  🔴 ██████████ 100%  ⏳2h 30m
     📅 7d Overall:   🟢 ████░░░░░░ 41%   ⏳6d 12h
     💎 7d Opus:      🟢 ░░░░░░░░░░ 0%
     💬 7d Sonnet:    🟢 █░░░░░░░░░ 18%
     💰 Extra usage:  🔴 $32.39/$20.00

  👤 personal (personal@example.com) — Max 5x
     ⏱️  5h Session:  🟢 ███░░░░░░░ 30%   ⏳4h 10m
     📅 7d Overall:   🟢 █░░░░░░░░░ 12%   ⏳5d 3h

━━━ Google Gemini CLI ━━━━━━━━━━━━━━━━━━━━━━━

  ♊
     ♊ Pro                🟢 ░░░░░░░░░░ 0%
     ⚡ Flash              🟢 ░░░░░░░░░░ 0%

━━━ Google Antigravity ━━━━━━━━━━━━━━━━━━━━━━━

  🌐 (Antigravity)
     🤖 claude-opus-4-6    🟢 ████░░░░░░ 40%  ⏳1h 27m
     🤖 claude-sonnet-4-6  🟢 ████░░░░░░ 40%  ⏳1h 27m
     ♊ gemini-3-pro-high  🟢 ░░░░░░░░░░ 0%   ⏳5h 0m
     ⚡ gemini-3-flash     🟢 ░░░░░░░░░░ 0%   ⏳5h 0m

━━━ OpenAI Codex ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🤖 (Pro)
     🤖 3h                 🟡 ██████░░░░ 60%  ⏳1h 15m
     🤖 Day                🟢 ██░░░░░░░░ 20%  ⏳18h

━━━ Ollama (Local) ━━━━━━━━━━━━━━━━━━━━━━━━━━

  🖥️  qwen3:235b (60.1GB)  🟢 Always available

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 02:02 PM PST · Feb 18, 2026
```

---

## 🧮 Scoring

```bash
$ flowclaw score
```
```
🧠 FlowClaw Scoring

  #1  ✅ xtreme          [opus]         score=0.2026  5h:74% 7d:51%    ← recommended
  #2  ✅ epic            [opus]         score=0.1525  5h:11% 7d:96%
  #3  ✅ google-claude   [opus]         score=0.5550  0% used
  #4  ✅ google-gemini   [gemini-pro]   score=0.5550  0% used
  #5  ✅ openai-codex    [gpt5]         score=0.6000  API
  #6  ✅ local-qwen3     [local]        score=0.2200  Local (60.1GB)

  🎯 Recommended: xtreme (anthropic/claude-opus-4-6)
```

> **Why xtreme over epic?** Even though epic has more 5h session capacity (11% vs 74%), xtreme has vastly more 7d weekly headroom (51% vs 96%). FlowClaw conserves the account with more long-term room.

---

## ⚡ Auto-Optimization

```bash
$ flowclaw optimize
```

FlowClaw detects the best routing option, swaps your primary model, and reorganizes fallbacks:

```
🧠 FlowClaw Optimization

  🎯 Recommended primary: google-gemini-cli/claude-opus-4-6-thinking
  📋 Anthropic profile order: anthropic:xtreme anthropic:epic

  ⚙️  Applying...
  ✅ Anthropic profile order updated
  ✅ Primary model set to google-gemini-cli/claude-opus-4-6-thinking
  ✅ Fallbacks: anthropic/claude-opus-4-6, openai/gpt-5.2

  ✅ FlowClaw optimized!
```

---

## 🔬 How the Scoring Algorithm Works

FlowClaw treats every subscription window as **perishable inventory** — like fresh groceries with expiration dates. Credits that expire soonest should be used first.

### The Formula

```
score = urgency × 0.30 + availability × 0.25 + proximity × 0.15
      + weekly_headroom × 0.20 + tier_bonus × 0.10
```

| Factor | Weight | Formula | What it measures |
|--------|--------|---------|-----------------|
| **Urgency** | 30% | `remaining / hours_to_reset` | Credits wasting per hour |
| **Availability** | 25% | `√(remaining)` | Dampened remaining capacity |
| **Proximity** | 15% | `1 - (hours / window)` | How close to reset deadline |
| **Weekly headroom** | 20% | `(100 - weekly%) / 100` | 7-day capacity remaining |
| **Tier bonus** | 10% | Free=+0.8, Paid=0, Local=-0.3 | Provider cost preference |

### Perishable Inventory: The Core Insight

Both the **5-hour session** and **7-day weekly** windows are perishable. The algorithm balances both:

```
  5h Session Window                    7-Day Weekly Window
  ┌──────────────────────┐             ┌──────────────────────┐
  │ ██████████████░░░░░░ │ 74%         │ █████████░░░░░░░░░░░ │ 51%
  │ Resets in 11h        │             │ Resets in 6d 10h     │
  │ → Session credits    │             │ → Weekly budget      │
  │   are replenished    │             │   NOT replenished    │
  │   frequently         │             │   for 6+ days!       │
  └──────────────────────┘             └──────────────────────┘
         ↑ Less urgent                        ↑ More important
```

### 📖 Real-World Scoring Examples

#### Scenario 1: Weekly Headroom Conservation

> *"Which account should I use when both have session capacity?"*

```
  Account A (xtreme):  5h session = 74%   7d weekly = 51%   resets in 6d
  Account B (epic):    5h session = 11%   7d weekly = 96%   resets in 1d
```

```
  xtreme  →  score = 0.2026   ✅ Winner
  epic    →  score = 0.1525   ❌ Deprioritized

  Why? epic is at 96% of its weekly budget. Using it more risks hitting
  the 7-day limit. xtreme has 49% weekly headroom — much safer to use.
```

#### Scenario 2: Burn Mode (≤6h to Weekly Reset)

> *"But what if epic's weekly window is about to reset?"*

```
  Account A (xtreme):  5h session = 74%   7d weekly = 51%   resets in 6d
  Account B (epic):    5h session = 11%   7d weekly = 96%   resets in 5h ← expiring!
```

```
  epic    →  score = 0.3679   ✅ Winner — BURN IT!
  xtreme  →  score = 0.2026   ❌ Save for later

  Why? epic's weekly window resets in 5h. Those remaining 4% of credits
  vanish in 5 hours anyway — use them now! The weekly penalty is removed
  entirely when ≤6h remain. This is the "perishable grocery" rule:
  eat what expires first.
```

#### Scenario 3: Session Limit Hit

> *"What if an account is completely blocked?"*

```
  Account A (xtreme):  5h session = 100%  ← BLOCKED   resets in 2h
  Account B (epic):    5h session = 11%   7d weekly = 96%   resets in 1d
  Google (free):       Claude = 0%        resets in 12h
```

```
  google  →  score = 0.5550   ✅ Winner — free tier, 0% used
  epic    →  score = 0.1525   ✅ Available but conserve it
  xtreme  →  score = 0.0000   🚫 Blocked (can't use until 2h reset)

  Why? 100% on ANY window = instant score 0. Google's free tier gets
  a +0.8 tier bonus, making it the clear winner when available.
```

#### Scenario 4: Cross-Provider Routing

> *"FlowClaw picks the best option across ALL providers."*

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  Provider              Model           Score    Status          │
  │─────────────────────────────────────────────────────────────────│
  │  Google Antigravity    claude-opus     0.5550   0% used   ← #1 │
  │  Google Antigravity    gemini-pro      0.5550   0% used        │
  │  Anthropic (xtreme)    claude-opus     0.2026   5h:74% 7d:51%  │
  │  Anthropic (epic)      claude-opus     0.1525   5h:11% 7d:96%  │
  │  OpenAI Codex          gpt-5.2        0.6000   API             │
  │  Ollama                qwen3:235b     0.2200   Local           │
  └─────────────────────────────────────────────────────────────────┘

  Family-aware routing:
    Opus family  → Google Antigravity (free, 0% used)
    Gemini family → Google Antigravity gemini-pro
    GPT family   → OpenAI Codex
    Local family → Ollama qwen3
```

### Transition Zones

The weekly headroom penalty doesn't flip like a switch — it fades smoothly:

```
  Time to weekly reset    Weekly penalty    Behavior
  ──────────────────────────────────────────────────────
  > 12h                   Full              Conserve weekly capacity
  12h → 6h                Fades linearly    Transitioning to burn mode
  ≤ 6h                    None (= 1.0)      Full burn — use it or lose it
```

### Hard Rules

- **100% on any window** → score = 0 (completely blocked)
- **Free tiers** (Google/Antigravity) → +0.8 bonus (always preferred)
- **Family-aware** — only swaps within same capability class (Opus↔Opus, Gemini↔Gemini)
- **Local models** — always available, never blocked, slight quality penalty

---

## 🏗️ Provider Details

| Provider | Reset Windows | Data Source | Notes |
|----------|---------------|-------------|-------|
| **Anthropic Claude Max** | 5h session + 7d weekly | `api.anthropic.com/api/oauth/usage` | Unlimited accounts via FlowClaw tokens |
| **Google Gemini CLI** | 24h rolling | `cloudcode-pa.googleapis.com` | Pro + Flash request quota |
| **Google Antigravity** | 12h rolling | codexbar | Per-model: Claude, Gemini Pro, Flash |
| **OpenAI Codex** | 3h + daily | `chatgpt.com/backend-api/wham/usage` | Plan type + credit balance |
| **GitHub Copilot** | Monthly | `api.github.com/copilot_internal/user` | Premium + Chat quota |
| **Ollama** | Never | `localhost:11434/api/tags` | Auto-detected, always available |

---

## 🚀 Installation

### Requirements

- macOS or Linux
- `bash`, `python3`, `curl`
- [OpenClaw](https://github.com/openclaw/openclaw) (for routing optimization)

### Quick Start

```bash
# Clone
git clone https://github.com/windseeker1111/flowclaw.git ~/clawd/skills/flowclaw

# Make executable
chmod +x ~/clawd/skills/flowclaw/scripts/*.sh
chmod +x ~/clawd/skills/flowclaw/scripts/*.py

# Add alias (optional)
echo 'alias flowclaw="bash ~/clawd/skills/flowclaw/scripts/flowclaw.sh"' >> ~/.zshrc
source ~/.zshrc
```

### Adding Providers

**Anthropic (Claude Max)** — unlimited accounts:
```bash
claude login                                     # Sign in with each account
bash ~/clawd/skills/flowclaw/scripts/save-account.sh  # Save token with label
# Repeat for each Anthropic account
```

**Google Gemini CLI:**
```bash
openclaw models auth login --provider google-gemini-cli
```

**Google Antigravity:**
```bash
openclaw models auth login --provider google-antigravity
brew install --cask steipete/tap/codexbar         # Required for usage metrics
```

**OpenAI Codex:**
```bash
openclaw models auth login --provider openai-codex
```

**GitHub Copilot:**
```bash
openclaw models auth login-github-copilot
```

**Ollama (Local):**
```bash
brew install ollama && ollama pull qwen3:235b
# Auto-detected — no configuration needed
```

---

## 📋 All Commands

| Command | Description |
|---------|-------------|
| `flowclaw status [--fresh] [--json]` | Full provider usage dashboard |
| `flowclaw monitor [--json] [--cached]` | Clean usage report (no scoring) |
| `flowclaw score [--json]` | Scored ranking of all accounts |
| `flowclaw optimize [--dry-run]` | Reorder OpenClaw routing |
| `flowclaw auto` | Silent optimization (for cron) |
| `flowclaw history [N]` | Routing history with timeline |
| `flowclaw test` | Run scoring engine unit tests |
| `flowclaw help` | Show help |

### Cron Automation

```bash
# Re-optimize routing every 30 minutes
*/30 * * * * bash ~/clawd/skills/flowclaw/scripts/flowclaw.sh auto
```

---

## 🏛️ Architecture

```
flowclaw/
├── SKILL.md                     # OpenClaw skill manifest
├── README.md                    # This file
├── LICENSE                      # MIT
├── scripts/
│   ├── flowclaw.sh             # Main CLI
│   ├── provider-usage.sh        # Usage collector (Anthropic direct + OpenClaw for rest)
│   ├── scoring-engine.py        # EDF urgency scoring algorithm
│   └── save-account.sh          # Anthropic account setup helper
└── config/                      # Auto-generated, gitignored
    ├── flowclaw-state.json     # Current routing state
    └── flowclaw-history.jsonl  # Routing decision log
```

---

## 🔒 Security

- OAuth tokens stored at `~/.openclaw/usage-tokens/` with `600` permissions
- No tokens or credentials in this repository
- Tokens are read-only — FlowClaw never modifies your credentials
- All API calls use HTTPS

---

## 🤝 Contributing

PRs welcome! Adding a new provider:

1. If OpenClaw already supports the provider, it's automatic — FlowClaw picks it up via `openclaw status --usage --json`
2. For custom providers, add a collector in `provider-usage.sh` and scorer in `scoring-engine.py`

The scoring engine is a pure function: usage JSON in → ranked recommendations out.

---

## 📜 License

MIT — see [LICENSE](LICENSE)

---

<p align="center">
  🦞<br>
  <i>A skill for <a href="https://github.com/openclaw/openclaw">OpenClaw</a></i><br>
  <i>LLM subscription usage monitoring and load balancing.</i>
</p>
