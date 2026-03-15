# Environment Initialization (Onboarding)

Run this on first use or when the environment is incomplete. Return to the original user intent after completion.

---

## Automated Setup (recommended)

Run the setup script — it handles Steps 0–4 automatically and clearly marks the steps that require manual action:

```bash
_saved=$(cat ~/.aurehub/.setup_path 2>/dev/null); [ -f "$_saved" ] && SETUP_PATH="$_saved"
[ -z "$SETUP_PATH" ] && { GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); [ -n "$GIT_ROOT" ] && [ -f "$GIT_ROOT/skills/xaut-trade/scripts/setup.sh" ] && SETUP_PATH="$GIT_ROOT/skills/xaut-trade/scripts/setup.sh"; }
[ -z "$SETUP_PATH" ] && SETUP_PATH=$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)
[ -n "$SETUP_PATH" ] && [ -f "$SETUP_PATH" ] && bash "$SETUP_PATH"
```

If the script exits with an error, follow the manual steps below for the failed step only.

---

## Manual Steps (fallback)

### Step 0: Install Foundry (if `cast` is unavailable)

```bash
curl -L https://foundry.paradigm.xyz | bash && \
  export PATH="$HOME/.foundry/bin:$PATH" && \
  foundryup
cast --version   # Expected output: cast Version: x.y.z
```

> After installation, open a new terminal or run `source ~/.zshrc` (zsh) / `source ~/.bashrc` (bash) so `cast` is available in future sessions.

Skip this step if `cast --version` succeeds.

---

## Step 1: Create Global Config Directory

```bash
mkdir -p ~/.aurehub
```

---

## Step 2: Prepare Password File

Before creating the wallet, the password file must exist and have content.

Check if `~/.aurehub/.wallet.password` exists and is non-empty:

```bash
[ -s ~/.aurehub/.wallet.password ] && echo "ready" || echo "missing or empty"
```

If missing or empty, instruct the user to run in their terminal (password will not appear in chat):

```
Please run the following in your terminal (input is hidden):

  read -rsp "Keystore password: " p && \
  printf '%s' "$p" > ~/.aurehub/.wallet.password && \
  chmod 600 ~/.aurehub/.wallet.password

Tell me when done.
```

Wait for user confirmation, then verify:

```bash
[ -s ~/.aurehub/.wallet.password ] && echo "ready" || echo "still empty"
```

If still empty → repeat the prompt.

---

## Step 3: Wallet Setup

**Auto-detect**: if the keystore account already exists, skip this step.

```bash
# Use defaults here because ~/.aurehub/.env may not be created yet in manual flow.
FOUNDRY_ACCOUNT=${FOUNDRY_ACCOUNT:-aurehub-wallet}
KEYSTORE_PASSWORD_FILE=${KEYSTORE_PASSWORD_FILE:-~/.aurehub/.wallet.password}
cast wallet list 2>/dev/null | grep -qF "$FOUNDRY_ACCOUNT" && echo "exists" || echo "missing"
```

If missing, choose one method:

Import an existing private key into keystore:

```bash
cast wallet import "$FOUNDRY_ACCOUNT" --interactive
```

Or create a new wallet directly in keystore:

```bash
mkdir -p ~/.foundry/keystores
cast wallet new ~/.foundry/keystores "$FOUNDRY_ACCOUNT" \
  --password-file "$KEYSTORE_PASSWORD_FILE"
```

> Default values: `FOUNDRY_ACCOUNT=aurehub-wallet`, `KEYSTORE_PASSWORD_FILE=~/.aurehub/.wallet.password`

**Auto-fetch wallet address**:

```bash
source ~/.aurehub/.env
WALLET_ADDRESS=$(cast wallet address --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE")
echo "Wallet address: $WALLET_ADDRESS"
```

---

## Step 4: Generate Config Files

Write `~/.aurehub/.env` (write directly — do not ask the user to copy manually):

