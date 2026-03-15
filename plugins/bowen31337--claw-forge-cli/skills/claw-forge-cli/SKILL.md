---
name: claw-forge-cli
description: "Use the claw-forge CLI to run autonomous coding agents on a project until all features pass. Covers the full workflow: init → spec → plan → run → status → ui. Use when a user asks to build a project with claw-forge, run agents on a codebase, generate a feature DAG, manage the provider pool, or fix bugs with the reproduce-first protocol."
---

# claw-forge CLI

**claw-forge** is a multi-provider autonomous coding agent harness.  
Agents run in parallel, claim features from a dependency DAG, and keep working
until every feature passes — or you stop them.

GitHub: https://github.com/clawinfra/claw-forge  
PyPI: https://pypi.org/project/claw-forge/

## Install

```bash
pip install claw-forge
# or (recommended):
uv pip install claw-forge
```

---

## Full Workflow

### 1 — Bootstrap a project

```bash
cd my-project
claw-forge init
```

Creates:
- `CLAUDE.md` — agent instructions (stack-aware)
- `.claude/` — slash commands (`/create-spec`, etc.)
- `claw-forge.yaml` — provider pool config
- `.env.example` — API key template

### 2 — Write a spec

Create `app_spec.txt` (plain text) or `app_spec.xml` (structured XML):

```text
Project: My App
Stack: Python, FastAPI, SQLite

Authentication:
- JWT login endpoint
- Token refresh
- Session management

Dashboard:
- Real-time stats via WebSocket
- Export CSV
```

Or use the Claude slash command inside Claude Code: `/create-spec`

### 3 — Plan: parse spec → feature DAG

```bash
claw-forge plan app_spec.txt
```

- Decomposes spec into atomic features
- Assigns dependency edges (A must pass before B starts)
- Writes task graph to `.claw-forge/state.db`
- Uses Opus by default (planning is the most critical step)

```bash
# Use Sonnet if cost matters more
claw-forge plan app_spec.txt --model claude-sonnet-4-6
```

### 4 — Run agents

```bash
claw-forge run
```

Default: 5 parallel coding agents, reads `claw-forge.yaml`.

```bash
# More concurrency
claw-forge run --concurrency 8

# Pin a specific model
claw-forge run --model claude-opus-4-6

# YOLO mode — skip human-input gates, max speed, aggressive retry
claw-forge run --yolo

# Preview without executing
claw-forge run --dry-run

# Use hashline edit mode (better for weaker models — 6.7%→68.3% benchmark)
claw-forge run --edit-mode hashline
```

### 5 — Check progress

```bash
claw-forge status
```

Shows: passing/failing/running/pending feature counts, recommended next action.

### 6 — Open the Kanban UI

```bash
claw-forge ui
```

Opens a browser-based Kanban board at `http://localhost:8888`.  
Shows real-time agent activity, feature status, costs, and logs.

---

## All Commands

| Command | Purpose |
|---------|---------|
| `init` | Bootstrap project (CLAUDE.md, config, slash commands) |
| `plan <spec>` | Parse spec → feature DAG in state DB |
| `run` | Run agents until all features pass |
| `status` | Show progress and recommended next action |
| `ui` | Launch Kanban UI at localhost:8888 |
| `dev` | Start API + Vite dev server (for UI development) |
| `add <spec>` | Add features to an existing project (brownfield) |
| `pause` | Drain mode: finish in-flight, start no new agents |
| `resume` | Resume after pause |
| `fix <desc>` | Fix a bug using RED→GREEN reproduce-first protocol |
| `merge` | Squash-merge a feature branch to target |
| `input` | Answer pending human-input questions interactively |
| `pool-status` | Show provider pool health and current routing |
| `state` | Start the AgentStateService REST + WebSocket API |

---

## Config: `claw-forge.yaml`

```yaml
# Provider pool — add as many as you have keys for
providers:
  anthropic-primary:
    type: anthropic
    api_key: ${ANTHROPIC_API_KEY}
    priority: 1
    enabled: true
    max_rpm: 50
    model: claude-sonnet-4-6

  anthropic-backup:
    type: anthropic
    api_key: ${ANTHROPIC_API_KEY_2}
    priority: 2
    enabled: true
    max_rpm: 30
    model: claude-sonnet-4-6

# Pool routing strategy
pool:
  strategy: priority       # priority | round_robin | least_cost

# Model aliases (use in --model flag)
model_aliases:
  fast: claude-haiku-4-5
  smart: claude-opus-4-6
  default: claude-sonnet-4-6

# Git integration
git:
  enabled: true
  merge_strategy: auto     # auto | squash | merge
```

---

## Edit Modes

### `str_replace` (default)
Standard exact-text matching. Works well with capable models (Sonnet, Opus).

### `hashline` (recommended for weaker models)
Content-addressed line tagging. Each line gets a 3-char hash prefix.  
Model references lines by hash — immune to whitespace/indentation drift.  
Benchmark: 6.7% → 68.3% success rate improvement on Grok Code Fast.

```bash
claw-forge run --edit-mode hashline
```

---

## Brownfield (add to existing project)

```bash
# Write additions spec
cat > additions_spec.xml << 'EOF'
<project_specification>
  <project_name>my-app</project_name>
  <features_to_add>
    <auth>
      - Add OAuth2 Google login
      - Add rate limiting to auth endpoints
    </auth>
  </features_to_add>
</project_specification>
EOF

claw-forge add additions_spec.xml
```

---

## Bug Fix Protocol

```bash
# Reproduce-first: agent writes failing test, then fixes it
claw-forge fix "Login fails when email has uppercase letters"
```

---

## Common Patterns

### Quick greenfield project
```bash
mkdir my-api && cd my-api
claw-forge init
# write app_spec.txt
claw-forge plan app_spec.txt
claw-forge run --concurrency 3
claw-forge status
```

### Cost-optimised run
```bash
# Mix cheap + expensive: cheap model in pool for simple tasks
claw-forge run --model claude-haiku-4-5 --concurrency 10
```

### Multi-provider failover
```bash
# Add multiple providers to claw-forge.yaml
# Pool auto-fails over on rate limits or errors
claw-forge pool-status    # check health
claw-forge run            # runs with automatic failover
```

### YOLO overnight run
```bash
claw-forge run --yolo --concurrency 8
# Come back in the morning — all features should be passing
```

---

## Tips

- **Planning quality = outcome quality.** Don't skimp on the planning model. Use Opus for `plan`.
- **More concurrency ≠ always better.** Each agent needs context. 3–5 is usually the sweet spot.
- **`--edit-mode hashline`** dramatically helps weaker/cheaper models that struggle with exact text matching.
- **`claw-forge status`** tells you exactly what to do next — trust it.
- **`claw-forge ui`** is the best way to monitor long runs — live logs per agent, cost tracking, dependency graph.
- Provider API keys go in `.env` (never commit). `.env.example` is the template.
