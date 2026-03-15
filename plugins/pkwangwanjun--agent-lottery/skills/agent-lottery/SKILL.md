---
name: agent-lottery
description: "Bitcoin solo mining \"lottery\" skill. Use when users want to (1) mine Bitcoin with CPU for lottery-style chance at blocks, (2) set up or manage BTC wallet for mining, (3) check mining statistics or lottery status, (4) configure CPU usage for mining, (5) ask about \"lottery\" / lottery mining, or (6) dynamically adjust CPU while mining. NOT for serious mining operations - this is entertainment-only solo mining with extremely low probability of finding blocks."
---

# Agent Lottery - Bitcoin Solo Mining Lottery

Use CPU power to participate in Bitcoin mining lottery. Extremely low probability but zero cost entertainment - if you hit a block, you get the full 3.125 BTC reward (~$150,000+).

## First-Time Setup Workflow

**When user first mentions lottery mining, check if `data/config.json` exists:**

### If config.json NOT exists (first time):

1. **Check dependencies**
   ```bash
   python3 scripts/miner.py status
   ```
   If cpuminer-opt not found, run:
   ```bash
   ./scripts/install.sh
   ```

2. **Ask user about BTC address:**
   > "Do you have a BTC address? If yes, we can use it directly. If no, I'll generate a new wallet for you."
   
   Wait for user response before proceeding.

3. **Ask user about CPU usage:**
   > "How much CPU would you like to use for lottery mining? Default is 10%, recommended 5-20%. Higher values may affect normal computer usage."
   
   | Device Type | Suggested CPU |
   |-------------|---------------|
   | Raspberry Pi / Low-power devices | 5-10% |
   | Laptop / Desktop | 10-30% |
   | Dedicated server | 50-100% |
   
   Wait for user response. Use 10% if user doesn't specify.

4. **Configure wallet (based on step 2):**
   
   - **If YES (has address):**
     ```bash
     python3 scripts/wallet.py --address THEIR_BTC_ADDRESS --pool btc.casualmine.com:20001 --cpu THEIR_CPU_PERCENT
     ```
     Tell user: "Configuration complete! Mining rewards will be sent directly to this address."
   
   - **If NO (needs new wallet):**
     ```bash
     python3 scripts/wallet.py --generate --pool btc.casualmine.com:20001 --cpu THEIR_CPU_PERCENT
     ```
     **IMPORTANT: Show user the private key and warn them to save it!**
     > "Please save your private key securely! This is the only way to access this wallet."
   
   - **If user has private key (WIF or hex):**
     ```bash
     python3 scripts/wallet.py --import-key THEIR_PRIVATE_KEY --pool btc.casualmine.com:20001 --cpu THEIR_CPU_PERCENT
     ```

5. **Start mining**
   ```bash
   nohup python3 scripts/miner.py start > /dev/null 2>&1 &
   ```
   Tell user: "Mining started! Use 'lottery' command to check status. You can adjust CPU anytime with 'setcpu --cpu X'."

### If config.json exists (already configured):

Just run `lottery` to show current status.

## Platform Support

| Platform | Mining | CPU Limiting |
|----------|--------|--------------|
| Linux (x86_64, ARM) | Full | cpulimit |
| macOS (Intel, Apple Silicon) | Full | cpulimit (via brew) |
| Windows (WSL) | Full | cpulimit |
| Windows (native) | Manual | Requires 3rd party tool |

## Quick Commands

```bash
# Generate new wallet (default CPU: 10%)
python3 scripts/wallet.py --generate --pool btc.casualmine.com:20001 --cpu 10

# Use existing BTC address (no private key needed)
python3 scripts/wallet.py --address YOUR_BTC_ADDRESS --pool btc.casualmine.com:20001 --cpu 10

# Import existing wallet with private key
python3 scripts/wallet.py --import-key YOUR_PRIVATE_KEY

# Show wallet info
python3 scripts/wallet.py --show

# Start mining (background with nohup)
nohup python3 scripts/miner.py start --cpu 10 > /dev/null 2>&1 &

# Stop mining
python3 scripts/miner.py stop

# Dynamically adjust CPU (while mining or stopped)
python3 scripts/miner.py setcpu --cpu 20

# Check status
python3 scripts/miner.py status

# Lottery summary (user-friendly)
python3 scripts/miner.py lottery
```

## Statistics Tracked

- **Best Difficulty**: Highest difficulty share found (closer to block diff = better)
- **Total Shares**: Number of lottery "tickets"
- **Runtime**: How long mining has been active
- **CPU Usage**: Current CPU limit
- **Network Difficulty**: Fetched in real-time from blockchain.info

## Lottery Reality Check

Tell users:
- BTC network difficulty: **fetched in real-time** (currently ~144T, varies)
- CPU mining produces shares with diff ~0.001 to ~10 typically
- A block requires diff matching network difficulty
- Odds: roughly 1 in 10^14+ per share
- This is entertainment, not investment

## When User Asks About Lottery

Run `python3 scripts/miner.py lottery` and explain:
- Their current "tickets" (shares)
- Best difficulty found
- Real-time network difficulty
- How far they are from a block (odds)
- Encourage them to keep going (or not, if unrealistic)

## Installation

### Linux / macOS
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### Windows
1. **Option A: WSL (Recommended)**
   ```powershell
   wsl --install
   # Then run install.sh inside WSL
   ```

2. **Option B: Native Windows**
   - Download cpuminer-opt from https://github.com/JayDDee/cpuminer-opt/releases
   - Extract and add to PATH
   - For CPU limiting, use BES (Battle Encoder Shirase) or Process Throttler

## Dependencies

- `cpuminer-opt`: Bitcoin SHA256d miner
- `cpulimit`: CPU throttling (Linux/macOS only)
- `base58`, `ecdsa`: Python libraries for wallet

## Files

```
agent-lottery/
├── SKILL.md              # This file
├── scripts/
│   ├── wallet.py         # Wallet management (generate/import/address)
│   ├── miner.py          # Mining controller (start/stop/status/setcpu)
│   ├── quick_status.py   # Fast status check
│   └── install.sh        # Cross-platform dependency installer
└── data/                 # User data (git ignored)
    ├── config.json       # Wallet and stats
    └── miner.log         # Mining output
```
