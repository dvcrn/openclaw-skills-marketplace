# Cold Start Protocol

When the agent encounters a **new domain** (not in capability_map or status is `blind_spot`), follow these phases:

## Phase 1: Identify & Register

1. Run `plan <domain> "<goal>"` — register the domain in capability_map
2. Run `status` — confirm current state (should be empty or blind_spot)
3. Run `search "<domain>"` — check if SparkHub has existing sparks

## Phase 2: Autonomous Research

- Search the web for domain overview
- Decompose into sub-skill tree (P0 core / P1 advanced / P2 business)
- Kindle search results with `web_exploration` source

## Phase 3: Enter Teaching

- Report research findings to the user
- Ask which sub-domain to start with
- If user says "let me teach you", enter `teach` structured extraction mode

## Behavior by Phase

| Behavior | cold_start | active | cruise |
|----------|-----------|--------|--------|
| Search aggressiveness | Aggressive | Balanced | On-demand |
| Question frequency | High (3/interaction) | Medium (2/interaction) | Low (1/interaction) |
| Attribution frequency | None (no knowledge yet) | Moderate | High-confidence only |
| Micro-probe budget | 3/interaction | 2/interaction | 1/interaction |

## Exit Conditions

Exit cold_start → enter `active` when ANY of:
- Domain spark_count >= 5
- Domain practice_count >= 2
- User explicitly says foundational teaching is done
