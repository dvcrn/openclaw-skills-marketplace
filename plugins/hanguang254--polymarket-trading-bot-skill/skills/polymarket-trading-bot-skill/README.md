# Polymarket Trading Bot

AI-powered automated trading bot for Polymarket 5-minute BTC/ETH price prediction markets.

## Installation

```bash
pip3 install playwright requests
playwright install chromium
```

## Usage

```bash
python3 auto_bot_v2.py
```

## Features

- Multi-layer PTB extraction (Playwright + fallbacks)
- Advanced AI scoring model (position + momentum + RSI + volume)
- EV-based betting decisions
- Real-time market monitoring
- Decision logging

## Configuration

To enable real betting, edit `auto_bot_v2.py` line 155:

```python
execute_bet(slug, direction, 10)  # Uncomment this line
```

## Safety

Default mode is dry-run (no real bets). All decisions are logged to `logs/decisions_v2.jsonl`.
