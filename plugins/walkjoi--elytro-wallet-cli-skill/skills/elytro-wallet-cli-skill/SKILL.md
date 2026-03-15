---
name: elytro-wallet-cli-skill
description: "Elytro — security-first ERC-4337 smart account wallet CLI for AI agents. On-chain 2FA, configurable spending limits, and macOS Keychain-backed vault. Send ETH, ERC-20 tokens, and batch transactions via UserOperations on Ethereum, Optimism, and Arbitrum. Account abstraction wallet with gas sponsorship, counterfactual deployment, social recovery, and guardian management."
---

# Elytro CLI — OpenClaw Agent Skill

This skill teaches an autonomous agent how to operate the Elytro CLI end-to-end.
Every command, flag, output format, and error shape is documented so the agent can
plan multi-step workflows and parse structured output without human intervention.

---

## Secret Management

### Vault Key (macOS Keychain — zero configuration)

The vault key is a 256-bit random key that decrypts the local keyring vault.

On macOS, `elytro init` generates the vault key and stores it in the **system
Keychain** automatically. Every subsequent CLI invocation loads it from Keychain
with no env vars, no SecretRef, and no user interaction. This is the only
officially supported platform.

**The user never sees, copies, or configures the vault key.** It is fully managed
by the OS.

#### Security Properties

- **Domain separation**: The encrypted vault (`keyring.json`) lives on disk; the
  decryption key lives in Keychain. Copying `~/.elytro/` to another machine is
  useless without the Keychain entry.
- **OS-level protection**: Keychain is encrypted with the user's login password and
  locked when the user is logged out or the machine is powered off.
- **Zero-fill**: The raw key buffer is zeroed in memory after the keyring is unlocked.

### Non-macOS Fallback (not recommended)

> **Warning**: Running on Windows, Linux or in containers weakens the security model.
> The vault key must be injected as an environment variable (`ELYTRO_VAULT_SECRET`),
> which is exposed to `/proc/PID/environ`, inherited by child processes before
> consume-once scrubbing, and lacks hardware-backed protection. Use at your own risk. **Users must be fully briefed on these limitations**
> On-chain SecurityHook (2FA + spending limits) is strongly recommended as
> compensating control.

If you must run on Non-macOS:

1. `elytro init` prints the vault key once as `ELYTRO_VAULT_SECRET="<base64>"`.
2. The agent captures this value and stores it in SecretRef.
3. On subsequent runs, OpenClaw injects it as an env var. The CLI reads it once
   and immediately deletes it from `process.env` (consume-once).

```jsonc
// openclaw.json — only needed on non-macOS
{
  "skills": {
    "entries": {
      "elytro-cli": {
        "env": {
          "ELYTRO_VAULT_SECRET": {
            "source": "env",
            "provider": "default",
            "id": "ELYTRO_VAULT_SECRET",
          },
        },
      },
    },
  },
}
```

### Optional API Keys

These improve reliability but are not required for basic operation:

| Variable             | Purpose                          | Injected Via                                     |
| -------------------- | -------------------------------- | ------------------------------------------------ |
| `ELYTRO_ALCHEMY_KEY` | Alchemy RPC (higher rate limits) | `elytro config set alchemy-key <KEY>` or env var |
| `ELYTRO_PIMLICO_KEY` | Pimlico bundler/paymaster        | `elytro config set pimlico-key <KEY>` or env var |

These can be persisted once via `config set` and don't need re-injection.

---

## First-Time Setup

An agent running against a fresh `~/.elytro/` must execute this sequence exactly once:

```bash
# Step 1: Initialize wallet
# Vault key is auto-stored in macOS Keychain. No secrets to manage.
elytro init

# Step 2: Create a smart account on a testnet
elytro account create --chain 11155420 --alias agent-primary

# Step 3: (Optional) Set API keys for better reliability
elytro config set alchemy-key "$ELYTRO_ALCHEMY_KEY"
elytro config set pimlico-key "$ELYTRO_PIMLICO_KEY"
```

The user does not need to configure any secrets. The Keychain handles vault key
storage and retrieval automatically.

**Idempotent**: Running `init` on an already-initialized wallet exits cleanly
(exit code 0) with message "Wallet already initialized."

---

## Command Reference

### Account Commands

#### `elytro account create`

```bash
elytro account create -c <chainId> [-a <name>]
elytro account create --chain <chainId> [--alias <name>]
```

- `-c, --chain` (required): Numeric chain ID.
- `-a, --alias` (optional): Human-readable name. Auto-generated if omitted (e.g. `swift-panda`).
- Computes a **counterfactual address** via CREATE2 (contract not deployed yet).
- Same owner can have multiple accounts on the same chain (unique index per account).

**Supported chains**: 1 (Ethereum), 10 (Optimism), 42161 (Arbitrum), 11155111 (Sepolia), 11155420 (OP Sepolia).

#### `elytro account list`

```bash
elytro account list                        # all accounts
elytro account list [alias|address]        # single account lookup
elytro account list -c <chainId>           # filter by chain
elytro account list --chain <chainId>      # filter by chain (long form)
```

