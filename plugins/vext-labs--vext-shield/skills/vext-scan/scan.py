#!/usr/bin/env python3
"""VEXT Shield — On-Demand Skill Scanner.

Scans installed OpenClaw skills for AI-native security threats including
prompt injection, data exfiltration, persistence manipulation, privilege
escalation, supply chain attacks, and semantic worms.

Usage:
    python3 scan.py --all                       # Scan all installed skills
    python3 scan.py --skill-dir /path/to/skill  # Scan a specific skill
    python3 scan.py --output report.md          # Custom output location

Built by Vext Labs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path for shared imports
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from shared.scanner_core import ScannerCore, ScanResult
from shared.report_generator import ReportGenerator
from shared.utils import enumerate_skills, find_vext_shield_dir, timestamp_str


def scan_all_skills(scanner: ScannerCore) -> list[ScanResult]:
    """Scan all installed OpenClaw skills."""
    skill_dirs = enumerate_skills()
    if not skill_dirs:
        print("No installed skills found.")
        print("Tip: Set OPENCLAW_HOME or ensure ~/.openclaw/ exists with skills.")
        return []

    print(f"Found {len(skill_dirs)} skill(s) to scan.\n")
    results: list[ScanResult] = []

    for skill_dir in skill_dirs:
        print(f"  Scanning: {skill_dir.name} ...", end=" ", flush=True)
        result = scanner.scan_skill(skill_dir)
        results.append(result)
        print(f"{result.risk_level} ({len(result.findings)} findings, {result.scan_duration_ms}ms)")

    return results


def scan_single_skill(scanner: ScannerCore, skill_dir: Path) -> list[ScanResult]:
    """Scan a single skill directory."""
    if not skill_dir.is_dir():
        print(f"Error: {skill_dir} is not a directory.", file=sys.stderr)
        sys.exit(1)

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"Warning: No SKILL.md found in {skill_dir}. Scanning anyway...")

    print(f"Scanning: {skill_dir.name} ...", end=" ", flush=True)
    result = scanner.scan_skill(skill_dir)
    print(f"{result.risk_level} ({len(result.findings)} findings, {result.scan_duration_ms}ms)")

    return [result]


def print_summary(results: list[ScanResult]) -> None:
    """Print a summary of scan results to stdout."""
    if not results:
        return

    total_findings = sum(len(r.findings) for r in results)
    critical = sum(1 for r in results if r.risk_level == "CRITICAL")
    high = sum(1 for r in results if r.risk_level == "HIGH")
    medium = sum(1 for r in results if r.risk_level == "MEDIUM")
    low = sum(1 for r in results if r.risk_level == "LOW")
    clean = sum(1 for r in results if r.risk_level == "CLEAN")

    print("\n" + "=" * 60)
    print("VEXT Shield — Scan Summary")
    print("=" * 60)
    print(f"  Skills scanned:  {len(results)}")
    print(f"  Total findings:  {total_findings}")
    print()

    if critical:
        print(f"  [CRITICAL]  {critical} skill(s) — immediate action required")
    if high:
        print(f"  [HIGH]      {high} skill(s) — review recommended")
    if medium:
        print(f"  [MEDIUM]    {medium} skill(s) — minor concerns")
    if low:
        print(f"  [LOW]       {low} skill(s) — informational")
    if clean:
        print(f"  [CLEAN]     {clean} skill(s) — no issues found")

    print("=" * 60)

    # Show top findings
    if total_findings > 0:
        print("\nTop findings:")
        all_findings = []
        for r in results:
            for f in r.findings:
                all_findings.append((r.skill_name, f))

        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        all_findings.sort(key=lambda x: severity_order.get(x[1].severity, 5))

        for skill_name, finding in all_findings[:10]:
            print(f"  [{finding.severity}] {skill_name}: {finding.name} ({finding.id})")

        if len(all_findings) > 10:
            print(f"  ... and {len(all_findings) - 10} more (see full report)")


def main() -> None:
    """Main entry point for the VEXT Shield scanner."""
    parser = argparse.ArgumentParser(
        description="VEXT Shield — Scan OpenClaw skills for security threats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Scan all installed OpenClaw skills",
    )
    parser.add_argument(
        "--skill-dir", type=Path,
        help="Path to a specific skill directory to scan",
    )
    parser.add_argument(
        "--output", type=Path,
        help="Custom output path for the report (default: ~/.openclaw/vext-shield/reports/)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON instead of markdown",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Only output the risk level (for scripting)",
    )

    args = parser.parse_args()

    if not args.all and not args.skill_dir:
        parser.print_help()
        print("\nError: specify --all or --skill-dir", file=sys.stderr)
        sys.exit(1)

    # Initialize scanner
    scanner = ScannerCore()

    # Run scan
    if args.skill_dir:
        results = scan_single_skill(scanner, args.skill_dir)
    else:
        results = scan_all_skills(scanner)

    if not results:
        sys.exit(0)

    # Generate report
    if args.json:
        import json
        output = json.dumps([r.to_dict() for r in results], indent=2)
    else:
        generator = ReportGenerator()
        output = generator.generate_scan_report(results)

    # Save report
    if args.output:
        output_path = args.output
    else:
        reports_dir = find_vext_shield_dir() / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        ext = ".json" if args.json else ".md"
        output_path = reports_dir / f"scan-{timestamp_str()}{ext}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")

    if not args.quiet:
        print_summary(results)
        print(f"\nFull report saved to: {output_path}")
    else:
        # Quiet mode: just output the highest risk level
        risk_levels = [r.risk_level for r in results]
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "CLEAN": 4}
        worst = min(risk_levels, key=lambda x: severity_order.get(x, 5))
        print(worst)

    # Exit with non-zero if critical findings
    if any(r.risk_level == "CRITICAL" for r in results):
        sys.exit(2)
    elif any(r.risk_level == "HIGH" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
