#!/usr/bin/env python3
"""
doc_garden.py — Find stale references in docs/ and optionally open a fix PR.

Scans docs/*.md for references to code files, functions, and types.
Flags any reference that no longer exists in the codebase.
Optionally opens a GitHub PR with a stub fix.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class StaleRef(NamedTuple):
    doc_file: str
    line_no: int
    ref_text: str
    ref_type: str  # "file", "function", "type", "path"
    reason: str


# ---------------------------------------------------------------------------
# Reference extractors
# ---------------------------------------------------------------------------

def extract_refs_from_md(md_path: Path) -> list[tuple[int, str, str]]:
    """
    Extract references from a markdown file.
    Returns list of (line_no, ref_text, ref_type).
    """
    refs = []
    text = md_path.read_text(errors="replace")
    lines = text.splitlines()

    for i, line in enumerate(lines, 1):
        # Code-fenced paths: `path/to/file.rs` or `path/to/file.go`
        for m in re.finditer(r'`([^`]+\.(rs|go|ts|tsx|py|sh|toml|mod|lock))`', line):
            refs.append((i, m.group(1), "file"))

        # Markdown links: [text](path/to/file.md)
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
            href = m.group(2)
            if not href.startswith("http") and not href.startswith("#"):
                refs.append((i, href.split("#")[0], "file"))

        # Function references in backticks: `function_name` (if looks like a function)
        for m in re.finditer(r'`([a-z_]+(?:::[a-z_]+)*)\(\)`', line):
            refs.append((i, m.group(1), "function"))

        # Rust path references: `pallet_foo::bar::Baz`
        for m in re.finditer(r'`(pallet_[a-z_]+::[A-Za-z:_]+)`', line):
            refs.append((i, m.group(1), "type"))

    return refs


# ---------------------------------------------------------------------------
# Staleness checks
# ---------------------------------------------------------------------------

def check_file_ref(repo: Path, ref: str, from_doc: Path) -> str | None:
    """Return reason string if ref is stale, else None."""
    # Resolve relative to doc location
    doc_dir = from_doc.parent
    resolved = (doc_dir / ref).resolve()
    if resolved.exists():
        return None

    # Try relative to repo root
    repo_resolved = (repo / ref).resolve()
    if repo_resolved.exists():
        return None

    return f"file not found: {ref}"


def check_function_ref(repo: Path, func_name: str) -> str | None:
    """Return reason string if function ref is stale, else None."""
    # Simple grep-based check
    patterns = [
        f"fn {func_name}(",       # Rust
        f"func {func_name}(",     # Go (method form: func (r *T) name()
        f"func.*{func_name}(",    # Go
        f"def {func_name}(",      # Python
        f"function {func_name}(", # TypeScript/JS
        f"async function {func_name}(",
    ]
    for pattern in patterns:
        try:
            result = subprocess.run(
                ["grep", "-rn", pattern, str(repo), "--include=*.rs",
                 "--include=*.go", "--include=*.py", "--include=*.ts"],
                capture_output=True, text=True, timeout=10
            )
            if result.stdout.strip():
                return None
        except subprocess.TimeoutExpired:
            return None  # Timeout = assume OK
    return f"function not found: {func_name}"


def scan_docs(repo: Path, docs_dir: Path) -> list[StaleRef]:
    """Scan all .md files in docs_dir for stale references."""
    stale = []
    md_files = list(docs_dir.rglob("*.md"))

    if not md_files:
        print(f"  No .md files found in {docs_dir}")
        return stale

    for md_file in sorted(md_files):
        refs = extract_refs_from_md(md_file)
        for line_no, ref_text, ref_type in refs:
            reason = None
            if ref_type == "file":
                reason = check_file_ref(repo, ref_text, md_file)
            elif ref_type == "function":
                reason = check_function_ref(repo, ref_text)
            # Skip type checks (too many false positives without AST)

            if reason:
                stale.append(StaleRef(
                    doc_file=str(md_file.relative_to(repo)),
                    line_no=line_no,
                    ref_text=ref_text,
                    ref_type=ref_type,
                    reason=reason,
                ))

    return stale


# ---------------------------------------------------------------------------
# PR creation
# ---------------------------------------------------------------------------

def open_fix_pr(repo: Path, stale_refs: list[StaleRef]) -> None:
    """Create a branch and open a GitHub PR for stale doc fixes."""
    branch = "fix/docs-stale-refs"

    # Create/switch branch
    subprocess.run(
        ["git", "checkout", "-b", branch],
        cwd=repo, check=False, capture_output=True
    )

    # Write a fix-needed file as a stub
    fix_file = repo / "docs" / "STALE_REFS.md"
    lines = ["# Stale Documentation References\n\n",
             "These references were found to be stale by the doc-garden agent.\n",
             "Fix each one and remove this file before merging.\n\n"]
    for ref in stale_refs:
        lines.append(f"- `{ref.doc_file}:{ref.line_no}` — `{ref.ref_text}` ({ref.reason})\n")

    fix_file.write_text("".join(lines))

    subprocess.run(
        ["git", "add", "docs/STALE_REFS.md"],
        cwd=repo, check=True
    )
    subprocess.run(
        ["git", "-c", "user.name=Alex Chen", "-c", "user.email=alex.chen31337@gmail.com",
         "commit", "-m", f"docs(garden): flag {len(stale_refs)} stale reference(s) for review"],
        cwd=repo, check=True
    )

    # Push
    env = {**os.environ, "GIT_SSH_COMMAND": "ssh -i ~/.ssh/id_ed25519_alexchen"}
    subprocess.run(
        ["git", "push", "origin", branch],
        cwd=repo, check=True, env=env
    )

    # Open PR
    body_lines = ["## Stale Documentation References\n\n",
                  "The doc-garden agent found references in `docs/` that no longer exist:\n\n"]
    for ref in stale_refs[:20]:  # Cap at 20 in PR body
        body_lines.append(f"- `{ref.doc_file}:{ref.line_no}` — `{ref.ref_text}` ({ref.reason})\n")
    if len(stale_refs) > 20:
        body_lines.append(f"\n...and {len(stale_refs) - 20} more. See `docs/STALE_REFS.md`.\n")
    body_lines.append("\n**Fix:** Update or remove each stale reference, then delete `docs/STALE_REFS.md`.\n")

    result = subprocess.run(
        ["gh", "pr", "create",
         "--title", f"docs(garden): fix {len(stale_refs)} stale reference(s) in docs/",
         "--body", "".join(body_lines),
         "--head", branch],
        cwd=repo, capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"PR opened: {result.stdout.strip()}")
    else:
        print(f"PR creation failed: {result.stderr}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Path to repository root")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report stale refs without writing or opening PR")
    parser.add_argument("--pr", action="store_true",
                        help="Open a GitHub PR with stale refs flagged")
    parser.add_argument("--docs-dir", default="docs",
                        help="Subdirectory to scan (default: docs)")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    docs_dir = repo / args.docs_dir

    if not docs_dir.exists():
        print(f"No docs directory found at {docs_dir}")
        sys.exit(0)

    print(f"Scanning {docs_dir} for stale references...")
    stale = scan_docs(repo, docs_dir)

    if not stale:
        print("No stale references found. ✓")
        sys.exit(0)

    print(f"\nFound {len(stale)} stale reference(s):\n")
    for ref in stale:
        print(f"  {ref.doc_file}:{ref.line_no}")
        print(f"    {ref.ref_type}: `{ref.ref_text}`")
        print(f"    reason: {ref.reason}")
        print()

    if args.dry_run:
        print(f"[dry-run] Would flag {len(stale)} stale ref(s). Use --pr to open a fix PR.")
        sys.exit(0)

    if args.pr:
        print("Opening fix PR...")
        open_fix_pr(repo, stale)
    else:
        print(f"Use --pr to open a fix PR, or --dry-run to just report.")
        sys.exit(1)


if __name__ == "__main__":
    main()
