# [PROJECT]: Autonomous Multi-Agent Workflow

> Based on the [AAHP Protocol](https://github.com/homeofe/AAHP).
> No manual triggers. Agents read `handoff/DASHBOARD.md` and work autonomously.

---

## Agent Roles

| Agent | Model | Role | Responsibility |
|-------|-------|------|---------------|
| 🔭 Researcher | e.g. perplexity/sonar-pro | Researcher | OSS research, compliance checks, doc review |
| 🏛️ Architect | e.g. claude-opus | Architect | System design, ADRs, interface definitions |
| ⚙️ Implementer | e.g. claude-sonnet | Implementer | Code, tests, refactoring, commits |
| 💬 Reviewer | e.g. gpt-4 / second model | Reviewer | Second opinion, edge cases, security review |

> Adapt roles and models to your team's tooling.

---

## The Pipeline

### Phase 1: Research & Context

```
Reads:   handoff/NEXT_ACTIONS.md or DASHBOARD.md (top unblocked task)
         handoff/STATUS.md (current project state)

Does:    Researches relevant OSS libraries / APIs / compliance requirements
         Checks whether similar solutions already exist in the project
         Clarifies ambiguities in the task

Writes:  handoff/LOG.md -research findings + sources + recommendation
```

### Phase 2: Architecture Decision

```
Reads:   Research output from LOG.md
         handoff/STATUS.md
         Relevant source files, config, docs

Does:    Decides architecture and interface design
         Chooses branch name
         Defines exactly what the Implementer should build

Writes:  handoff/LOG.md -ADR (Architecture Decision Record)

ADR format:
  ## [DATE] ADR: [Feature Name]
  **Decision:** ...
  **Rationale:** ...
  **Consequences:** ...
  **Branch:** feat/...
  **Instructions for Implementer:** [numbered steps]
```

### Phase 3: Implementation

```
Reads:   ADR from LOG.md
         CONTRIBUTING.md / CONVENTIONS.md (MANDATORY before first commit)

Does:    Creates feature branch: git checkout -b feat/<scope>-<name>
         Writes code + unit tests
         Runs tests and type-check
         Commits and pushes branch

Branch convention:
  feat/<scope>-<short-name>    → new feature
  fix/<scope>-<short-name>     → bug fix
  docs/<scope>-<name>          → documentation only

Commit format:
  feat(scope): description [AAHP-auto]
  fix(scope): description [AAHP-fix]
```

### Phase 4: Discussion Round

```
All agents review the completed code on the feature branch.

Architect  → "Does the implementation match the ADR?"
Reviewer   → "What could be more robust, simpler, or more secure?"
Researcher → "Were all task items fulfilled? Any compliance concerns?"

Outcome:
  - Minor fixes → Implementer fixes in the same branch
  - Larger issues → New tasks added to NEXT_ACTIONS.md / DASHBOARD.md
  - Everything documented in LOG.md
```

### Phase 5: Completion & Handoff

```
DASHBOARD.md:    Update build status, test counts, pipeline state
STATUS.md:       Update changed system state (Verified / Assumed / Unknown)
LOG.md:          Append session summary
NEXT_ACTIONS.md: Check off completed task, add newly discovered tasks

Git:     Branch pushed, PR-ready
Notify:  Project owner -only on fully completed tasks, not phase transitions
         Format: "✅ [Feature] done -Branch: feat/... -Tests: X/X"
```

---

## Autonomy Boundaries

| Allowed ✅ | Not allowed ❌ |
|-----------|--------------|
| Write & commit code | Push directly to `main` |
| Write & run tests | Install new dependencies without documenting |
| Push feature branches | Write secrets or PII into source |
| Research & propose OSS libraries | Call external APIs without credentials |
| Make architecture decisions | Perform production deployments |
| Break tests (when fixing identified bugs) | Delete tests without replacement |

---

## Task Selection Rules

1. Read `DASHBOARD.md`, take the top task where `Ready? = ✅`
2. If a task is **blocked** → skip it, take the next unblocked one
3. If **all tasks are blocked** → notify the project owner, pause
4. Never start a task without reading `STATUS.md` first
5. After completing a task → always update `DASHBOARD.md` before stopping

---

## Error Handling

If an agent fails or is uncertain:
- Mark task as `(Unknown)` in `STATUS.md`
- Document the specific blocker in `LOG.md`
- Notify the project owner
- **Never proceed on assumptions when certainty is missing**

---

## Open Source First

Before any custom implementation:
1. Researcher searches for existing OSS solutions
2. Architect evaluates: build vs. OSS vs. fork
3. Decision is documented in the ADR
4. Custom builds must be: clean abstraction, testable, documented

---

*This document lives in the repo and is continuously refined by the agents themselves.*
