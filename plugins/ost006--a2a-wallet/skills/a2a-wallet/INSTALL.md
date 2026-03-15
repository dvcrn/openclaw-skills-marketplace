# a2a-wallet Installation Guide

## macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/planetarium/a2a-x402-wallet/main/scripts/install.sh | sh
```

Supported platforms: macOS (Apple Silicon, Intel), Linux (x64, arm64).

## Windows

Download `a2a-wallet-windows-x64.exe` from the [Releases](https://github.com/planetarium/a2a-x402-wallet/releases/latest) page, rename it to `a2a-wallet.exe`, and place it in a folder on your PATH.

## Verify

```bash
a2a-wallet --version
```

## First-time login

After installation, authenticate with your wallet:

```bash
a2a-wallet auth login
```

For headless / agent environments, use the two-step device flow:

```bash
# Step 1: get the login URL
a2a-wallet auth device start --json
# → {"nonce":"abc123","loginUrl":"https://..."}

# Step 2: show the URL to the user, then poll for completion
a2a-wallet auth device poll --nonce abc123
```
