#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp"]
# ///
"""case-analyzer MCP server — Langfuse trace analysis + media extraction + admin upload.

Run with: uv run .cursor/skills/case-analyzer/mcp-server.py
"""

import io
import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
import os
import subprocess
from pathlib import Path
from typing import Optional
from urllib.parse import unquote

from mcp.server.fastmcp import FastMCP

server = FastMCP("case-analyzer")

SKILL_DIR = Path(__file__).parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
DEFAULT_OUTPUT_DIR = "analysis/langfuse-data"


@server.tool()
async def fetch_traces(conversation_id: str, output_dir: Optional[str] = None) -> str:
    """Fetch all Langfuse traces for a case/conversation.

    Downloads trace JSON files from Langfuse API and saves them locally.
    Requires LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST env vars.

    Args:
        conversation_id: The case/conversation ID to fetch traces for (e.g. "31574785111").
        output_dir: Base output directory (default: "analysis/langfuse-data").

    Returns:
        JSON with trace count, file paths, and case directory.
    """
    out_dir = output_dir or DEFAULT_OUTPUT_DIR

    for var in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"):
        if not os.environ.get(var):
            return json.dumps({"error": f"Missing env var: {var}"})

    script = str(SCRIPTS_DIR / "fetch-case.py")
    result = subprocess.run(
        [sys.executable, script,
         "--conversation-id", conversation_id,
         "--output-dir", out_dir],
        capture_output=True, text=True, timeout=300,
    )

    case_dir = os.path.join(out_dir, "cases", conversation_id)
    traces = sorted(Path(case_dir).glob("trace-*.json")) if Path(case_dir).exists() else []

    if result.returncode != 0:
        return json.dumps({
            "error": f"fetch-case.py failed: {result.stderr.strip()}",
            "stdout": result.stdout.strip(),
        })

    return json.dumps({
        "status": "ok",
        "conversation_id": conversation_id,
        "case_dir": case_dir,
        "trace_count": len(traces),
        "trace_files": [str(t) for t in traces],
        "output": result.stdout.strip(),
    }, ensure_ascii=False)


@server.tool()
async def extract_assets(case_dir: str, skip_download: bool = False) -> str:
    """Extract media assets (images, videos, audio) and their prompts from Langfuse trace JSON files.

    Scans trace-*.json files in the case directory, extracts tool call parameters,
    deduplicates, and optionally downloads media files.

    Args:
        case_dir: Path to case directory containing trace-*.json files
                  (e.g. "analysis/langfuse-data/cases/31574785111").
        skip_download: If True, only extract metadata without downloading files.

    Returns:
        JSON with asset counts by type, file paths, and download results.
    """
    script = str(SCRIPTS_DIR / "extract-assets.py")
    cmd = [sys.executable, script, "--case-dir", case_dir]
    if skip_download:
        cmd.append("--skip-download")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    assets_path = os.path.join(case_dir, "assets.json")
    assets = []
    if os.path.exists(assets_path):
        with open(assets_path) as f:
            assets = json.load(f)

    media_dir = os.path.join(case_dir, "media")
    media_files = sorted(os.listdir(media_dir)) if os.path.isdir(media_dir) else []

    by_type = {}
    for a in assets:
        t = a.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    return json.dumps({
        "status": "ok" if result.returncode == 0 else "error",
        "asset_count": len(assets),
        "by_type": by_type,
        "media_files": media_files,
        "media_count": len(media_files),
        "assets_json": assets_path,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None,
    }, ensure_ascii=False)


@server.tool()
async def upload_package(
    conversation_id: str,
    dashboard_dir: str,
    entry_file: str = "qa-report.html",
    description: str = "",
) -> str:
    """Package a QA dashboard with media and upload to Pexo admin backend.

    Creates a zip of the dashboard HTML + media/ directory, then uploads
    to admin.pexo.ai/api/strategy-packages.
    Requires PEXO_ADMIN_TOKEN env var.

    Args:
        conversation_id: Case ID used as the package name (e.g. "31574785111").
        dashboard_dir: Directory containing qa-report.html and media/.
        entry_file: HTML entry filename (default: "qa-report.html").
        description: Optional package description.

    Returns:
        JSON with package ID, preview URL, and upload status.
    """
    token = os.environ.get("PEXO_ADMIN_TOKEN")
    if not token:
        return json.dumps({
            "error": "Missing PEXO_ADMIN_TOKEN. Get it from admin.pexo.ai DevTools → Network → Authorization header."
        })

    entry_path = os.path.join(dashboard_dir, entry_file)
    if not os.path.exists(entry_path):
        return json.dumps({"error": f"Entry file not found: {entry_path}"})

    script = str(SCRIPTS_DIR / "upload-package.sh")
    env = os.environ.copy()
    env["PEXO_ADMIN_TOKEN"] = token

    cmd = [
        "bash", script,
        conversation_id, dashboard_dir,
        "--entry", entry_file,
    ]
    if description:
        cmd += ["--desc", description]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)

    output = result.stdout.strip()

    if result.returncode == 0:
        pkg_id = ""
        preview = ""
        for line in output.split("\n"):
            if "Package ID:" in line:
                pkg_id = line.split(":")[-1].strip()
            if "Preview:" in line:
                preview = line.split("Preview:")[-1].strip()

        return json.dumps({
            "status": "ok",
            "package_id": pkg_id,
            "preview_url": preview,
            "dashboard_url": "https://admin.pexo.ai/ai-workshop/strategy-optimizer",
            "output": output,
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "error",
            "output": output,
            "error": result.stderr.strip(),
        })


@server.tool()
async def list_cases(output_dir: Optional[str] = None) -> str:
    """List all analyzed cases with their current status.

    Scans the case data directory and reports which cases have traces,
    media assets, and dashboards.

    Args:
        output_dir: Base output directory (default: "analysis/langfuse-data").

    Returns:
        JSON array of case summaries with trace/media/dashboard counts.
    """
    out_dir = output_dir or DEFAULT_OUTPUT_DIR
    cases_dir = os.path.join(out_dir, "cases")

    if not os.path.isdir(cases_dir):
        return json.dumps({"error": f"No cases directory: {cases_dir}"})

    cases = []
    for d in sorted(os.listdir(cases_dir)):
        case_path = os.path.join(cases_dir, d)
        if not os.path.isdir(case_path):
            continue

        traces = list(Path(case_path).glob("trace-*.json"))
        media_dir = os.path.join(case_path, "media")
        media_count = len(os.listdir(media_dir)) if os.path.isdir(media_dir) else 0

        html_files = list(Path(case_path).glob("*.html"))
        html_name = html_files[0].name if html_files else None

        cases.append({
            "case_id": d,
            "trace_count": len(traces),
            "media_count": media_count,
            "dashboard": html_name,
            "has_assets_json": os.path.exists(os.path.join(case_path, "assets.json")),
        })

    return json.dumps(cases, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    server.run(transport="stdio")
