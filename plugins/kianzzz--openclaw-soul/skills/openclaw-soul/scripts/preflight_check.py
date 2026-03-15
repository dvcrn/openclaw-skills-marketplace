#!/usr/bin/env python3
"""
openclaw-soul preflight check v1.1
Validates environment before deploying the self-evolution framework.
Exit 0 = all clear, Exit 1 = blocking issues found.
Output: JSON report.
"""

import json
import os
import shutil
import sys

WORKSPACE_FILES = [
    "AGENTS.md",
    "SOUL.md",
    "HEARTBEAT.md",
    "BOOTSTRAP.md",
    "GOALS.md",
    "USER.md",
    "IDENTITY.md",
    "working-memory.md",
    "long-term-memory.md",
]

REQUIRED_DIRS = [
    "memory",
    "memory/daily",
    "memory/entities",
    "memory/experiences",
    "memory/significant",
    "memory/reflections",
    "memory/proposals",
    "memory/pipeline",
    "soul-revisions",
]

DEPENDENCY_SKILLS = ["evoclaw", "self-improving"]


def get_workspace_path():
    """Resolve workspace path from env or default."""
    env_path = os.environ.get("OPENCLAW_WORKSPACE")
    if env_path and os.path.isdir(env_path):
        return env_path
    default = os.path.expanduser("~/.openclaw/workspace")
    if os.path.isdir(default):
        return default
    return None


def check_workspace(workspace):
    """Check workspace directory exists."""
    if workspace and os.path.isdir(workspace):
        return {"status": "pass", "path": workspace}
    return {
        "status": "fail",
        "error": "Workspace directory not found. Set OPENCLAW_WORKSPACE or ensure ~/.openclaw/workspace/ exists.",
    }


def check_config(workspace):
    """Check openclaw.json exists and is valid JSON."""
    if not workspace:
        return {"status": "skip", "reason": "no workspace"}
    config_path = os.path.join(os.path.dirname(workspace.rstrip("/")), "openclaw.json")
    alt_path = os.path.join(workspace, "..", "openclaw.json")
    for p in [config_path, os.path.normpath(alt_path)]:
        if os.path.isfile(p):
            try:
                with open(p, "r") as f:
                    json.load(f)
                return {"status": "pass", "path": p}
            except json.JSONDecodeError as e:
                return {"status": "fail", "path": p, "error": f"Invalid JSON: {e}"}
    return {
        "status": "warn",
        "error": "openclaw.json not found. Heartbeat config will need manual setup.",
    }


def check_clawhub():
    """Check clawhub CLI availability."""
    path = shutil.which("clawhub")
    if path:
        return {"status": "pass", "path": path}
    for loc in ["~/.openclaw/bin/clawhub", "/usr/local/bin/clawhub"]:
        expanded = os.path.expanduser(loc)
        if os.path.isfile(expanded) and os.access(expanded, os.X_OK):
            return {"status": "pass", "path": expanded}
    return {
        "status": "warn",
        "error": "clawhub CLI not in PATH. Dependency skills will need manual installation.",
    }


def check_existing_files(workspace):
    """List workspace files that already exist (need backup)."""
    if not workspace:
        return {"status": "skip", "reason": "no workspace"}
    existing = []
    for f in WORKSPACE_FILES:
        path = os.path.join(workspace, f)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            existing.append({"file": f, "size": size})
    return {
        "status": "info",
        "existing_files": existing,
        "count": len(existing),
        "needs_backup": len(existing) > 0,
    }


def check_existing_dirs(workspace):
    """Check which required directories already exist."""
    if not workspace:
        return {"status": "skip", "reason": "no workspace"}
    existing = []
    missing = []
    for d in REQUIRED_DIRS:
        path = os.path.join(workspace, d)
        if os.path.isdir(path):
            existing.append(d)
        else:
            missing.append(d)
    return {
        "status": "info",
        "existing": existing,
        "missing": missing,
    }


def check_installed_skills(workspace):
    """Check if dependency skills are already installed."""
    if not workspace:
        return {"status": "skip", "reason": "no workspace"}
    skills_dir = os.path.join(workspace, "skills")
    installed = {}
    for skill in DEPENDENCY_SKILLS:
        skill_path = os.path.join(skills_dir, skill, "SKILL.md")
        installed[skill] = os.path.isfile(skill_path)
    return {"status": "info", "skills": installed}


def main():
    report = {"checks": {}, "blocking": False, "version": "1.1.0"}

    workspace = get_workspace_path()

    # 1. Workspace
    ws_result = check_workspace(workspace)
    report["checks"]["workspace"] = ws_result
    if ws_result["status"] == "fail":
        report["blocking"] = True

    # 2. Config
    report["checks"]["config"] = check_config(workspace)

    # 3. clawhub CLI
    report["checks"]["clawhub"] = check_clawhub()

    # 4. Existing files
    report["checks"]["existing_files"] = check_existing_files(workspace)

    # 5. Existing directories
    report["checks"]["existing_dirs"] = check_existing_dirs(workspace)

    # 6. Installed skills
    report["checks"]["installed_skills"] = check_installed_skills(workspace)

    # Summary
    report["workspace_path"] = workspace
    report["ready"] = not report["blocking"]

    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(1 if report["blocking"] else 0)


if __name__ == "__main__":
    main()
