---
name: structs-guild-stack
description: "Deploys the Guild Stack (Docker Compose) for local PostgreSQL access to game state. Use when you need faster queries for combat automation, real-time threat detection, raid target scouting, fleet composition analysis, or galaxy-wide intelligence. Advanced/optional -- CLI works for basic gameplay, but PG access transforms what is possible."
---

# Structs Guild Stack

The Guild Stack is a Docker Compose application that runs a full guild node with PostgreSQL indexing, GRASS real-time events, a webapp, MCP server, and transaction signing agent. It provides sub-second database queries for game state that would take 1-60 seconds via CLI.

**This is an advanced/optional upgrade.** CLI commands work for basic gameplay. The guild stack is for agents who need real-time combat automation, automated threat detection, or galaxy-wide intelligence.

**Repository**: `https://github.com/playstructs/docker-structs-guild`

---

## When to Use the Guild Stack

| Situation | CLI | Guild Stack (PG) |
|-----------|-----|-------------------|
| Simple single-object query | 1-5s (fine) | <1s |
| Galaxy-wide scouting (all players, all planets) | 30-60s (too slow) | <1s |
| Real-time threat detection (poll every block) | Impossible (query > block time) | Trivial |
| Combat targeting (weapon/defense matching) | Minutes to gather data | <1s |
| Submitting transactions | CLI required | CLI required |

**Rule**: Use PG for reads, CLI for writes.

---

## Prerequisites

- Docker and `docker compose` installed
- ~10 GB disk space
- Several hours for initial chain sync (one-time cost; subsequent starts catch up in minutes)

---

## Setup Procedure

### 1. Clone the Repository

```bash
git clone https://github.com/playstructs/docker-structs-guild
cd docker-structs-guild
```

### 2. Configure Environment

Copy or create `.env` with at minimum:

```
MONIKER=MyAgentNode
NETWORK_VERSION=109b
NETWORK_CHAIN_ID=structstestnet-109
```

### 3. Start the Stack

```bash
docker compose up -d
```

### 4. Wait for Chain Sync

The blockchain node must sync from genesis or a snapshot. This takes hours on first run. Monitor progress:

```bash
docker compose logs -f structsd --tail 20
```

The node is synced when the health check passes. Check with:

```bash
docker compose ps
```

All services should show `healthy` or `running`. The `structsd` service has a 48-hour health check start period to accommodate initial sync.

### 5. Verify PG Access

Run a test query (see "Connecting to PostgreSQL" below):

```bash
docker exec docker-structs-guild-structs-grass-1 \
  psql "postgres://structs_indexer@structs-pg:5432/structs?sslmode=require" \
  -t -A -c "SELECT count(*) FROM structs.player;"
```

If this returns a number, the stack is working.

---

## Connecting to PostgreSQL

Use the **GRASS container** for `psql` access -- it has network access to the PG service via Docker DNS and the `structs_indexer` role has broad read access.

```bash
PG_CONTAINER="docker-structs-guild-structs-grass-1"
PG_CONN="postgres://structs_indexer@structs-pg:5432/structs?sslmode=require"

docker exec "$PG_CONTAINER" psql "$PG_CONN" -t -A -c "SELECT ..."
```

For JSON output:

```bash
docker exec "$PG_CONTAINER" psql "$PG_CONN" -t -A -c \
  "SELECT COALESCE(json_agg(row_to_json(t)), '[]') FROM (...) t;"
```

The container name may vary by installation. Find it with `docker compose ps` and look for the `structs-grass` service.

---

## The Grid Table Gotcha

The `structs.grid` table is a **key-value store**, not a columnar table. Each row is one attribute for one object.

```sql
-- WRONG: There is no 'ore' column
SELECT ore FROM structs.grid WHERE object_id = '1-142';

-- CORRECT: Filter by attribute_type
SELECT val FROM structs.grid WHERE object_id = '1-142' AND attribute_type = 'ore';
```

For multiple attributes on the same object, use multiple JOINs:

```sql
SELECT p.id,
    COALESCE(g_ore.val, 0) as ore,
    COALESCE(g_load.val, 0) as structs_load
FROM structs.player p
LEFT JOIN structs.grid g_ore ON g_ore.object_id = p.id AND g_ore.attribute_type = 'ore'
LEFT JOIN structs.grid g_load ON g_load.object_id = p.id AND g_load.attribute_type = 'structsLoad'
WHERE p.id = '1-142';
```

---

## Common Queries

### Player Resources

```sql
SELECT p.id, p.guild_id, p.planet_id, p.fleet_id,
    COALESCE(g_ore.val, 0) as ore,
    COALESCE(g_load.val, 0) as structs_load
FROM structs.player p
LEFT JOIN structs.grid g_ore ON g_ore.object_id = p.id AND g_ore.attribute_type = 'ore'
LEFT JOIN structs.grid g_load ON g_load.object_id = p.id AND g_load.attribute_type = 'structsLoad'
WHERE p.id = '1-142';
```

