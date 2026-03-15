---
name: harness
description: "Agent engineering harness for any repo. Creates a short AGENTS.md table-of-contents, structured docs/ knowledge base (ARCHITECTURE, QUALITY, CONVENTIONS, COORDINATION), custom agent-readable linters (WHAT/FIX/REF format), CI enforcement, and execution plan templates. Supports Rust, Go, TypeScript, and Python. Use when setting up any repo for agent-first development, upgrading an existing AGENTS.md, or enforcing architectural lint gates. Includes --audit flag for tool lifecycle checks and L1/L2/L3 progressive disclosure."
---

# harness — Agent Engineering Harness

Implements the [OpenAI Codex team's agent-first engineering harness pattern](https://openai.com/index/harness-engineering/)
for any repo: short AGENTS.md TOC, structured docs/, custom linters with agent-readable errors,
CI enforcement, execution plan templates, doc-gardening.

Validated against: [Agent Tool Design Guidelines](https://github.com/bowen31337/agent-harness-skills/blob/main/docs/agent_tool_desig_guidelines.md) (2026-03-09)

## When to use
- Setting up a new repo for agent-first development
- Upgrading an existing repo's AGENTS.md to table-of-contents style
- Adding architectural lint enforcement to a repo
- Any repo where agents are doing most of the coding

## Supported Languages
- **Rust** (Substrate pallets, cargo workspace)
- **Go** (internal/ package structure)
- **TypeScript** (src/, npm)
- **Python** (pyproject.toml, uv/pytest) ← added 2026-03-09

## Usage

```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/harness"

# Scaffold harness for a repo (language auto-detected: Rust/Go/TypeScript/Python)
uv run python "$SKILL_DIR/scripts/scaffold.py" --repo /path/to/repo

# Scaffold with force-overwrite of existing AGENTS.md
uv run python "$SKILL_DIR/scripts/scaffold.py" --repo /path/to/repo --force

# Audit harness freshness (tool lifecycle check — no writes)
uv run python "$SKILL_DIR/scripts/scaffold.py" --repo /path/to/repo --audit

# Run lints locally
bash /path/to/repo/scripts/agent-lint.sh

# Check doc freshness (finds stale references in docs/)
uv run python "$SKILL_DIR/scripts/doc_garden.py" --repo /path/to/repo --dry-run

# Check doc freshness and open a fix PR
uv run python "$SKILL_DIR/scripts/doc_garden.py" --repo /path/to/repo --pr

# Generate execution plan for a complex task
uv run python "$SKILL_DIR/scripts/plan.py" \
  --task "Add IBC timeout handling" \
  --repo /path/to/repo
```

## What gets created

| File | Description |
|------|-------------|
| `AGENTS.md` | ~100 line TOC with L1/L2/L3 progressive disclosure markers |
| `docs/ARCHITECTURE.md` | Layer diagram + dependency rules (auto-generated from repo structure) |
| `docs/QUALITY.md` | Coverage targets + security invariants |
| `docs/CONVENTIONS.md` | Naming rules (language-specific) |
| `docs/COORDINATION.md` | Multi-agent task ownership + conflict resolution rules ← new |
| `docs/EXECUTION_PLAN_TEMPLATE.md` | Structured plan format for complex tasks |
| `scripts/agent-lint.sh` | Custom linter with agent-readable errors (WHAT / FIX / REF) |
| `.github/workflows/agent-lint.yml` | CI gate on every PR |

## Lint error format

Every lint error produced by `scripts/agent-lint.sh` follows this format:
```
LINT ERROR [<rule-id>]: <description of the problem>
  WHAT: <why this is a problem>
  FIX:  <exact steps to resolve it>
  REF:  <which doc to consult>
```

This means agents can read lint output and fix problems without asking a human.

## Agent Design Checklist (from tool design guidelines)

Before shipping any tool or skill change, verify:

- [ ] Is the tool shaped to what this model can actually do?
- [ ] Does it schema-enforce structured output where correctness matters?
- [ ] Is context loaded progressively (L1→L2→L3), not dumped upfront?
- [ ] Does it support multi-agent coordination if needed? (see COORDINATION.md)
- [ ] Have you measured model affinity (call frequency) vs just output quality?
- [ ] Is the total tool count at or below your ceiling? (target: ≤ 20 per agent)
- [ ] Do you have a plan to revisit this tool as model capabilities change?

## Progressive Disclosure Layers

The harness enforces a 3-layer context discipline:

| Layer | Where | When to load |
|-------|-------|--------------|
| L1 | `AGENTS.md` | Always — orientation, commands, invariants |
| L2 | `docs/` | Before coding — architecture, quality, conventions |
| L3 | Source files | On demand — grep/read specific files as needed |

**Rule:** Start with L1. Pull L2 before touching code. Pull L3 only when you need it.
Never pre-load all three layers — it crowds out working context.

## Tool Lifecycle (--audit)

Run `--audit` quarterly to check harness freshness:
- AGENTS.md has depth layer markers
- COORDINATION.md present (multi-agent support)
- Lint script uses current language tooling
- Python: ruff + pyright checks present
- AGENTS.md under 150 lines

## Safety

- **Never overwrites existing AGENTS.md** without `--force` flag
- Reads existing code structure before generating docs (no hallucinated APIs)
- All writes are previewed in `--dry-run` mode before committing

## References

- [OpenAI Codex harness engineering](https://openai.com/index/harness-engineering/)
- [Agent Tool Design Guidelines](https://github.com/bowen31337/agent-harness-skills/blob/main/docs/agent_tool_desig_guidelines.md)
- [ClawChain harness PR](https://github.com/clawinfra/claw-chain/pull/64)
- [EvoClaw harness PR](https://github.com/clawinfra/evoclaw/pull/27)
