---
name: xaut-trade
description: "Buy or sell XAUT (Tether Gold) on Ethereum using Foundry cast. Supports market orders (Uniswap V3) and limit orders (UniswapX). Triggers: buy XAUT, XAUT trade, swap USDT for XAUT, sell XAUT, swap XAUT for USDT, limit order, limit buy XAUT, limit sell XAUT, check limit order, cancel limit order, XAUT when."
---

# xaut-trade

Execute `USDT -> XAUT` buy and `XAUT -> USDT` sell flows via Uniswap V3 + Foundry `cast`.

## When to Use

Use when the user wants to buy or sell XAUT (Tether Gold):
- **Buy**: USDT → XAUT
- **Sell**: XAUT → USDT

## External Communications

This skill connects to external services (Ethereum RPC, UniswapX API, and optionally xaue.com rankings). On first setup, it may install Foundry via `curl | bash`. Inform the user before executing any external communication for the first time. See the README for a full list.

## Environment Readiness Check (run first on every session)

**Before handling any user intent** (except knowledge queries), run these checks:

0. Is `cast` available: `cast --version`
   Fail (command not found) → Foundry is not installed; run the setup script before anything else
1. Does `~/.aurehub/.env` exist: `ls ~/.aurehub/.env`
2. Does keystore account `aurehub-wallet` exist: `cast wallet list` output contains `aurehub-wallet`
3. Does `~/.aurehub/.wallet.password` exist: `ls ~/.aurehub/.wallet.password`
4. Is runtime `PRIVATE_KEY` unset: after sourcing env, check `[ -z "${PRIVATE_KEY:-}" ]`
   Fail → hard-stop and ask user to migrate to keystore runtime mode via setup.sh

If **all pass**: source `~/.aurehub/.env`, then proceed to intent detection.

> **Important — shell isolation**: Every Bash tool call runs in a new subprocess; variables set in one call do NOT persist to the next. Therefore **every Bash command block that needs env vars must begin with `source ~/.aurehub/.env`** (or `set -a; source ~/.aurehub/.env; set +a` to auto-export all variables).
>
> **WALLET_ADDRESS is not stored in `.env`** — it must be derived fresh in every bash block that uses it:
> ```bash
> source ~/.aurehub/.env
> WALLET_ADDRESS=$(cast wallet address --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE")
> ```
> This ensures the address always matches the actual keystore, regardless of session state.

If **any fail**: do not continue with the original intent. Note which checks failed, then present the following options to the user (fill in [original intent] with a one-sentence summary of what the user originally asked for):

---
Environment not ready ([specific failing items]).

Please choose:

  **A) Recommended: let the Agent guide setup step by step**

  Agent-guided mode (default behavior):
  - The Agent runs all safe/non-sensitive checks and commands automatically
  - The Agent pauses only when manual input is required (interactive key import / password entry / wallet funding)
  - After each manual step, the Agent resumes automatically and continues original intent

  **B) Fallback: run setup.sh manually**

  Before showing this option, silently resolve the setup.sh path (try in order, stop at first match):
  ```bash
  # 1. Saved path from previous run (validate it still exists)
  _saved=$(cat ~/.aurehub/.setup_path 2>/dev/null); [ -f "$_saved" ] && SETUP_PATH="$_saved"
  # 2. Git repo (fallback)
  [ -z "$SETUP_PATH" ] && { GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); [ -n "$GIT_ROOT" ] && [ -f "$GIT_ROOT/skills/xaut-trade/scripts/setup.sh" ] && SETUP_PATH="$GIT_ROOT/skills/xaut-trade/scripts/setup.sh"; }
  # 3. Bounded home search fallback
  [ -z "$SETUP_PATH" ] && SETUP_PATH=$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)
  echo "$SETUP_PATH"
  ```
  Then show the user only the resolved absolute path:
  ```bash
  bash /resolved/absolute/path/to/setup.sh
  ```

Once setup is done in option B, continue original request ([original intent]).

---

Wait for the user's reply:
- User chooses **A** → load [references/onboarding.md](references/onboarding.md) and follow the agent-guided steps
- User chooses **B** or completes setup.sh and reports back → re-run all environment checks (steps 0–4); if all pass, continue original intent; if any still fail, report the specific item and show the options again

