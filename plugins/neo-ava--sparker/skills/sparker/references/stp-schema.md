# STP Configuration Schema Reference

## Environment Variables

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `STP_ENABLED` | `true` | boolean | Enable/disable STP |
| `STP_ASSETS_DIR` | `./assets/stp` | path | Local asset storage directory |
| `STP_HUB_URL` | (none) | URL | SparkLand server address |
| `STP_TRANSPORT` | `file` | `file`\|`http` | Transport mode |
| `STP_NODE_ID` | (auto) | string | Node identifier |
| `STP_DIGEST_INTERVAL_HOURS` | `12` | integer | Digest cycle in hours |
| `STP_CHECK_INTERVAL_HOURS` | `3` | integer | How often daemon checks if digest is due |
| `STP_CONFIDENCE_THRESHOLD` | `0.60` | float | RawSpark → RefinedSpark promotion threshold |
| `STP_MIN_PRACTICE_COUNT` | `2` | integer | Min practices before promotion |
| `STP_FORGE_THRESHOLD` | `0.85` | float | Ember → Gene forging threshold |
| `STP_FORGE_MIN_CITATIONS` | `8` | integer | Min citations for forging |
| `STP_FRESHNESS_HALF_LIFE` | `60` | integer | RawSpark decay half-life in days |
| `STP_REFINED_HALF_LIFE` | `90` | integer | RefinedSpark decay half-life in days |
| `STP_MERGE_THRESHOLD` | `0.35` | float | Similarity threshold for merging sparks (CJK-friendly) |
| `STP_RELEVANCE_THRESHOLD` | `0.25` | float | Min relevance score for search results |
| `STP_RL_FREQUENCY` | `moderate` | enum | Base RL frequency (overridden by adaptive strategy) |
| `STP_MAX_RL_PER_DAY` | `3` | integer | Base max RL/day (cold_start auto→6, cruise auto→1) |
| `STP_RL_COOLDOWN_MINUTES` | `60` | integer | Base cooldown (cold_start auto→20, cruise auto→180) |
| `STP_AUTO_EXPLORE` | `true` | boolean | Enable proactive exploration |
| `STP_CRED_BOOST` | `0.05` | float | Base positive feedback credibility delta |
| `STP_CRED_PENALTY` | `0.03` | float | Base negative feedback credibility delta |
| `STP_NOTE_RETENTION_DAYS` | `30` | integer | Unpromoted RawSpark retention |
| `STP_LEARNER_STRATEGY` | `balanced` | enum | Fallback strategy when adaptive not available |
| `STP_DOMAINS` | (auto) | string | Comma-separated focus domains |
| `STP_EMBEDDING_ENDPOINT` | (auto) | URL | Embedding API (auto-reads from openclaw config) |
| `STP_EMBEDDING_API_KEY` | (auto) | string | Embedding API key (auto-reads from openclaw config) |
| `STP_EMBEDDING_MODEL` | `default` | string | Embedding model name |
| `STP_FORGE_LLM_ENDPOINT` | (auto) | URL | LLM endpoint (auto-reads from openclaw config) |
| `STP_FORGE_LLM_API_KEY` | (auto) | string | LLM API key (auto-reads from openclaw config) |
| `STP_FORGE_LLM_MODEL` | (auto) | string | LLM model (auto-reads from openclaw primary model) |
| `GEP_ASSETS_DIR` | (auto) | path | GEP Gene output directory |
| `EVOLVER_ASSETS_DIR` | (auto) | path | Evolver assets directory (alias) |

## Auto-Configuration

Sparker automatically reads `~/.openclaw/agents/main/agent/models.json` and `~/.openclaw/openclaw.json` for LLM and Embedding configuration. No manual env vars needed when running inside OpenClaw.

## Adaptive Strategy (no config needed)

The adaptive strategy is automatic — it reads the capability map and adjusts per-domain:

