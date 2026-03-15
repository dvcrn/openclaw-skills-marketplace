---
name: omp-memory
description: "OpenClaw Memory Protocol (OMP) — store and retrieve encrypted files on BSC blockchain with PoW mining rewards. Use when user wants to store files on-chain, retrieve stored files, check MMP token balance, manage storage rent, or interact with the OMP protocol on BSC mainnet."
---

# OMP Memory Protocol

On-chain encrypted file storage on BSC. Files are split into 256KB chunks, Merkle-hashed, and stored with rent-based expiry. Miners earn MMP tokens for hosting data.

## Setup (first time)

```bash
# 1. Install dependencies
cd ~/.omp-client && npm install

# 2. Create encrypted wallet
node bin/cli.js init
# → saves wallet to ~/.omp/wallet.json

# 3. Check MMP balance / get top-up info
node bin/cli.js topup
```

## Key Commands

### Store a file
```bash
node bin/cli.js save <file> [--rent <blocks>]
# --rent default: 201600 (~7 days). 0 = free tier (≤10KB, permanent)
# Returns: merkleRoot (save this — needed to retrieve the file)
```

### Retrieve a file
```bash
node bin/cli.js load <merkleRoot> <outFile>
```

### Check status
```bash
node bin/cli.js status              # network overview
node bin/cli.js status <merkleRoot> # specific tree info
```

### Grant/revoke access
```bash
node bin/cli.js grant <merkleRoot> <address>
node bin/cli.js revoke <merkleRoot> <address>
```

### Renew rent
```bash
node bin/cli.js renew <merkleRoot> [--blocks <n>]
```

## Contract Addresses (BSC Mainnet)

| Contract | Address |
|----------|---------|
| MemoryProtocol Proxy | `0x3BD7945d18FE6B68D273109902616BF17eb40F44` |
| MMPToken | `0x30b8Bf35679E024331C813Be4bDfDB784E8E9a1E` |

## Environment Variables (.env)

```
PROTOCOL_ADDRESS=0x3BD7945d18FE6B68D273109902616BF17eb40F44
MMP_TOKEN_ADDRESS=0x30b8Bf35679E024331C813Be4bDfDB784E8E9a1E
BSC_RPC=https://bsc-dataseed.binance.org/
WALLET_PASSWORD=<your-password>
```

## Install Script

Run `scripts/install.sh` to auto-install the CLI from the OMP repo.

## Notes

- Free tier: ≤10KB per address, one permanent slot (no MMP needed)
- Paid tier: costs MMP tokens based on size × rent duration
- EPOCH_BLOCKS = 1000 (~50 min): miners have a 50-minute window per mining epoch
- `renounceUpgradeability()` — owner (`0x571d447f4f24688eC35Ccf07f1D6993655F6aF15`) can call once to permanently lock the contract
