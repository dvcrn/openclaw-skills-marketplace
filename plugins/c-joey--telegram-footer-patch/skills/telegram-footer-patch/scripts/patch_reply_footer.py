#!/usr/bin/env python3
"""Patch OpenClaw dist JS bundles to append a Telegram private-chat footer.

Safety notes:
- This script modifies files under the OpenClaw installation directory.
- Always run with --dry-run first to see which files would be touched.
- The script creates timestamped backups (*.bak.telegram-footer.*) before writing.
- If anything fails, it restores from backup automatically.
"""

import argparse
import datetime as dt
import glob
import os
import pathlib
import re
import shutil
import subprocess
import sys

# Avoid generating __pycache__/*.pyc in the skill folder.
sys.dont_write_bytecode = True

MARKER_START = "/* OPENCLAW_TELEGRAM_STATUS_FOOTER_START */"
MARKER_END = "/* OPENCLAW_TELEGRAM_STATUS_FOOTER_END */"

SNIPPET = f'''
{MARKER_START}
const __ocSessionLooksTelegramDirect =
  typeof sessionKey === "string" && sessionKey.includes(":telegram:direct:");
const __ocShouldAppendStatusFooter =
  (__ocSessionLooksTelegramDirect || activeSessionEntry?.lastChannel === "telegram" || activeSessionEntry?.channel === "telegram") &&
  activeSessionEntry?.chatType !== "group" &&
  activeSessionEntry?.chatType !== "channel";

if (__ocShouldAppendStatusFooter) {{
  const __ocTotalTokens = resolveFreshSessionTotalTokens(activeSessionEntry);
  const __ocThinkingLevel = activeSessionEntry?.thinkingLevel || "default";

  const __ocStatusFooter = [
    `🧠 ${{providerUsed && modelUsed ? `${{providerUsed}}/${{modelUsed}}` : modelUsed || "unknown"}}`,
    `💭 Think: ${{__ocThinkingLevel}}`,
    `📊 ${{formatTokens(
      typeof __ocTotalTokens === "number" && Number.isFinite(__ocTotalTokens) && __ocTotalTokens > 0
        ? __ocTotalTokens
        : null,
      contextTokensUsed ?? activeSessionEntry?.contextTokens ?? null
    )}}`
  ].join(" " );

  finalPayloads = appendUsageLine(finalPayloads, `\n──────────\n${{__ocStatusFooter}}`);
}}
{MARKER_END}
'''.strip("\n")

PATTERN = re.compile(
    r"(if\s*\(\s*responseUsageLine\s*\)\s*finalPayloads\s*=\s*appendUsageLine\(\s*finalPayloads\s*,\s*responseUsageLine\s*\);)",
    flags=re.M,
)
MARKER_BLOCK_RE = re.compile(
    re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
    flags=re.S,
)
TARGET_GLOBS = ["reply-*.js", "compact-*.js", "pi-embedded-*.js"]
LEGACY_BLOCK_RE = re.compile(
    r"\n?\s*const shouldAppendStatusFooter = activeSessionEntry\?\.chatType !== \"group\" && activeSessionEntry\?\.chatType !== \"channel\" && \(activeSessionEntry\?\.lastChannel === \"telegram\" \|\| activeSessionEntry\?\.channel === \"telegram\"\);\s*"
    r"if \(shouldAppendStatusFooter\) \{\s*"
    r"const totalTokens = resolveFreshSessionTotalTokens\(activeSessionEntry\);\s*"
    r"const statusFooter = \[\s*"
    r"`🧠 Model: \$\{providerUsed && modelUsed \? `\$\{providerUsed\}/\$\{modelUsed\}` : modelUsed \|\| \"unknown\"\}`\s*,\s*"
    r"`📊 Context: \$\{formatTokens\(typeof totalTokens === \"number\" && Number\.isFinite\(totalTokens\) && totalTokens > 0 \? totalTokens : null, contextTokensUsed \?\? activeSessionEntry\?\.contextTokens \?\? null\)\}`\s*"
    r"\]\.join\(\"  \"\);\s*"
    r"finalPayloads = appendUsageLine\(finalPayloads, statusFooter\);\s*"
    r"\}\s*",
    flags=re.S,
)


