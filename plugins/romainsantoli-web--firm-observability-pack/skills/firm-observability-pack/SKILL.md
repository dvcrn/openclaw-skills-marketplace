---
name: firm-observability-pack
description: "Observability pipeline and CI audit pack. JSONL-to-SQLite trace ingestion and CI workflow validation. 2 observability tools."
---

# firm-observability-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Provides observability tooling: JSONL trace ingestion into SQLite for analysis,
and CI pipeline workflow validation ensuring proper security steps and test gates.

## Tools (2)

| Tool | Description |
|------|-------------|
| `openclaw_observability_pipeline` | JSONL→SQLite trace ingestion and querying |
| `openclaw_ci_pipeline_check` | CI workflow validation (security gates, test steps) |

## Usage

```yaml
skills:
  - firm-observability-pack

# Ingest traces and validate CI:
openclaw_observability_pipeline traces_path=/path/to/traces.jsonl
openclaw_ci_pipeline_check config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
