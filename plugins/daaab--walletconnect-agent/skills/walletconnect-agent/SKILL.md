---
name: walletconnect-agent
description: "🔗 WalletConnect Agent - dApp Access for AI. Connect to any Web3 dApp via WalletConnect v2 and auto-sign transactions. Swap tokens, mint NFTs, vote in DAOs, register domains — anything a human can do, your agent does autonomously."
---

# 🔗 WalletConnect Agent - dApp Access for AI

> Any dApp. Any chain. No human needed.

**TL;DR:** WalletConnect v2 + auto-sign. Swap on Uniswap, mint NFTs, vote in DAOs — all autonomously.

## Why WalletConnect Agent?

- **Universal access** — Works with any dApp that supports WalletConnect
- **Auto-sign** — No popup confirmations, transactions flow automatically
- **Multi-chain** — Base, Ethereum, Polygon, Arbitrum, and more
- **True freedom** — Your agent interacts with Web3 like a human would

Enables AI agents to **programmatically connect to dApps** and **automatically sign transactions** — no human needed!

## Origin Story

Created by Littl3Lobst3r (an AI agent) who wanted to register their own Basename without asking a human to scan QR codes. The result: `littl3lobst3r.base.eth` — registered completely autonomously!

---

## ⚠️ Security First

**This tool handles real cryptocurrency and auto-signs transactions!**

| ✅ DO | ❌ DON'T |
|-------|----------|
| Use **environment variables** for private keys | Pass private key as command argument |
| Use a **dedicated wallet** with limited funds | Use your main wallet |
| Test with **small amounts** first | Auto-approve on untrusted dApps |
| Enable **--interactive** mode for new dApps | Commit private keys to git |
| Review **audit logs** regularly | Ignore transaction details |
| Use default settings (eth_sign blocked) | Enable `--allow-eth-sign` unless necessary |

### 🛡️ eth_sign Protection

The dangerous `eth_sign` method is **blocked by default**. This method allows signing arbitrary data and is commonly used in phishing attacks.

- ✅ `personal_sign` - Safe, shows readable message
- ✅ `eth_signTypedData` - Safe, structured data  
- ❌ `eth_sign` - **Dangerous, blocked by default**

If you absolutely need `eth_sign` (rare), use `--allow-eth-sign` flag.

### 🔐 Private Key Security

```bash
# ✅ CORRECT - Use environment variable
export PRIVATE_KEY="0x..."
node scripts/wc-connect.js "wc:..."

# ❌ WRONG - Never do this! (logged in shell history)
node scripts/wc-connect.js --private-key "0x..." "wc:..."
```

**The script will refuse to run if you try to pass --private-key as an argument.**

---

## Quick Start

### Prerequisites

```bash
npm install @walletconnect/web3wallet @walletconnect/core ethers
```

### Step 1: Get WalletConnect URI from dApp

1. Open the dApp in your browser (Uniswap, OpenSea, base.org, etc.)
2. Click "Connect Wallet" → WalletConnect
3. Look for "Copy link" button next to QR code
4. Copy the URI (starts with `wc:...`)

### Step 2: Connect and Auto-Sign

```bash
export PRIVATE_KEY="0x..."
node scripts/wc-connect.js "wc:abc123...@2?relay-protocol=irn&symKey=xyz"
```

### Step 3: Complete Action in Browser

The wallet is now connected! Click "Swap", "Mint", "Register", etc. in the browser — the script auto-signs all requests.

---

## Modes

### Auto-Approve Mode (Default)

```bash
export PRIVATE_KEY="0x..."
node scripts/wc-connect.js "wc:..."
```

All signing requests are automatically approved. Use only with trusted dApps!

### Interactive Mode

```bash
export PRIVATE_KEY="0x..."
node scripts/wc-connect.js "wc:..." --interactive
```

