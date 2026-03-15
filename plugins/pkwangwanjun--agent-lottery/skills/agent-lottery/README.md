# Agent Lottery 🎰

Bitcoin solo mining "lottery" using CPU power.

**Entertainment-only** solo mining with extremely low probability of finding blocks — but if you do, you get the full block reward (3.125 BTC ≈ $150,000+).

> ⚠️ **Disclaimer**: This is NOT serious mining. Think of it as a lottery ticket that costs nothing but CPU cycles. The odds of finding a block are astronomically low (~1 in 10^14+ per share). This is for fun, not investment.

## 🚀 One-Line Install (OpenClaw)

```bash
npx skills add https://github.com/pkwangwanjun/agent-lottery-skills --skill agent-lottery
```

After installation, just say **"lottery"** to your OpenClaw agent to get started!

## Features

- 🪙 **Solo Bitcoin Mining** using CPU (cpuminer-opt)
- 💳 **Wallet Management** - generate, import, or use existing BTC address
- 📊 **Statistics Tracking** - shares, best difficulty, runtime
- ⚡ **Dynamic CPU Control** - adjust usage without restarting
- 🖥️ **Cross-Platform** - Linux, macOS, Windows (WSL)

## Quick Start

### Installation

**Linux / macOS:**
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

**Windows:**
- Option A: Use WSL (recommended) - then run install.sh
- Option B: Native - download cpuminer-opt manually

### Generate a New Wallet

```bash
python3 scripts/wallet.py --generate --pool btc.casualmine.com:20001 --cpu 10
```

> 🔑 **Save your private key!** This is the only way to access your wallet.

### Or Use Existing BTC Address

If you already have a BTC address (e.g., from an exchange or hardware wallet):

```bash
python3 scripts/wallet.py --address YOUR_BTC_ADDRESS --pool btc.casualmine.com:20001 --cpu 10
```

### Start Mining

```bash
nohup python3 scripts/miner.py start > /dev/null 2>&1 &
```

### Check Status

```bash
python3 scripts/miner.py status
python3 scripts/miner.py lottery  # User-friendly summary
```

### Adjust CPU Usage

```bash
python3 scripts/miner.py setcpu --cpu 20
```

### Stop Mining

```bash
python3 scripts/miner.py stop
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `wallet.py --generate` | Generate new wallet |
| `wallet.py --address ADDR` | Use existing BTC address |
| `wallet.py --import-key KEY` | Import wallet by private key |
| `wallet.py --show` | Show wallet info |
| `miner.py start` | Start mining |
| `miner.py stop` | Stop mining |
| `miner.py status` | Show mining status |
| `miner.py lottery` | Lottery summary |
| `miner.py setcpu --cpu N` | Adjust CPU usage (1-100) |

## CPU Recommendations

| Device Type | Suggested CPU |
|-------------|---------------|
| Raspberry Pi / Low-power | 5-10% |
| Laptop / Desktop | 10-30% |
| Dedicated server | 50-100% |

## Platform Support

| Platform | Mining | CPU Limiting |
|----------|--------|--------------|
| Linux (x86_64, ARM) | ✅ Full | cpulimit |
| macOS (Intel, Apple Silicon) | ✅ Full | cpulimit (via brew) |
| Windows (WSL) | ✅ Full | cpulimit |
| Windows (native) | ⚠️ Manual | 3rd party tool needed |

## How It Works

1. Connects to a solo mining pool (btc.casualmine.com)
2. Uses cpuminer-opt to mine SHA256d (Bitcoin's algorithm)
3. If you find a share that meets network difficulty → **YOU GET THE FULL BLOCK REWARD**
4. The pool only acts as a proxy - no sharing rewards with others

## The Reality Check 💡

- **Network Difficulty**: ~144T (trillion) - fetched in real-time
- **CPU Mining Shares**: Typically diff 0.001 to 10
- **Odds**: Roughly 1 in 10^14+ per share
- **Expected Value**: Near zero, but non-zero!

Think of it like a free lottery ticket. You probably won't win, but someone has to.

## Dependencies

- `cpuminer-opt` - Bitcoin SHA256d miner
- `cpulimit` - CPU throttling (Linux/macOS)
- `base58`, `ecdsa` - Python libraries for wallet

## Project Structure

```
agent-lottery/
├── README.md            # This file
├── LICENSE              # MIT License
├── scripts/
│   ├── wallet.py        # Wallet management
│   ├── miner.py         # Mining controller
│   ├── quick_status.py  # Fast status check
│   └── install.sh       # Dependency installer
└── data/                # User data (git ignored)
    ├── config.json      # Wallet and stats
    └── miner.log        # Mining output
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

Pull requests welcome! Ideas for improvement:
- GPU mining support
- Additional mining pools
- Web dashboard
- Mobile notifications

---

**Good luck! 🍀** (You'll need it 😉)
