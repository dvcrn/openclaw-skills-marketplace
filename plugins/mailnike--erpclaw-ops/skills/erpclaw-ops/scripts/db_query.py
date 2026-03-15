#!/usr/bin/env python3
"""ERPClaw-Ops v2 — Unified router for 91 actions across 5 domains.

Routes --action to the correct domain script via os.execvp().
Domains: manufacturing, projects, assets, quality, support.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout (passed through from domain script)
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Action → domain mapping (86 unique actions + 5 status aliases)
# Only collision: `status` in all 5 domains → routes to manufacturing.
ACTION_MAP = {
    # === Manufacturing (24 actions) ===
    "add-bom": "erpclaw-manufacturing",
    "update-bom": "erpclaw-manufacturing",
    "get-bom": "erpclaw-manufacturing",
    "list-boms": "erpclaw-manufacturing",
    "explode-bom": "erpclaw-manufacturing",
    "add-operation": "erpclaw-manufacturing",
    "add-workstation": "erpclaw-manufacturing",
    "add-routing": "erpclaw-manufacturing",
    "add-work-order": "erpclaw-manufacturing",
    "get-work-order": "erpclaw-manufacturing",
    "list-work-orders": "erpclaw-manufacturing",
    "start-work-order": "erpclaw-manufacturing",
    "transfer-materials": "erpclaw-manufacturing",
    "create-job-card": "erpclaw-manufacturing",
    "complete-job-card": "erpclaw-manufacturing",
    "complete-work-order": "erpclaw-manufacturing",
    "cancel-work-order": "erpclaw-manufacturing",
    "create-production-plan": "erpclaw-manufacturing",
    "run-mrp": "erpclaw-manufacturing",
    "get-production-plan": "erpclaw-manufacturing",
    "generate-work-orders": "erpclaw-manufacturing",
    "generate-purchase-requests": "erpclaw-manufacturing",
    "add-subcontracting-order": "erpclaw-manufacturing",
    "status": "erpclaw-manufacturing",

    # === Projects (19 actions) ===
    "add-project": "erpclaw-projects",
    "update-project": "erpclaw-projects",
    "get-project": "erpclaw-projects",
    "list-projects": "erpclaw-projects",
    "add-task": "erpclaw-projects",
    "update-task": "erpclaw-projects",
    "list-tasks": "erpclaw-projects",
    "add-milestone": "erpclaw-projects",
    "update-milestone": "erpclaw-projects",
    "add-timesheet": "erpclaw-projects",
    "get-timesheet": "erpclaw-projects",
    "list-timesheets": "erpclaw-projects",
    "submit-timesheet": "erpclaw-projects",
    "bill-timesheet": "erpclaw-projects",
    "create-billing-from-timesheets": "erpclaw-projects",
    "project-profitability": "erpclaw-projects",
    "gantt-data": "erpclaw-projects",
    "resource-utilization": "erpclaw-projects",

    # === Assets (16 actions) ===
    "add-asset-category": "erpclaw-assets",
    "list-asset-categories": "erpclaw-assets",
    "add-asset": "erpclaw-assets",
    "update-asset": "erpclaw-assets",
    "get-asset": "erpclaw-assets",
    "list-assets": "erpclaw-assets",
    "generate-depreciation-schedule": "erpclaw-assets",
    "post-depreciation": "erpclaw-assets",
    "run-depreciation": "erpclaw-assets",
    "record-asset-movement": "erpclaw-assets",
    "schedule-maintenance": "erpclaw-assets",
    "complete-maintenance": "erpclaw-assets",
    "dispose-asset": "erpclaw-assets",
    "asset-register-report": "erpclaw-assets",
    "depreciation-summary": "erpclaw-assets",

    # === Quality (14 actions) ===
    "add-inspection-template": "erpclaw-quality",
    "get-inspection-template": "erpclaw-quality",
    "list-inspection-templates": "erpclaw-quality",
    "add-quality-inspection": "erpclaw-quality",
    "record-inspection-readings": "erpclaw-quality",
    "evaluate-inspection": "erpclaw-quality",
    "list-quality-inspections": "erpclaw-quality",
    "add-non-conformance": "erpclaw-quality",
    "update-non-conformance": "erpclaw-quality",
    "list-non-conformances": "erpclaw-quality",
    "add-quality-goal": "erpclaw-quality",
    "update-quality-goal": "erpclaw-quality",
    "quality-dashboard": "erpclaw-quality",

    # === Support (18 actions) ===
    "add-issue": "erpclaw-support",
    "update-issue": "erpclaw-support",
    "get-issue": "erpclaw-support",
    "list-issues": "erpclaw-support",
    "add-issue-comment": "erpclaw-support",
    "resolve-issue": "erpclaw-support",
    "reopen-issue": "erpclaw-support",
    "add-sla": "erpclaw-support",
    "list-slas": "erpclaw-support",
    "add-warranty-claim": "erpclaw-support",
    "update-warranty-claim": "erpclaw-support",
    "list-warranty-claims": "erpclaw-support",
    "add-maintenance-schedule": "erpclaw-support",
    "list-maintenance-schedules": "erpclaw-support",
    "record-maintenance-visit": "erpclaw-support",
    "sla-compliance-report": "erpclaw-support",
    "overdue-issues-report": "erpclaw-support",
}

# Aliases: domain-specific status commands
ALIASES = {
    "manufacturing-status": ("erpclaw-manufacturing", "status"),
    "projects-status": ("erpclaw-projects", "status"),
    "assets-status": ("erpclaw-assets", "status"),
    "quality-status": ("erpclaw-quality", "status"),
    "support-status": ("erpclaw-support", "status"),
}


def find_action():
    """Extract --action value from sys.argv."""
    for i, arg in enumerate(sys.argv):
        if arg == "--action" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def forward(domain, action_override=None):
    """Forward execution to the domain script via os.execvp."""
    script = os.path.join(BASE_DIR, domain, "db_query.py")
    if not os.path.isfile(script):
        print(json.dumps({
            "status": "error",
            "error": f"Domain script not found: {domain}/db_query.py"
        }))
        sys.exit(1)

    args = list(sys.argv[1:])

    if action_override:
        for i, arg in enumerate(args):
            if arg == "--action" and i + 1 < len(args):
                args[i + 1] = action_override
                break

    os.execvp(sys.executable, [sys.executable, script] + args)


def main():
    action = find_action()
    if not action:
        print(json.dumps({
            "status": "error",
            "error": "Missing --action flag. Usage: python3 db_query.py --action <action-name> [flags]"
        }))
        sys.exit(1)

    if action in ALIASES:
        domain, original_action = ALIASES[action]
        forward(domain, action_override=original_action)
        return

    domain = ACTION_MAP.get(action)
    if not domain:
        print(json.dumps({
            "status": "error",
            "error": f"Unknown action: {action}",
            "hint": "Run --action status for system overview"
        }))
        sys.exit(1)

    forward(domain)


if __name__ == "__main__":
    main()