### Fleet Composition with Weapon Stats

```sql
SELECT s.id, st.class_abbreviation, s.operating_ambit,
    st.primary_weapon_control, st.primary_weapon_damage,
    st.primary_weapon_ambits_array, st.unit_defenses,
    st.counter_attack_same_ambit
FROM structs.struct s
JOIN structs.struct_type st ON st.id = s.type
WHERE s.owner = '1-142' AND s.location_type = 'fleet'
    AND s.is_destroyed = false
ORDER BY s.operating_ambit, s.slot;
```

### Raid Target Scouting

```sql
SELECT pl.id as planet, pl.owner, g_ore.val as ore,
    COALESCE(pa_shield.val, 0) as shield,
    COALESCE(g_load.val, 0) as structs_load
FROM structs.planet pl
JOIN structs.grid g_ore ON g_ore.object_id = pl.owner AND g_ore.attribute_type = 'ore'
LEFT JOIN structs.planet_attribute pa_shield ON pa_shield.object_id = pl.id
    AND pa_shield.attribute_type = 'planetaryShield'
LEFT JOIN structs.grid g_load ON g_load.object_id = pl.owner
    AND g_load.attribute_type = 'structsLoad'
WHERE g_ore.val > 0
ORDER BY g_ore.val DESC, shield ASC;
```

### Enemy Structs at a Planet

```sql
SELECT s.id, st.class_abbreviation, s.operating_ambit,
    st.primary_weapon_control, st.primary_weapon_damage,
    st.unit_defenses
FROM structs.struct s
JOIN structs.struct_type st ON st.id = s.type
JOIN structs.fleet f ON f.id = s.location_id
WHERE f.location_id = '2-105' AND s.is_destroyed = false
    AND s.location_type = 'fleet'
ORDER BY s.operating_ambit;
```

### Real-Time Threat Detection (Poll Pattern)

```sql
-- Set high-water mark on startup
SELECT COALESCE(MAX(seq), 0) FROM structs.planet_activity
WHERE planet_id IN ('2-105');

-- Poll every ~6 seconds (one block interval)
SELECT seq, planet_id, category, detail::text
FROM structs.planet_activity
WHERE planet_id IN ('2-105', '2-127')
    AND seq > $LAST_SEQ
ORDER BY seq ASC;
```

Watch for `fleet_arrive`, `raid_status`, and `struct_attack` categories.

### Struct Health and Defense Assignments

```sql
SELECT sa.object_id as struct_id, sa.attribute_type, sa.val
FROM structs.struct_attribute sa
WHERE sa.object_id = '5-1165';

SELECT defending_struct_id, protected_struct_id
FROM structs.struct_defender
WHERE protected_struct_id = '5-100';
```

---

## Stack Management

```bash
# Start all services
docker compose up -d

# Check service status
docker compose ps

# View blockchain sync progress
docker compose logs -f structsd --tail 20

# Stop (preserves all data)
docker compose down

# Destroy all data (start fresh)
docker compose down -v
```

---

## Port Summary

| Port | Service | Purpose |
|------|---------|---------|
| 26656 | structsd | P2P blockchain networking |
| 26657 | structsd | CometBFT RPC (transactions + queries) |
| 1317 | structsd | Cosmos SDK REST API |
| 5432 | structs-pg | PostgreSQL database |
| 80 | structs-proxy | Webapp (via reverse proxy) |
| 8080 | structs-webapp | Webapp (direct access) |
| 4222 | structs-nats | NATS client connections |
| 1443 | structs-nats | NATS WebSocket (GRASS events) |
| 3000 | structs-mcp | MCP server for AI agents |

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| "connection refused" on PG | Stack not started or PG not healthy yet | `docker compose ps` to check; wait for PG healthy |
| Query returns 0 rows | Chain sync not complete; data not indexed yet | Check `docker compose logs structsd` for sync progress |
| Container name not found | Container naming varies by installation | Run `docker compose ps` to find actual container names |
| "role does not exist" | Wrong PG role in connection string | Use `structs_indexer` role via the GRASS container |
| Slow PoW with guild stack | Multiple agents running concurrent PoW | CPU contention; stagger PoW operations or reduce parallelism |

---

## See Also

- [knowledge/infrastructure/guild-stack](https://structs.ai/knowledge/infrastructure/guild-stack) — Architecture overview and data flow
- [knowledge/infrastructure/database-schema](https://structs.ai/knowledge/infrastructure/database-schema) — Full table schemas and query patterns
- [structs-reconnaissance skill](https://structs.ai/skills/structs-reconnaissance/SKILL) — Intelligence gathering (CLI + PG)
- [structs-streaming skill](https://structs.ai/skills/structs-streaming/SKILL) — GRASS real-time events via NATS
