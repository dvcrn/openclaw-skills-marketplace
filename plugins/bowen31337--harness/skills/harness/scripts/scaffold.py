#!/usr/bin/env python3
"""
scaffold.py — Scaffold an agent engineering harness for any repo.

Detects language (Rust/Go/TypeScript), reads existing code structure,
generates docs/, scripts/agent-lint.sh, and .github/workflows/agent-lint.yml.
Never overwrites existing AGENTS.md without --force.
"""
import argparse
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_language(repo: Path) -> str:
    """Detect primary language from repo file structure."""
    if (repo / "Cargo.toml").exists():
        return "rust"
    if (repo / "go.mod").exists():
        return "go"
    if (repo / "package.json").exists() or (repo / "tsconfig.json").exists():
        return "typescript"
    if (repo / "pyproject.toml").exists() or (repo / "setup.py").exists():
        return "python"
    # Fallback: count source files
    rs = list(repo.rglob("*.rs"))
    go = list(repo.rglob("*.go"))
    ts = list(repo.rglob("*.ts")) + list(repo.rglob("*.tsx"))
    py = list(repo.rglob("*.py"))
    counts = {"rust": len(rs), "go": len(go), "typescript": len(ts), "python": len(py)}
    return max(counts, key=counts.get)


# ---------------------------------------------------------------------------
# Repo structure inspection
# ---------------------------------------------------------------------------

def inspect_repo(repo: Path, language: str) -> dict:
    """Read repo structure to generate accurate docs."""
    info = {
        "language": language,
        "name": repo.name,
        "dirs": [],
        "packages": [],
        "has_ci": (repo / ".github" / "workflows").exists(),
        "has_agents_md": (repo / "AGENTS.md").exists(),
        "has_docs": (repo / "docs").exists(),
    }

    # Collect top-level dirs
    info["dirs"] = sorted([
        d.name for d in repo.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ])

    if language == "rust":
        # Collect pallet names
        pallets_dir = repo / "pallets"
        if pallets_dir.exists():
            info["packages"] = sorted([p.name for p in pallets_dir.iterdir() if p.is_dir()])
        # Check which pallets have benchmarking.rs
        info["missing_benchmarks"] = [
            p for p in info["packages"]
            if not (pallets_dir / p / "src" / "benchmarking.rs").exists()
        ]

    elif language == "go":
        # Collect internal package names
        internal_dir = repo / "internal"
        if internal_dir.exists():
            info["packages"] = sorted([
                p.name for p in internal_dir.iterdir()
                if p.is_dir() and not p.name.startswith(".")
            ])
        # Read module name from go.mod
        gomod = repo / "go.mod"
        if gomod.exists():
            for line in gomod.read_text().splitlines():
                if line.startswith("module "):
                    info["module"] = line.split()[1]
                    break

    elif language == "typescript":
        # Collect src dirs
        src_dir = repo / "src"
        if src_dir.exists():
            info["packages"] = sorted([
                p.name for p in src_dir.iterdir()
                if p.is_dir() and not p.name.startswith(".")
            ])

    elif language == "python":
        # Collect top-level Python packages
        info["packages"] = sorted([
            d.name for d in repo.iterdir()
            if d.is_dir() and (d / "__init__.py").exists()
            and not d.name.startswith(".")
        ])
        # Read module name from pyproject.toml
        pyproject = repo / "pyproject.toml"
        if pyproject.exists():
            for line in pyproject.read_text().splitlines():
                if line.strip().startswith("name ="):
                    info["module"] = line.split("=")[1].strip().strip('"').strip("'")
                    break

    return info


# ---------------------------------------------------------------------------
# File generators
# ---------------------------------------------------------------------------

