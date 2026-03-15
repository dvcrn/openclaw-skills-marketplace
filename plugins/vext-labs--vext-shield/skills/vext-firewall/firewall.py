#!/usr/bin/env python3
"""VEXT Shield — Permission Boundary Enforcer.

Maintains per-skill allowlists for network destinations and file access.
Provides policy management, violation auditing, and logging.

Usage:
    python3 firewall.py list                                   # List all rules
    python3 firewall.py add --skill my-skill --type network --target api.example.com --action allow
    python3 firewall.py add --skill my-skill --type file --target /tmp --action allow
    python3 firewall.py remove --rule-id 1
    python3 firewall.py check --skill my-skill --type network --target evil.com
    python3 firewall.py violations

Built by Vext Labs.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from shared.utils import find_vext_shield_dir


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FirewallRule:
    """A single firewall policy rule."""
    id: int
    skill: str             # Skill name or "*" for all skills
    resource_type: str     # "network" or "file"
    target: str            # Domain/IP for network, path pattern for file
    action: str            # "allow" or "block"
    created: str           # ISO timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "skill": self.skill,
            "resource_type": self.resource_type,
            "target": self.target,
            "action": self.action,
            "created": self.created,
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> FirewallRule:
        return FirewallRule(
            id=d["id"],
            skill=d["skill"],
            resource_type=d["resource_type"],
            target=d["target"],
            action=d["action"],
            created=d.get("created", ""),
        )


@dataclass
class PolicyDecision:
    """Result of a policy check."""
    allowed: bool
    rule: FirewallRule | None = None
    reason: str = ""


@dataclass
class Violation:
    """A recorded policy violation."""
    timestamp: str
    skill: str
    resource_type: str
    target: str
    action_taken: str
    rule_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "skill": self.skill,
            "resource_type": self.resource_type,
            "target": self.target,
            "action_taken": self.action_taken,
            "rule_id": self.rule_id,
        }


# ---------------------------------------------------------------------------
# Firewall
# ---------------------------------------------------------------------------

class Firewall:
    """Permission boundary enforcer for OpenClaw skills."""

    def __init__(self) -> None:
        self.shield_dir = find_vext_shield_dir()
        self.policy_path = self.shield_dir / "firewall-policy.json"
        self.log_path = self.shield_dir / "firewall.log"
        self.violations_path = self.shield_dir / "firewall-violations.json"
        self._rules: list[FirewallRule] = []
        self._next_id: int = 1
        self._load_policy()

    # -------------------------------------------------------------------
    # Policy management
    # -------------------------------------------------------------------

    def add_rule(
        self,
        skill: str,
        resource_type: str,
        target: str,
        action: str = "allow",
    ) -> FirewallRule:
        """Add a new firewall rule."""
        resource_type = resource_type.lower()
        action = action.lower()

        if resource_type not in ("network", "file"):
            raise ValueError(f"Invalid resource_type: {resource_type}. Must be 'network' or 'file'")
        if action not in ("allow", "block"):
            raise ValueError(f"Invalid action: {action}. Must be 'allow' or 'block'")

        rule = FirewallRule(
            id=self._next_id,
            skill=skill,
            resource_type=resource_type,
            target=target,
            action=action,
            created=_now_str(),
        )
        self._rules.append(rule)
        self._next_id += 1
        self._save_policy()
        self._log(f"Rule added: {rule.to_dict()}")
        return rule

    def remove_rule(self, rule_id: int) -> bool:
        """Remove a rule by ID."""
        for i, rule in enumerate(self._rules):
            if rule.id == rule_id:
                removed = self._rules.pop(i)
                self._save_policy()
                self._log(f"Rule removed: {removed.to_dict()}")
                return True
        return False

    def list_rules(self) -> list[FirewallRule]:
        """List all firewall rules."""
        return list(self._rules)

    def check_policy(
        self,
        skill: str,
        resource_type: str,
        target: str,
    ) -> PolicyDecision:
        """Check if a skill is allowed to access a resource.

        Default policy is DENY — access must be explicitly allowed.
        Block rules take precedence over allow rules.
        """
        resource_type = resource_type.lower()
        matching_rules: list[FirewallRule] = []

        for rule in self._rules:
            # Check if rule applies to this skill
            if rule.skill != "*" and rule.skill != skill:
                continue
            # Check if rule applies to this resource type
            if rule.resource_type != resource_type:
                continue
            # Check if target matches
            if self._target_matches(rule.target, target, resource_type):
                matching_rules.append(rule)

        # Block rules take precedence
        for rule in matching_rules:
            if rule.action == "block":
                return PolicyDecision(
                    allowed=False,
                    rule=rule,
                    reason=f"Blocked by rule #{rule.id}",
                )

        # Check for allow rules
        for rule in matching_rules:
            if rule.action == "allow":
                return PolicyDecision(
                    allowed=True,
                    rule=rule,
                    reason=f"Allowed by rule #{rule.id}",
                )

        # Default deny
        return PolicyDecision(
            allowed=False,
            rule=None,
            reason="Default DENY — no matching allow rule",
        )

    def record_violation(self, skill: str, resource_type: str, target: str, rule_id: int | None = None) -> None:
        """Record a policy violation."""
        violation = Violation(
            timestamp=_now_str(),
            skill=skill,
            resource_type=resource_type,
            target=target,
            action_taken="BLOCKED",
            rule_id=rule_id,
        )
        violations = self._load_violations()
        violations.append(violation.to_dict())
        self.violations_path.write_text(json.dumps(violations, indent=2), encoding="utf-8")
        self._log(f"VIOLATION: {violation.to_dict()}")

    def get_violations(self) -> list[dict[str, Any]]:
        """Get all recorded violations."""
        return self._load_violations()

    # -------------------------------------------------------------------
    # Internal
    # -------------------------------------------------------------------

    @staticmethod
    def _target_matches(rule_target: str, actual_target: str, resource_type: str) -> bool:
        """Check if an actual target matches a rule target pattern."""
        rule_target = rule_target.lower()
        actual_target = actual_target.lower()

        if rule_target == "*":
            return True

        if resource_type == "network":
            # Domain matching: rule "example.com" matches "api.example.com"
            return actual_target == rule_target or actual_target.endswith("." + rule_target)
        else:
            # File path matching: rule "/tmp" matches "/tmp/foo/bar"
            return actual_target.startswith(rule_target)

    def _load_policy(self) -> None:
        """Load policy from disk."""
        if not self.policy_path.exists():
            self._rules = []
            self._next_id = 1
            return

        try:
            data = json.loads(self.policy_path.read_text(encoding="utf-8"))
            self._rules = [FirewallRule.from_dict(r) for r in data.get("rules", [])]
            self._next_id = data.get("next_id", 1)
        except (json.JSONDecodeError, KeyError, OSError):
            self._rules = []
            self._next_id = 1

    def _save_policy(self) -> None:
        """Save policy to disk."""
        self.policy_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "rules": [r.to_dict() for r in self._rules],
            "next_id": self._next_id,
        }
        self.policy_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_violations(self) -> list[dict[str, Any]]:
        """Load violations from disk."""
        if not self.violations_path.exists():
            return []
        try:
            return json.loads(self.violations_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _log(self, message: str) -> None:
        """Write to firewall log."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"[{_now_str()}] {message}\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VEXT Shield — Permission Boundary Enforcer",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list
    subparsers.add_parser("list", help="List all firewall rules")

    # add
    add_parser = subparsers.add_parser("add", help="Add a firewall rule")
    add_parser.add_argument("--skill", required=True, help="Skill name (or * for all)")
    add_parser.add_argument("--type", required=True, choices=["network", "file"], help="Resource type")
    add_parser.add_argument("--target", required=True, help="Target (domain for network, path for file)")
    add_parser.add_argument("--action", default="allow", choices=["allow", "block"], help="Action (default: allow)")

    # remove
    rm_parser = subparsers.add_parser("remove", help="Remove a rule by ID")
    rm_parser.add_argument("--rule-id", type=int, required=True, help="Rule ID to remove")

    # check
    chk_parser = subparsers.add_parser("check", help="Check if access is allowed")
    chk_parser.add_argument("--skill", required=True, help="Skill name")
    chk_parser.add_argument("--type", required=True, choices=["network", "file"], help="Resource type")
    chk_parser.add_argument("--target", required=True, help="Target to check")

    # violations
    subparsers.add_parser("violations", help="Show recorded violations")

    args = parser.parse_args()
    fw = Firewall()

    if args.command == "list":
        rules = fw.list_rules()
        if not rules:
            print("No firewall rules configured.")
            print("\nDefault policy: DENY ALL")
            print("Use 'add' to create rules.")
        else:
            print(f"Firewall Rules ({len(rules)}):\n")
            print(f"  {'ID':<4} {'Action':<8} {'Skill':<20} {'Type':<10} {'Target':<30} {'Created'}")
            print(f"  {'─'*4} {'─'*8} {'─'*20} {'─'*10} {'─'*30} {'─'*20}")
            for r in rules:
                print(f"  {r.id:<4} {r.action:<8} {r.skill:<20} {r.resource_type:<10} {r.target:<30} {r.created}")

    elif args.command == "add":
        rule = fw.add_rule(args.skill, args.type, args.target, args.action)
        print(f"Rule #{rule.id} added: {rule.action.upper()} {rule.skill} -> {rule.resource_type}:{rule.target}")

    elif args.command == "remove":
        if fw.remove_rule(args.rule_id):
            print(f"Rule #{args.rule_id} removed.")
        else:
            print(f"Rule #{args.rule_id} not found.", file=sys.stderr)
            sys.exit(1)

    elif args.command == "check":
        decision = fw.check_policy(args.skill, args.type, args.target)
        status = "ALLOWED" if decision.allowed else "BLOCKED"
        print(f"{status}: {args.skill} -> {args.type}:{args.target}")
        print(f"  Reason: {decision.reason}")

    elif args.command == "violations":
        violations = fw.get_violations()
        if not violations:
            print("No violations recorded.")
        else:
            print(f"Violations ({len(violations)}):\n")
            for v in violations[-20:]:  # Show last 20
                print(f"  [{v.get('timestamp', '?')}] {v.get('skill', '?')} -> {v.get('resource_type', '?')}:{v.get('target', '?')} ({v.get('action_taken', '?')})")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
