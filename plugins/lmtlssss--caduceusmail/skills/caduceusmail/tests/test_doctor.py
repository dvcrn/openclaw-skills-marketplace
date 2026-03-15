from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_doctor_json_reports_device_in_sandbox(tmp_path):
    env = os.environ.copy()
    env["OPENCLAW_SANDBOX"] = "1"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "caduceusmail-doctor.py"), "--json", "--base-dir", str(ROOT)],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    report = json.loads(proc.stdout)
    assert report["auth"]["recommended"] == "device"
    assert report["skill"]["metadata_is_single_line_json"] is True


def test_doctor_strict_fails_without_runtime_keys(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "caduceusmail-doctor.py"), "--strict", "--base-dir", str(ROOT)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
