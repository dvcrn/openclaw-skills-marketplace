---
name: llm-signal-geo-analyst
description: "Run LLM Signal GEO analyst workflows from OpenClaw. Use when you need to fetch deterministic GEO action plans, check site health status, and execute/review hosted or self-hosted agent workflows with approval-safe guidance."
homepage: https://www.llmsignal.app/docs/agents
---

# LLM Signal GEO Analyst

Use this skill to operate LLM Signal agent flows from OpenClaw.

## Required environment

- `LLMSIGNAL_BASE_URL` (example: `https://www.llmsignal.app`)
- `LLMSIGNAL_SITE_ID`
- `LLMSIGNAL_API_KEY`

## Execution policy

1. Call `POST /api/agent/v1/plan` before recommending actions.
2. Automatically execute only `auto_safe` actions.
3. Route `manual` and `assist` actions to human approval.
4. Never output API keys or secrets.

## Run plan request

```bash
{baseDir}/scripts/fetch-plan.sh
```

## Run status request

```bash
{baseDir}/scripts/fetch-status.sh
```

## Output format for each recommended action

Return:

1. `title`
2. `priority`
3. `reason`
4. `exact steps`
5. `command/diff scaffold` (if present)
6. `approval required` (`yes` for manual/assist, `no` for auto_safe)

## Notes

- Agent API access is limited to Growth and Pro plans.
- Use `persist=true` in plan calls to store run history and outcomes.

