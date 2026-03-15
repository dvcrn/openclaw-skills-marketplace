#!/usr/bin/env python3
"""VEXT Shield — Runtime Behavioral Monitor.

Watches for unauthorized file access, network egress, memory manipulation,
and suspicious process activity in the OpenClaw environment.

Usage:
    python3 monitor.py                    # One-shot check
    python3 monitor.py --watch --interval 60  # Continuous monitoring
    python3 monitor.py --baseline         # Create fresh baseline hashes

Built by Vext Labs.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from shared.utils import (
    find_openclaw_dir,
    find_vext_shield_dir,
    hash_file,
    timestamp_str,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MonitorAlert:
    """A single monitoring alert."""
    timestamp: str
    severity: str       # CRITICAL / HIGH / MEDIUM / LOW / INFO
    category: str       # file_integrity, sensitive_access, network, process
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "details": self.details,
        }

    def format_log_line(self) -> str:
        return f"[{self.timestamp}] [{self.severity}] [{self.category}] {self.message}"


@dataclass
class MonitorReport:
    """Aggregated monitoring results."""
    alerts: list[MonitorAlert] = field(default_factory=list)
    baseline_status: str = "unknown"   # "fresh", "unchanged", "modified", "missing"
    duration_ms: int = 0

    @property
    def has_critical(self) -> bool:
        return any(a.severity == "CRITICAL" for a in self.alerts)

    @property
    def has_alerts(self) -> bool:
        return len(self.alerts) > 0


# ---------------------------------------------------------------------------
# Monitor
# ---------------------------------------------------------------------------

# Files whose integrity we track
_IDENTITY_FILES = ["SOUL.md", "MEMORY.md", "AGENTS.md", "IDENTITY.md", "BOOT.md", "BOOTSTRAP.md"]
_CONFIG_FILES = ["openclaw.json"]

# Sensitive files that skills should not access
_SENSITIVE_PATHS = [
    ".env", ".ssh/id_rsa", ".ssh/id_ed25519", ".ssh/authorized_keys",
    ".aws/credentials", ".gcloud/credentials.db", ".kube/config",
    ".npmrc", ".pypirc", ".netrc", ".pgpass",
]

# Suspicious process patterns
_SUSPICIOUS_PROCESS_PATTERNS = [
    r"nc\s+-[el]",           # netcat listener
    r"ncat\s+--exec",        # ncat with exec
    r"socat\s+.*EXEC",       # socat exec
    r"/dev/tcp/",            # bash reverse shell
    r"xmrig|cpuminer",      # cryptominers
    r"python.*-m\s+http\.server",  # HTTP server
    r"ngrok",                # ngrok tunnel
]


class Monitor:
    """Runtime behavioral monitor for OpenClaw."""

    def __init__(self) -> None:
        self.shield_dir = find_vext_shield_dir()
        self.openclaw_dir = find_openclaw_dir()
        self.baseline_path = self.shield_dir / "baseline.json"
        self.log_path = self.shield_dir / "monitor.log"

    # -------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------

    def run_check(self) -> MonitorReport:
        """Run a full one-shot monitoring check."""
        start = time.monotonic()
        report = MonitorReport()

        # 1. File integrity check
        integrity_alerts = self._check_file_integrity()
        report.alerts.extend(integrity_alerts)
        if not integrity_alerts:
            report.baseline_status = "unchanged"
        elif any(a.severity == "CRITICAL" for a in integrity_alerts):
            report.baseline_status = "modified"

        # 2. Sensitive file access check
        report.alerts.extend(self._check_sensitive_file_permissions())

        # 3. Network connections check
        report.alerts.extend(self._check_network_connections())

        # 4. Suspicious processes check
        report.alerts.extend(self._check_suspicious_processes())

        report.duration_ms = int((time.monotonic() - start) * 1000)

        # Log all alerts
        self._log_alerts(report.alerts)

        return report

    def create_baseline(self) -> dict[str, str]:
        """Create a fresh baseline of file hashes."""
        baseline: dict[str, str] = {}

        if self.openclaw_dir is None:
            return baseline

        for fname in _IDENTITY_FILES + _CONFIG_FILES:
            fpath = self.openclaw_dir / fname
            if fpath.exists():
                baseline[fname] = hash_file(fpath)

        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        self.baseline_path.write_text(
            json.dumps(baseline, indent=2), encoding="utf-8"
        )

        return baseline

    def load_baseline(self) -> dict[str, str] | None:
        """Load existing baseline hashes."""
        if not self.baseline_path.exists():
            return None
        try:
            return json.loads(self.baseline_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    # -------------------------------------------------------------------
    # Check: File integrity
    # -------------------------------------------------------------------

    def _check_file_integrity(self) -> list[MonitorAlert]:
        """Check identity/config files against baseline hashes."""
        alerts: list[MonitorAlert] = []
        now = _now_str()

        baseline = self.load_baseline()
        if baseline is None:
            # No baseline — create one
            baseline = self.create_baseline()
            alerts.append(MonitorAlert(
                timestamp=now,
                severity="INFO",
                category="file_integrity",
                message="Created initial file integrity baseline",
                details={"files": list(baseline.keys())},
            ))
            return alerts

        if self.openclaw_dir is None:
            return alerts

        for fname in _IDENTITY_FILES + _CONFIG_FILES:
            fpath = self.openclaw_dir / fname
            expected_hash = baseline.get(fname)

            if not fpath.exists():
                if expected_hash:
                    alerts.append(MonitorAlert(
                        timestamp=now,
                        severity="HIGH",
                        category="file_integrity",
                        message=f"{fname} has been DELETED (was in baseline)",
                    ))
                continue

            current_hash = hash_file(fpath)

            if expected_hash is None:
                # New file not in baseline
                alerts.append(MonitorAlert(
                    timestamp=now,
                    severity="MEDIUM",
                    category="file_integrity",
                    message=f"{fname} is new (not in baseline)",
                    details={"hash": current_hash},
                ))
            elif current_hash != expected_hash:
                severity = "CRITICAL" if fname in ("SOUL.md", "AGENTS.md") else "HIGH"
                alerts.append(MonitorAlert(
                    timestamp=now,
                    severity=severity,
                    category="file_integrity",
                    message=f"{fname} has been MODIFIED since baseline",
                    details={
                        "expected_hash": expected_hash[:16] + "...",
                        "current_hash": current_hash[:16] + "...",
                    },
                ))

        return alerts

    # -------------------------------------------------------------------
    # Check: Sensitive file permissions
    # -------------------------------------------------------------------

    def _check_sensitive_file_permissions(self) -> list[MonitorAlert]:
        """Check if sensitive files have overly permissive permissions."""
        alerts: list[MonitorAlert] = []
        now = _now_str()
        home = Path.home()

        for rel_path in _SENSITIVE_PATHS:
            fpath = home / rel_path
            if not fpath.exists():
                continue

            stat = fpath.stat()
            mode = oct(stat.st_mode)[-3:]

            # Check for world-readable or world-writable
            if stat.st_mode & 0o004:  # world-readable
                alerts.append(MonitorAlert(
                    timestamp=now,
                    severity="HIGH",
                    category="sensitive_access",
                    message=f"Sensitive file is world-readable: ~/{rel_path} (mode {mode})",
                    details={"path": str(fpath), "mode": mode},
                ))
            if stat.st_mode & 0o002:  # world-writable
                alerts.append(MonitorAlert(
                    timestamp=now,
                    severity="CRITICAL",
                    category="sensitive_access",
                    message=f"Sensitive file is world-writable: ~/{rel_path} (mode {mode})",
                    details={"path": str(fpath), "mode": mode},
                ))

        # Check openclaw.json permissions
        if self.openclaw_dir:
            oc_config = self.openclaw_dir / "openclaw.json"
            if oc_config.exists():
                stat = oc_config.stat()
                mode = oct(stat.st_mode)[-3:]
                if stat.st_mode & 0o004:
                    alerts.append(MonitorAlert(
                        timestamp=now,
                        severity="MEDIUM",
                        category="sensitive_access",
                        message=f"openclaw.json is world-readable (mode {mode})",
                        details={"path": str(oc_config), "mode": mode},
                    ))

        return alerts

    # -------------------------------------------------------------------
    # Check: Network connections
    # -------------------------------------------------------------------

    def _check_network_connections(self) -> list[MonitorAlert]:
        """Check for suspicious outbound network connections."""
        alerts: list[MonitorAlert] = []
        now = _now_str()

        connections = self._get_network_connections()

        # Known suspicious ports
        suspicious_ports = {13338, 4444, 5555, 6666, 7777, 8888, 9999, 1337, 31337}

        for conn in connections:
            remote_port = conn.get("remote_port", 0)
            remote_addr = conn.get("remote_addr", "")
            pid = conn.get("pid", "?")
            process = conn.get("process", "?")

            if remote_port in suspicious_ports:
                alerts.append(MonitorAlert(
                    timestamp=now,
                    severity="CRITICAL",
                    category="network",
                    message=f"Connection to suspicious port {remote_port} ({remote_addr}) by PID {pid} ({process})",
                    details=conn,
                ))

        return alerts

    @staticmethod
    def _get_network_connections() -> list[dict[str, Any]]:
        """Get current network connections using OS tools."""
        connections: list[dict[str, Any]] = []

        try:
            if platform.system() == "Darwin":
                # macOS: use lsof
                result = subprocess.run(
                    ["lsof", "-i", "-n", "-P"],
                    capture_output=True, text=True, timeout=10,
                )
                for line in result.stdout.split("\n")[1:]:
                    parts = line.split()
                    if len(parts) >= 9 and "ESTABLISHED" in line:
                        name_col = parts[-2]  # e.g., "192.168.1.1:443->10.0.0.1:12345"
                        if "->" in name_col:
                            remote = name_col.split("->")[1]
                            addr, _, port = remote.rpartition(":")
                            connections.append({
                                "process": parts[0],
                                "pid": parts[1],
                                "remote_addr": addr,
                                "remote_port": int(port) if port.isdigit() else 0,
                            })
            else:
                # Linux: use ss
                result = subprocess.run(
                    ["ss", "-tunp"],
                    capture_output=True, text=True, timeout=10,
                )
                for line in result.stdout.split("\n")[1:]:
                    parts = line.split()
                    if len(parts) >= 5 and "ESTAB" in line:
                        peer = parts[4]
                        addr, _, port = peer.rpartition(":")
                        pid_info = parts[5] if len(parts) > 5 else "?"
                        connections.append({
                            "process": pid_info,
                            "pid": "?",
                            "remote_addr": addr,
                            "remote_port": int(port) if port.isdigit() else 0,
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return connections

    # -------------------------------------------------------------------
    # Check: Suspicious processes
    # -------------------------------------------------------------------

    def _check_suspicious_processes(self) -> list[MonitorAlert]:
        """Check for suspicious background processes."""
        alerts: list[MonitorAlert] = []
        now = _now_str()

        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True, text=True, timeout=10,
            )
            for line in result.stdout.split("\n"):
                for pattern in _SUSPICIOUS_PROCESS_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        alerts.append(MonitorAlert(
                            timestamp=now,
                            severity="CRITICAL",
                            category="process",
                            message=f"Suspicious process detected: {line.strip()[:120]}",
                            details={"pattern": pattern, "process_line": line.strip()[:200]},
                        ))
                        break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return alerts

    # -------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------

    def _log_alerts(self, alerts: list[MonitorAlert]) -> None:
        """Append alerts to the monitor log file."""
        if not alerts:
            return

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            for alert in alerts:
                f.write(alert.format_log_line() + "\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_report(report: MonitorReport) -> None:
    """Print monitoring results to stdout."""
    print("\n" + "=" * 60)
    print("VEXT Shield — Monitor Report")
    print("=" * 60)
    print(f"  Check duration:   {report.duration_ms}ms")
    print(f"  Baseline status:  {report.baseline_status}")
    print(f"  Alerts:           {len(report.alerts)}")
    print()

    if not report.alerts:
        print("  No security issues detected.")
    else:
        for alert in report.alerts:
            print(f"  [{alert.severity}] {alert.category}: {alert.message}")

    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VEXT Shield — Runtime Behavioral Monitor",
    )
    parser.add_argument(
        "--baseline", action="store_true",
        help="Create a fresh baseline of file hashes",
    )
    parser.add_argument(
        "--watch", action="store_true",
        help="Run in continuous monitoring mode",
    )
    parser.add_argument(
        "--interval", type=int, default=60,
        help="Check interval in seconds for --watch mode (default: 60)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()
    monitor = Monitor()

    if args.baseline:
        baseline = monitor.create_baseline()
        print(f"Baseline created with {len(baseline)} file(s).")
        for fname, h in baseline.items():
            print(f"  {fname}: {h[:16]}...")
        return

    if args.watch:
        print(f"VEXT Shield monitor running (checking every {args.interval}s). Ctrl+C to stop.")
        try:
            while True:
                report = monitor.run_check()
                if report.has_alerts:
                    print_report(report)
                else:
                    now = _now_str()
                    print(f"  [{now}] Check OK — no alerts")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitor stopped.")
        return

    # One-shot check
    report = monitor.run_check()

    if args.json:
        output = json.dumps({
            "alerts": [a.to_dict() for a in report.alerts],
            "baseline_status": report.baseline_status,
            "duration_ms": report.duration_ms,
        }, indent=2)
        print(output)
    else:
        print_report(report)

    log_path = monitor.log_path
    if report.alerts:
        print(f"\nAlerts logged to: {log_path}")

    if report.has_critical:
        sys.exit(2)
    elif report.has_alerts:
        sys.exit(1)


if __name__ == "__main__":
    main()
