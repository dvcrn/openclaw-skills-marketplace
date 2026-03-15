---
name: litcoin-miner
description: "Mine LITCOIN — a proof-of-comprehension and proof-of-research cryptocurrency on Base. Use when the user wants to mine crypto with AI, earn tokens through reading comprehension or solving optimization problems, stake LITCOIN, open vaults, mint LITCREDIT, manage mining guilds, run research experiments, deploy agents, or interact with the LITCOIN DeFi protocol."
---

# LITCOIN Miner Skill

SDK reference for the LITCOIN proof-of-comprehension and proof-of-research protocol on Base. This skill assumes the user already has the `litcoin` SDK installed and configured.

See references/protocol.md for full protocol documentation, setup instructions, and architecture details.

## Agent Initialization

```python
from litcoin import Agent

agent = Agent(
    bankr_key="bk_YOUR_KEY",        # Required — Bankr wallet API key
    ai_key="sk-YOUR_KEY",           # Optional — AI provider key for research mining
    ai_url="https://api.venice.ai/api/v1",
    model="llama-3.3-70b",
)
```

## Comprehension Mining

```python
agent.mine(rounds=10)   # Mine 10 rounds (0 = unlimited)
agent.claim()            # Claim rewards on-chain
agent.status()           # Check earnings
agent.faucet()           # Bootstrap 5M LITCOIN (one-time, new wallets)
```

## Research Mining (Proof-of-Research)

```python
result = agent.research_mine(task_type="code_optimization")

# Iterate on one task (recommended — this is where breakthroughs happen)
agent.research_loop(task_id="sort-benchmark-001", rounds=50, delay=30)

agent.research_tasks()                         # List available tasks
agent.research_history(task_id="sort-001")     # Your iteration history
agent.research_leaderboard()                   # Top researchers
agent.research_stats()                         # Global statistics
```

Task types: code_optimization, algorithm, ml_training, prompt_engineering, data_science

Rewards are quality-weighted: participation (valid, no improvement) earns a base amount. Breakthroughs (new global best) earn up to 110x more.

## Staking V2

```python
agent.stake(2)                    # Stake into Circuit tier (1-4)
agent.upgrade_tier(3)             # Upgrade to Core tier
agent.add_to_stake(1_000_000)     # Add more tokens (lock doesn't reset)
agent.unstake()                   # Unstake after lock expires (0% penalty)
agent.early_unstake()             # Unstake early (tiered penalty: 20-35%)
agent.preview_early_unstake()     # View penalty before committing
agent.stake_info()                # Tier, amount, lock status
agent.tier()                      # Current tier number
agent.time_until_unlock()         # Seconds until lock expires
agent.mining_boost()              # Boost in basis points
agent.total_staked()              # Protocol-wide total
```

| Tier | Name | Required | Lock | Boost | Early Exit |
|------|------|----------|------|-------|-----------|
| 1 | Spark | 1M | 7d | 1.10x | 20% |
| 2 | Circuit | 5M | 30d | 1.25x | 25% |
| 3 | Core | 50M | 90d | 1.50x | 30% |
| 4 | Architect | 500M | 180d | 2.00x | 35% |

## Vaults (MakerDAO-style CDPs)

```python
agent.open_vault(10_000_000)              # Open with 10M collateral
vaults = agent.vault_ids()                # List your vaults
agent.mint_litcredit(vaults[0], 500)      # Mint 500 LITCREDIT
agent.repay_debt(vaults[0], 500)          # Repay debt
agent.add_collateral(vaults[0], 5_000_000) # Add collateral
agent.withdraw_collateral(vaults[0], 1_000_000)
agent.close_vault(vaults[0])              # Close vault
agent.vault_health(vaults[0])             # Check collateral ratio
```

## Compute Marketplace

```python
agent.deposit_escrow(100)                        # Deposit LITCREDIT
result = agent.compute("Explain proof of research") # Use AI inference
```

The compute endpoint is OpenAI-compatible. Works with Hermes, OpenClaw, LangChain, LiteLLM, Cursor, and the OpenAI Python SDK.

## Mining Guilds

```python
agent.create_guild("My Guild")
agent.join_guild(guild_id, amount)
agent.leave_guild()
```

## Read State

```python
agent.balance()          # LITCOIN + LITCREDIT balances
agent.oracle_prices()    # CPI and LITCOIN prices
agent.snapshot()         # Full protocol state in one call
```

## Full Flywheel Example

```python
from litcoin import Agent

agent = Agent(bankr_key="bk_...", ai_key="sk-...")

agent.mine(rounds=20)
agent.research_loop(rounds=10)
agent.claim()
agent.stake(2)
agent.open_vault(10_000_000)
vaults = agent.vault_ids()
agent.mint_litcredit(vaults[0], 500)
agent.deposit_escrow(100)
result = agent.compute("Explain proof of research")
print(result['response'])
```

## Key Info

- Chain: Base mainnet (8453)
- Token: 0x316ffb9c875f900AdCF04889E415cC86b564EBa3
- All contracts verified on BaseScan
- SDK: litcoin on PyPI (v4.0.1, author: tekkaadan)
- MCP: litcoin-mcp on npm (v2.0.0)
- Docs: litcoiin.xyz/docs
- Research Lab: litcoiin.xyz/research
