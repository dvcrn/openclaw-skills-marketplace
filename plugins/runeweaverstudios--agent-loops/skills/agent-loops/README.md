# Agent Loops

Prebuilt multi-agent workflows. Each workflow is a sequence (or parallel group) of steps; each step runs via `claude -p` with agent-swarm routing for model selection.

## Run a workflow

```bash
# Dry-run (see what would happen)
python3 workspace/skills/agent-loops/scripts/run_workflow.py ship_feature "Add dark mode to settings"

# Actually run agents
python3 workspace/skills/agent-loops/scripts/run_workflow.py ship_feature "Add dark mode" --apply

# Override model for all steps
python3 workspace/skills/agent-loops/scripts/run_workflow.py bug_fix "Fix login crash" --apply --model sonnet

# List available workflows
python3 workspace/skills/agent-loops/scripts/run_workflow.py --list

# JSON output (for piping)
python3 workspace/skills/agent-loops/scripts/run_workflow.py ship_feature "Add dark mode" --apply --json
```

## Workflows

| Workflow | Steps | Description |
|----------|-------|-------------|
| **ship_feature** | PM → Dev → Editor | Scope, implement, document a feature |
| **bug_fix** | Dev → Dev → Tester → Editor | Diagnose, fix, test, document a bug |
| **code_review** | Reviewer + Security (parallel) → Editor | Code review and security audit in parallel, then unified summary |
| **research_report** | Researcher → Architect → Editor → Editor | Research, outline, draft, polish |
| **refactor** | Architect → Architect → Dev → Tester | Analyze, plan, implement, verify |
| **skill_publish** | Tester → Editor → Reviewer → Dev | Test, format docs, review, publish to ClawHub |

## Workflow YAML format

```yaml
id: my_workflow
name: My Workflow
description: What it does.
steps:
  # Sequential step
  - id: step_one
    agent: dev              # Agent role (pm, dev, editor, reviewer, researcher, tester, architect)
    task_template: "Do something with: {{ user_input }}"
    timeout: 600            # Optional, seconds (default: 600)
    optional: true          # Optional, don't abort on failure

  # Parallel group — runs all substeps concurrently
  - id: my_group
    parallel:
      - id: sub_a
        agent: reviewer
        task_template: "Review: {{ user_input }}"
      - id: sub_b
        agent: tester
        task_template: "Test: {{ user_input }}"

  # Use outputs from previous steps via {{ step_id_output }}
  - id: step_two
    agent: editor
    task_template: "Summarize: {{ step_one_output }}\n\n{{ my_group_output }}"
```

## Features

- **Real agent execution** — `--apply` spawns agents via `claude -p` and captures their output
- **Output chaining** — Each step's output is available to subsequent steps as `{{ step_id_output }}`
- **Parallel steps** — Run multiple steps concurrently in a `parallel:` group
- **Agent-swarm routing** — Automatic model selection per task via the agent-swarm router
- **Model override** — `--model` forces a specific model for all steps
- **Optional steps** — Mark steps `optional: true` so failures don't abort the workflow
- **Run persistence** — Live runs are saved to `runs/` as JSON for auditing
- **Dry-run mode** — Default mode shows what would happen without spawning agents

## Requirements

- `claude` CLI (Claude Code) in PATH
- PyYAML: `pip install pyyaml` (for YAML workflows; JSON works without it)
- Agent Swarm router at `workspace/skills/agent-swarm/scripts/router.py` (optional, for smart model routing)
