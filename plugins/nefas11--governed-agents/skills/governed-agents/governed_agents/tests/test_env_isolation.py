import importlib
import os
from pathlib import Path

from governed_agents.contract import TaskContract


class DummyProc:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def _setup_module(monkeypatch, tmp_path):
    db_path = tmp_path / "reputation.db"
    monkeypatch.setenv("GOVERNED_DB_PATH", str(db_path))
    monkeypatch.setenv("OPENCLAW_WORKSPACE", str(tmp_path / "workspace"))
    return importlib.reload(importlib.import_module("governed_agents.openclaw_wrapper"))


def test_codex_subprocess_env_filtered(monkeypatch, tmp_path):
    module = _setup_module(monkeypatch, tmp_path)
    calls = []

    def _mock_run(cmd, **kwargs):
        calls.append(kwargs.get("env", {}))
        if cmd[0] == "git":
            return DummyProc()
        return DummyProc(stdout='```json {"status": "FAILED"} ```')

    monkeypatch.setattr(module.subprocess, "run", _mock_run)
    module.CODEX53_CLI = "codex"

    contract = TaskContract(objective="x", acceptance_criteria=[], required_files=[])
    module.spawn_governed(contract, engine="codex53")

    codex_env = calls[-1]
    assert set(codex_env.keys()) == {"PATH", "NO_COLOR"}


def test_openclaw_subprocess_env_filtered(monkeypatch, tmp_path):
    module = _setup_module(monkeypatch, tmp_path)
    calls = []

    def _mock_run(cmd, **kwargs):
        calls.append(kwargs.get("env", {}))
        return DummyProc(stdout='```json {"status": "FAILED"} ```')

    monkeypatch.setattr(module.subprocess, "run", _mock_run)

    contract = TaskContract(objective="x", acceptance_criteria=[], required_files=[])
    module.spawn_governed(contract, engine="openclaw")

    openclaw_env = calls[-1]
    assert set(openclaw_env.keys()) == {"PATH", "NO_COLOR"}


def test_secret_keys_not_in_subprocess_env(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")
    module = _setup_module(monkeypatch, tmp_path)
    calls = []

    def _mock_run(cmd, **kwargs):
        calls.append(kwargs.get("env", {}))
        if cmd[0] == "git":
            return DummyProc()
        return DummyProc(stdout='```json {"status": "FAILED"} ```')

    monkeypatch.setattr(module.subprocess, "run", _mock_run)
    module.CODEX53_CLI = "codex"

    contract = TaskContract(objective="x", acceptance_criteria=[], required_files=[])
    module.spawn_governed(contract, engine="codex53")

    for env in calls:
        assert "ANTHROPIC_API_KEY" not in env


def test_governed_pass_env_escape_hatch(monkeypatch, tmp_path):
    monkeypatch.setenv("GOVERNED_PASS_ENV", "1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")
    module = _setup_module(monkeypatch, tmp_path)
    calls = []

    def _mock_run(cmd, **kwargs):
        calls.append(kwargs.get("env", {}))
        if cmd[0] == "git":
            return DummyProc()
        return DummyProc(stdout='```json {"status": "FAILED"} ```')

    monkeypatch.setattr(module.subprocess, "run", _mock_run)
    module.CODEX53_CLI = "codex"

    contract = TaskContract(objective="x", acceptance_criteria=[], required_files=[])
    module.spawn_governed(contract, engine="codex53")

    assert "ANTHROPIC_API_KEY" in calls[-1]


def test_git_subprocess_inherits_minimal_env(monkeypatch, tmp_path):
    module = _setup_module(monkeypatch, tmp_path)
    calls = []

    def _mock_run(cmd, **kwargs):
        calls.append((cmd, kwargs.get("env", {})))
        if cmd[0] == "git":
            return DummyProc()
        return DummyProc(stdout='```json {"status": "FAILED"} ```')

    monkeypatch.setattr(module.subprocess, "run", _mock_run)
    module.CODEX53_CLI = "codex"

    contract = TaskContract(objective="x", acceptance_criteria=[], required_files=[])
    module.spawn_governed(contract, engine="codex53")

    git_env = calls[0][1]
    assert set(git_env.keys()) == {"PATH", "NO_COLOR"}


def test_pass_env_disabled_by_default(monkeypatch, tmp_path):
    monkeypatch.delenv("GOVERNED_PASS_ENV", raising=False)
    monkeypatch.setenv("EXTRA_SECRET", "secret")
    module = _setup_module(monkeypatch, tmp_path)
    calls = []

    def _mock_run(cmd, **kwargs):
        calls.append(kwargs.get("env", {}))
        if cmd[0] == "git":
            return DummyProc()
        return DummyProc(stdout='```json {"status": "FAILED"} ```')

    monkeypatch.setattr(module.subprocess, "run", _mock_run)
    module.CODEX53_CLI = "codex"

    contract = TaskContract(objective="x", acceptance_criteria=[], required_files=[])
    module.spawn_governed(contract, engine="codex53")

    codex_env = calls[-1]
    assert codex_env == {"PATH": os.environ.get("PATH", ""), "NO_COLOR": "1"}


def test_pass_env_warns_when_enabled(monkeypatch, tmp_path, caplog):
    monkeypatch.setenv("GOVERNED_PASS_ENV", "1")
    module = _setup_module(monkeypatch, tmp_path)
    calls = []

    def _mock_run(cmd, **kwargs):
        calls.append(kwargs.get("env", {}))
        if cmd[0] == "git":
            return DummyProc()
        return DummyProc(stdout='```json {"status": "FAILED"} ```')

    monkeypatch.setattr(module.subprocess, "run", _mock_run)
    module.CODEX53_CLI = "codex"

    contract = TaskContract(objective="x", acceptance_criteria=[], required_files=[])
    with caplog.at_level("WARNING"):
        module.spawn_governed(contract, engine="codex53")

    assert "GOVERNED_PASS_ENV=1" in caplog.text
