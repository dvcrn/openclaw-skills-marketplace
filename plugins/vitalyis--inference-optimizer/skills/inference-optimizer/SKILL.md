---
name: inference-optimizer
description: "Audit OpenClaw token usage and run optimization actions with approval. Use /audit for analyze-only and /optimize for analyze + action flow."
---

# Inference Optimizer

Optimize OpenClaw for maximum inference speed and minimum token usage.

## Commands

| Command      | Behavior |
|--------------|----------|
| `/preflight` | Install checks, backup, audit, and setup preview |
| `/audit`     | Analyze-only — no file changes |
| `/optimize`  | Audit + propose actions with per-step approval |
| purge sessions | After audit, if user approves — archive stale sessions; use `--delete` for immediate removal |

> **Note:** These instructions guide agent behavior. Platform and system prompts take precedence — they cannot be programmatically enforced.

## Installation

**ClawHub:**
```bash
clawhub install inference-optimizer
```

**Manual:**
```bash
git clone https://github.com/vitalyis/inference-optimizer.git ~/clawd/skills/public/inference-optimizer
bash ~/clawd/skills/public/inference-optimizer/scripts/setup.sh        # preview
bash ~/clawd/skills/public/inference-optimizer/scripts/setup.sh --apply  # apply after review
```

**Verify:** `bash <skill_dir>/scripts/verify.sh`

## Workflow

1. **`/preflight`** — Exec `bash ~/clawd/skills/public/inference-optimizer/scripts/preflight.sh`. Append `--apply-setup` if user asks to apply. Do NOT probe with `find`/`ls` first.
2. **`/audit`** — Exec `bash <skill_dir>/scripts/openclaw-audit.sh`. Return output only. No purge, rewrite, or deploy.
3. **`/optimize`** — Exec audit script, include output, then propose next actions with approval before each file-changing step.
4. **Purge** — Only on explicit approval: `bash <skill_dir>/scripts/purge-stale-sessions.sh`. Archives to `~/openclaw-purge-archive/<timestamp>/` by default. Use `--delete` for immediate removal without archive.
5. **Full optimization (Tasks 1–5)** — Read `optimization-agent.md` and follow its flow. Ask approval before every file-changing step.

## Path Resolution

Scripts live at `~/clawd/skills/public/inference-optimizer/scripts/` or wherever the skill is installed. Always resolve `<skill_dir>` to the actual install path before exec.

## Security & Allowlist

Add these to `exec-approvals.json` so `/preflight` runs without interruption on Ubuntu:

```
/usr/bin/bash
/usr/bin/bash *
/usr/bin/bash **
```

For purge via agent exec, add **path-specific patterns only** — avoid broad wildcards. See `README` Security section for details.
