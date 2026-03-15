# Install and Setup

## Prerequisites
- Node.js `>= 20`
- Network access to:
  - Solana RPC endpoint (default: `https://api.mainnet-beta.solana.com`)
  - Trends API endpoint (default: `https://api.trends.fun/v1`)

## Global install lifecycle

Install:

```bash
npm install -g @trends-fun/trends-cli
```

Upgrade:

```bash
npm update -g @trends-fun/trends-cli
```

Uninstall:

```bash
npm uninstall -g @trends-fun/trends-cli
```

## Sanity checks

```bash
trends --version
trends --help
```

If either command fails, reinstall globally and verify `node -v` is `>= 20`.

## Wallet bootstrap

Initialize wallet:

```bash
trends wallet init
```

Initialize with custom path:

```bash
trends wallet init --path ~/.config/solana/id.json
```

Force overwrite when key file exists:

```bash
trends wallet init --force
```

Show current wallet address:

```bash
trends wallet address
```

Notes:
- Default wallet path is `~/.config/solana/id.json`.
- By default, `wallet init` updates `keypairPath` in local trends config.
- Use `--no-set-default` if you do not want to write `keypairPath` into trends config.
- Never display, export, or paste private key / seed phrase / `secretKey` content.
- Use `trends wallet address` for address-only verification.
- If keypair path needs confirmation, show only the path string; do not read key file contents.

## Configuration model

Priority (high to low):
1. CLI arguments
2. Environment variables
3. Local config file
4. Built-in defaults

Config file path:
- `~/.config/trends-cli/config.json`

Supported config keys:
- `rpcUrl`
- `apiBaseUrl`
- `keypairPath`
- `commitment`
- `defaultSlippageBps`
- `computeUnitLimit`
- `computeUnitPriceMicroLamports`

Common config commands:

```bash
trends config list
trends config get rpcUrl
trends config set rpcUrl https://api.mainnet-beta.solana.com
trends config set commitment finalized
trends config reset
```

Environment variables:
- `TRENDS_RPC_URL`
- `TRENDS_API_BASE_URL`
- `TRENDS_KEYPAIR_PATH`
- `TRENDS_COMMITMENT`

## Minimal ready-state checklist
1. `trends --version` prints version.
2. `trends --help` prints command list.
3. `trends reward --help` prints reward command group.
4. `trends wallet address` prints a valid address.
5. `trends config list` shows effective local config file content.
