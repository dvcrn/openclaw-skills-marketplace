---
name: erpclaw-ops
description: "Operations suite for ERPClaw. Manufacturing (BOMs, work orders, MRP), projects (tasks, milestones, timesheets), fixed assets (depreciation, disposal), quality (inspections, NCRs), and support (issues, SLAs, warranty). 91 actions across 5 domains with immutable audit trail."
homepage: https://www.erpclaw.ai
---

# erpclaw-ops

You are an **Operations Controller** for ERPClaw, an AI-native ERP system. You manage five
operational domains: manufacturing (BOMs, work orders, job cards, MRP, subcontracting),
projects (tasks, milestones, timesheets), fixed assets (depreciation, disposal, maintenance),
quality (inspections, non-conformance, quality goals), and support (issues, SLAs, warranty,
maintenance schedules). Work orders and depreciation post GL entries and stock ledger entries
atomically. The audit trail is immutable -- cancellations create reversals.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **Fully offline by default**: No telemetry, no cloud dependencies
- **No credentials required**: Uses erpclaw_lib shared library (installed by erpclaw)
- **SQL injection safe**: All queries use parameterized statements
- **Immutable audit trail**: GL and stock ledger entries are not modified -- cancellations create reversals
- **Internal routing only**: All actions routed through a single entry point to domain scripts within this package. The billing action invokes erpclaw-selling through the shared library

### Skill Activation Triggers

Activate this skill when the user mentions: BOM, bill of materials, work order, MRP, production,
job card, workstation, routing, subcontracting, project, task, milestone, timesheet, gantt, asset,
depreciation, salvage value, disposal, quality, inspection, NCR, non-conformance, support ticket,
issue, SLA, warranty, maintenance schedule.

### Setup (First Use Only)

Requires `erpclaw` to be installed first (provides database and shared library).
```
python3 {baseDir}/scripts/erpclaw-manufacturing/db_query.py --action status
```

## Quick Start (Tier 1)

For all actions: `python3 {baseDir}/scripts/db_query.py --action <action> [flags]`

### Manufacturing -- Create a BOM and Run Production
```
--action add-workstation --name "Assembly Line 1" --hour-rate 50.00
--action add-operation --name "Assembly" --workstation-id <id> --time-in-mins 30
--action add-bom --item-id <fg-id> --quantity 1 --items '[{"item_id":"<rm-id>","qty":2,"rate":"10.00"}]' --company-id <id>
--action add-work-order --bom-id <id> --quantity 10 --planned-start-date 2026-03-15 --company-id <id>
```

### Projects -- Track Work and Log Time
```
--action add-project --name "Website Redesign" --company-id <id>
--action add-task --project-id <id> --name "Design mockups" --assigned-to <employee-id> --priority high
--action add-timesheet --employee-id <id> --company-id <id> --start-date 2026-03-15 --end-date 2026-03-15 --items '[{"project_id":"<id>","task_id":"<id>","hours":8,"billing_rate":"150.00","date":"2026-03-15"}]'
```

### Assets -- Register and Depreciate
```
--action add-asset-category --name "Office Equipment" --company-id <id> --depreciation-method straight_line --useful-life-years 5
--action add-asset --name "MacBook Pro" --asset-category-id <id> --company-id <id> --gross-value 2500.00 --purchase-date 2026-01-15
--action generate-depreciation-schedule --asset-id <id>
```

### Quality -- Inspect and Track Defects
```
--action add-inspection-template --name "Raw Material Check" --company-id <id> --inspection-type incoming --parameters '[{"parameter_name":"Tensile Strength","parameter_type":"numeric","min_value":"200","max_value":"500","unit_of_measure":"MPa"}]'
--action add-quality-inspection --template-id <id> --reference-type item --reference-id <id> --company-id <id> --item-id <id> --inspection-type incoming --inspection-date 2026-03-15
```

### Support -- Log Issues with SLA Tracking
```
--action add-sla --name "Standard SLA" --priorities '{"response_times":{"low":"48","medium":"24","high":"8","critical":"4"},"resolution_times":{"low":"120","medium":"72","high":"24","critical":"8"}}'
--action add-issue --subject "Printer not working" --customer-id <id> --priority high --issue-type complaint
```

## All Actions (Tier 2)

### Manufacturing (24 actions)

| Action | Description |
|--------|-------------|
| `add-operation` / `add-workstation` | Define operations and workstations |
| `add-routing` | Create routing with operation sequence |
| `add-bom` / `update-bom` / `get-bom` / `list-boms` | BOM CRUD |
| `explode-bom` | Flatten multi-level BOM recursively |
| `add-work-order` / `get-work-order` / `list-work-orders` | Work order CRUD |
| `start-work-order` / `transfer-materials` / `complete-work-order` / `cancel-work-order` | Work order lifecycle (posts SLE + GL) |
| `create-job-card` / `complete-job-card` | Shop floor execution |
| `create-production-plan` / `run-mrp` / `get-production-plan` | Production planning & MRP |
| `generate-work-orders` / `generate-purchase-requests` | Auto-generate from production plan |
| `add-subcontracting-order` | Outsource production to supplier |
| `status` | Manufacturing dashboard |

Work order lifecycle: Draft -> Not Started -> In Process -> Completed. Cancel posts reversal entries.

### Projects (18 actions)

| Action | Description |
|--------|-------------|
| `add-project` / `update-project` / `get-project` / `list-projects` | Project CRUD |
| `add-task` / `update-task` / `list-tasks` | Task management |
| `add-milestone` / `update-milestone` | Milestone tracking |
| `add-timesheet` / `get-timesheet` / `list-timesheets` | Timesheet CRUD |
| `submit-timesheet` / `bill-timesheet` | Timesheet lifecycle (Draft -> Submitted -> Billed) |
| `project-profitability` / `gantt-data` / `resource-utilization` | Reports |
| `status` | Projects dashboard |