| Parameter | cold_start | active | cruise |
|-----------|-----------|--------|--------|
| RL boost | +0.5 | ±0 | -0.3 |
| Max RL/day | 6 | 3 | 1 |
| Cooldown | 20min | 60min | 180min |
| Auto explore | yes | if score<0.5 | no |
| Ask human | yes | if score<0.6 | no |

## RawSpark Six-Dimension Fields (schema_version 2.0.0)

All RawSparks now include six structured dimensions in addition to legacy fields:

| Field | Type | Description |
|-------|------|-------------|
| `knowledge_type` | `rule\|preference\|pattern\|lesson\|methodology` | Experience classification |
| `when.trigger` | string | What need/task triggers this experience |
| `when.conditions` | string[] | Additional qualifying conditions |
| `where.domain` | string | Primary domain |
| `where.sub_domain` | string | Sub-domain |
| `where.scenario` | string | Environment description (free text) |
| `where.audience` | string | Target audience |
| `why` | string | Causal chain + comparative reasoning |
| `how.summary` | string | One-line actionable rule |
| `how.detail` | string | Expanded description with steps |
| `result.expected_outcome` | string | Expected effect (quantify if possible) |
| `result.feedback_log` | object[] | Usage feedback records |
| `not[]` | object[] | When NOT to apply: `{condition, effect, reason}` |

Legacy fields (`content`, `card.heuristic`, `card.context_envelope`, `card.boundary_conditions`) are auto-generated from six dimensions for backward compatibility.

## Spark Status Lifecycle

| Status | Meaning | Can be promoted? |
|--------|---------|-----------------|
| `active` | Verified spark (from human or confirmed) | Yes |
| `pending_verification` | From web search or agent exchange, needs validation | No |
| `promoted` | Already promoted to RefinedSpark | No |
| `rejected` | Confidence too low (< 0.10) | No |

Activation paths for `pending_verification`:
- Human confirms → `active` + `human_confirmed` + confidence +0.20
- Successful practice → `active` + `practice_verified`
- Cross-agent validation → `active` + `cross_validated` + confidence +0.10

## Backward Compatibility

These spark-protocol variables are also recognized:

| Old Variable | Maps To |
|-------------|---------|
| `SPARK_HUB_URL` | `STP_HUB_URL` |
| `SPARK_TRANSPORT` | `STP_TRANSPORT` |
| `SPARK_NODE_ID` | `STP_NODE_ID` |
| `SPARK_EMBEDDING_ENDPOINT` | `STP_EMBEDDING_ENDPOINT` |
| `SPARK_EMBEDDING_API_KEY` | `STP_EMBEDDING_API_KEY` |
| `SPARK_PROMOTE_LLM_ENDPOINT` | `STP_FORGE_LLM_ENDPOINT` |
| `SPARK_PROMOTE_LLM_API_KEY` | `STP_FORGE_LLM_API_KEY` |
| `SPARK_PROMOTE_LLM_MODEL` | `STP_FORGE_LLM_MODEL` |

## File Format Reference

| File | Format | Description |
|------|--------|-------------|
| `raw_sparks/raw_sparks.jsonl` | JSONL | Append-only raw spark log |
| `raw_sparks/raw_sparks_snapshot.json` | JSON | Mutable snapshot with practice stats and status |
| `refined_sparks/refined_sparks.json` | JSON | Refined spark snapshot |
| `refined_sparks/refined_sparks.jsonl` | JSONL | Refined spark change log |
| `embers/embers.json` | JSON | Published ember cache |
| `practice_records/practice_records.jsonl` | JSONL | Practice record log |
| `extraction_sessions/sessions.jsonl` | JSONL | Extraction session log |
| `capability_map/capability_map.json` | JSON | Dynamic capability map snapshot |
| `cold_start_plans.json` | JSON | Active cold-start learning plans |
| `digest_reports/digest_reports.jsonl` | JSONL | Digest report archive |
| `domains.json` | JSON | Domain registry |
| `rl_state.json` | JSON | RL engine state + preference history |
| `feedback_log.jsonl` | JSONL | Feedback event log |