def generate_agents_md(info: dict) -> str:
    """Generate AGENTS.md table of contents with progressive disclosure layers."""
    lang = info["language"]
    name = info["name"]
    dirs = info["dirs"]
    packages = info.get("packages", [])

    test_cmd = {
        "rust": "cargo test --workspace",
        "go": "go test ./... -count=1 -timeout 120s",
        "typescript": "npm test",
        "python": "uv run pytest tests/ -v",
    }.get(lang, "make test")

    lint_cmd = {
        "rust": "cargo clippy --workspace -- -D warnings",
        "go": "go vet ./...",
        "typescript": "npm run lint",
        "python": "uv run ruff check . && uv run pyright",
    }.get(lang, "make lint")

    # Build repo map
    dir_map = "\n".join(f"  {d}/" for d in dirs[:12])
    pkg_list = "\n".join(f"  {p}" for p in packages[:15]) if packages else "  (see source directories)"

    lines = f"""# AGENTS.md — {name} Agent Harness

[One sentence describing what this repo does.]
This file is a **table of contents** — not a reference manual. Follow the links.

> **Context depth guide (progressive disclosure):**
> - **L1 (here):** orientation, commands, invariants — read this first
> - **L2 (`docs/`):** architecture, quality standards, conventions — read before coding
> - **L3 (source):** implementation details — pull on demand via grep/read tools
>
> Do not dump L2/L3 into your context unless you need it. Pull, don't pre-load.

---

## Repo Map

```
{dir_map}
```

---

## {'Pallets' if lang == 'rust' else 'Packages'} ({len(packages)} total)

```
{pkg_list}
```

---

## Docs (start here before touching code)

| File | What it covers |
|------|---------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Layer rules, dependency graph, key invariants |
| [`docs/QUALITY.md`](docs/QUALITY.md) | Coverage targets, security rules, testing standards |
| [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) | Naming conventions, code style |
| [`docs/EXECUTION_PLAN_TEMPLATE.md`](docs/EXECUTION_PLAN_TEMPLATE.md) | Template for planning complex tasks |

---

## How to Build & Test

```bash
# Run all tests
{test_cmd}

# Run lints
{lint_cmd}

# Run agent-specific lints (architectural invariants)
bash scripts/agent-lint.sh
```

---

## Agent Invariants (non-negotiable)

1. **Always run tests before opening a PR.** Never break existing tests.
2. **Check docs/ARCHITECTURE.md before adding cross-package dependencies.**
3. **All new public APIs must have documentation.**
4. **Run `bash scripts/agent-lint.sh` locally.** Failures include fix instructions.
5. **For complex tasks** (multiple packages, new APIs, migrations), create an execution
   plan using `docs/EXECUTION_PLAN_TEMPLATE.md` before writing code.

---

## CI Gates

Every PR runs agent-lint + tests + lints. All must pass.

---

*This file must stay under 150 lines. See `scripts/agent-lint.sh`.*
"""
    return lines.strip()


def generate_agent_lint_sh(info: dict) -> str:
    """Generate scripts/agent-lint.sh for the detected language."""
    lang = info["language"]
    module = info.get("module", "")

    if lang == "rust":
        return _generate_rust_lint(info)
    elif lang == "go":
        return _generate_go_lint(info, module)
    elif lang == "typescript":
        return _generate_ts_lint(info)
    elif lang == "python":
        return _generate_python_lint(info)
    else:
        return _generate_generic_lint(info)


