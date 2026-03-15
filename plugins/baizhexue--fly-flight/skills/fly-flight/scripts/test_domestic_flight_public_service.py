#!/usr/bin/env python3
"""Basic regression checks for domestic_flight_public_service.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "domestic_flight_public_service.py"
SAMPLE = ROOT / "assets" / "sample-public-state.json"


def run_command(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def main() -> int:
    payload = run_command(
        "search",
        "--from",
        "北京首都",
        "--to",
        "上海",
        "--date",
        "2026-03-20",
        "--sample-state",
        str(SAMPLE),
        "--limit",
        "1",
        "--sort-by",
        "price",
    )
    assert payload["trip_type"] == "one-way"
    assert payload["outbound"]["route"]["from"]["code"] == "PEK"
    assert payload["outbound"]["route"]["to"]["code"] == "SHA"
    assert payload["outbound"]["count"] == 1
    assert payload["outbound"]["flights"][0]["ticket_price"] == 700
    assert payload["outbound"]["flights"][0]["flight_no"] == "MU5100"

    round_trip = run_command(
        "search",
        "--from",
        "北京首都",
        "--to",
        "上海",
        "--date",
        "2026-03-20",
        "--return-date",
        "2026-03-22",
        "--sample-state",
        str(SAMPLE),
        "--return-sample-state",
        str(SAMPLE),
        "--limit",
        "1",
        "--direct-only",
    )
    assert round_trip["trip_type"] == "round-trip"
    assert round_trip["return"]["route"]["from"]["code"] == "SHA"
    assert round_trip["return"]["route"]["to"]["code"] == "PEK"
    assert round_trip["return"]["count"] == 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
