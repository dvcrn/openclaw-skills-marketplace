#!/usr/bin/env python3
"""ERPClaw-People v2 — Unified router for 50 actions across 2 domains.

Routes --action to the correct domain script via os.execvp().
Domains: hr, payroll.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout (passed through from domain script)
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Action → domain mapping (48 unique actions + 2 status aliases)
# Only collision: `status` in both domains → routes to hr.
ACTION_MAP = {
    # === HR (28 actions) ===
    "add-employee": "erpclaw-hr",
    "update-employee": "erpclaw-hr",
    "get-employee": "erpclaw-hr",
    "list-employees": "erpclaw-hr",
    "add-department": "erpclaw-hr",
    "list-departments": "erpclaw-hr",
    "add-designation": "erpclaw-hr",
    "list-designations": "erpclaw-hr",
    "add-leave-type": "erpclaw-hr",
    "list-leave-types": "erpclaw-hr",
    "add-leave-allocation": "erpclaw-hr",
    "get-leave-balance": "erpclaw-hr",
    "add-leave-application": "erpclaw-hr",
    "approve-leave": "erpclaw-hr",
    "reject-leave": "erpclaw-hr",
    "list-leave-applications": "erpclaw-hr",
    "mark-attendance": "erpclaw-hr",
    "bulk-mark-attendance": "erpclaw-hr",
    "list-attendance": "erpclaw-hr",
    "add-holiday-list": "erpclaw-hr",
    "add-expense-claim": "erpclaw-hr",
    "submit-expense-claim": "erpclaw-hr",
    "approve-expense-claim": "erpclaw-hr",
    "reject-expense-claim": "erpclaw-hr",
    "update-expense-claim-status": "erpclaw-hr",
    "list-expense-claims": "erpclaw-hr",
    "record-lifecycle-event": "erpclaw-hr",
    "status": "erpclaw-hr",

    # === Payroll (22 actions) ===
    "add-salary-component": "erpclaw-payroll",
    "list-salary-components": "erpclaw-payroll",
    "add-salary-structure": "erpclaw-payroll",
    "get-salary-structure": "erpclaw-payroll",
    "list-salary-structures": "erpclaw-payroll",
    "add-salary-assignment": "erpclaw-payroll",
    "list-salary-assignments": "erpclaw-payroll",
    "add-income-tax-slab": "erpclaw-payroll",
    "update-fica-config": "erpclaw-payroll",
    "update-futa-suta-config": "erpclaw-payroll",
    "create-payroll-run": "erpclaw-payroll",
    "generate-salary-slips": "erpclaw-payroll",
    "get-salary-slip": "erpclaw-payroll",
    "list-salary-slips": "erpclaw-payroll",
    "submit-payroll-run": "erpclaw-payroll",
    "cancel-payroll-run": "erpclaw-payroll",
    "generate-w2-data": "erpclaw-payroll",
    "add-garnishment": "erpclaw-payroll",
    "update-garnishment": "erpclaw-payroll",
    "list-garnishments": "erpclaw-payroll",
    "get-garnishment": "erpclaw-payroll",
}

# Aliases: domain-specific status commands
ALIASES = {
    "hr-status": ("erpclaw-hr", "status"),
    "payroll-status": ("erpclaw-payroll", "status"),
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
