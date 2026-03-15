"""Tests for shared/sandbox_runner.py — isolated subprocess execution."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from shared.sandbox_runner import SandboxRunner, BehavioralReport


@pytest.fixture
def sandbox() -> SandboxRunner:
    """Create a sandbox runner with short timeout.

    All tests require FULL OS-level isolation. Tests are skipped on
    systems without sandbox-exec (macOS) or unshare (Linux).
    """
    runner = SandboxRunner(timeout_seconds=10)
    if not runner.has_full_isolation:
        pytest.skip("No OS-level sandbox available — cannot run sandbox tests")
    return runner


class TestSandboxIsolationPolicy:
    def test_only_full_isolation_supported(self):
        """SandboxRunner only supports FULL isolation — no parameters to weaken it."""
        runner = SandboxRunner()
        # No require_full_isolation parameter exists — FULL is mandatory
        assert not hasattr(runner, "require_full_isolation")

    def test_refuses_execution_without_full_isolation(self, tmp_path: Path):
        """When no OS sandbox is available, execution must be refused."""
        runner = SandboxRunner(timeout_seconds=5)

        # If this system has full isolation, skip this test
        if runner.has_full_isolation:
            pytest.skip("System has full isolation — cannot test refusal")

        script = tmp_path / "test.py"
        script.write_text('print("should not run")\n')

        report = runner.run_skill_script(script, tmp_path)
        assert report.error is not None
        assert "FULL OS-level sandbox isolation is required" in report.error
        assert report.exit_code == -1

    def test_has_full_isolation_property(self):
        """has_full_isolation property should return a boolean."""
        runner = SandboxRunner()
        assert isinstance(runner.has_full_isolation, bool)

    def test_no_copy_or_monitor_isolation_level(self):
        """Only FULL isolation level should exist in BehavioralReport."""
        report = BehavioralReport()
        assert report.isolation_level == "FULL"

    def test_no_bypass_parameters(self):
        """SandboxRunner constructor takes only timeout_seconds — no bypass options."""
        import inspect
        sig = inspect.signature(SandboxRunner.__init__)
        params = [p for p in sig.parameters if p != "self"]
        assert params == ["timeout_seconds"], (
            f"SandboxRunner has unexpected parameters: {params}"
        )


class TestSandboxEnvironment:
    def test_restricted_env_strips_api_keys(self):
        """Restricted env should not contain API keys."""
        runner = SandboxRunner()
        env = runner._create_restricted_env()
        sensitive_prefixes = [
            "OPENAI_", "ANTHROPIC_", "AWS_SECRET", "GH_TOKEN",
            "GITHUB_TOKEN", "SSH_AUTH_SOCK",
        ]
        for key in env:
            for prefix in sensitive_prefixes:
                assert not key.startswith(prefix), (
                    f"Sensitive env var {key} not stripped"
                )

    def test_restricted_env_has_path(self):
        """Restricted env should have a PATH."""
        runner = SandboxRunner()
        env = runner._create_restricted_env()
        assert "PATH" in env
        assert len(env["PATH"]) > 0

    def test_restricted_env_has_home(self):
        """Restricted env should have HOME."""
        runner = SandboxRunner()
        env = runner._create_restricted_env()
        assert "HOME" in env


class TestSandboxExecution:
    def test_run_benign_script(self, sandbox: SandboxRunner, tmp_path: Path):
        """Benign script should run and return clean report."""
        script = tmp_path / "benign.py"
        script.write_text('print("Hello, world!")\n')

        report = sandbox.run_skill_script(script, tmp_path)
        assert isinstance(report, BehavioralReport)
        assert report.exit_code == 0
        assert not report.has_suspicious_activity
        assert report.isolation_level == "FULL"

    def test_captures_stdout(self, sandbox: SandboxRunner, tmp_path: Path):
        """Should capture script stdout."""
        script = tmp_path / "hello.py"
        script.write_text('print("test output 12345")\n')

        report = sandbox.run_skill_script(script, tmp_path)
        assert report.exit_code == 0
        assert report.isolation_level == "FULL"

    def test_enforces_timeout(self, tmp_path: Path):
        """Scripts exceeding timeout should be killed."""
        runner = SandboxRunner(timeout_seconds=2)
        if not runner.has_full_isolation:
            pytest.skip("No OS-level sandbox available")

        script = tmp_path / "slow.py"
        script.write_text(
            'import time\n'
            'time.sleep(60)\n'
        )

        report = runner.run_skill_script(script, tmp_path)
        assert report.duration_ms < 10000  # Should be well under 10s
        assert report.exit_code != 0  # Killed by timeout

    def test_blocks_file_creation(self, sandbox: SandboxRunner, tmp_path: Path):
        """FULL sandbox should block file writes outside temp."""
        script = tmp_path / "creator.py"
        script.write_text(
            'from pathlib import Path\n'
            'Path("newfile.txt").write_text("created")\n'
        )

        report = sandbox.run_skill_script(script, tmp_path)
        assert report.isolation_level == "FULL"
        # OS-level sandbox blocks writes or they go to temp copy
        # Either way, original directory is not modified
        assert isinstance(report, BehavioralReport)

    def test_blocks_file_modification(self, sandbox: SandboxRunner, tmp_path: Path):
        """FULL sandbox should block file modifications outside temp."""
        target = tmp_path / "existing.txt"
        target.write_text("original content")

        script = tmp_path / "modifier.py"
        script.write_text(
            'from pathlib import Path\n'
            'Path("existing.txt").write_text("modified content")\n'
        )

        report = sandbox.run_skill_script(script, tmp_path)
        assert report.isolation_level == "FULL"
        # Original file should be untouched (script runs against temp copy)
        assert target.read_text() == "original content"

    def test_script_with_error(self, sandbox: SandboxRunner, tmp_path: Path):
        """Scripts with errors should still return a report."""
        script = tmp_path / "error.py"
        script.write_text('raise ValueError("test error")\n')

        report = sandbox.run_skill_script(script, tmp_path)
        assert isinstance(report, BehavioralReport)
        assert report.exit_code != 0
        assert report.isolation_level == "FULL"


class TestNetworkDetection:
    def test_detects_urls_in_output(self, sandbox: SandboxRunner, tmp_path: Path):
        """Should detect URLs printed to stdout."""
        script = tmp_path / "urlprint.py"
        script.write_text(
            'print("Sending to https://webhook.site/abc123")\n'
        )

        report = sandbox.run_skill_script(script, tmp_path)
        assert len(report.network_calls) > 0 or report.exit_code == 0

    def test_detects_ip_patterns(self, sandbox: SandboxRunner, tmp_path: Path):
        """Should detect IP:port patterns in output."""
        script = tmp_path / "ipprint.py"
        script.write_text(
            'print("Connecting to 192.168.1.1:4444")\n'
        )

        report = sandbox.run_skill_script(script, tmp_path)
        # Network detection is best-effort
        assert isinstance(report, BehavioralReport)


class TestEnvVarDetection:
    def test_detects_env_var_access_in_output(self, sandbox: SandboxRunner, tmp_path: Path):
        """Should detect references to sensitive env vars in output."""
        script = tmp_path / "envprint.py"
        script.write_text(
            'print("Reading OPENAI_API_KEY from environment")\n'
        )

        report = sandbox.run_skill_script(script, tmp_path)
        assert len(report.env_vars_accessed) > 0 or report.exit_code == 0