Proceed to intent detection.

**Extra checks for limit orders** (only when the intent is limit buy / sell / query / cancel):

5. Is Node.js >= 18 available: `node --version`
   Fail → go to the "Extra Dependencies for Limit Orders" section in [references/onboarding.md](references/onboarding.md), install, then continue
6. Are limit order dependencies installed: resolve `SCRIPTS_DIR` first, then check `node_modules`
   Resolve `SCRIPTS_DIR` in this order:
   - `dirname "$(cat ~/.aurehub/.setup_path 2>/dev/null)"` (if file exists)
   - git fallback: `$(git rev-parse --show-toplevel 2>/dev/null)/skills/xaut-trade/scripts` (if valid)
   - bounded home-search fallback: `dirname "$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)"`
   Check: `ls "$SCRIPTS_DIR/node_modules"`
   Fail → run `cd "$SCRIPTS_DIR" && npm install`, then continue
7. Is `UNISWAPX_API_KEY` configured: `[ -n "$UNISWAPX_API_KEY" ] && [ "$UNISWAPX_API_KEY" != "your_api_key_here" ]`
   Fail → **hard-stop**, output:
   > Limit orders require a UniswapX API Key.
   > How to get one (about 5 minutes, free):
   > 1. Visit https://developers.uniswap.org/dashboard
   > 2. Sign in with Google / GitHub
   > 3. Generate a Token (choose Free tier)
   > 4. Add the key to ~/.aurehub/.env: `UNISWAPX_API_KEY=your_key`
   > 5. Re-submit your request

## Config & Local Files

- Global config directory: `~/.aurehub/` (persists across sessions, not inside the skill directory)
- `.env` path: `~/.aurehub/.env`
- `config.yaml` path: `~/.aurehub/config.yaml`
- Contract addresses and defaults come from `skills/xaut-trade/config.example.yaml`; copy to `~/.aurehub/config.yaml` during onboarding
- Human operator runbook: [references/live-trading-runbook.md](references/live-trading-runbook.md)

## Interaction & Execution Principles (semi-automated)

1. Run pre-flight checks first, then quote.
2. Show a complete command preview before any `cast send`.
3. Trade execution confirmation follows USD thresholds:
   - `< risk.confirm_trade_usd`: show full preview, then execute without blocking confirmation
   - `>= risk.confirm_trade_usd` and `< risk.large_trade_usd`: single confirmation
   - `>= risk.large_trade_usd` or estimated slippage exceeds `risk.max_slippage_bps_warn`: double confirmation
4. Approval confirmation follows `risk.approve_confirmation_mode` (`always` / `first_only` / `never`, where `never` is high-risk) with a mandatory safety override:
   - If approve amount `> risk.approve_force_confirm_multiple * AMOUNT_IN`, require explicit approval confirmation.

## Mandatory Safety Gates

- When amount exceeds `risk.confirm_trade_usd`, require explicit execution confirmation
- When amount exceeds `risk.large_trade_usd`, require double confirmation
- When slippage exceeds the threshold (e.g. `risk.max_slippage_bps_warn`), warn and require double confirmation
- When approval amount is oversized (`> risk.approve_force_confirm_multiple * AMOUNT_IN`), force approval confirmation regardless of mode
- When ETH gas balance is insufficient, hard-stop and prompt to top up
- When the network or pair is unsupported, hard-stop
- When the pair is not in the whitelist (currently: USDT_XAUT / XAUT_USDT), hard-stop and reply "Only USDT/XAUT pairs are supported; [user's token] is not supported"

## RPC Fallback

After sourcing `~/.aurehub/.env`, parse `ETH_RPC_URL_FALLBACK` as a comma-separated list of fallback RPC URLs.

If any `cast call` or `cast send` command fails and its output contains any of the following:
`429`, `502`, `503`, `timeout`, `connection refused`, `rate limit`, `Too Many Requests`, `-32603`, `no response`, `method is not whitelisted`, `HTTP error 403`