Prints table with: active marker (`→`), alias, full address (42 chars), chain name,
deployed status, recovery status.

#### `elytro account info`

```bash
elytro account info [alias|address]
```

Fetches **live on-chain data**: balance, deployment status, recovery status, explorer link.
Requires RPC access. Defaults to current account.

#### `elytro account switch`

```bash
elytro account switch <alias|address>
```

Changes the active account. **Always pass alias or address** — without arguments
it shows an interactive selector (not suitable for agents).

After switching, SDK and wallet client re-initialize to the new account's chain.

#### `elytro account activate`

```bash
elytro account activate [alias|address] [--no-sponsor]
```

Deploys the smart contract wallet on-chain. The address must have ETH or sponsorship
must succeed. `--no-sponsor` forces self-pay.

**Important**: Fund the CREATE2 address _before_ activation. The address is
deterministic — send ETH to it pre-deployment.

---

### Transaction Commands

All transaction commands use the unified `--tx` flag:

```
--tx "to:0xAddress,value:0.1,data:0xAbcDef"
```

**Rules**:

- `to` is always required (valid Ethereum address).
- At least one of `value` or `data` must be present.
- `value` is in ETH (e.g. `"0.001"`), not wei.
- `data` is hex-encoded calldata (`0x` prefix, even length).
- Multiple `--tx` flags → batch (`executeBatch`). Order preserved.

#### `elytro tx send`

```bash
elytro tx send [account] --tx <spec> [--no-sponsor] [--no-hook] [--userop <json>]
```

```bash
# ETH transfer
elytro tx send --tx "to:0xRecipient,value:0.001"

# Contract call
elytro tx send --tx "to:0xContract,data:0xa9059cbb..."

# Batch
elytro tx send --tx "to:0xA,value:0.1" --tx "to:0xB,data:0xab"

# From specific account
elytro tx send my-alias --tx "to:0xAddr,value:0.01"

# Skip sponsorship
elytro tx send --tx "to:0xAddr,value:0.01" --no-sponsor

# Skip 2FA hook
elytro tx send --tx "to:0xAddr,value:0.01" --no-hook

# Send pre-built UserOp (skips build step entirely)
elytro tx send --userop '{"sender":"0x...","callData":"0x...",...}'
```

**Pipeline**: resolve account → balance pre-check → build UserOp → fee data →
estimate gas (fakeBalance) → sponsor → sign → send → wait for receipt.

**Critical**: Sponsor covers gas only, **not** the transaction value. If sending
0.1 ETH, the account must hold ≥ 0.1 ETH regardless of sponsorship.

**Exit codes**: 0 = success, 1 = error or execution reverted.

#### `elytro tx build`

```bash
elytro tx build [account] --tx "to:0xAddr,value:0.1" [--no-sponsor]
```

Same pipeline as `send` but stops before signing. Outputs the full unsigned UserOp
as JSON (bigints serialized as hex). Useful for inspection or piping into
`tx send --userop`.

#### `elytro tx simulate`

```bash
elytro tx simulate [account] --tx "to:0xAddr,value:0.1" [--no-sponsor]
```

Dry-run showing: tx type, gas breakdown, max cost in ETH, sponsor status, balance,
and warnings if balance insufficient. Does not sign or send. For contract calls,
also checks whether the target address has deployed code.

---

### Query Commands

All query commands output **structured JSON**:

```json
{ "success": true, "result": { ... } }
{ "success": false, "error": { "code": -32001, "message": "...", "data": { ... } } }
```

Error codes follow JSON-RPC conventions. Parse stdout as JSON for programmatic use.

#### `elytro query balance`

```bash
elytro query balance [alias|address]                 # ETH balance
elytro query balance [alias|address] --token 0xAddr  # ERC-20 balance
```

#### `elytro query tokens`

```bash
elytro query tokens [alias|address]
```

Lists all ERC-20 tokens with symbol, decimals, and formatted balance.
Uses Alchemy `alchemy_getTokenBalances` — requires Alchemy key.

#### `elytro query tx`

```bash
elytro query tx <hash>
```

Looks up transaction by hash on the current account's chain.

#### `elytro query chain`

```bash
elytro query chain
```

Shows chain ID, name, block number, gas price, RPC endpoint (API keys masked).

#### `elytro query address`

```bash
elytro query address <0xAddress>
```

Reports EOA vs contract, ETH balance, code size (if contract).

---

### Security Commands (2FA)

All security commands require the account to be **deployed**.

```bash
# Check hook status
elytro security status

# Install 2FA (capability: 1=sig, 2=userop, 3=both)
elytro security 2fa install [--capability <1|2|3>]

# Uninstall (normal or force)
elytro security 2fa uninstall [--force] [--force --execute]

# Bind email for OTP
elytro security email bind user@example.com

# Change email
elytro security email change new@example.com

# View/set daily spending limit (USD)
elytro security spending-limit [amount]
```

