---
name: memory-health-probe
description: "QMD memory system telemetry — measure index health, BM25 retrieval quality, coverage maps, and trend analysis. Use when running QMD memory backend and need diagnostics on retrieval quality, index freshness, or collection coverage."
---

# Memory Health Probe

Telemetry for QMD memory systems. Measures index health, retrieval quality, and coverage to catch degradation before it affects agent performance.

## Metrics Captured

1. **Index health** — file count, chunk count, index size, staleness
2. **BM25 quality** — hit rate + score distribution over canonical queries
3. **Gateway events** — session-memory saves, QMD armed events
4. **Coverage map** — which collections are hit for which query categories

## Usage

```bash
python3 scripts/memory_probe.py              # Run probe, log to Langfuse
python3 scripts/memory_probe.py --dry-run    # Print results only
python3 scripts/memory_probe.py --trend      # Show trend over stored snapshots
```

## Files

- `scripts/memory_probe.py` — Probe script with Langfuse integration
