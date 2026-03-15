from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sandbox_smoke_passes():
    proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "caduceusmail-sandbox-smoke.sh")],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "PASS" in proc.stdout