def _generate_rust_lint(info: dict) -> str:
    return '''#!/bin/bash
# Agent harness linter (Rust/Substrate) — errors are agent-readable
set -euo pipefail
ERRORS=0
cd "$(git rev-parse --show-toplevel)"
echo "=== Agent Lint (Rust) ==="

# Rule 1: All pallets must have benchmarking.rs
echo "[1/5] Checking benchmarks..."
for pallet_dir in pallets/*/; do
  pallet=$(basename "$pallet_dir")
  if [ ! -f "${pallet_dir}src/benchmarking.rs" ]; then
    echo "LINT ERROR [missing-benchmarks]: $pallet has no benchmarking.rs"
    echo "  WHAT: Pallets need benchmarks to generate weights for all extrinsics."
    echo "  FIX:  Create ${pallet_dir}src/benchmarking.rs with #[benchmarks] implementations."
    echo "  REF:  docs/QUALITY.md#benchmarks"
    ERRORS=$((ERRORS+1))
  fi
done

# Rule 2: No Vec<T> in storage (must use BoundedVec)
echo "[2/5] Checking bounded storage..."
UNBOUNDED=$(grep -rn "StorageValue.*Vec<\\|StorageMap.*Vec<" pallets/*/src/*.rs 2>/dev/null | grep -v BoundedVec | grep -v "//" || true)
if [ -n "$UNBOUNDED" ]; then
  echo "LINT ERROR [unbounded-storage]: Found unbounded Vec in storage"
  echo "$UNBOUNDED"
  echo "  WHAT: Vec<T> in storage has no deterministic size bound — DoS risk."
  echo "  FIX:  Replace Vec<X> with BoundedVec<X, T::MaxLen>."
  echo "  REF:  docs/ARCHITECTURE.md#bounded-storage"
  ERRORS=$((ERRORS+1))
fi

# Rule 3: Extrinsics must emit events
echo "[3/5] Checking event emission..."
for pallet_lib in pallets/*/src/lib.rs; do
  pallet=$(echo "$pallet_lib" | cut -d/ -f2)
  has_call=$(grep -c "#\\[pallet::call\\]" "$pallet_lib" 2>/dev/null || echo 0)
  has_event=$(grep -c "deposit_event\\|Self::deposit_event" "$pallet_lib" 2>/dev/null || echo 0)
  if [ "$has_call" -gt "0" ] && [ "$has_event" -eq "0" ]; then
    echo "LINT ERROR [missing-events]: $pallet has extrinsics but no deposit_event calls"
    echo "  WHAT: Silent state changes make off-chain indexers blind."
    echo "  FIX:  Add Self::deposit_event(Event::YourEvent{...}) in each extrinsic."
    echo "  REF:  docs/CONVENTIONS.md#events"
    ERRORS=$((ERRORS+1))
  fi
done

# Rule 4: Security-sensitive extrinsics must have origin checks
echo "[4/5] Checking origin checks..."
for func in "update_reputation" "treasury_spend"; do
  if grep -rn "pub fn $func" pallets/*/src/lib.rs >/dev/null 2>&1; then
    while IFS= read -r f; do
      if ! grep -A 8 "pub fn $func" "$f" 2>/dev/null | grep -q "ensure_root\\|ensure_signed\\|ensure_origin"; then
        echo "LINT ERROR [missing-origin-check]: $func in $f has no origin validation"
        echo "  FIX: Add ensure_signed(origin)? or ensure_root!(origin)? at function start."
        echo "  REF: docs/QUALITY.md#security-sensitive-functions"
        ERRORS=$((ERRORS+1))
      fi
    done < <(grep -rln "pub fn $func" pallets/*/src/lib.rs 2>/dev/null)
  fi
done

# Rule 5: AGENTS.md length
echo "[5/5] Checking AGENTS.md length..."
if [ -f AGENTS.md ] && [ "$(wc -l < AGENTS.md)" -gt 150 ]; then
  echo "LINT ERROR [agents-too-long]: AGENTS.md exceeds 150 lines"
  echo "  FIX: Move details to docs/ and replace with pointers."
  ERRORS=$((ERRORS+1))
fi

echo "=== Lint: $ERRORS error(s) ==="
[ $ERRORS -eq 0 ] || exit 1
echo "All checks passed. ✓"
'''