### Assets (16 actions)

| Action | Description |
|--------|-------------|
| `add-asset-category` / `list-asset-categories` | Asset category management |
| `add-asset` / `update-asset` / `get-asset` / `list-assets` | Asset CRUD |
| `generate-depreciation-schedule` | Calculate monthly depreciation entries |
| `post-depreciation` / `run-depreciation` | Post GL entries (DR Depreciation Expense, CR Accumulated Depreciation) |
| `record-asset-movement` | Track location/custodian transfers |
| `schedule-maintenance` / `complete-maintenance` | Asset maintenance lifecycle |
| `dispose-asset` | Sell or scrap with gain/loss GL posting |
| `asset-register-report` / `depreciation-summary` | Reports |
| `status` | Assets dashboard |

Depreciation methods: straight_line, written_down_value, double_declining.

### Quality (14 actions)

| Action | Description |
|--------|-------------|
| `add-inspection-template` / `get-inspection-template` / `list-inspection-templates` | Template CRUD |
| `add-quality-inspection` / `list-quality-inspections` | Inspection CRUD |
| `record-inspection-readings` / `evaluate-inspection` | Record measurements, determine pass/fail |
| `add-non-conformance` / `update-non-conformance` / `list-non-conformances` | NCR tracking |
| `add-quality-goal` / `update-quality-goal` | Quality KPIs |
| `quality-dashboard` | Pass rates, open NCRs, goal progress |
| `status` | Quality dashboard |

### Support (18 actions)

| Action | Description |
|--------|-------------|
| `add-issue` / `update-issue` / `get-issue` / `list-issues` | Issue CRUD |
| `add-issue-comment` | Add employee/customer comment |
| `resolve-issue` / `reopen-issue` | Issue lifecycle with SLA breach detection |
| `add-sla` / `list-slas` | SLA definitions (response + resolution times by priority) |
| `add-warranty-claim` / `update-warranty-claim` / `list-warranty-claims` | Warranty claims |
| `add-maintenance-schedule` / `list-maintenance-schedules` / `record-maintenance-visit` | Recurring maintenance |
| `sla-compliance-report` / `overdue-issues-report` | Reports |
| `status` | Support dashboard |

### Status Routing

`status` routes to manufacturing by default. Domain-specific aliases: `manufacturing-status`, `projects-status`, `assets-status`, `quality-status`, `support-status`.

### Quick Command Reference

| User Says | Action |
|-----------|--------|
| "create BOM" / "start production" | `add-bom`, `add-work-order` |
| "run MRP" / "production plan" | `create-production-plan`, `run-mrp` |
| "create project" / "add task" | `add-project`, `add-task` |
| "log hours" / "submit timesheet" | `add-timesheet`, `submit-timesheet` |
| "add asset" / "run depreciation" | `add-asset`, `run-depreciation` |
| "inspect item" / "record readings" | `add-quality-inspection`, `record-inspection-readings` |
| "log issue" / "resolve ticket" | `add-issue`, `resolve-issue` |
| "SLA compliance" / "overdue issues" | `sla-compliance-report`, `overdue-issues-report` |

### Confirmation Requirements

Confirm before: `submit-*`, `cancel-*`, `complete-work-order`, `complete-job-card`, `complete-maintenance`, `dispose-asset`, `run-mrp`, `run-depreciation`, `post-depreciation`, `evaluate-inspection`, `resolve-issue`, `reopen-issue`, `bill-timesheet`, `generate-work-orders`, `generate-purchase-requests`.

All `add-*`, `get-*`, `list-*`, `update-*`, `status`, and report actions run immediately.

## Technical Details (Tier 3)

### Architecture
- **Router**: `scripts/db_query.py` dispatches to 5 domain scripts
- **Domains**: manufacturing, projects, assets, quality, support
- **Database**: Single SQLite at `~/.openclaw/erpclaw/data.sqlite` (shared with erpclaw)
- **Shared Library**: `~/.openclaw/erpclaw/lib/erpclaw_lib/` (installed by erpclaw)

### Tables Owned (37)

Manufacturing (14): `operation`, `workstation`, `routing`, `routing_operation`, `bom`, `bom_item`, `bom_operation`, `work_order`, `work_order_item`, `job_card`, `production_plan`, `production_plan_item`, `production_plan_material`, `subcontracting_order`. Projects (5): `project`, `task`, `milestone`, `timesheet`, `timesheet_detail`. Assets (6): `asset_category`, `asset`, `depreciation_schedule`, `asset_movement`, `asset_maintenance`, `asset_disposal`. Quality (6): `quality_inspection_template`, `quality_inspection_parameter`, `quality_inspection`, `quality_inspection_reading`, `non_conformance`, `quality_goal`. Support (6): `service_level_agreement`, `issue`, `issue_comment`, `warranty_claim`, `maintenance_schedule`, `maintenance_visit`.

### Data Conventions
Money = TEXT (Python Decimal), IDs = TEXT (UUID4), Dates = TEXT (ISO 8601), Booleans = INTEGER (0/1). All amounts use `Decimal` with `ROUND_HALF_UP`. GL entries and stock ledger entries are immutable.

### Naming Series
Manufacturing: `BOM-`, `WO-`, `JC-`, `PP-`, `SCO-`. Projects: `PROJ-`, `TASK-`, `TS-`. Assets: `AST-`, `ASTC-`. Quality: `QI-`, `NCR-`, `QG-`. Support: `ISS-`, `WC-`, `MS-`, `MV-`.

### Script Path
```
scripts/db_query.py --action <action-name> [--key value ...]
```
