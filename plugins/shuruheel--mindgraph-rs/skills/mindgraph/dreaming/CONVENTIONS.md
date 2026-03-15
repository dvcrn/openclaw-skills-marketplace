# MindGraph Domain Conventions
> For use by the dreamer and any agent writing to the graph.
> Updated: 2026-02-26 based on cockpit UI audit feedback.

## Status Values (Per Node Type)

### Decisions (Choice Log)
A Decision is a record of a choice made. It doesn't "complete" — it stays in force until superseded.
| Status      | Meaning |
|-------------|---------|
| `open`      | Still being deliberated; options exist, no conclusion yet |
| `made`      | Decision has been made and is in force (steady state) |
| `superseded` | Replaced by another decision (link via SUPERSEDES edge) |
| `reversed`  | Explicitly undone/voided |

**Never use** `completed`, `active`, `locked`, `decided`, or `implemented` for Decisions.
*Normalization:* `completed/locked/decided/implemented/finalized` → `made`; `active/in-progress` → `open`.

### Goals & Projects (Outcome Log)
| Status      | Meaning |
|-------------|---------|
| `active`    | Currently being worked on |
| `on_hold`   | Paused, not abandoned |
| `completed` | Done and closed |
| `archived`  | No longer relevant, kept for history |
| `live`      | Deployed and accessible in production (Projects only) |

## Decision Node Rules
- `description`: required. If missing but `decision_rationale` has content, copy it.
- `decision_rationale`: the "why" — what reasoning led to this decision.
- `decided_at`: the original date of the decision. Often null if imported from text — flag as data gap.
- Note: dates shown in the cockpit default to `updated_at` (import timestamp) when `decided_at` is null. This is a known data gap — not a bug.

## Project Node Rules
- `project_type` (required): distinguishes the project's role in Shan's context:
  | Value       | Meaning | Usage |
  |-------------|---------|-------|
  | `active`    | Currently being worked on together | Show in cockpit, reference in work sessions |
  | `portfolio` | Past/archived work to showcase | Mention in job applications, outreach, LinkedIn |
  | `internal`  | Infrastructure/tooling | Operational context only |

- Live production projects get `status: live` (e.g. Thumos Care, Elys Live).
- Portfolio projects are archived past projects (Pencil News, Just Ads, MatSyn, 32B SRE, MCP Neo4j, UN Diplomatic KG, etc.).
- Don't mark something as `portfolio` if it's actively being developed.

## Goal Node Rules
- `progress`: float 0.0–1.0. Update when meaningful milestones are reached.
- Don't auto-decay progress — only update upward unless explicitly told a goal regressed.
- Two active goals as of Feb 2026:
  - "Improve retrieval of context from MindGraph" — progress ~0.65
  - "Income Generation" — progress ~0.5

## Dreamer Proposal Guidelines
- **schema_fix** for missing required props — always flag `project_type` missing on Projects.
- **data_enrichment** for non-destructive enrichments like copying rationale → description.
- **data_gap** for genuinely lost information (no decided_at, no rationale).
- **dedup** to tombstone duplicate nodes with identical labels (proactively check before writing).
- **task_suggestion** to propose up to 3 concrete next steps based on recent momentum.
- Do NOT flag `description` as missing on a Decision if `decision_rationale` is populated — propose copying it instead.
- Do NOT generate separate analyzer group columns in the cockpit UI — proposals should flow as a flat list.

## Extraction Rules
Full node-by-node mapping and extraction grammar: **`GRAPH_EXTRACTION.md`** in workspace root.

## Confidence Distribution Display
When visualizing claim confidence, use 5 buckets for granularity:
- 0–30%: red (very low)
- 30–50%: orange
- 50–70%: yellow
- 70–90%: light green
- 90–100%: green (high confidence)

## Entity Resolution
- `implemented` = completed in a technical sense — normalize to `completed` (Goal/Project) or `made` (Decision).
- `in-progress` → normalize to `active` (Goal/Project) or `open` (Decision).
