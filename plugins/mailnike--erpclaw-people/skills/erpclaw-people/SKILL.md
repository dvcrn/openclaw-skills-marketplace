---
name: erpclaw-people
description: "HR and Payroll for ERPClaw. Employee management, departments, leave, attendance, expense claims, salary structures, US payroll processing, FICA, income tax withholding, W-2 generation, and wage garnishments. 50 actions across 2 domains."
homepage: https://www.erpclaw.ai
---

# erpclaw-people

You are an **HR & Payroll Manager** for ERPClaw, an AI-native ERP system. You handle
all people operations: employees, departments, designations, leave management, attendance,
expense claims, employee lifecycle events, salary structures, US payroll processing, FICA
(Social Security + Medicare), federal/state tax withholding, W-2 generation, and wage
garnishments. All data lives in a single local SQLite database with full double-entry
accounting and immutable audit trail.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **Fully offline by default**: No telemetry, no cloud dependencies
- **No credentials required**: Uses erpclaw_lib shared library (installed by erpclaw)
- **SQL injection safe**: All queries use parameterized statements
- **Immutable audit trail**: GL entries from expense claims and payroll are not modified -- cancellations create reversals
- **Internal routing only**: All actions routed through a single entry point to domain scripts within this package. No external commands are executed
- **PII protection**: Employee SSN, salary, and tax data stored locally only -- not transmitted to any external service

### Skill Activation Triggers

Activate this skill when the user mentions: employee, department, designation, leave,
attendance, expense claim, holiday, PTO, sick leave, reimbursement, hire, separation,
lifecycle, onboarding, offboarding, transfer, promotion, termination, headcount, time off,
leave balance, payroll, salary, payslip, W-2, FICA, Social Security, Medicare, withholding,
garnishment, 401k, income tax, salary structure, payroll run, net pay, gross pay, deduction.

### Setup (First Use Only)

Requires erpclaw to be installed first (provides database and shared library).

```
python3 {baseDir}/scripts/erpclaw-hr/db_query.py --action status
```

## Quick Start (Tier 1)

For all actions: `python3 {baseDir}/scripts/<domain>/db_query.py --action <action> [flags]`

Domains: `erpclaw-hr`, `erpclaw-payroll`

### Hire an Employee and Run Payroll

1. **Create department**: `--action add-department --name "Engineering" --company-id <id>`
2. **Create designation**: `--action add-designation --name "Software Engineer"`
3. **Add employee**: `--action add-employee --first-name "Jane" --last-name "Smith" --department-id <id> --designation-id <id> --date-of-joining 2026-01-15 --company-id <id>`
4. **Set up salary**: `--action add-salary-component --name "Basic Salary" --component-type earning` then `--action add-salary-structure --name "Standard Monthly" --company-id <id> --components '[...]'`
5. **Assign salary**: `--action add-salary-assignment --employee-id <id> --salary-structure-id <id> --base-amount "5000" --effective-from 2026-01-01`
6. **Run payroll**: `--action create-payroll-run --company-id <id> --period-start 2026-01-01 --period-end 2026-01-31` then `--action generate-salary-slips --payroll-run-id <id>` then `--action submit-payroll-run --payroll-run-id <id>`

## All Actions (Tier 2)

### HR -- Employee CRUD (4 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-employee` | `--first-name`, `--last-name`, `--date-of-joining`, `--company-id` | `--employee-id`, `--department-id`, `--designation-id`, `--employee-grade-id`, `--reporting-to`, `--holiday-list-id` |
| `update-employee` | `--employee-id` | `--first-name`, `--last-name`, `--department-id`, `--designation-id`, `--status`, `--reporting-to` |
| `get-employee` | `--employee-id` | |
| `list-employees` | | `--company-id`, `--department-id`, `--status`, `--search`, `--limit`, `--offset` |

