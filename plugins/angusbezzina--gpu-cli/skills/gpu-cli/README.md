GPU CLI ClawHub Skill (Stable)

Purpose: Safely run local `gpu` commands from OpenClaw/ClawHub agents with guardrails (dry‑run preview, command whitelist, budget/time caps, and clear remediation), without modifying GPU CLI itself.

What this skill does
- Executes only `gpu …` commands via a wrapper (`runner.sh`) with a strict whitelist and injection checks.
- Performs preflight checks (`gpu --version`, `gpu doctor --json`).
- Defaults to dry‑run previews; can enforce confirm + caps.
- Provides optional cost/time caps before execution; attempts cleanup (`gpu stop -y`) on timeout/cancel.
- Maps common exit codes to helpful guidance (auth, daemon restart, transient retry).

Non-goals
- No telemetry, no secret handling; uses the installed GPU CLI and your provider keys in OS keychain.
- Does not change GPU CLI behavior; all safeguards are in this skill only.

Quick usage (from an agent)
- Trigger: "/gpu" or phrases like "Use GPU CLI to …" (as configured on ClawHub)
- Example: "Use GPU CLI to run gpu status --json"
- Example: "Use GPU CLI to run gpu run python train.py on an RTX 4090"

Files
- `manifest.yaml` — ClawHub skill metadata, permissions, triggers, settings.
- `runner.sh` — Execution wrapper with guardrails.
- `selftest.sh` — Local checks for preflight and injection denial.
- `templates/prompts.md` — Curated prompts for common tasks.

Notes for publishers
- Mark channel as Stable, add logo/screenshots/demo, and link docs at `apps/portal/content/docs/ai-agent-skill.mdx`.
- Keep permissions minimal: Bash + Read, workspace‑scoped; network off for the skill itself.