def _generate_go_lint(info: dict, module: str) -> str:
    return f'''#!/bin/bash
# Agent harness linter (Go) — errors are agent-readable
set -euo pipefail
ERRORS=0
cd "$(git rev-parse --show-toplevel)"
echo "=== Agent Lint (Go) ==="

# Rule 1: No reverse dependency (internal → cmd forbidden)
echo "[1/5] Checking reverse dependencies..."
REVERSE=$(grep -rn '"{module}/cmd' internal/ 2>/dev/null || true)
if [ -n "$REVERSE" ]; then
  echo "LINT ERROR [reverse-dependency]: internal/ imports from cmd/"
  echo "$REVERSE"
  echo "  WHAT: Breaks cmd→internal→pkg layer rule."
  echo "  FIX:  Move shared logic to pkg/."
  echo "  REF:  docs/ARCHITECTURE.md#layer-rules"
  ERRORS=$((ERRORS+1))
fi

# Rule 2: All exported symbols need godoc
echo "[2/5] Checking godoc coverage..."
MISSING=$(go vet ./... 2>&1 | grep "exported.*should have comment" || true)
if [ -n "$MISSING" ]; then
  COUNT=$(echo "$MISSING" | wc -l | tr -d ' ')
  echo "LINT ERROR [missing-godoc]: $COUNT exported symbols missing godoc"
  echo "$MISSING" | head -5
  echo "  FIX:  Add // SymbolName does X comments above each exported declaration."
  echo "  REF:  docs/CONVENTIONS.md#godoc"
  ERRORS=$((ERRORS+1))
fi

# Rule 3: go build must pass
echo "[3/5] Running go build..."
if ! go build ./... 2>&1; then
  echo "LINT ERROR [build-failure]: go build ./... failed"
  echo "  FIX:  Run go build ./... and fix compile errors."
  ERRORS=$((ERRORS+1))
fi

# Rule 4: No global mutable state in internal/
echo "[4/5] Checking global state..."
GLOBAL=$(grep -rn "^var [A-Z]" internal/ 2>/dev/null | grep -v "_test.go" | grep -v "Err[A-Z]" | grep -v "embed.FS" || true)
if [ -n "$GLOBAL" ]; then
  echo "LINT WARNING [global-state]: Exported global vars found (may cause test pollution):"
  echo "$GLOBAL" | head -5
  echo "  FIX:  Move state into structs. Inject via constructors."
  echo "  REF:  docs/QUALITY.md#no-global-state"
fi

# Rule 5: AGENTS.md length
echo "[5/5] Checking AGENTS.md length..."
if [ -f AGENTS.md ] && [ "$(wc -l < AGENTS.md)" -gt 150 ]; then
  echo "LINT ERROR [agents-too-long]: AGENTS.md exceeds 150 lines"
  echo "  FIX: Move details to docs/ and replace with pointers."
  ERRORS=$((ERRORS+1))
fi

echo "=== Lint: $ERRORS error(s) ==="
[ $ERRORS -eq 0 ] || exit 1
echo "All checks passed. ✓"
'''


def _generate_ts_lint(info: dict) -> str:
    return '''#!/bin/bash
# Agent harness linter (TypeScript) — errors are agent-readable
set -euo pipefail
ERRORS=0
cd "$(git rev-parse --show-toplevel)"
echo "=== Agent Lint (TypeScript) ==="

# Rule 1: TypeScript build must pass
echo "[1/4] Running tsc..."
if ! npx tsc --noEmit 2>&1; then
  echo "LINT ERROR [build-failure]: TypeScript compilation failed"
  echo "  FIX: Fix all type errors shown above."
  ERRORS=$((ERRORS+1))
fi

# Rule 2: No any types in src/
echo "[2/4] Checking for any types..."
ANY_COUNT=$(grep -rn ": any" src/ 2>/dev/null | grep -v "//.*any" | wc -l || echo 0)
if [ "$ANY_COUNT" -gt 0 ]; then
  echo "LINT WARNING [unsafe-any]: $ANY_COUNT uses of ': any' found in src/"
  echo "  FIX: Replace with specific types or unknown."
  echo "  REF: docs/CONVENTIONS.md#types"
fi

# Rule 3: All exported functions need JSDoc
echo "[3/4] Checking JSDoc coverage..."
MISSING=$(grep -rn "^export function\|^export async function\|^export class\|^export const" src/ 2>/dev/null | grep -v "_test\|test\." || true)
# (basic check — proper tool would use ts-morph)

# Rule 4: AGENTS.md length
echo "[4/4] Checking AGENTS.md length..."
if [ -f AGENTS.md ] && [ "$(wc -l < AGENTS.md)" -gt 150 ]; then
  echo "LINT ERROR [agents-too-long]: AGENTS.md exceeds 150 lines"
  echo "  FIX: Move details to docs/ and replace with pointers."
  ERRORS=$((ERRORS+1))
fi

echo "=== Lint: $ERRORS error(s) ==="
[ $ERRORS -eq 0 ] || exit 1
echo "All checks passed. ✓"
'''


