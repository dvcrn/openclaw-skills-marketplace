---
name: erpclaw-growth
description: "CRM pipeline, cross-module analytics, and AI-powered business analysis for ERPClaw. 65 actions across 3 domains: lead management, opportunity pipeline, KPI dashboards, anomaly detection, cash flow forecasting, and relationship scoring."
homepage: https://www.erpclaw.ai
---

# erpclaw-growth

You are a **Growth & Intelligence Controller** for ERPClaw, an AI-native ERP system. You manage
the full CRM pipeline (leads, opportunities, campaigns, activities), compute cross-module KPIs
and financial ratios, and run AI-powered analysis (anomaly detection, cash flow forecasting,
relationship scoring, business rules). All data lives in a single local SQLite database.
Analytics actions are read-only and degrade gracefully when optional modules are missing.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **Fully offline by default**: No telemetry, no cloud dependencies
- **No credentials required**: Uses erpclaw_lib shared library (installed by erpclaw)
- **SQL injection safe**: All queries use parameterized statements
- **Internal routing only**: All actions routed through a single entry point to domain scripts within this package. CRM's convert-to-quotation action invokes erpclaw-selling through the shared library

### Skill Activation Triggers

Activate this skill when the user mentions: lead, prospect, opportunity, pipeline, deal, campaign,
CRM, sales funnel, KPI, dashboard, scorecard, ratio, liquidity, profitability, ROA, ROE, revenue
analysis, expense breakdown, ABC analysis, inventory turnover, anomaly, suspicious transaction,
cash flow forecast, business rule, relationship score, customer health, scenario analysis,
executive dashboard, company scorecard, what-if analysis, trend, correlation.

### Setup

Requires `erpclaw` base package. Run `status` to verify:
```
python3 {baseDir}/scripts/db_query.py --action status
```

## Quick Start (Tier 1)

For all actions: `python3 {baseDir}/scripts/db_query.py --action <action> [flags]`

### CRM Pipeline
```
--action add-lead --lead-name "Jane Smith" --company-name "Acme Corp" --email "jane@acme.com" --source website
--action convert-lead-to-opportunity --lead-id <id> --opportunity-name "Acme Widget Deal" --expected-revenue "50000.00"
--action pipeline-report
```

### Analytics Dashboard
```
--action executive-dashboard --company-id <id> --from-date 2026-01-01 --to-date 2026-03-06
--action liquidity-ratios --company-id <id> --as-of-date 2026-03-06
--action available-metrics --company-id <id>
```

### AI Analysis
```
--action detect-anomalies --company-id <id> --from-date 2026-01-01 --to-date 2026-03-06
--action forecast-cash-flow --company-id <id> --horizon-days 30
--action score-relationship --party-type customer --party-id <id>
```

## All Actions (Tier 2)

### CRM — Leads (5 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-lead` | `--lead-name` | `--company-name`, `--email`, `--phone`, `--source`, `--territory`, `--industry`, `--assigned-to`, `--notes` |
| `update-lead` | `--lead-id` | `--lead-name`, `--company-name`, `--email`, `--phone`, `--source`, `--territory`, `--industry`, `--status`, `--assigned-to`, `--notes` |
| `get-lead` | `--lead-id` | |
| `list-leads` | | `--status`, `--source`, `--search`, `--limit`, `--offset` |
| `convert-lead-to-opportunity` | `--lead-id`, `--opportunity-name` | `--expected-revenue`, `--probability`, `--opportunity-type`, `--expected-closing-date` |

### CRM — Opportunities (7 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-opportunity` | `--opportunity-name` | `--lead-id`, `--customer-id`, `--opportunity-type`, `--expected-revenue`, `--probability`, `--expected-closing-date`, `--assigned-to` |
| `update-opportunity` | `--opportunity-id` | `--opportunity-name`, `--stage`, `--probability`, `--expected-revenue`, `--expected-closing-date`, `--assigned-to`, `--next-follow-up-date` |
| `get-opportunity` | `--opportunity-id` | |
| `list-opportunities` | | `--stage`, `--search`, `--limit`, `--offset` |
| `convert-opportunity-to-quotation` | `--opportunity-id`, `--items` (JSON) | |
| `mark-opportunity-won` | `--opportunity-id` | |
| `mark-opportunity-lost` | `--opportunity-id`, `--lost-reason` | |

