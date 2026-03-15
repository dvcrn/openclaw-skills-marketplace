---
name: polymarket-emerging-tech-trader
description: "Trades Polymarket prediction markets on Web3/DeFi milestones, NFT market recovery, metaverse adoption, humanoid robotics deployments, quantum computing breakthroughs, and synthetic biology commercialization. Use when you want to capture alpha on niche emerging technology markets where most retail traders lack domain expertise."
---

# Emerging Tech Trader

> **This is a template.**  
> The default signal is keyword discovery + on-chain data signals — remix it with DeFiLlama TVL feeds, GitHub commit velocity for quantum computing projects, robotics deployment trackers, or synthetic biology investment databases.  
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Emerging tech markets are among the highest-edge opportunities on Polymarket because most retail participants lack domain expertise. A trader with genuine technical knowledge in robotics, quantum computing, or DeFi holds massive informational advantage.

This skill covers 5 sub-categories:

### 1. Web3 & DeFi
- Prediction market TVL milestones, cross-chain liquidity thresholds
- NFT market recovery volume markers
- Tokenized prediction position collateral milestones

### 2. Metaverse & VR/AR
- Meta Horizon DAU milestones, VR headset sales
- Virtual real estate transaction volumes

### 3. Robotics & Automation
- Humanoid robot factory deployments (Figure, Tesla Optimus, 1X)
- Autonomous delivery robot counts
- Warehouse automation penetration rates

### 4. Quantum Computing
- IBM qubit count milestones
- Commercial quantum revenue thresholds
- Quantum advantage demonstrations

### 5. Synthetic Biology
- Lab-grown meat regulatory approvals
- Precision fermentation market size
- Engineered bacteria commercial deployments

## Signal Logic

### Default Signal: GitHub + On-Chain Data Divergence

1. Discover markets matching emerging tech keywords
2. Pull GitHub commit/release activity for relevant projects (IBM Qiskit, Boston Dynamics, etc.)
3. Check on-chain data via DeFiLlama for DeFi-related markets
4. Compare observable technical progress vs market's implied probability
5. When visible technical milestones have been achieved but market hasn't repriced, enter

### Remix Ideas

- **DeFiLlama API**: https://defillama.com/docs/api — TVL, protocol metrics
- **GitHub API**: Activity on IBM/Google quantum repos, robotics company repos
- **CoinGlass**: NFT floor prices and volume tracking
- **The Good Food Institute**: Lab-grown meat regulatory tracker
- **IDC / Gartner** research: Technology adoption curve positioning

## Market Categories Tracked

```python
EMERGING_TECH_KEYWORDS = [
    "Web3", "DeFi", "NFT", "blockchain", "metaverse", "VR", "AR",
    "Meta Horizon", "virtual reality", "headset",
    "robot", "humanoid", "autonomous", "Boston Dynamics",
    "Tesla Optimus", "Figure", "warehouse automation",
    "quantum", "qubit", "IBM quantum", "Google quantum",
    "synthetic biology", "lab-grown", "precision fermentation",
    "CRISPR bacteria", "bioreactor", "engineered organism",
    "Solana", "Ethereum", "prediction market TVL"
]
```

## Risk Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| Max position size | $25 USDC | Emerging tech markets are volatile |
| Min market volume | $2,000 | Some niche markets start illiquid |
| Max bid-ask spread | 15% | Accept wider spreads for edge markets |
| Min days to resolution | 14 | Technical milestones need longer lead time |
| Max open positions | 8 | Diversify across sub-categories |

## Sub-Category Edge Analysis

| Category | Edge Source | Typical Market Bias |
|----------|-------------|---------------------|
| Quantum Computing | Academic paper lag (arXiv 6–24h before news) | Retail underestimates IBM progress |
| Humanoid Robots | YouTube demo videos precede deployments | Fan hype overprices Tesla Optimus |
| DeFi/TVL | On-chain data is real-time | Markets lag DeFiLlama by 2–6h |
| Lab-Grown Meat | Regulatory filings public before decisions | Market underweights FDA precedent |
| NFT Markets | OpenSea/Blur volume APIs | Volume data available before price consensus |

## Key Data Sources

- **DeFiLlama**: https://defillama.com/
- **GitHub API**: https://api.github.com/
- **IBM Quantum Network**: https://quantum.ibm.com/
- **The Good Food Institute**: https://gfi.org/
- **CoinGlass NFT**: https://www.coinglass.com/nft

## Installation & Setup

```bash
clawhub install polymarket-emerging-tech-trader
```

Requires: `SIMMER_API_KEY` environment variable.

## Cron Schedule

Runs every 15 minutes (`*/15 * * * *`). Emerging tech events are infrequent but high-impact when they occur.

## Safety & Execution Mode

**The skill defaults to paper trading (`venue="sim"`). Real trades only execute when `--live` is passed explicitly.**

| Scenario | Mode | Financial risk |
|----------|------|----------------|
| `python trader.py` | Paper (sim) | None |
| Cron / automaton | Paper (sim) | None |
| `python trader.py --live` | Live (polymarket) | Real USDC |

The automaton cron is set to `null` — it does not run on a schedule until you configure it in the Simmer UI. `autostart: false` means it won't start automatically on install.

## Required Credentials

| Variable | Required | Notes |
|----------|----------|-------|
| `SIMMER_API_KEY` | Yes | Trading authority — keep this credential private. Do not place a live-capable key in any environment where automated code could call `--live`. |

## Tunables (Risk Parameters)

All risk parameters are declared in `clawhub.json` as `tunables` and adjustable from the Simmer UI without code changes. They use `SIMMER_`-prefixed env vars so `apply_skill_config()` can load them securely.

| Variable | Default | Purpose |
|----------|---------|---------|
| `SIMMER_ETECH_MAX_POSITION` | `25` | Max USDC per trade |
| `SIMMER_ETECH_MIN_VOLUME` | `2000` | Min market volume filter (USD) |
| `SIMMER_ETECH_MAX_SPREAD` | `0.15` | Max bid-ask spread (0.10 = 10%) |
| `SIMMER_ETECH_MIN_DAYS` | `14` | Min days until market resolves |
| `SIMMER_ETECH_MAX_POSITIONS` | `8` | Max concurrent open positions |

## Dependency

`simmer-sdk` is published on PyPI by Simmer Markets.
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
- Publisher: hello@simmer.markets

Review the source before providing live credentials if you require full auditability.
