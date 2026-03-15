# Scripts - Memory Optimization Skill

This directory contains executable scripts for the memory optimization system.

## Scripts

### daily-cleanup.sh

Automated 3-minute daily memory maintenance script.

**Usage:**
```bash
./memory/daily-cleanup.sh
```

**Features:**
- Verifies TL;DR exists
- Checks for bullet points
- Validates progress tracking
- Confirms MEMORY.md
- Reports file statistics

**Test Result:** 6/6 checks passed ✅

---

### test-memory-system.sh

Complete testing framework for memory improvements.

**Usage:**
```bash
./memory/test-memory-system.sh
```

**Tests:**
1. ✅ TL;DR Recovery - Content present and formatted
2. ✅ Tags Search - Grep for #memory, #decision, #improvement
3. ✅ Three-File Pattern - All 3 files exist
4. ✅ Progress Tracking - Tasks tracked correctly
5. ✅ HEARTBEAT Integration - Memory checklist present
6. ✅ File Size Check - Under 10KB target

**Test Result:** 6/6 passed ✅

---

### memory_ontology.py

Knowledge Graph management tool.

**Usage:**
```bash
python3 scripts/memory_ontology.py <command> [options]
```

**Commands:**
- `create` - Create new entity with validation
- `relate` - Establish relationships
- `query` - Search by type, tags, status
- `get` - Retrieve specific entity
- `related` - Find related entities
- `validate` - Verify graph integrity
- `list` - List all entities
- `export` - Export to Markdown
- `stats` - Show statistics

**Examples:**

```bash
# Create a decision
python3 scripts/memory_ontology.py create --type Decision --props '{"title":"Use KG","rationale":"Based on Moltbook advice","made_at":"2026-03-12T23:00:00+08:00","confidence":0.9,"status":"final","tags":["#decision","#memory"]}'

# Query by tags
python3 scripts/memory_ontology.py query --tags "#memory" "#decision"

# Get related entities
python3 scripts/memory_ontology.py related --id dec_xxx

# Validate graph
python3 scripts/memory_ontology.py validate

# Show stats
python3 scripts/memory_ontology.py stats
```

---

## Installation

These scripts are bundled with the memory-optimization skill. They work in the OpenClaw workspace environment.

## Requirements

- Bash 4.0+
- Python 3.8+
- Standard Unix tools (grep, sed, awk)

## Notes

- All scripts expect to run from workspace root
- Paths are relative to `/root/.openclaw/workspace/`
- KG tool requires PyYAML: `pip install pyyaml`