def verify_node_syntax(path: pathlib.Path):
    result = subprocess.run(
        ["node", "--check", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "node --check failed").strip()
        raise RuntimeError(details)


def iter_target_files(dist: pathlib.Path) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for pattern in TARGET_GLOBS:
        files.extend(sorted(dist.glob(pattern)))
    seen: set[str] = set()
    unique: list[pathlib.Path] = []
    for fp in files:
        key = str(fp)
        if key in seen:
            continue
        seen.add(key)
        unique.append(fp)
    return unique


def patch_file(path: pathlib.Path, dry_run: bool):
    content = path.read_text(encoding="utf-8")
    has_marker = MARKER_START in content
    has_pattern = PATTERN.search(content) is not None
    has_legacy = LEGACY_BLOCK_RE.search(content) is not None
    backups = sorted(glob.glob(str(path) + ".bak.telegram-footer.*"))

    is_candidate = has_marker or has_pattern or has_legacy
    if not is_candidate:
        print(f"[skip] non-target dist bundle: {path}")
        return {"status": "skip", "candidate": False, "changed": False}

    if (not has_marker) and backups:
        print(
            f"[info] marker missing but backups exist ({len(backups)}): likely overwritten by upgrade, reapplying: {path}"
        )

    updated = content
    legacy_removed = 0
    if has_legacy:
        updated, legacy_removed = LEGACY_BLOCK_RE.subn("\n", updated)

    if MARKER_START in updated:
        updated, count = MARKER_BLOCK_RE.subn(SNIPPET, updated, count=1)
        if count == 0:
            print(f"[err] marker block found but could not be replaced: {path}", file=sys.stderr)
            return {"status": "error", "candidate": True, "changed": False}
        action = "update patch"
    else:
        match = PATTERN.search(updated)
        if not match:
            print(
                f"[err] insertion needle not found in candidate dist bundle: {path} (upstream dist likely changed; rework patch)",
                file=sys.stderr,
            )
            return {"status": "error", "candidate": True, "changed": False}
        replacement = match.group(1) + "\n\n" + SNIPPET
        updated = updated[: match.start()] + replacement + updated[match.end() :]
        action = "patch"

    changed = updated != content
    if not changed:
        print(f"[skip] already up to date: {path}")
        return {"status": "ok", "candidate": True, "changed": False}

    if dry_run:
        extra = f" (legacy cleaned: {legacy_removed})" if legacy_removed else ""
        print(f"[dry-run] would {action}: {path}{extra}")
        return {"status": "ok", "candidate": True, "changed": True}

    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_suffix(path.suffix + f".bak.telegram-footer.{ts}")
    shutil.copy2(path, backup)
    try:
        path.write_text(updated, encoding="utf-8")
        verify_node_syntax(path)
    except Exception as exc:
        shutil.copy2(backup, path)
        print(f"[err] patch failed, restored backup: {path}", file=sys.stderr)
        print(f"[err] reason: {exc}", file=sys.stderr)
        return {"status": "error", "candidate": True, "changed": False}

    extra = f" (legacy cleaned: {legacy_removed})" if legacy_removed else ""
    print(f"[ok] {action}ed: {path}{extra}")
    print(f"[ok] backup      : {backup}")
    print(f"[ok] syntax check: node --check passed")
    return {"status": "ok", "candidate": True, "changed": True}


def preflight(dist: pathlib.Path, dry_run: bool) -> int:
    print("[warn] This tool patches OpenClaw installation files (dist JS bundles).")
    print("[warn] Recommended: run --dry-run first and review the candidate files.")
    node_path = shutil.which("node")
    if not node_path:
        print("[err] node not found in PATH (required for syntax validation via node --check)", file=sys.stderr)
        return 2
    if not dist.exists() or not dist.is_dir():
        print(f"[err] dist directory not found: {dist}", file=sys.stderr)
        return 2
    if not dry_run:
        # When applying, ensure we can write to the install directory.
        if not os.access(dist, os.W_OK):
            print(
                f"[err] no write permission for dist directory: {dist} (try sudo or adjust permissions)",
                file=sys.stderr,
            )
            return 2
    else:
        if not os.access(dist, os.R_OK):
            print(f"[err] no read permission for dist directory: {dist}", file=sys.stderr)
            return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch OpenClaw dist files to append Telegram status footer.")
    parser.add_argument("--dist", default="/usr/lib/node_modules/openclaw/dist", help="OpenClaw dist directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, do not write")
    args = parser.parse_args()

    dist = pathlib.Path(args.dist)
    rc = preflight(dist, dry_run=args.dry_run)
    if rc != 0:
        return rc

    files = iter_target_files(dist)
    if not files:
        print("[err] no target dist files found", file=sys.stderr)
        return 2

    changed = 0
    candidate_count = 0
    errors = 0
    for fp in files:
        result = patch_file(fp, dry_run=args.dry_run)
        if result["candidate"]:
            candidate_count += 1
        if result["changed"]:
            changed += 1
        if result["status"] == "error":
            errors += 1

    if candidate_count == 0:
        print(
            "[err] no patchable dist bundle found; marker and insertion needle were absent in all target files. OpenClaw dist likely changed.",
            file=sys.stderr,
        )
        return 3

    if errors > 0:
        print(f"[done] encountered errors: {errors}", file=sys.stderr)
        return 1

    if changed == 0:
        print("[done] no files changed")
    else:
        print(f"[done] changed files: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
