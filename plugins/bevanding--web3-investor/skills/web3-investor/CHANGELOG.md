# Changelog

All notable changes to the Web3 Investor Skill will be documented in this file.

## [0.5.0] - 2026-03-08

### Configuration Refactoring

#### Simplified Config Structure
- **Refactored**: `config.json` reorganized into 6 clear sections
  - `chain`: Network and RPC configuration
  - `api`: Signer service endpoint settings
  - `security`: Trading limits, slippage, whitelist controls
  - `preflight`: Pre-execution validation checks
  - `rpc`: RPC connection management
  - `discovery`: Data source configuration

#### Whitelist Enhancement
- **New**: `whitelist_enabled` parameter (default: `false`)
  - When `false`: Skip whitelist filtering in trade execution
  - When `true`: Enforce whitelist checks for chains/protocols/tokens
  - Backward compatible: Defaults to `false` if not specified

#### Dune MCP Integration
- **New**: Dune analytics data source in discovery module
  - MCP endpoint: `https://api.dune.com/mcp/v1`
  - Support for header auth (`x-dune-api-key`) and query param auth
  - Environment variable: `DUNE_API_KEY`
- **Updated**: SKILL.md with Discovery Data Sources section
- **Updated**: `references/discovery.md` with Dune documentation

#### MCP Multi-Server Support (NEW)
- **New**: Multi-server MCP configuration structure
  - Support for multiple MCP servers with primary/fallback URLs
  - In-memory caching with configurable TTL (default: 300s)
  - Automatic failover between primary and fallback endpoints
- **Fixed**: `find_opportunities.py` MCP config reading
  - Now correctly reads from `discovery.mcp.servers[]` array
  - Each server can have its own name, URLs, and timeout settings

#### Execution Readiness Check (NEW)
- **New**: `preflight.py` module for payment capability check
  - `check_execution_readiness()` function
  - Returns available payment methods (keystore_signer vs eip681_payment_link)
  - Automatic detection of signer API availability
- **New**: `execution_readiness` field in opportunity results
  - Auto-attached to each opportunity
  - Recommends appropriate payment method
- **Updated**: SKILL.md with Rule 5: Check Payment Capability FIRST

#### Code Fixes
- **Fixed**: `preflight.py` load_config path resolution (parent directory)
- **Fixed**: `trade_executor.py` SKILL_DIR path resolution
- **Fixed**: `rpc_manager.py` adapted to new config structure (`chain.rpc`)
- **Fixed**: RWA product chain assignment (now defaults to "Base" instead of search param)

#### Documentation Cleanup
- **Removed**: `config.example.json` (obsolete, structure incompatible)
- **Updated**: CHANGELOG.md with v0.5.0 changes
- **Updated**: TODO.md version tracking
- **Updated**: `references/discovery.md` with data source details

---

## [0.4.0] - 2026-03-05

### Framework Optimization

