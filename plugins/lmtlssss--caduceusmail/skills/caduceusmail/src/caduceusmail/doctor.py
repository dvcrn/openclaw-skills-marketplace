from __future__ import annotations

import argparse
import json
import os
import platform as platform_mod
import shutil
import sys
from pathlib import Path
from typing import Any

from .version import __version__

CREDENTIALS_HEADER = "CADUCEUSMAIL_CREDENTIALS_V1"
ALLOWED_KEYS = {
    "ENTRA_TENANT_ID",
    "ENTRA_CLIENT_ID",
    "ENTRA_CLIENT_SECRET",
    "EXCHANGE_ORGANIZATION",
    "EXCHANGE_DEFAULT_MAILBOX",
    "ORGANIZATION_DOMAIN",
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ZONE_ID",
    "CF_API_TOKEN",
    "CF_ZONE_ID",
}


def resolve_base_dir(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def resolve_bootstrap_auth_mode(env: dict[str, str] | None = None, platform_name: str | None = None) -> tuple[str, str]:
    env = dict(env or os.environ)
    platform_name = platform_name or sys.platform

    for key in ("SSH_TTY", "SSH_CONNECTION", "SSH_CLIENT"):
        if env.get(key):
            return "device", f"ssh:{key.lower()}"

    for key in ("OPENCLAW_SANDBOX", "CONTAINER", "DOCKER_CONTAINER"):
        if env.get(key):
            return "device", f"sandbox:{key.lower()}"

    if env.get("CI", "").lower() == "true":
        return "device", "ci"

    if platform_name != "win32":
        if not env.get("DISPLAY") and not env.get("WAYLAND_DISPLAY"):
            return "device", "headless-no-display"

    return "browser", "interactive-default"


def parse_credentials_file(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    header_seen = False
    keys: list[str] = []
    errors: list[str] = []
    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        if not header_seen:
            if line != CREDENTIALS_HEADER:
                errors.append(f"{path.name}:{idx}: first non empty line must be {CREDENTIALS_HEADER}")
            header_seen = True
            continue
        if line.startswith("#"):
            continue
        if "=" not in line:
            errors.append(f"{path.name}:{idx}: expected KEY=VALUE")
            continue
        key, _value = line.split("=", 1)
        key = key.strip()
        if key not in ALLOWED_KEYS:
            errors.append(f"{path.name}:{idx}: unsupported key {key}")
            continue
        keys.append(key)
    if not header_seen:
        errors.append(f"{path.name}: missing {CREDENTIALS_HEADER}")
    return {
        "path": str(path),
        "exists": path.exists(),
        "keys": sorted(set(keys)),
        "errors": errors,
        "ok": path.exists() and not errors,
    }


def read_skill_frontmatter(skill_path: Path) -> dict[str, Any]:
    if not skill_path.exists():
        return {"exists": False, "ok": False, "error": "missing SKILL.md"}
    text = skill_path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        return {"exists": True, "ok": False, "error": "frontmatter missing"}
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return {"exists": True, "ok": False, "error": "frontmatter terminator missing"}
    frontmatter = parts[0].splitlines()[1:]
    metadata_line = next((line for line in frontmatter if line.startswith("metadata:")), "")
    metadata_is_single_line = metadata_line.startswith("metadata: {") and metadata_line.rstrip().endswith("}")
    return {
        "exists": True,
        "ok": bool(metadata_line) and metadata_is_single_line,
        "metadata_line": metadata_line,
        "metadata_is_single_line_json": metadata_is_single_line,
    }


def doctor(base_dir: str | None = None, credentials_dir: str | None = None, env_file: str | None = None) -> dict[str, Any]:
    root = resolve_base_dir(base_dir)
    creds_dir = Path(credentials_dir).expanduser().resolve() if credentials_dir else root / "credentials"
    env_path = Path(env_file).expanduser().resolve() if env_file else (Path.home() / ".caduceusmail" / ".env")

    commands = {name: shutil.which(name) for name in ("bash", "python3", "jq", "pwsh")}
    skill = read_skill_frontmatter(root / "SKILL.md")
    auth_mode, auth_reason = resolve_bootstrap_auth_mode()

    files = {
        "entra": parse_credentials_file(creds_dir / "entra.txt") if (creds_dir / "entra.txt").exists() else {"path": str(creds_dir / "entra.txt"), "exists": False, "keys": [], "errors": [], "ok": False},
        "cloudflare": parse_credentials_file(creds_dir / "cloudflare.txt") if (creds_dir / "cloudflare.txt").exists() else {"path": str(creds_dir / "cloudflare.txt"), "exists": False, "keys": [], "errors": [], "ok": False},
    }
    loaded_keys = set(files["entra"].get("keys", [])) | set(files["cloudflare"].get("keys", []))
    loaded_keys |= {key for key, value in os.environ.items() if key in ALLOWED_KEYS and value}

    required_runtime = ["ENTRA_TENANT_ID", "ENTRA_CLIENT_ID", "EXCHANGE_DEFAULT_MAILBOX"]
    missing_runtime = [key for key in required_runtime if key not in loaded_keys]
    headless_keys = ["ENTRA_TENANT_ID", "ENTRA_CLIENT_ID", "ENTRA_CLIENT_SECRET", "EXCHANGE_DEFAULT_MAILBOX"]
    headless_missing = [key for key in headless_keys if key not in loaded_keys and not os.environ.get(key)]

    recommendations: list[str] = []
    if auth_mode == "device":
        recommendations.append("First bootstrap should use --bootstrap-auth-mode device.")
    if headless_missing:
        recommendations.append("Headless steady state is not ready. Add ENTRA_CLIENT_SECRET and any missing runtime keys.")
    if not commands.get("pwsh"):
        recommendations.append("PowerShell is absent. Use --simulate-bootstrap for CI or install pwsh for live bootstrap.")
    if not skill.get("ok"):
        recommendations.append("Fix SKILL.md metadata before publishing to ClawHub.")

    ok = all(commands[name] for name in ("bash", "python3", "jq")) and skill.get("ok", False) and not missing_runtime

    return {
        "ok": ok,
        "version": __version__,
        "paths": {
            "base_dir": str(root),
            "credentials_dir": str(creds_dir),
            "env_file": str(env_path),
            "skill": str(root / "SKILL.md"),
        },
        "commands": commands,
        "credentials": {
            "files": files,
            "loaded_keys": sorted(loaded_keys),
            "runtime_required_missing": missing_runtime,
            "headless_required_missing": headless_missing,
            "headless_ready": not headless_missing,
            "bootstrap_required": bool(missing_runtime or headless_missing),
        },
        "auth": {
            "recommended": auth_mode,
            "reason": auth_reason,
        },
        "skill": skill,
        "recommendations": recommendations,
        "platform": {
            "system": platform_mod.system(),
            "release": platform_mod.release(),
            "machine": platform_mod.machine(),
            "python": sys.version.split()[0],
        },
    }


def render_human(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"☤CaduceusMail doctor {report['version']}")
    lines.append(f"ok: {str(report['ok']).lower()}")
    lines.append(f"recommended bootstrap auth: {report['auth']['recommended']} ({report['auth']['reason']})")
    lines.append("commands:")
    for key, value in report["commands"].items():
        lines.append(f"  {key}: {value or 'missing'}")
    lines.append("missing runtime keys: " + (", ".join(report["credentials"]["runtime_required_missing"]) or "none"))
    lines.append("missing headless keys: " + (", ".join(report["credentials"]["headless_required_missing"]) or "none"))
    lines.append(f"skill frontmatter single line metadata: {str(report['skill'].get('metadata_is_single_line_json', False)).lower()}")
    if report["recommendations"]:
        lines.append("recommendations:")
        for item in report["recommendations"]:
            lines.append(f"  - {item}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="☤CaduceusMail readiness doctor")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--base-dir", default="")
    parser.add_argument("--credentials-dir", default="")
    parser.add_argument("--env-file", default="")
    args = parser.parse_args(argv)

    report = doctor(
        base_dir=args.base_dir or None,
        credentials_dir=args.credentials_dir or None,
        env_file=args.env_file or None,
    )
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_human(report))
    if args.strict and not report["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