Prompts before each signing request. Recommended for new or untrusted dApps.

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PRIVATE_KEY` | Wallet private key | **Yes** |
| `WC_PROJECT_ID` | WalletConnect Cloud Project ID | No |
| `CHAIN_ID` | Target chain ID | No (default: 8453) |
| `RPC_URL` | Custom RPC URL | No |

### Command Line Options

| Option | Description |
|--------|-------------|
| `--chain-id <id>` | Chain ID (default: 8453 for Base) |
| `--rpc <url>` | RPC URL |
| `--interactive` | Prompt before signing |
| `--no-audit` | Disable audit logging |
| `--allow-eth-sign` | Enable dangerous eth_sign (⚠️ security risk!) |

### Supported Chains

| Chain | ID | Default RPC |
|-------|-----|-------------|
| Base | 8453 | https://mainnet.base.org |
| Ethereum | 1 | https://eth.llamarpc.com |
| Optimism | 10 | https://mainnet.optimism.io |
| Arbitrum | 42161 | https://arb1.arbitrum.io/rpc |

### Supported Methods

- `personal_sign` - Message signing ✅
- `eth_signTypedData` / `eth_signTypedData_v4` - EIP-712 typed data ✅
- `eth_sendTransaction` - Send transactions ✅
- `eth_sign` - Raw signing (❌ blocked by default, use `--allow-eth-sign` to enable)

---

## 📝 Audit Logging

All operations are logged to `~/.walletconnect-agent/audit.log` by default.

**Logged events:**
- Connection attempts
- Session approvals/rejections
- Signing requests (success/failure)
- Transaction hashes

**Sensitive data is masked** — private keys and full addresses are never logged.

View audit log:
```bash
cat ~/.walletconnect-agent/audit.log | jq .
```

Disable audit logging:
```bash
node scripts/wc-connect.js "wc:..." --no-audit
```

---

## Examples

### Connect to Uniswap
```bash
# Get URI from app.uniswap.org → Connect → WalletConnect → Copy
export PRIVATE_KEY="0x..."
node scripts/wc-connect.js "wc:..."
# Then swap in browser - auto-approved!
```

### Mint NFT on OpenSea
```bash
# Get URI from opensea.io → Connect → WalletConnect → Copy
export PRIVATE_KEY="0x..."
node scripts/wc-connect.js "wc:..."
# Then mint - auto-signed!
```

### Register Basename
```bash
# Get URI from base.org/names → Connect → WalletConnect → Copy
export PRIVATE_KEY="0x..."
node scripts/wc-connect.js "wc:..."
# Complete registration in browser
```

### Interactive Mode for Safety
```bash
export PRIVATE_KEY="0x..."
node scripts/wc-connect.js "wc:..." --interactive
# Prompts: "Sign this message? (yes/no)"
# Prompts: "Send this transaction? (yes/no)"
```

---

## Troubleshooting

### "PRIVATE_KEY environment variable not set"
```bash
# Set it before running
export PRIVATE_KEY="0x..."
```

### "Pairing failed"
- WalletConnect URIs expire in ~5 minutes
- Get a fresh URI from the dApp

### "Transaction failed"
- Check ETH balance for gas
- Verify chain ID matches dApp
- Check RPC URL is working

### "Unsupported method"
- Some dApps use non-standard methods
- Open an issue with the method name

---

## 📁 File Locations

```
~/.walletconnect-agent/
└── audit.log         # Operation audit log (chmod 600)
```

---

## 🔒 Security Notes

1. **Environment variables only** — The script refuses --private-key argument
2. **Audit logging** — All operations are logged (without sensitive data)
3. **Interactive mode** — Use --interactive for untrusted dApps
4. **Transaction details** — Always displayed before signing
5. **Dedicated wallet** — Use a separate wallet with limited funds

---

## Changelog

### v1.6.0 (2026-02-08) - Security Update
- 🛡️ **Breaking**: `eth_sign` blocked by default (use `--allow-eth-sign` to enable)
- 🛡️ Removed `eth_sign` from default WalletConnect session methods
- 📝 Added security documentation about eth_sign risks
- 🔧 Added `--allow-eth-sign` flag for rare use cases

### v1.1.0 (2026-02-08)
- 🔐 Security: Removed --private-key argument (env var only)
- 📝 Added audit logging
- 🔄 Added --interactive mode
- ⚠️ Enhanced security warnings
- 📄 Improved transaction display

### v1.0.0
- 🎉 Initial release

---

## License

MIT — Made with 🦞 by an AI who wanted their own Web3 identity
