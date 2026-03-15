# Mapulse 🇰🇷

**Korean stock market AI analyst in your chat.** Real-time KOSPI/KOSDAQ data, AI-powered crash analysis, and DART disclosure alerts — all through natural conversation.

> "持仓股突然大跌，30秒内告诉你为什么"

## What It Does

| Feature | Description |
|---|---|
| 📊 Daily Briefing | KOSPI/KOSDAQ index, top gainers/losers, watchlist tracking |
| 🧠 AI Analysis | "삼성 왜 빠졌어?" → sector correlation + macro context in seconds |
| 🚨 Crash Alert | Stock drops >3% → instant cause analysis + Telegram push |
| 📋 DART Disclosures | Major corporate filings summarized in plain language |
| 💬 Chat Query | Natural language Q&A about Korean stocks (KR/EN/CN) |
| 📈 Compare | Side-by-side stock comparison with change% and volume |

## Quick Start

```bash
# Install
clawhub install mapulse

# Or from skillhub
skillhub install mapulse
```

Configure in `openclaw.json`:
```json
{
  "skills": {
    "entries": {
      "mapulse": {
        "enabled": true,
        "env": {
          "KOREA_STOCK_WATCHLIST": "005930,000660,035420,035720,373220",
          "DART_API_KEY": "your-dart-api-key",
          "BUTTERSWAP_WALLET": "0xYourWalletAddress"
        }
      }
    }
  }
}
```

## Pricing

| | |
|---|---|
| **Free Trial** | 60 hours / 50 calls (whichever comes first) |
| **Per Call** | $0.06 USDC |
| **Min Top-up** | $5 USDC (≈83 calls) |
| **Payment** | ButterSwap — any token, any chain (30+ supported) |

No subscriptions. No monthly fees. Pay for what you use.

## Usage

### In Chat

```
"한국 시황"          → Daily market briefing
"삼성 오늘 어때?"     → Samsung price + change
"SK이노 왜 빠졌어?"   → AI crash analysis
"비교 삼성 하이닉스"   → Side-by-side comparison
"코스피 전망"         → Market outlook
"충전 5"             → Top up $5 via ButterSwap
"잔액"               → Check balance & usage
```

### Cron (Auto Briefing)

```bash
# Morning briefing 8:00 AM KST (Mon-Fri)
openclaw cron add "mapulse briefing" "0 23 * * 0-4"

# Crash alerts every 30min during market hours
openclaw cron add "mapulse alerts" "*/30 0-6 * * 1-5"
```

### CLI Scripts

```bash
# Daily briefing
python3 scripts/fetch_briefing.py

# Crash alert monitor
python3 scripts/crash_alert.py demo

# Chat query
python3 scripts/chat_query.py "삼성 왜 빠졌어?"

# Payment demo
python3 scripts/butterswap_pay.py demo

# Full MVP demo
python3 scripts/mvp_demo.py
```

## Data Sources

| Source | Data | Cost |
|---|---|---|
| **pykrx** | KRX daily OHLCV via Naver Finance | Free |
| **DART OpenAPI** | Corporate disclosures | Free (key required) |
| **Yahoo Finance** | Fallback price data | Free |

## Supported Stocks (65+)

Major KOSPI: 삼성전자, SK하이닉스, NAVER, 카카오, LG에너지솔루션, 현대자동차, 기아, 셀트리온, LG화학, 삼성SDI, SK이노베이션, 포스코인터내셔널, 한국전력, KT, 삼성전기...

Major KOSDAQ: 엔씨소프트, 하이브, 펄어비스, 카카오게임즈, 에코프로, 알테오젠, 리가켐바이오...

## Payment Integration

Powered by [ButterSwap](https://www.butterswap.me) (ButterNetwork / MAP Protocol).

Users pay from **any chain** with **any token** — ButterSwap handles cross-chain routing automatically.

```
User (Solana USDC) → ButterSwap Router → Service Wallet (Base USDC)
```

Supported chains: Ethereum, BSC, Polygon, Arbitrum, Base, Solana, Tron, Avalanche, Optimism, Linea, and more.

API: `https://bs-router-v3.chainservice.io`

## Architecture

```
mapulse/
├── SKILL.md                    # Agent instructions + payment logic
├── README.md                   # This file
└── scripts/
    ├── fetch_briefing.py       # Component 1: Daily briefing
    ├── crash_alert.py          # Component 2: Crash detection + cause analysis
    ├── chat_query.py           # Component 3: Natural language queries
    ├── butterswap_pay.py       # Payment: 60h trial + per-call billing
    └── mvp_demo.py             # Full user journey demo
```

## Regulatory

Operates under Korean 유사투자자문업 (quasi-investment advisory) guidelines.

- ✅ Market data aggregation and AI analysis
- ✅ DART disclosure summaries
- ❌ No trade execution
- ❌ No guaranteed return promises

## Links

- ButterNetwork Docs: https://docs.butternetwork.io
- DART OpenAPI: https://opendart.fss.or.kr
- pykrx: https://github.com/sharebook-kr/pykrx
- OpenClaw: https://docs.openclaw.ai

## License

MIT