**Note**: Email bind/change and spending-limit require OTP verification (code sent
to the email). The agent must handle stdin for OTP input.

---

### Configuration Commands

#### `elytro config show`

```bash
elytro config show
```

Displays: RPC provider source (Alchemy or public), bundler provider source (Pimlico
or public), masked API keys if set, current chain info (name, ID), RPC and bundler
endpoints (with API keys masked). Human-readable output (not JSON).

#### `elytro config set`

```bash
elytro config set alchemy-key <KEY>
elytro config set pimlico-key <KEY>
```

Persists an API key to `~/.elytro/config.json`. Valid keys: `alchemy-key`,
`pimlico-key`. Once set, the key is used for all subsequent commands — no need to
set env vars each time. After setting, shows the updated RPC/bundler endpoints.

#### `elytro config remove`

```bash
elytro config remove alchemy-key
elytro config remove pimlico-key
```

Removes a persisted API key and reverts to the public endpoint.

---

## Output Parsing Rules

For **tx** and **query** commands, always parse stdout as JSON:

```typescript
const result = JSON.parse(stdout);
if (result.success) {
  // result.result contains the data
} else {
  // result.error.code (number), result.error.message (string)
}
```

**Account** commands use human-readable display (not JSON). Parse alias and address
from the output text.

Non-JSON output (spinners, headings, info lines) goes to **stderr**.

---

## Agent Workflow Patterns

### Pattern 1: Fresh Setup + Send ETH

```bash
elytro init
elytro account create --chain 11155420 --alias agent-primary
# → capture address from output
# → fund address via faucet or external transfer
elytro account activate agent-primary
elytro tx send --tx "to:0xRecipient,value:0.001"
```

### Pattern 2: Check Balance Before Transfer

```bash
BALANCE=$(elytro query balance agent-primary)
# → parse JSON: result.balance
# → verify sufficient funds (sponsor covers gas, NOT value)
elytro tx send --tx "to:0xRecipient,value:0.001"
```

### Pattern 3: Batch Multiple Operations

```bash
elytro tx send \
  --tx "to:0xAlice,value:0.01" \
  --tx "to:0xBob,value:0.02" \
  --tx "to:0xContract,data:0xa9059cbb..."
```

All packed into one UserOp (`executeBatch`), executed atomically.

### Pattern 4: Simulate → Send

```bash
elytro tx simulate --tx "to:0xAddr,value:0.5"
# → check gas cost, sponsor status, balance warnings
elytro tx send --tx "to:0xAddr,value:0.5"
```

### Pattern 5: Multi-Account Management

```bash
elytro account create --chain 11155420 --alias hot-wallet
elytro account create --chain 11155420 --alias cold-storage
elytro account switch hot-wallet
elytro tx send --tx "to:0xAddr,value:0.01"
elytro account switch cold-storage
elytro query balance
```

---

## Invariants the Agent Must Respect

1. **Always `init` before anything else.** Every command needs the vault key.
2. **Always `account create` before `activate` or `tx`.** A local account record must exist.
3. **Always `activate` before `tx send`.** Transactions require a deployed contract.
4. **Fund before `activate` if sponsorship might fail.** The CREATE2 address is deterministic.
5. **Sponsor covers gas, not value.** If sending ETH, the account needs that ETH.
6. **Chain is per-account.** Switching accounts may change the active chain.
7. **Always pass alias/address to `account switch`.** The interactive selector is not agent-compatible.
8. **Parse JSON from `query` and `tx` commands.** Success/failure is in the `success` field.
9. **API keys are never exposed.** All error messages sanitize embedded URLs.

---

## Error Recovery

| Error Pattern                | Cause                                           | Recovery                               |
| ---------------------------- | ----------------------------------------------- | -------------------------------------- |
| "Wallet not initialized"     | No `~/.elytro/keyring.json`                     | Run `elytro init`                      |
| "Vault key not available"    | Missing `ELYTRO_VAULT_SECRET` or Keychain entry | Check SecretRef injection              |
| "Failed to decrypt vault"    | Wrong vault key                                 | Verify the correct key is in SecretRef |
| "No accounts found"          | No account created yet                          | Run `elytro account create`            |
| "Account not deployed"       | Trying to send tx before activation             | Run `elytro account activate`          |
| "Insufficient balance"       | Value exceeds account balance                   | Fund the account first                 |
| JSON-RPC error code `-32001` | RPC/bundler error                               | Check network connectivity, retry      |
| "AA21" in error              | UserOp simulation failed                        | Usually a balance or nonce issue       |

---

## Storage Layout

```
~/.elytro/
├── keyring.json      # AES-GCM encrypted EOA private key vault
├── accounts.json     # Account list (alias, address, chainId, index, owner, deployed)
└── config.json       # Chain config, current chain, API keys (persisted)
```

No plaintext key files on disk. The vault key lives in macOS Keychain or is injected
via `ELYTRO_VAULT_SECRET` environment variable. Deleting `~/.elytro/` resets local
state; on-chain contracts are unaffected.
