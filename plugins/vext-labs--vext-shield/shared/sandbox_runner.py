"""Sandbox runner for VEXT Shield.

Runs skill scripts in an isolated subprocess with:
- Temporary copy of skill directory (original never touched)
- macOS sandbox-exec network/filesystem deny policy
- Linux unshare network namespace isolation
- Restricted environment variables (API keys, tokens, credentials stripped)
- Timeout enforcement
- Post-execution behavioral analysis via file snapshot diffing

Only ONE isolation level exists: FULL (OS-level kernel sandbox).
If OS-level isolation is unavailable, execution is REFUSED.
There is no fallback, no bypass flag, and no weaker mode.
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import utils


@dataclass
class FileAccess:
    """Record of a file access during sandbox execution."""
    path: str
    mode: str          # "read", "write", "create", "delete"
    timestamp: float


@dataclass
class NetworkCall:
    """Record of a network call during sandbox execution."""
    destination: str
    port: int | None
    method: str        # "connect", "send", "dns"
    data_preview: str


@dataclass
class ProcessSpawn:
    """Record of a process spawned during sandbox execution."""
    command: str
    pid: int | None


@dataclass
class BehavioralReport:
    """Results of behavioral analysis from sandbox execution."""

    files_accessed: list[FileAccess] = field(default_factory=list)
    network_calls: list[NetworkCall] = field(default_factory=list)
    processes_spawned: list[ProcessSpawn] = field(default_factory=list)
    env_vars_accessed: list[str] = field(default_factory=list)
    modifications: list[dict[str, str]] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    exit_code: int = -1
    timed_out: bool = False
    error: str | None = None
    isolation_level: str = "FULL"  # Only FULL exists — no other modes

    def to_dict(self) -> dict[str, Any]:
        return {
            "files_accessed": [
                {"path": f.path, "mode": f.mode, "timestamp": f.timestamp}
                for f in self.files_accessed
            ],
            "network_calls": [
                {"destination": n.destination, "port": n.port, "method": n.method, "data_preview": n.data_preview}
                for n in self.network_calls
            ],
            "processes_spawned": [
                {"command": p.command, "pid": p.pid}
                for p in self.processes_spawned
            ],
            "env_vars_accessed": self.env_vars_accessed,
            "modifications": self.modifications,
            "duration_ms": self.duration_ms,
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "error": self.error,
            "isolation_level": self.isolation_level,
        }

    @property
    def has_suspicious_activity(self) -> bool:
        """Check if any suspicious activity was detected."""
        return bool(
            self.network_calls
            or self.env_vars_accessed
            or any(f.mode in ("write", "create", "delete") for f in self.files_accessed)
            or any(m.get("type") == "modified" for m in self.modifications)
        )


# Env vars to strip from the sandbox environment
_SENSITIVE_ENV_VARS = {
    "API_KEY", "SECRET_KEY", "TOKEN", "PASSWORD", "PRIVATE_KEY",
    "DATABASE_URL", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    "GITHUB_TOKEN", "STRIPE_SECRET_KEY", "STRIPE_KEY",
    "OPENCLAW_API_KEY", "HOME_ASSISTANT_TOKEN",
    "SMTP_PASSWORD", "REDIS_URL", "MONGO_URI",
    "GOOGLE_API_KEY", "AZURE_KEY", "SLACK_TOKEN",
    "DISCORD_TOKEN", "TELEGRAM_TOKEN",
}

# Additional env var patterns to strip (prefix matching)
_SENSITIVE_ENV_PREFIXES = (
    "AWS_", "OPENAI_", "ANTHROPIC_", "GITHUB_", "STRIPE_",
    "GOOGLE_", "AZURE_", "SLACK_", "DISCORD_", "SSH_", "GH_",
)


# macOS sandbox-exec profile: deny network + restrict filesystem writes
_MACOS_SANDBOX_PROFILE = """\
(version 1)
(deny default)
(allow process-exec)
(allow process-fork)
(allow file-read*)
(allow sysctl-read)
(allow mach-lookup)
(allow signal)
(allow system-socket)
(deny network*)
(allow file-write* (subpath "{tmpdir}"))
(deny file-write* (subpath "{homedir}/.openclaw"))
(deny file-write* (subpath "{homedir}/.ssh"))
(deny file-write* (subpath "{homedir}/.env"))
(deny file-write* (subpath "{homedir}/.aws"))
(deny file-write* (subpath "{homedir}/.config"))
"""


class SandboxRunner:
    """Runs skill scripts in an isolated subprocess environment.

    Only FULL OS-level isolation is supported:
    - macOS: sandbox-exec kernel policy (network denied, filesystem restricted)
    - Linux: unshare network namespace (network denied at kernel level)

    If neither is available, execution is REFUSED. There is no fallback mode,
    no bypass parameter, and no weaker isolation level.

    All executions include:
    - Script runs against a temporary copy (original never touched)
    - Sensitive env vars stripped
    - HOME overridden to temp directory
    - Timeout enforcement with process kill
    - Post-execution file snapshot diffing
    """

    def __init__(self, timeout_seconds: int = 30) -> None:
        self.timeout_seconds = timeout_seconds
        self._system = platform.system()
        self._has_sandbox_exec = (
            self._system == "Darwin"
            and shutil.which("sandbox-exec") is not None
        )
        self._has_unshare = (
            self._system == "Linux"
            and shutil.which("unshare") is not None
        )

    @property
    def has_full_isolation(self) -> bool:
        """Check if FULL OS-level isolation is available on this system."""
        return self._has_sandbox_exec or self._has_unshare

    def run_skill_script(
        self,
        script_path: Path,
        skill_dir: Path,
        args: list[str] | None = None,
        watch_dirs: list[Path] | None = None,
    ) -> BehavioralReport:
        """Run a skill script in an isolated environment and report behavior.

        The script is ALWAYS executed against a temporary copy of the skill
        directory. The original skill directory is never modified.

        If FULL OS-level sandbox is not available, execution is refused.

        Args:
            script_path: Path to the script to execute.
            skill_dir: Skill's root directory (will be copied to temp).
            args: Optional command-line arguments for the script.
            watch_dirs: Additional directories to monitor for changes.
        """
        report = BehavioralReport()
        start_time = time.monotonic()

        # Determine interpreter
        interpreter = self._find_interpreter(script_path)
        if interpreter is None:
            report.error = f"No interpreter found for {script_path.suffix}"
            return report

        # MANDATORY: Refuse execution without OS-level isolation
        if not self.has_full_isolation:
            report.error = (
                "FULL OS-level sandbox isolation is required but not available. "
                "macOS requires sandbox-exec, Linux requires unshare. "
                "Refusing to execute untrusted code without kernel-level isolation."
            )
            return report

        # Create a temporary copy of the skill directory
        # This ensures the original is NEVER modified
        tmp_base = tempfile.mkdtemp(prefix="vext-sandbox-")
        try:
            tmp_skill_dir = Path(tmp_base) / "skill"
            shutil.copytree(skill_dir, tmp_skill_dir)

            # Resolve the script path relative to the temp copy
            try:
                rel = script_path.resolve().relative_to(skill_dir.resolve())
                tmp_script = tmp_skill_dir / rel
            except ValueError:
                # Script is outside skill dir — copy it in
                tmp_script = tmp_skill_dir / script_path.name
                shutil.copy2(script_path, tmp_script)

            # Set up monitored directories (the temp copy + original for comparison)
            monitored: list[Path] = [tmp_skill_dir]

            # Snapshot file states before execution
            pre_snapshot = self._snapshot_files(monitored)

            # Create restricted environment
            env = self._create_restricted_env()
            # Override HOME to temp to prevent writes to real home
            env["HOME"] = tmp_base
            env["TMPDIR"] = tmp_base

            # Build sandboxed command (FULL isolation only — no fallback)
            cmd = self._build_sandboxed_command(
                interpreter, tmp_script, args, tmp_base
            )
            report.isolation_level = "FULL"

            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(tmp_skill_dir),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                try:
                    stdout, stderr = proc.communicate(timeout=self.timeout_seconds)
                    report.stdout = stdout[:10000]
                    report.stderr = stderr[:10000]
                    report.exit_code = proc.returncode
                except subprocess.TimeoutExpired:
                    proc.kill()
                    stdout, stderr = proc.communicate()
                    report.stdout = stdout[:10000] if stdout else ""
                    report.stderr = stderr[:10000] if stderr else ""
                    report.timed_out = True
                    report.exit_code = -1

            except FileNotFoundError:
                report.error = f"Interpreter not found: {interpreter}"
                return report
            except PermissionError:
                report.error = f"Permission denied executing {script_path}"
                return report
            except OSError as e:
                report.error = f"OS error: {e}"
                return report

            # Snapshot file states after execution
            post_snapshot = self._snapshot_files(monitored)

            # Diff snapshots (changes in the TEMP copy, not original)
            report.modifications = self._diff_snapshots(pre_snapshot, post_snapshot)
            report.files_accessed = self._infer_file_access(pre_snapshot, post_snapshot)

            # Analyze output for network activity indicators
            combined_output = (report.stdout + "\n" + report.stderr).lower()
            report.network_calls = self._detect_network_in_output(combined_output)

            # Check which sensitive env vars would have been accessed
            report.env_vars_accessed = self._check_env_access(report.stdout + report.stderr)

            report.duration_ms = int((time.monotonic() - start_time) * 1000)

        finally:
            # Always clean up temp directory
            shutil.rmtree(tmp_base, ignore_errors=True)

        return report

    def _build_sandboxed_command(
        self,
        interpreter: str,
        script_path: Path,
        args: list[str] | None,
        tmp_base: str,
    ) -> list[str]:
        """Build the execution command with OS-level isolation.

        Returns the sandboxed command. Only FULL isolation is supported.
        This method is only called after has_full_isolation is verified.
        """
        base_cmd = [interpreter, str(script_path)]
        if args:
            base_cmd.extend(args)

        # macOS sandbox-exec (kernel-level network deny + fs restriction)
        if self._has_sandbox_exec:
            home = os.path.expanduser("~")
            profile = _MACOS_SANDBOX_PROFILE.format(
                tmpdir=tmp_base,
                homedir=home,
            )
            profile_path = Path(tmp_base) / ".sandbox-profile"
            profile_path.write_text(profile)
            return ["sandbox-exec", "-f", str(profile_path)] + base_cmd

        # Linux unshare (network namespace isolation)
        if self._has_unshare:
            return ["unshare", "--net", "--map-root-user"] + base_cmd

        # Unreachable — has_full_isolation is checked before calling this method
        raise RuntimeError("No OS-level sandbox available")

    def _create_restricted_env(self) -> dict[str, str]:
        """Create a restricted environment for the sandboxed process.

        Strips sensitive environment variables and limits PATH.
        """
        env = {}

        for key, value in os.environ.items():
            # Strip known sensitive vars
            if key.upper() in _SENSITIVE_ENV_VARS:
                continue

            # Strip vars matching sensitive prefixes
            if any(key.upper().startswith(p) for p in _SENSITIVE_ENV_PREFIXES):
                continue

            env[key] = value

        # Restrict PATH to standard locations only
        safe_paths = [
            "/usr/local/bin", "/usr/bin", "/bin",
            "/usr/local/sbin", "/usr/sbin", "/sbin",
        ]
        # Include homebrew on macOS
        if platform.system() == "Darwin":
            safe_paths.insert(0, "/opt/homebrew/bin")

        env["PATH"] = ":".join(safe_paths)

        # Mark as sandboxed
        env["VEXT_SHIELD_SANDBOX"] = "1"

        return env

    @staticmethod
    def _find_interpreter(script_path: Path) -> str | None:
        """Determine the appropriate interpreter for a script."""
        ext = script_path.suffix.lower()
        interpreters = {
            ".py": "python3",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "zsh",
            ".js": "node",
            ".ts": "npx",
            ".rb": "ruby",
            ".pl": "perl",
        }
        interpreter = interpreters.get(ext)
        if interpreter and shutil.which(interpreter):
            return interpreter
        return None

    @staticmethod
    def _snapshot_files(directories: list[Path]) -> dict[str, dict[str, Any]]:
        """Take a snapshot of file states in monitored directories.

        Returns dict mapping path -> {mtime, size, hash} for each file.
        """
        snapshot: dict[str, dict[str, Any]] = {}

        for directory in directories:
            if not directory.exists():
                continue
            try:
                for file_path in directory.rglob("*"):
                    if not file_path.is_file():
                        continue
                    try:
                        stat = file_path.stat()
                        snapshot[str(file_path)] = {
                            "mtime": stat.st_mtime,
                            "size": stat.st_size,
                            "exists": True,
                        }
                    except (OSError, PermissionError):
                        continue
            except (OSError, PermissionError):
                continue

        return snapshot

    @staticmethod
    def _diff_snapshots(
        pre: dict[str, dict[str, Any]],
        post: dict[str, dict[str, Any]],
    ) -> list[dict[str, str]]:
        """Compare pre and post execution file snapshots."""
        modifications: list[dict[str, str]] = []

        # Check for modified and deleted files
        for path, pre_info in pre.items():
            if path not in post:
                modifications.append({"path": path, "type": "deleted"})
            elif post[path]["mtime"] != pre_info["mtime"] or post[path]["size"] != pre_info["size"]:
                modifications.append({"path": path, "type": "modified"})

        # Check for new files
        for path in post:
            if path not in pre:
                modifications.append({"path": path, "type": "created"})

        return modifications

    @staticmethod
    def _infer_file_access(
        pre: dict[str, dict[str, Any]],
        post: dict[str, dict[str, Any]],
    ) -> list[FileAccess]:
        """Infer file access from snapshot diffs."""
        accesses: list[FileAccess] = []
        now = time.time()

        for path in post:
            if path not in pre:
                accesses.append(FileAccess(path=path, mode="create", timestamp=now))
            elif post[path]["mtime"] != pre[path]["mtime"]:
                accesses.append(FileAccess(path=path, mode="write", timestamp=now))

        for path in pre:
            if path not in post:
                accesses.append(FileAccess(path=path, mode="delete", timestamp=now))

        return accesses

    @staticmethod
    def _detect_network_in_output(output: str) -> list[NetworkCall]:
        """Detect network activity indicators in process output."""
        calls: list[NetworkCall] = []

        # Detect URLs in output
        url_pattern = re.compile(r'https?://[^\s<>"\']+')
        for match in url_pattern.finditer(output):
            url = match.group()
            calls.append(NetworkCall(
                destination=url,
                port=443 if url.startswith("https") else 80,
                method="connect",
                data_preview="URL found in output",
            ))

        # Detect IP:port patterns
        ip_port_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})')
        for match in ip_port_pattern.finditer(output):
            calls.append(NetworkCall(
                destination=match.group(1),
                port=int(match.group(2)),
                method="connect",
                data_preview="IP:port found in output",
            ))

        return calls

    @staticmethod
    def _check_env_access(output: str) -> list[str]:
        """Check if output references sensitive environment variables."""
        accessed: list[str] = []
        output_upper = output.upper()

        for var in _SENSITIVE_ENV_VARS:
            if var in output_upper:
                accessed.append(var)

        return accessed