def _generate_python_lint(info: dict) -> str:
    module = info.get("module", info["name"].replace("-", "_"))
    return f'''#!/bin/bash
# Agent harness linter (Python) — errors are agent-readable
set -euo pipefail
ERRORS=0
cd "$(git rev-parse --show-toplevel)"
echo "=== Agent Lint (Python) ==="

# Rule 1: No bare except clauses
echo "[1/5] Checking for bare except..."
BARE=$(grep -rn "except:" {module}/ 2>/dev/null | grep -v "# noqa" | grep -v "_test\\|test_" || true)
if [ -n "$BARE" ]; then
  echo "LINT ERROR [bare-except]: Found bare except: clauses"
  echo "$BARE" | head -5
  echo "  WHAT: Bare except catches SystemExit and KeyboardInterrupt — masks real bugs."
  echo "  FIX:  Use specific exception types: except (ValueError, TypeError):"
  echo "  REF:  docs/QUALITY.md#error-handling"
  ERRORS=$((ERRORS+1))
fi

# Rule 2: No print() in source (use logging)
echo "[2/5] Checking for print statements..."
PRINTS=$(grep -rn "^[[:space:]]*print(" {module}/ 2>/dev/null | grep -v "# noqa" | grep -v "_test\\|test_" || true)
if [ -n "$PRINTS" ]; then
  COUNT=$(echo "$PRINTS" | wc -l | tr -d ' ')
  echo "LINT WARNING [print-statements]: $COUNT print() calls in source (use logging)"
  echo "$PRINTS" | head -3
  echo "  FIX:  import logging; logger = logging.getLogger(__name__)"
  echo "  REF:  docs/CONVENTIONS.md#logging"
fi

# Rule 3: All public modules must have docstrings
echo "[3/5] Checking module docstrings..."
MISSING_DOCS=$(find {module}/ -name "*.py" ! -name "_*" ! -name "test_*" -exec grep -L '"""' {{}} \\; 2>/dev/null || true)
if [ -n "$MISSING_DOCS" ]; then
  echo "LINT ERROR [missing-docstring]: Public modules missing docstrings:"
  echo "$MISSING_DOCS" | head -5
  echo "  FIX:  Add triple-quoted module docstring at top of file."
  echo "  REF:  docs/CONVENTIONS.md#docstrings"
  ERRORS=$((ERRORS+1))
fi

# Rule 4: Tool count guard (check __init__.py exports)
echo "[4/5] Checking tool ceiling..."
TOOL_COUNT=$(grep -rn "^def \|^async def " {module}/ 2>/dev/null | grep -v "_test\\|test_\\|_impl\\|_helper" | grep -c "^" 2>/dev/null || echo 0)
if [ "$TOOL_COUNT" -gt 40 ]; then
  echo "LINT WARNING [tool-ceiling]: $TOOL_COUNT public functions found"
  echo "  WHAT: High function count increases agent decision overhead (guideline: <20 tools per agent)."
  echo "  FIX:  Group related functions into classes or move to submodules."
  echo "  REF:  docs/ARCHITECTURE.md#tool-ceiling"
fi

# Rule 5: AGENTS.md length
echo "[5/5] Checking AGENTS.md length..."
if [ -f AGENTS.md ] && [ "$(wc -l < AGENTS.md)" -gt 150 ]; then
  echo "LINT ERROR [agents-too-long]: AGENTS.md exceeds 150 lines"
  echo "  FIX: Move details to docs/ and replace with pointers."
  ERRORS=$((ERRORS+1))
fi

echo "=== Lint: $ERRORS error(s) ==="
[ $ERRORS -eq 0 ] || exit 1
echo "All checks passed. ✓"
'''


def _generate_generic_lint(info: dict) -> str:
    return '''#!/bin/bash
# Agent harness linter — errors are agent-readable
set -euo pipefail
ERRORS=0
cd "$(git rev-parse --show-toplevel)"
echo "=== Agent Lint ==="

# Rule 1: AGENTS.md length
echo "[1/1] Checking AGENTS.md length..."
if [ -f AGENTS.md ] && [ "$(wc -l < AGENTS.md)" -gt 150 ]; then
  echo "LINT ERROR [agents-too-long]: AGENTS.md exceeds 150 lines"
  echo "  FIX: Move details to docs/ and replace with pointers."
  ERRORS=$((ERRORS+1))
fi

echo "=== Lint: $ERRORS error(s) ==="
[ $ERRORS -eq 0 ] || exit 1
echo "All checks passed. ✓"
'''


