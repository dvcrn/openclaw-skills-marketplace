---
name: medpilot-self-use
description: "Manage a single-patient medication and health-tracking workflow with MedPilot. Use when the user wants to ingest doctor orders, confirm active medications, record intakes or skipped doses, log blood pressure or glucose, generate follow-up summaries, or operate the MedPilot self-use edition through its CLI or local API. NOT for: multi-patient clinic workflows, diagnosis, treatment decisions, or replacing physician judgment."
---

# MedPilot Self-Use

Operate MedPilot as a single-patient medication and health-management assistant.

## Input to ask for
- patient identity for this local instance
- doctor order text
- medication intake updates
- home metrics such as blood pressure or glucose
- report date range when the user wants a summary

## Output
- structured order ingestion
- active medication/reminder state
- intake or skip logs
- abnormal metric alerts
- follow-up summary / weekly report

## Workflow
1. Register or identify the local patient profile.
2. Ingest the doctor order text.
3. Confirm the order before treating reminders as active.
4. Record intake, skip, or missed states.
5. Record home metrics and review generated alerts.
6. Build a follow-up report when needed.

## Boundaries
- Keep the scope to one patient in one local deployment.
- Treat MedPilot as a health-management and record-keeping tool, not a diagnosis system.
- Never present medication changes as autonomous medical advice.

## References
- Read `references/quickstart.md` for CLI and API examples when you need exact commands.
