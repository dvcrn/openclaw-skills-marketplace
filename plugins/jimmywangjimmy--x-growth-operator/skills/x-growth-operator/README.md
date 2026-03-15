# X Growth Operator

An OpenClaw-style skill for X operations.

It turns a brief into a mission, pulls opportunities from X, scores them, drafts actions, and can execute approved posts through the official X OAuth API.

## What It Includes

- `SKILL.md`: the skill entrypoint and operating rules
- `scripts/`: deterministic workflow and execution scripts
- `references/`: scoring and mission references
- `examples/`: sample briefs, opportunities, notes, and queries

## Install

Clone or copy this folder into your local skills directory, or keep it as a standalone repo and point OpenClaw at it.

Install Node dependencies:

```bash
cd scripts
npm install
```

Create `scripts/.env` from `scripts/.env.example` and fill:

- `X_API_KEY`
- `X_API_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`
- `DESEARCH_API_KEY`

If you need a proxy for X:

- `HTTP_PROXY`
- `HTTPS_PROXY`
- `ALL_PROXY`
- `NO_PROXY`

## Quick Start

Build a mission:

```bash
python3 scripts/ingest_goal.py --doc examples/brand_brief.md --mission data/mission.json
```

Run live search to plan:

```bash
python3 scripts/live_search_and_plan.py \
  --mission data/mission.json \
  --query "openclaw OR local agent OR coding agent" \
  --count 10
```

Generate an action:

```bash
python3 scripts/propose_action.py \
  --mission data/mission.json \
  --opportunities data/opportunities_scored.json \
  --opportunity-id YOUR_OPPORTUNITY_ID \
  --output data/action.json
```

Execute an approved action:

```bash
python3 scripts/execute_action.py \
  --mission data/mission.json \
  --action data/action.json \
  --log data/execution_log.jsonl \
  --approved \
  --mode x-api
```

## Share It

Use the packaging script to build a clean skill bundle without secrets or generated data:

```bash
python3 scripts/build_skill_bundle.py
```

The zip will be written to `dist/x-growth-operator-skill.zip`.

## Current Limits

- Reply and quote actions can be blocked by X conversation permissions
- The best-supported path today is:
  - mission
  - live search
  - scoring
  - draft
  - approved original post