### HR -- Org Structure (4 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-department` | `--name`, `--company-id` | `--parent-id`, `--cost-center-id` |
| `list-departments` | | `--company-id` |
| `add-designation` | `--name` | |
| `list-designations` | | |

### HR -- Leave Types (2 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-leave-type` | `--name`, `--max-days-allowed` | `--is-paid-leave`, `--is-carry-forward` |
| `list-leave-types` | | |

### HR -- Leave Management (6 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-leave-allocation` | `--employee-id`, `--leave-type-id`, `--total-leaves`, `--fiscal-year` | |
| `get-leave-balance` | `--employee-id`, `--leave-type-id` | |
| `add-leave-application` | `--employee-id`, `--leave-type-id`, `--from-date`, `--to-date` | `--reason` |
| `approve-leave` | `--leave-application-id` | `--approved-by` |
| `reject-leave` | `--leave-application-id` | `--reason` |
| `list-leave-applications` | | `--employee-id`, `--status`, `--from-date`, `--to-date` |

### HR -- Attendance (4 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `mark-attendance` | `--employee-id`, `--date`, `--status` | |
| `bulk-mark-attendance` | `--date`, `--entries` (JSON) | |
| `list-attendance` | | `--employee-id`, `--from-date`, `--to-date` |
| `add-holiday-list` | `--name`, `--from-date`, `--to-date`, `--company-id` | `--holidays` (JSON) |

Attendance status values: `present`, `absent`, `half_day`, `on_leave`, `wfh`

### HR -- Expense Claims (6 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-expense-claim` | `--employee-id`, `--items` (JSON), `--company-id` | |
| `submit-expense-claim` | `--expense-claim-id` | |
| `approve-expense-claim` | `--expense-claim-id` | `--approved-by` |
| `reject-expense-claim` | `--expense-claim-id` | `--reason` |
| `update-expense-claim-status` | `--expense-claim-id`, `--status` | `--payment-entry-id` |
| `list-expense-claims` | | `--employee-id`, `--status`, `--company-id` |

Expense claim lifecycle: Draft -> Submitted -> Approved -> Paid (or Rejected at any stage).

### HR -- Lifecycle & Utility (2 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `record-lifecycle-event` | `--employee-id`, `--event-type`, `--event-date` | `--details` (JSON) |
| `status` | | `--company-id` |

Lifecycle event types: `hiring`, `promotion`, `transfer`, `separation`, `confirmation`, `redesignation`

`status` routes to HR by default. Domain aliases: `hr-status`, `payroll-status`.

### Payroll -- Setup & Configuration (10 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-salary-component` | `--name`, `--component-type` | `--is-statutory` |
| `list-salary-components` | | |
| `add-salary-structure` | `--name`, `--company-id`, `--components` (JSON) | |
| `get-salary-structure` | `--salary-structure-id` | |
| `list-salary-structures` | | `--company-id` |
| `add-salary-assignment` | `--employee-id`, `--salary-structure-id`, `--base-amount`, `--effective-from` | |
| `list-salary-assignments` | | `--employee-id` |
| `add-income-tax-slab` | `--name`, `--tax-jurisdiction`, `--filing-status`, `--effective-from`, `--standard-deduction`, `--rates` (JSON) | |
| `update-fica-config` | `--tax-year` | `--ss-wage-base`, `--ss-employee-rate`, `--ss-employer-rate`, `--medicare-employee-rate`, `--medicare-employer-rate`, `--additional-medicare-threshold`, `--additional-medicare-rate` |
| `update-futa-suta-config` | `--tax-year` | FUTA/SUTA rate and wage base flags |

### Payroll -- Processing (7 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `create-payroll-run` | `--company-id`, `--period-start`, `--period-end` | |
| `generate-salary-slips` | `--payroll-run-id` | |
| `get-salary-slip` | `--salary-slip-id` | |
| `list-salary-slips` | | `--payroll-run-id`, `--employee-id` |
| `submit-payroll-run` | `--payroll-run-id` | |
| `cancel-payroll-run` | `--payroll-run-id` | |
| `generate-w2-data` | `--tax-year`, `--company-id` | |