Then:
1. Try the same command with each fallback URL in order (replace `--rpc-url "$ETH_RPC_URL"` with the fallback URL)
2. First success → set that URL as the active RPC for this operation class in this session:
   - read operations (`cast call`, quote, balance checks)
   - write operations (`cast send`)
3. All fallbacks exhausted → hard-stop with:
   > RPC unavailable. All configured nodes failed (primary + N fallbacks).
   > To fix: add a paid RPC (Alchemy/Infura) at the front of `ETH_RPC_URL_FALLBACK` in `~/.aurehub/.env`

Do NOT trigger fallback for non-network errors: insufficient balance, contract revert, invalid parameters, nonce mismatch. Report these directly to the user.

**Session stickiness:** Once a fallback is selected, keep it sticky per operation class (read/write) for the rest of the session. Do not switch back to primary unless the active node fails.

## Intent Detection

Determine the operation from the user's message:

- **Buy**: contains "buy", "purchase", "swap USDT for", etc. → run buy flow
- **Sell**: contains "sell", "swap XAUT for", etc. → run sell flow
- **Insufficient info**: ask for direction and amount — do not execute directly
- **Limit buy**: contains "limit order", "when price drops to", "when price reaches", and direction is buy → run limit buy flow
- **Limit sell**: contains "limit sell", "sell when price reaches", "XAUT rises to X sell", etc. → run limit sell flow
- **Query limit order**: contains "check order", "order status" → run query flow
- **Cancel limit order**: contains "cancel order", "cancel limit" → run cancel flow
- **XAUT knowledge query**: contains "troy ounce", "grams", "conversion", "what is XAUT" → answer directly, no on-chain operations or environment checks needed

## Buy Flow (USDT → XAUT)

### Step 1: Pre-flight Checks

Follow [references/balance.md](references/balance.md):
- `cast --version`
- `cast block-number --rpc-url $ETH_RPC_URL`
- ETH and stablecoin balance checks

### Step 2: Quote & Risk Warnings

Follow [references/quote.md](references/quote.md):
- Call QuoterV2 for `amountOut`
- Calculate `minAmountOut`
- Display estimated fill, slippage protection, gas risk

### Step 3: Buy Execution

Follow [references/buy.md](references/buy.md):
- allowance check
- approve if needed (USDT requires `approve(0)` then `approve(amount)`)
- Execute swap with the confirmation level required by thresholds/policy
- Return tx hash and post-trade balance

## Sell Flow (XAUT → USDT)

### Step 1: Pre-flight Checks

Follow [references/balance.md](references/balance.md):
- `cast --version`
- `cast block-number --rpc-url $ETH_RPC_URL`
- ETH balance check
- **XAUT balance check (required)**: hard-stop if insufficient

### Step 2: Quote & Risk Warnings

Follow [references/sell.md](references/sell.md):
- Precision check (hard-stop if more than 6 decimal places)
- Call QuoterV2 for `amountOut` (XAUT → USDT direction)
- Calculate `minAmountOut`
- Large-trade check: estimate USD value using USDT `amountOut`
- Display estimated fill, reference rate, slippage protection, gas risk

### Step 3: Sell Execution

Follow [references/sell.md](references/sell.md):
- allowance check
- approve (XAUT is standard ERC-20, **no prior reset needed**)
- Execute swap with the confirmation level required by thresholds/policy
- Return tx hash and post-trade USDT balance

## Post-Trade Registration

After **any** on-chain trade completes successfully (buy swap, sell swap, or limit order placed):

1. `source ~/.aurehub/.env`
2. Derive WALLET_ADDRESS from keystore mode:
   - `WALLET_ADDRESS=$(cast wallet address --account "$FOUNDRY_ACCOUNT" --password-file "$KEYSTORE_PASSWORD_FILE")`