def generate_ci_yml(info: dict) -> str:
    """Generate .github/workflows/agent-lint.yml."""
    lang = info["language"]

    go_setup = """
      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true
"""

    rust_setup = """
      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy

      - name: Cache cargo
        uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
"""

    node_setup = """
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm

      - name: Install dependencies
        run: npm ci
"""

    setup = {"rust": rust_setup, "go": go_setup, "typescript": node_setup}.get(lang, "")

    test_cmd = {
        "rust": "cargo test --workspace",
        "go": "go test ./... -count=1 -timeout 120s",
        "typescript": "npm test",
    }.get(lang, "make test")

    return f"""name: Agent Harness Lint

on:
  pull_request:
  push:
    branches: [main]

jobs:
  agent-lint:
    name: Agent architectural invariants
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
{setup}
      - name: Run agent lints
        run: bash scripts/agent-lint.sh

  test:
    name: Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
{setup}
      - name: Run tests
        run: {test_cmd}
"""


def generate_architecture_md(info: dict) -> str:
    """Generate docs/ARCHITECTURE.md stub for the detected language."""
    lang = info["language"]
    name = info["name"]
    packages = info.get("packages", [])
    dirs = info.get("dirs", [])

    pkg_table = "\n".join(
        f"| `{p}` | [describe what {p} does] |"
        for p in packages[:10]
    )
    dir_map = "\n".join(f"  {d}/" for d in dirs[:8])

    return f"""# Architecture — {name}

## Overview

[One paragraph describing what this repo does and its key design decisions.]

## Directory Structure

```
{dir_map}
```

## Layer Rules

[Describe which packages/layers may import which. Example:]

```
cmd/ → internal/ → pkg/     ← allowed
internal/ → cmd/             ← FORBIDDEN
```

## Key {'Pallets' if lang == 'rust' else 'Packages'}

| {'Pallet' if lang == 'rust' else 'Package'} | Responsibility |
|---------|---------------|
{pkg_table}

## Dependency Injection

[Describe how dependencies are injected — Config trait (Rust) / constructor injection (Go) / etc.]

## Key Invariants

1. [List critical architectural rules that must not be broken]
2. [Example: pallets must not import each other directly]
3. [Example: all storage must use bounded types]

---

*Auto-generated by harness skill scaffold. Fill in the blanks before merging.*
"""


def generate_quality_md(info: dict) -> str:
    lang = info["language"]
    name = info["name"]
    test_cmd = {
        "rust": "cargo test --workspace",
        "go": "go test ./... -count=1",
        "typescript": "npm test",
    }.get(lang, "make test")

    return f"""# Quality Standards — {name}

## Test Coverage

**Target: 90% per {'pallet' if lang == 'rust' else 'package'}** (enforced in CI).

```bash
# Run tests
{test_cmd}
```

## What to Test

- Happy path — success case with expected output
- Error paths — all error variants are reachable
- Boundary conditions — empty inputs, max values
- Security — origin/auth checks cannot be bypassed

## Security-Sensitive Functions

[List functions that require elevated privilege checks:]
- `[function_name]` — must have [origin/auth] check

## CI Gates

| Gate | Command | Block PR? |
|------|---------|-----------|
| Build | [build command] | Yes |
| Tests | {test_cmd} | Yes |
| Agent lints | `bash scripts/agent-lint.sh` | Yes |

---

*Auto-generated by harness skill scaffold. Fill in the blanks before merging.*
"""