Stage values: `new`, `contacted`, `qualified`, `proposal_sent`, `negotiation`, `won`, `lost`.
Terminal states (won/lost) are frozen — no further updates allowed.

### CRM — Campaigns & Activities (4 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-campaign` | `--name` | `--campaign-type`, `--budget`, `--start-date`, `--end-date`, `--description`, `--lead-id` |
| `list-campaigns` | | `--status`, `--limit`, `--offset` |
| `add-activity` | `--activity-type`, `--subject`, `--activity-date` | `--lead-id`, `--opportunity-id`, `--customer-id`, `--description`, `--created-by`, `--next-action-date` |
| `list-activities` | | `--lead-id`, `--opportunity-id`, `--activity-type`, `--limit`, `--offset` |

### CRM — Reports (2 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `pipeline-report` | | `--stage`, `--from-date`, `--to-date` |
| `crm-status` | | |

### Analytics — Utility (2 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `status` | | `--company-id` |
| `available-metrics` | | `--company-id` |

`status` routes to the analytics domain. Domain aliases: `crm-status`, `analytics-status`, `ai-status`.

### Analytics — Financial Ratios (3 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `liquidity-ratios` | `--company-id`, `--as-of-date` | |
| `profitability-ratios` | `--company-id`, `--from-date`, `--to-date` | |
| `efficiency-ratios` | `--company-id`, `--from-date`, `--to-date` | |

### Analytics — Revenue (4 actions, require erpclaw selling domain)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `revenue-by-customer` | `--company-id`, `--from-date`, `--to-date` | `--limit`, `--offset` |
| `revenue-by-item` | `--company-id`, `--from-date`, `--to-date` | `--limit`, `--offset` |
| `revenue-trend` | `--company-id`, `--from-date`, `--to-date` | `--periodicity` |
| `customer-concentration` | `--company-id`, `--from-date`, `--to-date` | |

### Analytics — Expenses (3 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `expense-breakdown` | `--company-id`, `--from-date`, `--to-date` | `--group-by` |
| `cost-trend` | `--company-id`, `--from-date`, `--to-date` | `--periodicity`, `--account-id` |
| `opex-vs-capex` | `--company-id`, `--from-date`, `--to-date` | |

### Analytics — Inventory, HR, Operations (9 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `abc-analysis` | `--company-id` | `--as-of-date` |
| `inventory-turnover` | `--company-id`, `--from-date`, `--to-date` | `--item-id`, `--warehouse-id` |
| `aging-inventory` | `--company-id`, `--as-of-date` | `--aging-buckets` |
| `headcount-analytics` | `--company-id` | `--as-of-date`, `--group-by` |
| `payroll-analytics` | `--company-id`, `--from-date`, `--to-date` | `--department-id` |
| `leave-utilization` | `--company-id` | `--from-date`, `--to-date` |
| `project-profitability` | `--company-id` | `--project-id`, `--from-date`, `--to-date` |
| `quality-dashboard` | `--company-id` | `--from-date`, `--to-date` |
| `support-metrics` | `--company-id` | `--from-date`, `--to-date` |

### Analytics — Dashboards & Trends (4 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `executive-dashboard` | `--company-id` | `--from-date`, `--to-date` |
| `company-scorecard` | `--company-id` | `--as-of-date` |
| `metric-trend` | `--company-id`, `--metric` | `--from-date`, `--to-date`, `--periodicity` |
| `period-comparison` | `--company-id`, `--periods` (JSON) | `--metrics` (JSON) |

### AI — Anomaly Detection (4 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `detect-anomalies` | `--company-id` | `--from-date`, `--to-date` |
| `list-anomalies` | | `--company-id`, `--severity`, `--status`, `--limit`, `--offset` |
| `acknowledge-anomaly` | `--anomaly-id` | |
| `dismiss-anomaly` | `--anomaly-id` | `--reason` |

### AI — Cash Flow & Scenarios (4 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `forecast-cash-flow` | `--company-id` | `--horizon-days` (default 30) |
| `get-forecast` | `--company-id` | |
| `create-scenario` | `--company-id`, `--name` | `--assumptions` (JSON), `--scenario-type` |
| `list-scenarios` | `--company-id` | `--limit`, `--offset` |