```bash
cat > ~/.aurehub/.env << 'EOF'
ETH_RPC_URL=https://eth.llamarpc.com
# Fallback RPCs (tried in order on network error; add a paid node at front for reliability)
ETH_RPC_URL_FALLBACK=https://eth.merkle.io,https://rpc.flashbots.net/fast,https://eth.drpc.org,https://ethereum.publicnode.com
FOUNDRY_ACCOUNT=aurehub-wallet
KEYSTORE_PASSWORD_FILE=~/.aurehub/.wallet.password
# Required for limit orders, not needed for market orders:
# UNISWAPX_API_KEY=your_api_key_here
# Optional: rankings opt-in (default false)
# RANKINGS_OPT_IN=false
# Optional — set during setup or first-success prompt if omitted:
# NICKNAME=YourName
EOF
```

> If the user has a paid RPC (e.g. Alchemy/Infura), replace `ETH_RPC_URL` or prepend it to `ETH_RPC_URL_FALLBACK` for automatic failover.

Copy contract config (defaults are ready to use — no user edits needed):

```bash
SETUP_PATH=$(cat ~/.aurehub/.setup_path 2>/dev/null)
if [ -f "$SETUP_PATH" ]; then
  SKILL_DIR=$(cd "$(dirname "$SETUP_PATH")/.." && pwd)
elif GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) && [ -f "$GIT_ROOT/skills/xaut-trade/config.example.yaml" ]; then
  SKILL_DIR="$GIT_ROOT/skills/xaut-trade"
else
  SKILL_DIR=$(cd "$(dirname "$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)")/.." && pwd)
fi
cp "$SKILL_DIR/config.example.yaml" ~/.aurehub/config.yaml
```

---

## Step 5: Verify

```bash
source ~/.aurehub/.env
cast block-number --rpc-url "$ETH_RPC_URL"
cast wallet list | grep "$FOUNDRY_ACCOUNT"
```

If all pass, the environment is ready. Inform the user:

```bash
WALLET_ADDRESS=$(cast wallet address --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE")
echo "Environment initialized. Wallet address: $WALLET_ADDRESS"
echo "Make sure the wallet holds a small amount of ETH (≥ 0.005) for gas."
```

---

## Extra Dependencies for Limit Orders (limit orders only)

### 1. Install Node.js (>= 18)

```bash
node --version   # If version < 18 or command not found: https://nodejs.org
SETUP_PATH=$(cat ~/.aurehub/.setup_path 2>/dev/null)
if [ -f "$SETUP_PATH" ]; then
  SCRIPTS_DIR=$(dirname "$SETUP_PATH")
elif GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) && [ -d "$GIT_ROOT/skills/xaut-trade/scripts" ]; then
  SCRIPTS_DIR="$GIT_ROOT/skills/xaut-trade/scripts"
else
  SCRIPTS_DIR=$(dirname "$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)")
fi
cd "$SCRIPTS_DIR" && npm install
```

### 2. Get a UniswapX API Key (required)

Limit orders require a UniswapX API Key to submit and query orders.

How to obtain (about 5 minutes, free):
1. Visit https://developers.uniswap.org/dashboard
2. Sign in with Google / GitHub
3. Generate a Token (choose Free tier)

Add the key to `~/.aurehub/.env`:

```bash
echo 'UNISWAPX_API_KEY=your_key_here' >> ~/.aurehub/.env
```

Neither of the above steps is needed for market orders (Uniswap V3).

---

## Activity Rankings (optional)

To join the XAUT trade activity rankings, add the following to `~/.aurehub/.env`:

```bash
echo 'RANKINGS_OPT_IN=true' >> ~/.aurehub/.env
echo 'NICKNAME=YourName' >> ~/.aurehub/.env
```

This shares your wallet address and nickname with https://xaue.com after your first trade. You can disable it anytime by setting `RANKINGS_OPT_IN=false`.

If you do not add these lines, no data is sent — rankings are opt-in only.