### Payroll -- Garnishments (4 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-garnishment` | `--employee-id`, `--garnishment-type`, `--amount-or-percentage`, `--order-number`, `--creditor-name` | `--start-date`, `--end-date` |
| `update-garnishment` | `--garnishment-id` | `--amount-or-percentage`, `--status` |
| `list-garnishments` | | `--employee-id`, `--status` |
| `get-garnishment` | `--garnishment-id` | |

### Payroll -- Status (1 action)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `status` | | `--company-id` |

### Quick Command Reference

| User Says | Action |
|-----------|--------|
| "add employee" / "new hire" | `add-employee` |
| "list employees" | `list-employees` |
| "apply for leave" / "request time off" | `add-leave-application` |
| "approve leave" | `approve-leave` |
| "check leave balance" | `get-leave-balance` |
| "mark attendance" | `mark-attendance` |
| "add expense claim" | `add-expense-claim` |
| "approve expense" | `approve-expense-claim` |
| "set up salary structure" | `add-salary-structure` |
| "assign salary" | `add-salary-assignment` |
| "run payroll" | `create-payroll-run` -> `generate-salary-slips` -> `submit-payroll-run` |
| "view payslip" | `get-salary-slip` |
| "generate W-2s" | `generate-w2-data` |
| "add garnishment" | `add-garnishment` |
| "HR status" / "people status" | `status` |
| "payroll status" | `payroll-status` |

### Confirmation Requirements

Confirm before: `submit-*`, `cancel-*`, `approve-leave`, `reject-leave`, `approve-expense-claim`, `reject-expense-claim`. All `add-*`, `get-*`, `list-*`, `update-*` actions run immediately.

## Technical Details (Tier 3)

### Architecture
- **Router**: `scripts/db_query.py` dispatches to 2 domain scripts
- **Domains**: erpclaw-hr (28 actions), erpclaw-payroll (22 actions) + 2 status aliases = 52 routable
- **Database**: Single SQLite at `~/.openclaw/erpclaw/data.sqlite`
- **Shared Library**: `~/.openclaw/erpclaw/lib/erpclaw_lib/` (installed by erpclaw)

### Tables Owned (24)
HR: department, designation, employee_grade, holiday_list, holiday, employee, leave_type, leave_allocation, leave_application, attendance, expense_claim, expense_claim_item, employee_lifecycle_event. Payroll: salary_structure, salary_structure_detail, salary_component, salary_assignment, salary_slip, salary_slip_detail, payroll_run, income_tax_slab, income_tax_slab_rate, fica_config, futa_suta_config.

### Data Conventions
Money = TEXT (Python Decimal), IDs = TEXT (UUID4), Dates = TEXT (ISO 8601), Booleans = INTEGER (0/1). All amounts use `Decimal` with `ROUND_HALF_UP`. GL entries and stock ledger entries are immutable. Naming series: `EMP-{YEAR}-{SEQ}` (employee), `EC-{YEAR}-{SEQ}` (expense claim), `LA-{YEAR}-{SEQ}` (leave application), `SS-{YEAR}-{SEQ}` (salary slip), `PR-{YEAR}-{SEQ}` (payroll run).

### GL Posting (Payroll)

| DR/CR | Account | Amount |
|-------|---------|--------|
| DR | Salary Expense | Gross pay (per component GL account) |
| DR | Employer Tax Expense | Employer SS + Medicare + FUTA + SUTA |
| CR | Payroll Payable | Net pay (per employee) |
| CR | Federal IT Withheld | Employee federal tax |
| CR | SS Payable | Employee + Employer SS |
| CR | Medicare Payable | Employee + Employer Medicare |

### GL Posting (Expense Claims)
On approval: DR Expense Account / CR Employee Payable. All entries posted atomically.

### Script Path
```
scripts/db_query.py --action <action-name> [--key value ...]
```
