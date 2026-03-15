# Cognition — Recommended Configuration

Add these settings to your `openclaw.json` under `agents.defaults`.

## Compaction & Memory Flush

```json
"compaction": {
  "reserveTokensFloor": 40000,
  "memoryFlush": {
    "enabled": true,
    "softThresholdTokens": 4000,
    "systemPrompt": "Session nearing compaction. Store durable memories now.",
    "prompt": "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store."
  }
}
```

**Why 40K:** Default 20K is too tight for agents with heavy tool use. 40K gives enough headroom for the memory flush to complete before compaction fires.

**softThresholdTokens:** 4K is the guide recommendation. 10K is more conservative (triggers flush earlier). Both work.

## Hybrid Search

```json
"memorySearch": {
  "enabled": true,
  "query": {
    "maxResults": 8,
    "hybrid": {
      "enabled": true,
      "vectorWeight": 0.7,
      "textWeight": 0.3,
      "candidateMultiplier": 4,
      "mmr": {
        "enabled": true,
        "lambda": 0.7
      },
      "temporalDecay": {
        "enabled": true,
        "halfLifeDays": 30
      }
    }
  },
  "cache": {
    "enabled": true,
    "maxEntries": 50000
  }
}
```

**vectorWeight 0.7 / textWeight 0.3:** Semantic similarity dominates, keyword matching catches exact terms. Proven ratio from OpenClaw's own implementation.

**MMR lambda 0.7:** Balanced diversity. Prevents 8 results that all say the same thing.

**temporalDecay halfLifeDays 30:** Recent memories score higher. Evergreen files (MEMORY.md, non-dated files) are never decayed.

## Context Pruning

```json
"contextPruning": {
  "mode": "cache-ttl",
  "ttl": "5m"
}
```

**Note:** 5m is the guide default. Longer TTLs (e.g., 4h) keep tool results in context longer — useful if your agent frequently re-references recent results, but consumes more context.