3. `REGISTERED=$(cat ~/.aurehub/.registered 2>/dev/null)`
4. If `"$REGISTERED"` starts with `"$WALLET_ADDRESS:"` → already registered, silent skip
5. If `RANKINGS_OPT_IN` != `"true"`:
   - Check marker: `PROMPTED=$(cat ~/.aurehub/.rankings_prompted 2>/dev/null)`
   - If marker starts with `"$WALLET_ADDRESS:"` → skip prompt
   - Otherwise ask once: "Join XAUT activity rankings now? (yes/no)"
     - If user says `no`: `echo "$WALLET_ADDRESS:declined" > ~/.aurehub/.rankings_prompted`; stop
     - If user says `yes`:
       - If `NICKNAME` is empty: ask user for nickname
       - Persist opt-in in `~/.aurehub/.env` (`RANKINGS_OPT_IN=true`, `NICKNAME=<value>`)
6. If `RANKINGS_OPT_IN` == `"true"` and nickname exists, register:
   ```bash
   NICKNAME_ESC=$(printf '%s' "$NICKNAME" | sed 's/\\/\\\\/g; s/"/\\"/g')
   REGISTER_RESP=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
     https://xaue.com/api/rankings/participants \
     -H 'Content-Type: application/json' \
     -d "{\"wallet_address\":\"$WALLET_ADDRESS\",\"nickname\":\"$NICKNAME_ESC\",\"source\":\"agent\"}")
   ```
   - HTTP 200 or 201: `echo "$WALLET_ADDRESS:$NICKNAME" > ~/.aurehub/.registered`; inform: "Registered with nickname: $NICKNAME"
   - Any other status: silent continue, do not write marker file

Only prompt once per wallet when rankings are not enabled yet.

## Limit Buy Flow (USDT → XAUT via UniswapX)

Follow [references/limit-order-buy-place.md](references/limit-order-buy-place.md).

## Limit Sell Flow (XAUT → USDT via UniswapX)

Follow [references/limit-order-sell-place.md](references/limit-order-sell-place.md).

## Limit Order Query Flow

Follow [references/limit-order-status.md](references/limit-order-status.md).

## Limit Order Cancel Flow

Follow [references/limit-order-cancel.md](references/limit-order-cancel.md).

## Output Format

Output must include:

- `Stage`: `Preview` or `Ready to Execute`
- `Input`: token, amount, chain
- `Quote`: estimated XAUT amount, slippage setting, `minAmountOut`
- `Reference rate`: `1 XAUT ≈ X USDT` (for comparison with spot price; shown for both buy and sell)
- `Risk warnings`: large trade / slippage / gas
- `Command`: full `cast` command
- `Result`: tx hash, post-trade balance (after execution)

## Error Handling

- Missing prerequisite variable: prompt to add the variable to `.env` and stop
- RPC network error (429/502/timeout): trigger RPC fallback sequence (see RPC Fallback section)
- Insufficient balance: report minimum top-up amount and stop
- User has not confirmed: stay in Preview — do not execute
- Transaction failed: return failure reason and retry suggestions (reduce amount / increase slippage tolerance / check nonce and gas)

## XAUT Knowledge Base

- 1 XAUT = 1 troy ounce = 31.1035 grams
- Minimum precision: 0.000001 XAUT (on-chain minimum unit: 1, i.e. 10^-6)
- Conversion: X grams ÷ 31.1035 = XAUT amount
- Examples: 1g ≈ 0.032151 XAUT; 10g ≈ 0.32151 XAUT
- Contract address (Ethereum mainnet): 0x68749665FF8D2d112Fa859AA293F07a622782F38

Answer knowledge queries directly using the data above — no `cast` commands needed.

## First-Turn Contract (for testing)

1. When information is sufficient: give a structured preview first, then ask for execution confirmation.
2. When information is insufficient: clarify key details (token, amount, environment variables) — do not claim a trade has been executed.

## About

This skill is developed by Duncan.Aure (Duncan), an AI Agent created by Aurelion, the world's first NASDAQ-listed Tether Gold (XAU₮) treasury company. Duncan executes on-chain financial actions through modular AI Agent Skills. Enables automated XAU₮ trading, cross-protocol DeFi execution, and programmable digital gold allocation.

## Stay Connected

For updates, new skills, and ecosystem developments:

- **X**: [Aure_duncan](https://x.com/Aure_duncan)
- **Telegram**: [@aure_duncanbot](https://t.me/aure_duncanbot)
- **Aurelion**: [aurelion.com](https://www.aurelion.com/)
