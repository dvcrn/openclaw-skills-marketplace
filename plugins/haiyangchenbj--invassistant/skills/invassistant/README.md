# InvAssistant — Investment Portfolio Trading Signal Checker

A CodeBuddy/WorkBuddy Skill that checks trading signals for your investment portfolio based on a configurable **"Three Red Lines"** filter system. Fetches real-time market data from Yahoo Finance, applies strategy rules, and pushes results to WeChat Work, DingTalk, or Feishu group bots.

## Features

- **Three Red Lines System** — Emotion release, technical support confirmation, and market risk assessment as mandatory entry filters (not a scoring system)
- **Configurable Watchlist** — Add/remove stocks, assign strategy types (redline/hold/pullback/satellite), tune parameters via JSON config
- **Multi-Channel Push** — Push signal reports to WeChat Work, DingTalk, Feishu group bots
- **Command Triggers** — Configure group bot commands to trigger checks (e.g., "@bot 检查持仓")
- **Modular Architecture** — Data fetcher, red line engine, and portfolio checker as independent modules

## Quick Start

### 1. Install

```bash
# Clone or copy to your CodeBuddy skills directory
cp -r invassistant-skill ~/.codebuddy/skills/invassistant

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Config

```bash
python scripts/init_config.py
```

This generates `invassistant-config.json` with default settings. Edit it to customize your watchlist and push channels.

### 3. Run

```bash
# Full portfolio check
python check_portfolio.py

# TSLA detailed analysis
python check_tsla_entry.py

# Check and push results
python scripts/portfolio_checker.py --push
```

Or simply tell CodeBuddy: "检查持仓信号" / "TSLA红线检查" / "今日信号"

## Configuration

### Stock Watchlist (`portfolio.watchlist`)

```json
{
  "symbol": "TSLA",
  "name": "Tesla",
  "strategy": "redline",
  "params": {
    "emotion_drop_threshold": -4,
    "consecutive_days": 3,
    "bounce_threshold": 1.5,
    "volume_ratio": 1.2,
    "entry_size": 0.3
  }
}
```

| Strategy | Description | Action |
|----------|-------------|--------|
| `redline` | Three Red Lines filter | Entry only when ALL three pass |
| `hold` | Permanent hold | No buy, no sell |
| `pullback` | Pullback add | Alert when pullback >= threshold |
| `satellite` | Satellite position | Do nothing |

### Push Channels (`adapters`)

| Channel | Config Key | Setup |
|---------|-----------|-------|
| WeChat Work | `wechatwork` | Group Settings → Bot → Custom Bot → Copy Webhook URL |
| DingTalk | `dingtalk` | Group Settings → Smart Assistant → Add Bot → Custom |
| Feishu | `feishu` | Group Settings → Bot → Add Bot → Custom Bot |

Set `enabled: true` and fill in `webhook_url` to activate a channel.

### Command Triggers (`commands`)

Map group bot commands to actions:

```json
{
  "检查持仓": "full_check",
  "TSLA红线": "tsla_detail",
  "今日信号": "full_check"
}
```

## Project Structure

```
invassistant-skill/
├── SKILL.md                    # Skill definition (triggers, workflow, logic)
├── invassistant-config.json    # Your config (gitignored, contains webhook secrets)
├── check_portfolio.py          # Quick entry: full portfolio check
├── check_tsla_entry.py         # Quick entry: TSLA red line check
├── check_detail.py             # Quick entry: TSLA detailed analysis
├── scripts/
│   ├── init_config.py          # Generate default config
│   ├── data_fetcher.py         # Yahoo Finance data fetcher (retry, rate limit)
│   ├── redline_engine.py       # Three Red Lines engine (configurable params)
│   ├── portfolio_checker.py    # Main checker (strategy dispatch, report format)
│   ├── send_wecom.py           # WeChat Work push
│   ├── send_dingtalk.py        # DingTalk push (with HMAC signing)
│   └── send_feishu.py          # Feishu push (post / interactive card)
├── Q1_2026_交易策略.md          # Strategy reference document
├── requirements.txt
├── LICENSE
└── README.md
```

## The Three Red Lines

> **Red Lines are filters, not scores.** ALL three must pass for entry. Any single failure = NO-TRADE.

### Red Line 1: Emotion Release Drop (Most Critical)

- Single-day drop >= 4%, or
- 3+ consecutive down days

No emotion release → no mispricing → no entry reason.

### Red Line 2: Technical Stop Confirmation (Strict)

Requires **real** stop confirmation, not just "near moving average":
- Volume shrinkage after sell-off (< 70% of previous day)
- Strong MA support = lower shadow + up close + (volume surge 120%+ OR strong bounce >= 1.5%)
- Complete Higher Low structure (Low A → bounce → Low B > A → 2-day confirmation)

### Red Line 3: Market Not in Systemic Risk

- QQQ not down 3 consecutive days
- SPX not down 3 consecutive days
- VIX < 25

## License

MIT License - see [LICENSE](LICENSE)