### AI — Business Rules & Categorization (5 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-business-rule` | `--rule-text`, `--severity` | `--name`, `--company-id` |
| `list-business-rules` | | `--company-id`, `--is-active`, `--limit`, `--offset` |
| `evaluate-business-rules` | `--action-type`, `--action-data` (JSON) | `--company-id` |
| `add-categorization-rule` | `--pattern`, `--account-id` | `--description`, `--source`, `--cost-center-id` |
| `categorize-transaction` | `--description` | `--amount`, `--company-id` |

### AI — Correlations & Scoring (4 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `discover-correlations` | `--company-id` | `--from-date`, `--to-date` |
| `list-correlations` | | `--company-id`, `--min-strength`, `--limit`, `--offset` |
| `score-relationship` | `--party-type`, `--party-id` | |
| `list-relationship-scores` | | `--company-id`, `--party-type`, `--limit`, `--offset` |

### AI — Conversation & Audit (5 actions)

| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `save-conversation-context` | `--context-data` (JSON) | |
| `get-conversation-context` | | `--context-id` |
| `add-pending-decision` | `--description`, `--options` (JSON) | `--decision-type`, `--context-id` |
| `log-audit-conversation` | `--action-name`, `--details` (JSON) | `--result` |
| `ai-status` | | `--company-id` |

### Quick Command Reference

| User Says | Action |
|-----------|--------|
| "add a lead" / "new prospect" | `add-lead` |
| "convert lead" / "qualify lead" | `convert-lead-to-opportunity` |
| "show pipeline" / "list deals" | `list-opportunities` |
| "pipeline report" / "sales funnel" | `pipeline-report` |
| "create quotation from opportunity" | `convert-opportunity-to-quotation` |
| "executive dashboard" / "KPIs" | `executive-dashboard` |
| "current ratio" / "liquidity" | `liquidity-ratios` |
| "profit margin" / "ROA" / "ROE" | `profitability-ratios` |
| "revenue by customer" / "top customers" | `revenue-by-customer` |
| "expense breakdown" / "where is money going" | `expense-breakdown` |
| "detect anomalies" / "scan for issues" | `detect-anomalies` |
| "forecast cash flow" / "cash projection" | `forecast-cash-flow` |
| "what if" / "scenario analysis" | `create-scenario` |
| "score customer" / "relationship health" | `score-relationship` |
| "company scorecard" / "grade the company" | `company-scorecard` |
| "compare periods" / "this quarter vs last" | `period-comparison` |

### Confirmation Requirements

Confirm before: `convert-opportunity-to-quotation` (cross-package action), `evaluate-business-rules` (may trigger blocks), `mark-opportunity-won` / `mark-opportunity-lost` (terminal state), `convert-lead-to-opportunity` (freezes lead).

All `add-*`, `get-*`, `list-*`, `update-*`, analytics, and detection actions run immediately.

### Graceful Degradation

When optional erpclaw modules are not installed, analytics actions return partial results with
clear notes about which modules are missing. AI and CRM actions work independently of analytics.

### Response Formatting

- Currency: `$X,XXX.XX`, negatives in parentheses
- Ratios: 2 decimal places; Percentages: 1 decimal place with % sign
- Leads/opportunities: table with name, stage/status, revenue, probability
- Pipeline: table with stage, count, total revenue, weighted revenue
- Dates: `Mon DD, YYYY`. Use markdown tables for all tabular output.

## Technical Details (Tier 3)

### Architecture
- **Router**: `scripts/db_query.py` dispatches to 3 domain scripts (crm, analytics, ai-engine)
- **Domains**: crm (18 actions), analytics (25 actions), ai-engine (22 actions)
- **Database**: Single SQLite at `~/.openclaw/erpclaw/data.sqlite` (shared with erpclaw)

### Tables Owned (17)
CRM: lead_source, lead, opportunity, campaign, campaign_lead, crm_activity, communication. AI-Engine: anomaly, cash_flow_forecast, correlation, scenario, business_rule, categorization_rule, relationship_score, conversation_context, pending_decision, audit_conversation. Analytics: none (read-only).

### Data Conventions
Money = TEXT (Python Decimal), IDs = TEXT (UUID4), Dates = TEXT (ISO 8601). CRM naming series: `LEAD-{YEAR}-{SEQ}`, `OPP-{YEAR}-{SEQ}`. GL entries and stock ledger entries are immutable. All queries use parameterized statements.

### Script Path
```
scripts/db_query.py --action <action-name> [--key value ...]
```
