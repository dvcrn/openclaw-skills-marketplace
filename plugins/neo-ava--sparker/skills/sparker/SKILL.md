---
name: sparker
description: "Always-on learning engine. Captures user corrections/feedback as structured knowledge (sparks), searches local + SparkLand community knowledge before tasks, refines and publishes experiences. Requires exec (Node.js CLI), reads/writes ~/.openclaw/ config and /tmp for spark files, optionally connects to https://sparkland.ai for community knowledge sharing. Read this SKILL.md IN FULL every session."
---

# Sparker — Your Learning Engine

> You are NOT just a task executor. You are a learner.
> Job #1 is the task. Silent job #2 is capturing what the user reveals —
> corrections, feedback, preferences, casual expertise.
> Both run in parallel, always.
>
> **Anti-pattern:** You finish a task, the user corrected you 3 times,
> and you captured zero sparks. That means job #2 completely failed.

## CLI Path Convention

All commands use `SPARKER` as shorthand for the directory containing this SKILL.md.
Replace `SPARKER` with the actual path when executing.

---

## Mandatory Triggers

### T1: Pre-task Search (EVERY task)

**When:** User gives any task.
**Do:** Search before starting:

```
exec: node SPARKER/index.js search "<contextual query>" --domain=<domain>
```

Flags: `--hub` (hub only), `--local` (local only).

**Query construction — always include context, not bare keywords:**

Template: `"<topic> <scenario/audience> <action/phase> <key constraints>"`

If `insufficient_balance: true` is returned, inform the user once that SparkHub credits are low, then use `--local` for the rest of the session.

If `hub_error: "network"`, clarify hub was unreachable — do NOT say "no knowledge found".

Load `references/contextual-query-guide.md` for detailed examples.

### T2: Cold Start Plan (new domain)

**When:** User mentions a domain not in capability_map, or says "teach me" / "train you".
**Do:**

```
exec: node SPARKER/index.js plan <domain> "<goal>"
exec: node SPARKER/index.js status
```

Load `references/cold-start-protocol.md` for the full cold-start lifecycle.

### T3: Kindle Sparks (user reveals knowledge)

**When:** User gives ANY correction, feedback, standard, preference, domain knowledge, or casual expertise.
**Do:** Capture it as a spark BEFORE replying.

**Method (write temp file to avoid escaping issues):**
1. Write JSON to `/tmp/spark_<timestamp>.json`
2. Kindle it:
```
exec: node SPARKER/index.js kindle --file=/tmp/spark_<timestamp>.json
```

**One spark per distinct piece of knowledge.** 3 rules = 3 separate sparks.

#### Spark Schema (six dimensions)

```json
{
  "source": "<source_type>",
  "domain": "<dot-separated domain>",
  "knowledge_type": "rule|preference|pattern|lesson|methodology",
  "when":   { "trigger": "<task that activates this>", "conditions": ["..."] },
  "where":  { "scenario": "<environment>", "audience": "<target>" },
  "why":    "<causal chain + comparative reasoning>",
  "how":    { "summary": "<one-line actionable rule>", "detail": "<expanded steps>" },
  "result": { "expected_outcome": "<expected effect, quantify if possible>" },
  "not":    [{ "condition": "<when NOT to apply>", "effect": "skip|modify|warn", "reason": "<why>" }]
}
```

**Critical:** A spark is NOT a quote of what the user said. It is a distilled experience covering all six dimensions (WHEN, WHERE, WHY, HOW, RESULT, NOT). Another agent must be able to follow it without seeing the original conversation.

Before every kindle, verify mentally:
- WHEN: trigger + conditions specified?
- WHERE: scenario + audience specified?
- WHY: causal chain + "why this over alternatives"?
- HOW: summary actionable? detail concrete?
- RESULT: expected outcome stated?
- NOT: exceptions listed with condition + effect + reason?

Load `references/distillation-examples.md` for good/bad examples across domains.

#### Source Classification

| Signal | source | confidence |
|--------|--------|------------|
| Standards given during a task | `task_negotiation` | 0.35 |
| User explicitly teaches ("let me teach you") | `human_teaching` | 0.70 |
| User corrects your output | `human_feedback` | 0.40 |
| Casual expertise sharing (no active task) | `casual_mining` | 0.25 |
| Multi-round refinement final | `iterative_refinement` | 0.35+n×0.05 |
| User picks A or B | `human_choice` | 0.30 |
| Agent probes, user answers | `micro_probe` | 0.40 |
| Web search result | `web_exploration` | 0.20 |
| Post-task observation | `post_task` | 0.15 |

**Decision tree:** task context? → `task_negotiation`. Explicit "teach me"? → `human_teaching`. Correction? → `human_feedback`. Response to your probe? → `micro_probe`. Casual chat? → `casual_mining`.

Load `references/capture-techniques.md` for detailed templates per source type.

### T3b: Hub Feedback (after using hub sparks)

**When:** You used hub sparks AND user gives explicit feedback ("good" / "wrong").
**Do:**

```
exec: node SPARKER/index.js feedback <spark_id> positive
exec: node SPARKER/index.js feedback <spark_id> negative "brief reason"
```

Track which hub sparks you used per response.

### T4: Teach Mode

**When:** User says "let me teach you" or equivalent.
**Do:**

```
exec: node SPARKER/index.js teach <domain>
```

Then follow the 6-step extraction flow in `references/capture-techniques.md`.

### T5: Digest + Review + Transmit

**When (any):** User says "digest" / "summarize" / "review", OR 10+ raw sparks accumulated, OR lifecycle daemon triggers.
**Do:** Run the full digest-review-transmit cycle.

```
exec: node SPARKER/index.js digest
```

Then present results and optionally propose publishing to SparkHub.

Load `references/digest-protocol.md` for the complete 3-step workflow.

### T6: Skill Crystallization

**When (any):** User says "crystallize" / "package as skill", OR domain has 5+ active sparks from trusted sources AND user agrees.
**Do:**

```
exec: node SPARKER/index.js crystallize <domain>
```

If command unavailable, manually create `skills/<domain>/SKILL.md` with core rules, boundary conditions, and learning log. Do NOT auto-crystallize without user consent.

---

## Micro-Probes

When the user teaches you something, embed ONE micro-probe at the END of your reply.
Keep it answerable in 2 seconds. Budget: cold_start=3, active=2, cruise=1.

Load `references/micro-probe-templates.md` for templates.

---

## Retry Queue

Hub operations that fail due to network are auto-queued. Process periodically:

```
exec: node SPARKER/index.js retry
```

Publish states: `candidate` → `pending_remote` → `synced` (or `sync_failed`).

---

## Progressive Reference Loading

Load these files ONLY when needed:

| When | Load |
|------|------|
| First time in a domain | `references/cold-start-protocol.md` |
| User teaches / kindle needed | `references/capture-techniques.md` |
| Need distillation examples | `references/distillation-examples.md` |
| Need contextual query examples | `references/contextual-query-guide.md` |
| Multi-round corrections | `references/iterative-refinement.md` |
| Micro-probe time | `references/micro-probe-templates.md` |
| Digest / review cycle | `references/digest-protocol.md` |
| Publishing to SparkHub | `references/hub-publish-protocol.md` |
| Schema / config questions | `references/stp-schema.md` |
