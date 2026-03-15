---
name: polymarket-trading-bot-skill
description: "Polymarket Trading Bot"
---

# Polymarket Trading Bot

AI-powered trading bot for Polymarket 5-minute BTC/ETH price prediction markets.

## Features

- **Accurate PTB Extraction**: Multi-layer fallback (API → HTML → Playwright → Binance)
- **Advanced AI Model**: Position + momentum + RSI + volume analysis
- **EV-Based Decisions**: Only bet when expected value > 0.05
- **Real-time Monitoring**: Auto-detect new markets and pre-fetch PTB
- **Risk Management**: Confidence threshold + odds filtering

## Quick Start

```bash
# Install dependencies
pip3 install playwright requests

# Install Playwright browser
playwright install chromium

# Run the bot
python3 auto_bot_v2.py
```

## How It Works

1. **Market Detection**: Polls Polymarket API every 2 seconds
2. **PTB Pre-fetch**: Gets Price to Beat when market appears (~10s)
3. **AI Analysis**: Triggers 40 seconds before market close
4. **Decision**: Outputs bet recommendation (betting disabled by default)

## AI Model

### Scoring System (0-100)

| Signal | Weight | Description |
|--------|--------|-------------|
| Position | 50% | Current price vs PTB (ATR-normalized) |
| Momentum | 30% | 3-min trend + 1-min micro momentum |
| RSI | 10% | Overbought/oversold correction |
| Volume | 10% | Volume confirmation |

### Betting Criteria

- Confidence ≥ 55%
- Expected Value > 0.05
- Target odds < 0.90

## Configuration

Edit `auto_bot_v2.py` to enable real betting:

```python
# Line ~155
execute_bet(slug, direction, 10)  # Uncomment to enable
```

## Files

- `auto_bot_v2.py` - Main bot script
- `ai_analyze_v2.py` - Decision engine
- `ai_trader/ai_model_v2.py` - Scoring model
- `ai_trader/playwright_ptb.py` - PTB extraction
- `logs/decisions_v2.jsonl` - Decision history

## Example Output

```
🆕 新市场: BTC | btc-updown-5m-1772806500
   结束: 14:20:00 UTC | 剩余: 296s
   📡 提前获取 PTB...
✅ PTB=68824.89 (Playwright, 14.2s)

============================================================
🔔 触发分析: BTC | btc-updown-5m-1772806500 | 剩余 39s
  💰 PTB: $68,824.89
  📊 赔率: UP=0.455 DOWN=0.545
  🤖 AI: UP | 置信度: 88%
  📈 位置: UP(45) 动量: UP(25) ATR: 1.26x
  💵 EV: +0.923 | 目标赔率: 0.455
  ✅ 满足下注条件！conf=88% ev=+0.923 odds=0.455
============================================================
```

## Safety

- **Default**: Betting disabled (dry-run mode)
- **Logs**: All decisions saved to `logs/decisions_v2.jsonl`
- **No API keys required** for monitoring mode

## Requirements

- Python 3.8+
- playwright
- requests

## License

MIT