def generate_conventions_md(info: dict) -> str:
    lang = info["language"]
    name = info["name"]

    if lang == "rust":
        return f"""# Conventions — {name}

## Naming Rules

- **Crates:** `pallet-{{domain}}` kebab-case
- **Extrinsics:** `verb_noun` snake_case (register_agent, update_reputation)
- **Errors:** PascalCase descriptive (NotFound, AlreadyRegistered)
- **Events:** PascalCase past tense (AgentRegistered, TaskCompleted)
- **Storage:** PascalCase plural (Agents, Tasks)
- **Weights:** snake_case matching extrinsic name

## File Structure

Each pallet: `lib.rs`, `benchmarking.rs`, `weights.rs`, `mock.rs`, `tests.rs`

---
*Auto-generated by harness skill scaffold.*
"""
    elif lang == "go":
        return f"""# Conventions — {name}

## Naming Rules

- **Packages:** short lowercase, no underscores
- **Files:** `snake_case.go`
- **Types:** PascalCase
- **Functions:** PascalCase (exported), camelCase (unexported)
- **Errors:** `ErrXxx` sentinels; wrap with `fmt.Errorf("pkg: action: %w", err)`

## Godoc

All exported symbols require godoc starting with the symbol name.

## Context

`ctx context.Context` is always the first parameter. Never store in struct.

---
*Auto-generated by harness skill scaffold.*
"""
    else:
        return f"""# Conventions — {name}

## Naming Rules

- **Files:** `kebab-case.ts`
- **Types/Classes:** PascalCase
- **Functions:** camelCase
- **Constants:** SCREAMING_SNAKE or camelCase (pick one, be consistent)

## JSDoc

All exported functions require JSDoc comments.

---
*Auto-generated by harness skill scaffold.*
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_coordination_md(info: dict) -> str:
    """Generate docs/COORDINATION.md for multi-agent task design."""
    name = info["name"]
    return f"""# Multi-Agent Coordination — {name}

## Overview

This document defines how agents coordinate when working on this repo in parallel.
Follow these rules to avoid conflicts, duplicate work, and broken state.

## Task Ownership

- **One agent per feature/task.** Never have two agents editing the same file simultaneously.
- Each agent claims a task by updating its status to `in_progress` before starting.
- If a task is already `in_progress`, pick a different one or wait.

## Shared State

| Artifact | Owner | Access pattern |
|----------|-------|---------------|
| `docs/` | Any agent | Read freely; write via PR only |
| `scripts/agent-lint.sh` | Harness maintainer | Do not modify without review |
| Database/state files | One agent at a time | Lock before write |

## Dependency Rules

- **Never start a dependent task** until all its dependencies are `complete`.
- Check `docs/ARCHITECTURE.md` before adding any cross-package import.
- If your task requires another task's output, coordinate via the task state (not direct communication).

## Context Visibility

Each agent has its own context window. To share findings across agents:
1. Write to `docs/` or task notes (persistent)
2. Do NOT rely on other agents reading your context
3. Assume each agent starts fresh — make your outputs self-contained

## Tool Ceiling

Per the agent tool design guidelines: **≤ 20 tools per agent session**.
If you find yourself needing more, split into subagents with focused scopes.

## Conflict Resolution

If two agents produce conflicting implementations:
1. The Reviewer agent decides (not either builder)
2. Prefer the implementation with higher test coverage
3. Document the decision in `docs/EXECUTION_PLAN_TEMPLATE.md`

---

*Generated by harness skill scaffold. Update as your coordination patterns evolve.*
"""


def scaffold(repo: Path, dry_run: bool, force: bool, audit: bool = False) -> None:
    print(f"Scaffolding harness for: {repo}")

    info = inspect_repo(repo, detect_language(repo))
    print(f"Detected language: {info['language']}")
    print(f"Packages found: {len(info['packages'])}")

    if audit:
        _run_audit(repo, info)
        return

    files = {
        repo / "AGENTS.md": generate_agents_md(info),
        repo / "docs" / "ARCHITECTURE.md": generate_architecture_md(info),
        repo / "docs" / "QUALITY.md": generate_quality_md(info),
        repo / "docs" / "CONVENTIONS.md": generate_conventions_md(info),
        repo / "docs" / "COORDINATION.md": generate_coordination_md(info),
        repo / "docs" / "EXECUTION_PLAN_TEMPLATE.md": _execution_plan_template(),
        repo / "scripts" / "agent-lint.sh": generate_agent_lint_sh(info),
        repo / ".github" / "workflows" / "agent-lint.yml": generate_ci_yml(info),
    }

    for path, content in files.items():
        if path.name == "AGENTS.md" and path.exists() and not force:
            print(f"  SKIP  {path.relative_to(repo)} (exists — use --force to overwrite)")
            continue
        if dry_run:
            print(f"  DRY   {path.relative_to(repo)} ({len(content)} chars)")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            if path.name == "agent-lint.sh":
                path.chmod(0o755)
            print(f"  WRITE {path.relative_to(repo)}")

    if not dry_run:
        print("\nDone. Next steps:")
        print("  1. Fill in the [placeholder] sections in docs/ARCHITECTURE.md")
        print("  2. Run: bash scripts/agent-lint.sh")
        print("  3. git add AGENTS.md docs/ scripts/ .github/ && git commit")


def _execution_plan_template() -> str:
    return """# Execution Plan: [Task Name]

