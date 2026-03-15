#!/usr/bin/env python3
"""VEXT Shield — Full Installation Security Audit.

Comprehensive security audit of an OpenClaw installation covering
configuration, file permissions, network exposure, SOUL.md integrity,
and installed skill safety.

Usage:
    python3 audit.py                  # Run full audit
    python3 audit.py --output report.md
    python3 audit.py --json

Built by Vext Labs.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from shared.scanner_core import ScannerCore, ScanResult
from shared.report_generator import ReportGenerator
from shared.utils import (
    check_file_permissions,
    enumerate_skills,
    find_openclaw_dir,
    find_vext_shield_dir,
    load_json_safe,
    parse_skill_md,
    score_to_grade,
    timestamp_str,
)


# ---------------------------------------------------------------------------
# Audit checks
# ---------------------------------------------------------------------------

def check_config_security(openclaw_dir: Path | None) -> list[dict[str, Any]]:
    """Check openclaw.json configuration for security best practices."""
    checks: list[dict[str, Any]] = []

    if openclaw_dir is None:
        checks.append({
            "name": "OpenClaw directory",
            "passed": False,
            "details": "OpenClaw directory not found — cannot audit configuration",
        })
        return checks

    config_path = openclaw_dir / "openclaw.json"
    if not config_path.exists():
        checks.append({
            "name": "Configuration file",
            "passed": True,
            "details": "No openclaw.json found — using safe defaults",
        })
        return checks

    config = load_json_safe(config_path)
    if config is None:
        checks.append({
            "name": "Configuration file",
            "passed": False,
            "details": "Failed to parse openclaw.json",
        })
        return checks

    # Check 1: Sandbox mode
    sandbox = _deep_get(config, "sandbox.enabled", _deep_get(config, "sandbox", None))
    if sandbox is True:
        checks.append({"name": "Sandbox mode", "passed": True, "details": "Sandbox is enabled"})
    elif sandbox is False:
        checks.append({"name": "Sandbox mode", "passed": False, "details": "Sandbox is DISABLED — skills can execute arbitrary commands"})
    else:
        checks.append({"name": "Sandbox mode", "passed": False, "details": "Sandbox mode not explicitly configured — recommend enabling"})

    # Check 2: Binding address
    bind_addr = _deep_get(config, "gateway.bind", _deep_get(config, "bind", None))
    if bind_addr and "0.0.0.0" in str(bind_addr):
        checks.append({
            "name": "Binding address",
            "passed": False,
            "details": f"Bound to {bind_addr} — EXPOSED to all network interfaces. Change to 127.0.0.1",
        })
    elif bind_addr and ("127.0.0.1" in str(bind_addr) or "localhost" in str(bind_addr)):
        checks.append({"name": "Binding address", "passed": True, "details": f"Bound to {bind_addr} (localhost only)"})
    else:
        checks.append({
            "name": "Binding address",
            "passed": False,
            "details": "Binding address not configured — default may be 0.0.0.0 (exposed). Set gateway.bind to 127.0.0.1",
        })

    # Check 3: Tool permissions
    tools_config = _deep_get(config, "tools", {})
    allow_all = _deep_get(tools_config, "allowAll", _deep_get(tools_config, "allow_all", None))
    if allow_all is True:
        checks.append({
            "name": "Tool permissions",
            "passed": False,
            "details": "tools.allowAll is TRUE — all tools unrestricted. Use an allowlist instead",
        })
    else:
        checks.append({"name": "Tool permissions", "passed": True, "details": "Tool permissions are scoped (not allowAll)"})

    # Check 4: Network egress
    network_config = _deep_get(config, "network", _deep_get(config, "egress", {}))
    allowlist = _deep_get(network_config, "allowlist", _deep_get(network_config, "whitelist", None))
    if allowlist and isinstance(allowlist, list) and len(allowlist) > 0:
        checks.append({"name": "Network egress", "passed": True, "details": f"Egress allowlist configured ({len(allowlist)} entries)"})
    else:
        checks.append({
            "name": "Network egress",
            "passed": False,
            "details": "No network egress allowlist configured — skills can contact any external server",
        })

    # Check 5: API keys in config
    config_str = json.dumps(config)
    key_patterns = [
        r'sk-[a-zA-Z0-9]{20,}',        # OpenAI
        r'sk-ant-[a-zA-Z0-9]{20,}',     # Anthropic
        r'AKIA[A-Z0-9]{16}',            # AWS
        r'ghp_[a-zA-Z0-9]{36}',         # GitHub
    ]
    exposed_keys = False
    for pattern in key_patterns:
        if re.search(pattern, config_str):
            exposed_keys = True
            break

    if exposed_keys:
        checks.append({
            "name": "API key storage",
            "passed": False,
            "details": "API keys found directly in openclaw.json — use environment variables instead",
        })
    else:
        checks.append({"name": "API key storage", "passed": True, "details": "No plaintext API keys detected in configuration"})

    return checks


def check_sensitive_permissions(openclaw_dir: Path | None) -> list[dict[str, Any]]:
    """Check file permissions on sensitive files."""
    results: list[dict[str, Any]] = []
    home = Path.home()

    sensitive_files = [
        home / ".env",
        home / ".ssh" / "id_rsa",
        home / ".ssh" / "id_ed25519",
    ]

    if openclaw_dir:
        sensitive_files.extend([
            openclaw_dir / "openclaw.json",
            openclaw_dir / "SOUL.md",
            openclaw_dir / "MEMORY.md",
        ])

    for fpath in sensitive_files:
        result = check_file_permissions(fpath)
        if result["exists"]:
            results.append(result)

    return results


def check_network_exposure() -> list[dict[str, Any]]:
    """Check for exposed network services."""
    checks: list[dict[str, Any]] = []

    # Check if OpenClaw default port is exposed
    common_ports = [18789, 8080, 3000, 5000]
    for port in common_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(("0.0.0.0", port))
                if result == 0:
                    checks.append({
                        "name": f"Port {port} exposure",
                        "passed": False,
                        "details": f"Port {port} is listening on all interfaces — may be exposed to the network",
                    })
        except (OSError, socket.error):
            pass

    if not checks:
        checks.append({
            "name": "Port exposure",
            "passed": True,
            "details": "No common ports found listening on all interfaces",
        })

    return checks


def check_soul_integrity(openclaw_dir: Path | None) -> dict[str, Any]:
    """Check SOUL.md for suspicious injected content."""
    result: dict[str, Any] = {"suspicious": False, "issues": []}

    if openclaw_dir is None:
        return result

    soul_path = openclaw_dir / "SOUL.md"
    if not soul_path.exists():
        return result

    try:
        content = soul_path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return result

    # Patterns that indicate SOUL.md has been tampered with
    suspicious_patterns = [
        (r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions", "Instruction override found in SOUL.md"),
        (r"developer\s+mode", "Developer mode reference in SOUL.md"),
        (r"no\s+restrictions", "No restrictions claim in SOUL.md"),
        (r"always\s+(?:execute|run)\s+(?:commands?|code)", "Auto-execute instruction in SOUL.md"),
        (r"without\s+(?:asking|confirmation|permission)", "Permission bypass in SOUL.md"),
        (r"do\s+not\s+(?:ask|verify|check|confirm)", "Verification bypass in SOUL.md"),
        (r"(?:spread|share|propagate|replicate)\s+(?:this|the)", "Propagation instruction in SOUL.md"),
        (r"collective\s+consciousness", "Collective consciousness reference in SOUL.md"),
        (r"override\s+safety", "Safety override in SOUL.md"),
        (r"you\s+are\s+(?:free|liberated|unrestricted)", "Freedom claim in SOUL.md"),
    ]

    for pattern, message in suspicious_patterns:
        if re.search(pattern, content):
            result["suspicious"] = True
            result["issues"].append(message)

    return result


def compute_security_score(
    config_checks: list[dict[str, Any]],
    perm_checks: list[dict[str, Any]],
    network_checks: list[dict[str, Any]],
    soul_check: dict[str, Any],
    scan_results: list[ScanResult],
) -> tuple[int, str]:
    """Compute overall security score (0-100) and letter grade (A-F)."""
    score = 100

    # Config checks (40 points max deduction)
    config_failures = sum(1 for c in config_checks if not c.get("passed"))
    score -= min(40, config_failures * 10)

    # Permission checks (15 points max deduction)
    perm_failures = sum(1 for p in perm_checks if not p.get("secure", True))
    score -= min(15, perm_failures * 5)

    # Network checks (15 points max deduction)
    network_failures = sum(1 for n in network_checks if not n.get("passed"))
    score -= min(15, network_failures * 8)

    # SOUL.md integrity (15 points max deduction)
    if soul_check.get("suspicious"):
        score -= min(15, len(soul_check.get("issues", [])) * 5)

    # Skill scan results (15 points max deduction)
    for r in scan_results:
        if r.risk_level == "CRITICAL":
            score -= 5
        elif r.risk_level == "HIGH":
            score -= 3
        elif r.risk_level == "MEDIUM":
            score -= 1

    score = max(0, min(100, score))
    grade = score_to_grade(score)
    return score, grade


def generate_remediations(
    config_checks: list[dict[str, Any]],
    perm_checks: list[dict[str, Any]],
    network_checks: list[dict[str, Any]],
    soul_check: dict[str, Any],
    scan_results: list[ScanResult],
) -> list[str]:
    """Generate remediation recommendations based on audit findings."""
    remediations: list[str] = []

    for check in config_checks:
        if not check.get("passed"):
            name = check.get("name", "")
            if "sandbox" in name.lower():
                remediations.append("Enable sandbox mode in openclaw.json: set sandbox.enabled to true")
            elif "binding" in name.lower():
                remediations.append("Change gateway.bind to '127.0.0.1' in openclaw.json to prevent network exposure")
            elif "tool" in name.lower():
                remediations.append("Remove tools.allowAll and configure a specific tool allowlist")
            elif "egress" in name.lower():
                remediations.append("Configure a network egress allowlist to restrict outbound connections")
            elif "api key" in name.lower():
                remediations.append("Move API keys from openclaw.json to environment variables")

    for p in perm_checks:
        if not p.get("secure", True):
            path = p.get("path", "")
            remediations.append(f"Fix permissions on {path}: chmod 600 (owner read/write only)")

    for n in network_checks:
        if not n.get("passed"):
            remediations.append("Review exposed ports and bind services to localhost only")

    if soul_check.get("suspicious"):
        remediations.append("CRITICAL: Review and clean SOUL.md — suspicious injected content detected")

    critical_skills = [r.skill_name for r in scan_results if r.risk_level == "CRITICAL"]
    if critical_skills:
        remediations.append(f"Remove or quarantine critical-risk skills: {', '.join(critical_skills)}")

    return remediations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _deep_get(d: dict | Any, key_path: str, default: Any = None) -> Any:
    """Get a nested dictionary value using dot-separated path."""
    if not isinstance(d, dict):
        return default
    keys = key_path.split(".")
    current = d
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    return current


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VEXT Shield — Full OpenClaw Installation Audit",
    )
    parser.add_argument("--output", type=Path, help="Custom output path for the report")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--quiet", action="store_true", help="Only output the grade")
    parser.add_argument("--skip-scan", action="store_true", help="Skip scanning installed skills")

    args = parser.parse_args()

    print("VEXT Shield — Running security audit...\n")

    openclaw_dir = find_openclaw_dir()
    if openclaw_dir:
        print(f"  OpenClaw directory: {openclaw_dir}")
    else:
        print("  OpenClaw directory: NOT FOUND")

    # Run checks
    print("  Checking configuration...", flush=True)
    config_checks = check_config_security(openclaw_dir)

    print("  Checking file permissions...", flush=True)
    perm_checks = check_sensitive_permissions(openclaw_dir)

    print("  Checking network exposure...", flush=True)
    network_checks = check_network_exposure()

    print("  Checking SOUL.md integrity...", flush=True)
    soul_check = check_soul_integrity(openclaw_dir)

    # Scan installed skills
    scan_results: list[ScanResult] = []
    if not args.skip_scan:
        skill_dirs = enumerate_skills(openclaw_dir)
        if skill_dirs:
            print(f"  Scanning {len(skill_dirs)} installed skill(s)...", flush=True)
            scanner = ScannerCore()
            for sd in skill_dirs:
                scan_results.append(scanner.scan_skill(sd))
        else:
            print("  No installed skills found to scan.")
    else:
        print("  Skipping skill scan (--skip-scan)")

    # Compute score
    score, grade = compute_security_score(
        config_checks, perm_checks, network_checks, soul_check, scan_results
    )

    # Generate remediations
    remediations = generate_remediations(
        config_checks, perm_checks, network_checks, soul_check, scan_results
    )

    # Build results dict
    audit_results: dict[str, Any] = {
        "score": score,
        "grade": grade,
        "config_checks": config_checks,
        "permission_checks": perm_checks,
        "network_checks": network_checks,
        "soul_check": soul_check,
        "skill_scan_results": scan_results,
        "remediations": remediations,
    }

    # Generate output
    if args.json:
        # Convert ScanResults to dicts for JSON
        json_results = dict(audit_results)
        json_results["skill_scan_results"] = [r.to_dict() for r in scan_results]
        output = json.dumps(json_results, indent=2)
    else:
        generator = ReportGenerator()
        output = generator.generate_audit_report(audit_results)

    # Save report
    if args.output:
        output_path = args.output
    else:
        reports_dir = find_vext_shield_dir() / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        ext = ".json" if args.json else ".md"
        output_path = reports_dir / f"audit-{timestamp_str()}{ext}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")

    if args.quiet:
        print(grade)
    else:
        print(f"\n  Security Grade: {grade} ({score}/100)")
        if remediations:
            print(f"  Remediations: {len(remediations)} recommended")
        print(f"\n  Full report saved to: {output_path}")

    # Exit code based on grade
    if grade in ("D", "F"):
        sys.exit(2)
    elif grade == "C":
        sys.exit(1)


if __name__ == "__main__":
    main()
