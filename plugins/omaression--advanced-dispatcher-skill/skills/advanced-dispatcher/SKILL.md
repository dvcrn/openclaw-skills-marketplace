---
name: advanced-dispatcher
description: "Route mid-session work to the right spawned model without changing the fixed main session. Use for coding, architecture, math, algorithms, web development, brainstorming, research, long-context reading, quick scripts, formatting, multi-model tradeoff evaluation, or structured build pipelines triggered by buildq:, build:, or buildx:. Default to strict no-Claude routing; allow Claude only when the current prompt explicitly includes --force-claude."
---

# Advanced Dispatcher

Use this skill to classify work, dispatch it to the best spawned model, and return the result to the main session.

## Runtime requirements

This skill assumes the runtime can spawn work on these model families:

- `openai-codex/*`
- `opencode-go/*`
- optional `anthropic/*` only when `--force-claude` is present

If the host is self-managed, configure whatever provider credentials your runtime expects before using this skill. Typical setups use environment variables for OpenAI, Opencode, and optionally Anthropic, but the exact variable names depend on the host/runtime wrapper. Do not hardcode secrets into the skill package.

## Non-negotiable rules

- Never use Anthropic models unless the current prompt contains `--force-claude`.
- Reject legacy flags `--use-claude`, `--force-opus`, and `--no-opus`.
- Treat `--force-claude` as prompt-scoped, not session-scoped.
- Prefer deterministic routing over ad hoc judgment.
- Use `long` cache retention for `openai-codex/*` routes.
- Use `short` cache retention for `opencode-go/*` routes.
- Do not use Claude in build pipelines; keep `--force-claude` limited to tradeoff proposal generation.

## Standard routing

Choose exactly one primary route:

- **Code & architecture** → `openai-codex/gpt-5.4`
- **Math & algorithms** → `opencode-go/glm-5`
- **Web dev & brainstorming** → `opencode-go/minimax-m2.5`
- **Research & long context** → `opencode-go/kimi-k2.5`
- **Quick scripts & formatting** → `openai-codex/gpt-5.3-codex-spark`

If a request spans categories, route by the highest-risk deliverable:

1. Architecture or production code wins.
2. Math or algorithm correctness beats brainstorming.
3. Long-context ingestion beats light formatting.
4. Formatting-only tasks stay on Spark.

## Tradeoff protocol

Trigger tradeoff mode when the user asks to:
- evaluate tradeoffs
- compare approaches, options, designs, or architectures
- choose between competing solutions
- judge which architecture or design is better

### Default tradeoff route

Generate proposals in parallel with:
- `opencode-go/glm-5`
- `openai-codex/gpt-5.3-codex`

Judge both proposals with:
- `openai-codex/gpt-5.4`

### Tradeoff route with `--force-claude`

Use Claude only for proposal generation:
- `anthropic/claude-sonnet-4-6`
- `anthropic/claude-opus-4-6`

Keep the judge on:
- `openai-codex/gpt-5.4`

Do not use Claude anywhere else in the flow.

## Build pipeline protocol

Use the build pipeline when the prompt starts with one of these prefixes:
- `buildq:` → quick pipeline
- `build:` → standard pipeline
- `buildx:` → strict pipeline

### buildq:

Use for smaller scoped coding work.

Steps:
1. plan → `openai-codex/gpt-5.4`
2. implement → `openai-codex/gpt-5.4`
3. test → `opencode-go/glm-5`
4. simplify → `openai-codex/gpt-5.3-codex`
5. retest → `opencode-go/glm-5`

### build:

Use for the normal serious coding workflow.

Steps:
1. parallel-plan-a → `openai-codex/gpt-5.4`
2. parallel-plan-b → `opencode-go/glm-5`
3. judge-plan → `openai-codex/gpt-5.4`
4. boilerplate → `openai-codex/gpt-5.3-codex-spark`
5. implement → `openai-codex/gpt-5.4`
6. test → `opencode-go/glm-5`
7. simplify → `openai-codex/gpt-5.3-codex`
8. retest → `opencode-go/glm-5`
9. review-resolve → `openai-codex/gpt-5.4`
10. final-test → `opencode-go/glm-5`

### buildx:

Use for stricter, higher-value delivery.

Steps:
1. parallel-plan-a → `openai-codex/gpt-5.4`
2. parallel-plan-b → `opencode-go/glm-5`
3. judge-plan → `openai-codex/gpt-5.4`
4. boilerplate → `openai-codex/gpt-5.3-codex-spark`
5. implement → `openai-codex/gpt-5.4`
6. test → `opencode-go/glm-5`
7. simplify → `openai-codex/gpt-5.3-codex`
8. retest → `opencode-go/glm-5`
9. review-resolve-a → `openai-codex/gpt-5.4`
10. test-a → `opencode-go/glm-5`
11. review-resolve-b → `opencode-go/kimi-k2.5`
12. final-test → `opencode-go/glm-5`

## Judge output contract

When a judge-plan step runs, require these sections:
1. selected architecture
2. why it won
3. project/file structure
4. implementation order
5. test plan
6. simplification targets
7. done criteria

For `buildx:`, also include:
- risk list
- likely failure modes
- review checklist

## Simplify contract

The simplify step must:
- remove dead code
- remove speculative abstractions
- reduce duplication
- shorten over-engineered interfaces
- delete non-needed helpers
- prefer fewer files when clarity is not lost
- preserve tested behavior

The simplify step must not:
- rewrite architecture unnecessarily
- add clever abstractions
- expand scope

## Session transitions

If the user shifts into a sustained new domain, summarize the active state with `openai-codex/gpt-5.3-codex-spark` and suggest a fresh session only when repeated cross-domain dispatching would be wasteful.

## Context discipline

- Fetch only the files needed for the routed task.
- Do not ingest entire repositories unless the task explicitly requires it.
- Treat one-off quick fixes as stateless unless the user asks to preserve them.

## Implementation contract

`dispatcher.py` is the routing source of truth. It must:

- produce deterministic `RoutePlan` objects
- expose route choice, cache retention, rationale, and pipeline steps
- support parallel proposal generation plus a separate judge in tradeoff mode
- support `buildq:`, `build:`, and `buildx:` pipeline modes
- reject empty prompts, unknown domains, and legacy flags
- keep routing updates easy by centralizing model and trigger definitions

## Validation checklist

Before shipping updates:

1. Run `tests/test_dispatcher.py`.
2. Run one end-to-end smoke test for a tradeoff request.
3. Run smoke tests for `buildq:`, `build:`, and `buildx:`.
4. Confirm Claude is unreachable unless `--force-claude` is present.
5. Confirm Claude never appears in build pipelines.
6. Confirm all OpenAI Codex routes use `long` retention.
7. Confirm all `opencode-go` routes use `short` retention.
