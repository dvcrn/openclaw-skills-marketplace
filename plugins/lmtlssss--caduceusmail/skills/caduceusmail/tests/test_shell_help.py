from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_shell_help_mentions_simulate_bootstrap():
    proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "caduceusmail.sh"), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "--simulate-bootstrap" in proc.stdout
    assert "--bootstrap-auth-mode" in proc.stdout
