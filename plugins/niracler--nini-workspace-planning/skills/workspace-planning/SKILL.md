---
name: workspace-planning
description: "Manage project schedules stored as YAML in the workspace planning/ directory. Use whenever the user asks about project delivery progress, module status, weekly task breakdown (frontend/backend), milestone countdowns, risk analysis, or wants to update module status, link OpenSpec changes, create new schedules, or sync to Yunxiao. Triggers on \"planning\", \"schedule\", \"progress\", \"milestone\", \"what's this week\", \"what's left\", or Chinese equivalents like \"排期\", \"进度\", \"本周任务\", \"里程碑\", \"模块状态\", \"还剩多少\", \"风险\", \"deferred\". Also trigger when user mentions specific module names (e.g. \"auth\", \"zone-control\") in the context of status updates or progress tracking. Do NOT trigger for: calendar/reminder management (use schedule-manager), daily/weekly work reports (use worklog), or general Yunxiao task operations without schedule context (use yunxiao skill)."
---

# Workspace Planning

Workspace-level project schedule management. Operates on `planning/schedules/*.yaml`
files that track modules, milestones, and delivery phases.

Each schedule YAML is organized around **functional modules** (not tasks or tickets),
bridging the gap between Yunxiao work items and OpenSpec code changes.

## Prerequisites

| Dependency | Type | Required | Notes |
|------------|------|----------|-------|
| Schedule YAML | data | Yes | `planning/schedules/<project>.yaml` in workspace root |
| yunxiao skill | skill | For sync only | Must be installed before using `planning sync-yunxiao` |

> Do NOT verify prerequisites on skill load. If a command fails due to a missing
> dependency, guide the user through setup step by step.

## When to Use

- User asks about project progress, timeline, or delivery status
- User wants to check what's planned for a specific week
- User mentions milestones, deadlines, or "how much is left"
- User wants to update a module's status or mark something done
- User wants to connect an OpenSpec change to a schedule module
- User needs to create a new project schedule
- User wants to push schedule data to Yunxiao

## Module Status State Machine

```text
planned --> in_progress --> done (terminal)
   |
   +--> deferred --> planned / in_progress
```

Allowed: `planned -> in_progress`, `in_progress -> done`, `planned -> deferred`,
`deferred -> planned`, `deferred -> in_progress`.

Forbidden: any transition out of `done`.

## Module Types

| Type | Description | Key fields |
|------|-------------|------------|
| `feature` | Has UI frames, frontend/backend coordination | `frames`, `design`, `figma`, `backend`, `frontend`, `priority` |
| `infrastructure` | Backend-only, no UI | `description` |

For the complete YAML schema and field reference, read `references/yaml-schema.md`.

## Commands

### `planning init <project-name>`

Bootstrap a new schedule YAML for a project.

**Steps:**

1. Ask the user for basic project info:
   - Project title (display name)
   - Timeline start and end dates
   - Team capacity (optional)
2. Ask about milestones (at least one required) — for each: id, title, date, type, deliverable
3. Ask about phases (optional) — or suggest a default monthly split based on timeline
4. Create `planning/schedules/<project-name>.yaml` with the provided structure and an empty `modules: []`
5. Suggest next step: "Add modules manually or describe your feature list and I'll help structure them"

### `planning review`

Show overall schedule progress grouped by phase.

**Steps:**

1. Read `planning/schedules/*.yaml` (if multiple files, list them and let user choose)
2. Calculate current week from `today - timeline.start`
3. Display by phase:

```text
## sylsmart schedule (current: W3)

### month-1: Framework (2/6 done, 33%)
  V core-extraction         infrastructure  done
  V auth                    feature 14f     done
  * project-list            feature 12f     in_progress
  o project-overview        feature 10f     planned
  o common-dialogs          feature 18f     planned
  o core-regression         infrastructure  planned
```

Legend: V done, * in_progress, o planned, - deferred

1. After the module list, add a brief **Risks & Bottlenecks** section (2-4 bullets):
   - Highlight modules with `design: partial` or `pending`
   - Flag weeks where backend capacity is overloaded (many ready_week targets in same week)
   - Note any milestone within 14 days with low completion rate
   - Call out frontend modules that depend on not-yet-ready backend APIs

**Flags:**

- `--week <W>` — Show modules relevant to that week. A module is "relevant" if ANY of these apply: (1) `weeks` contains that week, (2) `backend.ready_week` equals that week, (3) `frontend.mock_from` equals that week. Split output into Backend and Frontend sections with dependency status.
- `--milestones` — Show milestone progress with countdown warnings (highlight if <= 14 days away)

### `planning update <module-id> --status <status>`

Update a module's status.

**Steps:**

1. Read YAML, find module by id
2. Validate transition against the state machine
3. If invalid, show error with the allowed target states from current state
4. Update the `status` field in YAML
5. Confirm the change

### `planning link <module-id> --change <change-name>`

Associate an OpenSpec change with a module.

**Steps:**

1. Verify `openspec/changes/<change-name>/` exists
2. Append change name to the module's `changes` list (create list if absent)
3. If module status is `planned`, auto-transition to `in_progress`
4. Confirm the change

### `planning sync-yunxiao`

Push unlinked modules to Yunxiao as work items.

**Prerequisite:** yunxiao skill must be installed and configured.

**Steps:**

1. Read YAML, find modules where `yunxiao_id` is null or missing
2. List modules to be created, wait for user confirmation
3. Use yunxiao skill to create a work item for each module
4. Write returned work item IDs back to `yunxiao_id` field in YAML
5. Report results; modules with existing `yunxiao_id` are skipped

## Common Mistakes

| Error | Cause | Fix |
|-------|-------|-----|
| Module not found | Typo in module id | Run `planning review` to see all ids |
| Invalid status transition | State machine violation | Check allowed transitions above |
| Change not found | Name mismatch | Verify change exists in `openspec/changes/` |
| No schedule files | Missing YAML | Run `planning init` to create one |
| Yunxiao sync fails | yunxiao skill not installed | Install yunxiao skill first |
