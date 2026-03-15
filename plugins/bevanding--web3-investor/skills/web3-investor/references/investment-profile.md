# Investment Profile & Filtering Module

> **Purpose**: Structured preference collection and opportunity filtering.

---

## What It Does

Structured preference collection and opportunity filtering.

## Why Use It

- Ensures consistent question flow across different agents
- Provides type-safe preference storage
- One-shot filtering based on multiple criteria

## Preference Parameters

| Preference | Key | Options | Why It Matters |
|------------|-----|---------|----------------|
| **Chain** | `chain` | ethereum, base, arbitrum, optimism | Determines which blockchain to search |
| **Capital Token** | `capital_token` | USDC, USDT, ETH, WBTC, etc. | The token they want to invest |
| **Reward Preference** | `reward_preference` | single / multi / any | Single token rewards vs multiple tokens (e.g., CRV+CVX) |
| **Accept IL** | `accept_il` | true / false / any | Impermanent loss tolerance for LP products |
| **Underlying Type** | `underlying_preference` | rwa / onchain / mixed / any | Real-world assets vs pure on-chain protocols |

## Code Example

```python
from scripts.discovery.investment_profile import InvestmentProfile

# Create profile
profile = InvestmentProfile()

# Method 1: Direct assignment
profile.chain = "ethereum"
profile.capital_token = "USDC"
profile.accept_il = False
profile.reward_preference = "single"
profile.min_apy = 5
profile.max_apy = 30

# Method 2: Batch setup
profile.set_preferences(
    chain="ethereum",
    capital_token="USDC",
    accept_il=False,
    reward_preference="single",
    underlying_preference="onchain",
    min_apy=5,
    max_apy=30
)

# Filter opportunities
filtered = profile.filter_opportunities(opportunities)

# Get human-readable explanation
print(profile.explain_filtering(len(opportunities), len(filtered)))
```

## Available Questions for UI Building

```python
questions = InvestmentProfile.get_questions()

# Returns structured dict:
{
  "required": [...],      # Must ask: chain, capital_token
  "preference": [...],    # Should ask: reward_preference, accept_il, etc.
  "constraints": [...]    # Optional: min_apy, max_apy, min_tvl
}
```

## Filtering Logic

The filtering applies all set preferences:

1. **Chain filter**: Exact match
2. **Capital token filter**: Match against opportunity's underlying tokens
3. **Reward preference filter**: 
   - `single`: Only single-token rewards
   - `multi`: Multi-token rewards acceptable
   - `any`: No filter
4. **IL tolerance filter**: 
   - `false`: Exclude LP products with IL risk
   - `true`: Include all
   - `any`: No filter
5. **Underlying type filter**: Match RWA/onchain/mixed
6. **APY range filter**: Min/max bounds
7. **TVL filter**: Minimum TVL threshold