#### SKILL.md Restructuring
- **Refactored**: Split monolithic SKILL.md (~700 lines) into Progressive Disclosure structure
- **New references/**:
  - `discovery.md` - Detailed opportunity discovery documentation
  - `investment-profile.md` - Investment preference system guide
  - `trade-executor.md` - Complete REST API documentation
  - `portfolio-indexer.md` - Portfolio balance query guide
- **SKILL.md streamlined**: Reduced from ~700 lines to 263 lines
  - Kept: Critical Rules, Quick Start, Module Overview with links
  - Moved: Detailed API docs, usage examples to references/
  - Removed: Version History section (kept in CHANGELOG.md)
  - Retained: Contributing section per maintainer request

#### Alignment with skill-creator Best Practices
- Implemented Progressive Disclosure pattern (3-level loading)
- Separated metadata (frontmatter), core workflow (SKILL.md), detailed docs (references/)
- Improved context efficiency for AI agents

---

## [0.3.0] - 2026-03-05

### Trade Executor Module (REST API Adapter)

#### New Module: `trade_executor.py`
- **Purpose**: REST API adapter for local keystore signer
- **Architecture**: Generates executable transaction requests, does NOT hold private keys
- **State Machine**: `preview` → `approve` → `execute` (mandatory flow)

#### Execution Model
| Property | Value |
|----------|-------|
| Wallet Type | Local keystore signer |
| Supported Chains | base, ethereum |
| Entry Point | REST API |
| State Machine | preview → approve → execute |

#### Security Constraints (Enforced)
- ❌ Cannot skip `approve` step
- ✅ Must simulate before execution (`eth_call`)
- ⚠️ Must return risk warnings (balance, allowance, route validity)
- 🔒 Default minimum permissions:
  - Whitelist chains/protocols/tokens
  - Transaction value limits ($10k default)
  - Max slippage caps (3% default)

#### Unified Transaction Request Format
```json
{
  "request_id": "uuid",
  "timestamp": "ISO8601",
  "network": "base",
  "chain_id": 8453,
  "type": "transfer|swap|deposit|contract_call",
  "description": "human readable",
  "transaction": {
    "to": "0x...",
    "value": "0x0",
    "data": "0x...",
    "gas_limit": 250000
  },
  "metadata": {
    "protocol": "uniswap|aave|compound|...",
    "from_token": "USDC",
    "to_token": "WETH",
    "amount": "5"
  }
}
```

#### API Endpoints Integrated
- `GET /api/wallet/balances` — Query wallet balances
- `POST /api/trades/preview` — Generate transaction preview
- `POST /api/uniswap/preview-swap` — Uniswap-specific swap preview
- `POST /api/zerox/preview-swap` — 0x protocol swap preview
- `POST /api/trades/approve` — Confirm transaction for execution
- `POST /api/trades/execute` — Broadcast signed transaction
- `GET /api/transactions/{tx_hash}` — Check transaction status
- `GET /api/allowances` — Query token allowances
- `POST /api/allowances/revoke-preview` — Preview allowance revoke

#### Return Specifications
- **Preview Response**: `preview_id`, `simulation_ok`, `risk`, `next_step`
- **Approve Response**: `approval_id`, `preview_id`, `approved_at`, `expires_at`
- **Execute Response**: `tx_hash`, `explorer_url`, `executed_at`, `network`
- **Error Format**: `code`, `message`, `diagnostics`

#### Configuration Updates
- New `security` section in `config.json`:
  - `max_slippage_percent`: 3.0
  - `whitelist_chains`: ["base", "ethereum"]
  - `whitelist_protocols`: ["uniswap", "aave", "compound", "lido", "0x"]
  - `whitelist_tokens`: ["USDC", "USDT", "DAI", "WETH", "ETH", "stETH", "rETH"]
  - `max_trade_value_usd`: 10000
- New `execution_model` section specifying wallet type and state machine
- New `api` section with endpoint registry

#### Documentation Updates
- SKILL.md updated to v0.3.0 with comprehensive Trade Executor documentation
- Added Skill Author Template with mandatory prompt guidelines
- Updated Quick Start guide with new execution flow
- Updated Project Structure with `trade_executor.py`

---

## [0.2.1] - 2026-03-04

### Added

#### Investment Preference System (B+C Hybrid Approach)
- **New Module**: `investment_profile.py` - User preference collection and filtering
  - `InvestmentProfile` class for structured preference management
  - Support for 5 key preference dimensions:
    - Chain selection (ethereum, base, arbitrum, optimism)
    - Capital token (USDC, USDT, ETH, etc.)
    - Reward preference (single/multi/none tokens)
    - Impermanent loss acceptance (True/False)
    - Underlying asset type (RWA/on-chain/mixed)
  - `get_questions()` method for Agent UI building
  - `filter_opportunities()` method for one-shot filtering
  - `explain_filtering()` for human-readable results

#### Enhanced Risk Signals
- **New fields** in `find_opportunities.py` risk_signals output:
  - `reward_type`: "none" | "single" | "multi" - Token reward structure
  - `has_il_risk`: True | False - Impermanent loss risk indicator
  - `underlying_type`: "rwa" | "onchain" | "mixed" | "unknown" - Asset backing type
- **Detection functions**:
  - `detect_reward_type()`: Analyzes rewardTokens array
  - `detect_il_risk()`: Identifies DEX LP and multi-asset volatility risks
  - `detect_underlying_type()`: Categorizes RWA vs on-chain protocols

#### Documentation Updates
- **Disclaimer added**: Clear statement that skill provides info only, not investment advice
- **Investment Preference Guide**: New section in SKILL.md with:
  - Required questions (chain, capital_token)
  - Important questions (reward preference, IL acceptance, underlying type)
  - Usage examples for InvestmentProfile class

### Fixed

- **Import bug**: `unified_search.py` Dune MCP import path issue
  - Added multi-layer fallback import mechanism
  - Supports absolute, relative, and dynamic imports

### Technical Details

**Architecture**: B+C Hybrid Approach
- **Approach B**: Standalone `InvestmentProfile` module for convenience
- **Approach C**: Enhanced `risk_signals` in existing API for flexibility
- Agents can choose: use convenience tool OR process raw signals themselves

**Backward Compatibility**: ✅ Fully maintained
- All existing APIs work unchanged
- New fields are additive only
- No breaking changes

---

## [0.2.0] - 2026-03-04

### Major Refactoring

#### Risk Assessment Redesign
- **Removed**: Local `calculate_risk_score()` function
- **Added**: `risk_signals` collection for LLM-based analysis
- **Philosophy**: Skill provides data, user's LLM makes risk judgments

#### Actionable Addresses
- **New structure**: `actionable_addresses` in opportunity output
  - `deposit_contract_candidates`: List of potential deposit contracts
  - `underlying_token_addresses`: Underlying asset addresses
  - `reward_token_addresses`: Reward token addresses
  - `has_actionable_address`: Boolean execution readiness flag
  - `primary_contract`: Main protocol contract from registry
  - `protocol_registry_match`: Whether protocol found in static registry

#### Trading Execution Optimization
- **Balance pre-check**: `check_balance_before_deposit()` function
  - Native token balance queries via RPC
  - ERC20 token balance queries
- **Deposit preview**: Calldata generation for Aave/Compound/Lido
  - `generate_aave_deposit_calldata()`
  - `generate_compound_deposit_calldata()`
- **Safe Vault v0.2.0**: Complete rewrite with CLI improvements

#### Protocol Registry
- **New file**: `config/protocols.json`
  - JSON format for reliable parsing
  - 12 protocols with metadata
  - Contract addresses and method signatures

#### Unified Search
- **Dune MCP integration**: Adapter for Dune Analytics
- **LLM-ready output**: `--llm-ready` flag for formatted prompts
- **Version tracking**: Output includes version field

---

## [0.1.0] - 2026-03-03

### Initial Release

#### Core Features
- Opportunity discovery via DefiLlama API
- Basic risk scoring (local algorithm)
- Safe Vault transaction preparation
- Whitelist and limit protection
- Portfolio indexing

#### Known Limitations (Documented)
- DefiLlama API data parsing issues
- Risk scoring algorithm accuracy concerns
- Portfolio indexer limited to basic token balances

---

## Version History Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 0.2.1 | 2026-03-04 | Investment preferences, enhanced risk signals, disclaimer |
| 0.2.0 | 2026-03-04 | Risk redesign, actionable addresses, trading optimization |
| 0.1.0 | 2026-03-03 | Initial release, basic functionality |

---

## Future Roadmap

### Phase 2 (Planned)
- Execute Dune queries for actual APY data
- Safe{Wallet} multisig integration
- Transaction history logging
- Gas optimization strategies

### Phase 3 (Roadmap)
- Insurance mechanism
- Drawdown controls
- Full autonomous mode

---

**Maintainer**: Web3 Investor Skill Team
**Repository**: https://github.com/openclaw/web3-investor
**Registry**: https://clawhub.com