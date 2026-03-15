---
name: agent-loops
description: "Multi-agent workflow orchestrator. Use when the user asks to build, create, make, ship, develop, or launch any software (apps, webapps, websites, mobile apps, APIs, tools, bots, dashboards, SaaS, MVPs); fix or debug bugs; review or audit code; research topics; refactor code; or publish skills."
---

# Agent Loops

Prebuilt multi-agent workflows that chain sequential and parallel steps, with real output passing between agents.

## Description

Agent Loops orchestrates multi-step agent pipelines. Each workflow defines a sequence of steps; each step runs via `claude -p` with a role-specific system prompt and agent-swarm model routing. Outputs chain between steps so each agent builds on the previous one's work.

Use when the user wants to:
- Build, create, or ship anything — apps, webapps, websites, mobile apps (iPhone/Android), desktop apps, APIs, CLIs, bots, dashboards, landing pages, SaaS products, MVPs, prototypes, plugins, extensions, microservices
- Fix, debug, troubleshoot, or diagnose bugs, errors, crashes, or failing tests
- Review, audit, or inspect code for bugs, security vulnerabilities, or quality issues
- Research, investigate, compare, or write reports on any topic
- Refactor, restructure, clean up, optimize, or modernize code
- Test, review, and publish a skill to ClawHub

## Installation

```bash
clawhub install agent-loops
```

Or clone into your skills directory:

```bash
git clone https://github.com/OpenClaw/agent-loops.git workspace/skills/agent-loops
```

Requires PyYAML for YAML workflows:

```bash
pip install pyyaml
```

## Usage

**Workflow selection — match the user's intent to a workflow:**

| User says something like... | Workflow |
|------------------------------|----------|
| "build me an app", "create a webapp", "make a website", "ship this feature", "develop a mobile app", "launch a SaaS", "make an iPhone app", "build an Android app", "create a desktop app", "make a CLI tool", "build an API", "create a bot", "make a dashboard", "build a landing page", "create an MVP", "prototype X", "add dark mode", "implement Y", "build a plugin", "make an extension", "create a service", "spin up a microservice", "scaffold a project" | `ship_feature` |
| "fix this bug", "debug X", "why is Y broken", "troubleshoot this error", "diagnose the crash", "this isn't working", "something's wrong with X", "getting an error when", "it crashes on", "the build is failing", "tests are broken", "patch this issue", "hotfix for X" | `bug_fix` |
| "review this code", "audit the codebase", "check for security issues", "inspect this PR", "find bugs in X", "analyze this module", "is this code safe", "check for vulnerabilities", "look over my changes", "do a security review", "scan for issues", "evaluate code quality" | `code_review` |
| "research X", "compare A vs B", "write a report on", "investigate Y", "explore options for", "what are the best practices for", "study the landscape of", "deep dive into", "summarize the state of", "pros and cons of", "analyze the market for", "write up findings on" | `research_report` |
| "refactor X", "clean up this code", "restructure Y", "reorganize the codebase", "optimize this module", "modernize the architecture", "reduce tech debt", "simplify this", "extract a service", "decouple X from Y", "improve code structure", "make this more maintainable" | `refactor` |
| "publish this skill", "push to ClawHub", "release this skill", "deploy to ClawHub", "ship this skill", "get this skill ready for publish" | `skill_publish` |

**Command pattern:**
```bash
python3 workspace/skills/agent-loops/scripts/run_workflow.py <workflow> "<user's request>" --apply
```

Pass the user's natural language request as the input. The workflow handles scoping, delegation, and output chaining automatically.

## Examples

**Example 1: Ship a feature**
*Scenario:* You want to scope, implement, and document a new feature.
*Action:* `python3 workspace/skills/agent-loops/scripts/run_workflow.py ship_feature "Add dark mode toggle to settings" --apply`
*Outcome:* PM scopes tasks, Dev implements with tests, Editor writes docs and changelog.

**Example 2: Fix a bug**
*Scenario:* A bug needs diagnosis, a fix, and regression tests.
*Action:* `python3 workspace/skills/agent-loops/scripts/run_workflow.py bug_fix "Login page crashes on empty password" --apply`
*Outcome:* Dev diagnoses root cause, Dev implements fix, Tester writes regression test, Editor documents the change.

**Example 3: Parallel code review**
*Scenario:* You want a code review and security audit run simultaneously.
*Action:* `python3 workspace/skills/agent-loops/scripts/run_workflow.py code_review "Review the auth module" --apply`
*Outcome:* Reviewer and Security auditor run in parallel, then Editor synthesizes a unified summary.

**Example 4: Override model**
*Scenario:* You want all steps to use a specific model.
*Action:* `python3 workspace/skills/agent-loops/scripts/run_workflow.py research_report "Compare REST vs GraphQL" --apply --model sonnet`
*Outcome:* All steps run with the specified model instead of agent-swarm routing.

## Commands

```bash
python3 workspace/skills/agent-loops/scripts/run_workflow.py <workflow> "<input>"              # Dry-run a workflow
python3 workspace/skills/agent-loops/scripts/run_workflow.py <workflow> "<input>" --apply       # Run agents for real
python3 workspace/skills/agent-loops/scripts/run_workflow.py --list                             # List available workflows
python3 workspace/skills/agent-loops/scripts/run_workflow.py --list --json                      # List workflows as JSON
python3 workspace/skills/agent-loops/scripts/run_workflow.py <workflow> "<input>" --apply --json # Output results as JSON
python3 workspace/skills/agent-loops/scripts/run_workflow.py <workflow> "<input>" --model sonnet # Override model for all steps
python3 workspace/skills/agent-loops/scripts/run_workflow.py <workflow> "<input>" --timeout 900  # Set per-step timeout (seconds)
python3 workspace/skills/agent-loops/scripts/run_workflow.py <workflow> "<input>" -v             # Verbose output
```

- **`<workflow>`** — Workflow id: `ship_feature`, `bug_fix`, `code_review`, `research_report`, `refactor`, `skill_publish`
- **`--apply`** — Actually spawn agents (default is dry-run)
- **`--list`** — List all available workflows
- **`--json`** — Output results as JSON for programmatic use
- **`--model`** — Override agent-swarm routing with a specific model
- **`--timeout`** — Per-step timeout in seconds (default: 600)
- **`-v`** — Show full task text per step
