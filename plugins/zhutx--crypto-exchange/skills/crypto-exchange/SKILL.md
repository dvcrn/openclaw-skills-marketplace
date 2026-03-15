---
name: crypto-exchange
description: "Cryptocurrency exchange service for LightningEX API supporting multi-mode interaction - natural language chat, CLI commands, and web UI. Use when user wants to swap/exchange cryptocurrencies, check exchange rates, view supported tokens, or manage crypto transactions. Triggers on phrases like \"exchange crypto\", \"swap tokens\", \"convert USDT to ETH\", \"check crypto rates\", \"open exchange UI\", \"lightningex\", or CLI commands like \"crypto-exchange\"."
---

# Crypto Exchange Skill (LightningEX)

A versatile cryptocurrency exchange service powered by LightningEX API with three interaction modes:
- **Chat Mode**: Natural language conversation for swaps and queries
- **CLI Mode**: Command-line interface for scripting and automation  
- **UI Mode**: Web-based DeFi interface for visual trading

## Quick Start

### Chat Mode (Default)
Simply talk to perform exchanges:
- "Swap 100 USDT to ETH"
- "What's the exchange rate for BTC to USDT?"
- "Show me supported tokens"
- "Check order status I1Y0EFP31Rwu"

### CLI Mode - Interactive Wizard (Default)

**Setup (one-time):**
```bash
# Create symlink for easy command access
sudo ln -sf ~/.openclaw/workspace/skills/crypto-exchange/scripts/cli.py /usr/local/bin/crypto-exchange

# Or use Python directly without symlink
python3 ~/.openclaw/workspace/skills/crypto-exchange/scripts/cli.py
```

**Run the wizard:**
```bash
# Start interactive wizard (recommended)
crypto-exchange
# or
crypto-exchange wizard
```

The wizard will guide you through:
1. Load available currencies
2. Select currency to send
3. Select network for sending
4. Select currency to receive
5. Select network for receiving (with pair validation)
6. Enter exchange amount
7. Enter receive address
8. Confirm and place order
9. Auto-monitor order progress with deposit instructions

**Features:**
- Step 5 automatically filters networks that support the trading pair
- Step 8 shows deposit address and QR code after order creation
- Step 9 auto-monitors order progress with progress bar until completion

### CLI Mode - Direct Commands

> **Note:** If you haven't created the symlink, use `python3 ~/.openclaw/workspace/skills/crypto-exchange/scripts/cli.py` instead of `crypto-exchange`

```bash
# Get pair info
crypto-exchange pair --send ETH --receive BTC --send-network BNB --receive-network BSC

# Check exchange rate
crypto-exchange rate --send ETH --receive BTC --amount 0.1

# Validate address
crypto-exchange validate --currency BTC --address 0x... --network BSC

# Place order directly (advanced users)
crypto-exchange order --send BTC --receive ETH --amount 0.123 --address 0x...

# Check order status
crypto-exchange status --id I1Y0EFP31Rwu

# Monitor order until complete
crypto-exchange monitor --id I1Y0EFP31Rwu

# List supported currencies
crypto-exchange currencies

# Launch web UI
crypto-exchange ui --port 8080
```

### UI Mode
```bash
crypto-exchange ui --port 8080
```
Then open http://localhost:8080 in your browser for the DeFi-style trading interface.