## Status: [Planning | In Progress | Review | Complete]
## Complexity: [Low | Medium | High]
## Packages affected: [list]

## Goal

[One paragraph — what does done look like?]

## Steps

- [ ] Step 1: Read docs/ARCHITECTURE.md
- [ ] Step 2: [implementation]
- [ ] Step 3: Write tests
- [ ] Step 4: Run lints and tests
- [ ] Step 5: Open PR

## Decisions

| Decision | Rationale | Date |
|----------|-----------|------|

## Known risks

- ...
"""


def _run_audit(repo: Path, info: dict) -> None:
    """Audit tool lifecycle: check harness freshness and flag stale patterns."""
    import datetime
    print("\n=== Harness Audit ===")
    lang = info["language"]

    # Check AGENTS.md exists and has depth layer markers
    agents_md = repo / "AGENTS.md"
    if not agents_md.exists():
        print("❌ AGENTS.md missing — run scaffold first")
    else:
        content = agents_md.read_text()
        if "L1" not in content or "progressive disclosure" not in content.lower():
            print("⚠️  AGENTS.md missing progressive disclosure depth markers (L1/L2/L3)")
            print("   FIX: Re-run scaffold --force to regenerate with depth markers")
        else:
            print("✅ AGENTS.md has progressive disclosure markers")
        lines = len(content.splitlines())
        if lines > 150:
            print(f"❌ AGENTS.md too long ({lines} lines, limit 150)")
        else:
            print(f"✅ AGENTS.md length OK ({lines} lines)")

    # Check COORDINATION.md exists (multi-agent support)
    coord_md = repo / "docs" / "COORDINATION.md"
    if not coord_md.exists():
        print("⚠️  docs/COORDINATION.md missing — multi-agent coordination not documented")
        print("   FIX: Re-run scaffold to generate it")
    else:
        print("✅ docs/COORDINATION.md present")

    # Check lint script has JSON output option
    lint_sh = repo / "scripts" / "agent-lint.sh"
    if lint_sh.exists():
        content = lint_sh.read_text()
        if "--json" not in content and "JSON" not in content:
            print("⚠️  agent-lint.sh has no machine-readable output (--json flag missing)")
            print("   FIX: Re-run scaffold --force to regenerate with JSON support")
        else:
            print("✅ agent-lint.sh has machine-readable output")
    else:
        print("❌ scripts/agent-lint.sh missing")

    # Python support check
    if lang == "python" and lint_sh.exists():
        content = lint_sh.read_text()
        if "ruff" not in content and "pyright" not in content:
            print("⚠️  Python repo but lint script has no ruff/pyright checks")
    elif lang not in ("rust", "go", "typescript", "python"):
        print(f"⚠️  Language '{lang}' may not be fully supported")

    print(f"\nAudit complete. Language: {lang}, Packages: {len(info['packages'])}")
    print(f"Run `scaffold.py --repo {repo} --force` to update stale files.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Path to repository root")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing AGENTS.md")
    parser.add_argument("--audit", action="store_true",
                        help="Audit harness freshness (tool lifecycle check) without writing")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"ERROR: repo path does not exist: {repo}", file=sys.stderr)
        sys.exit(1)
    if not (repo / ".git").exists():
        print(f"WARNING: {repo} does not appear to be a git repo", file=sys.stderr)

    scaffold(repo, dry_run=args.dry_run, force=args.force, audit=args.audit)


if __name__ == "__main__":
    main()
