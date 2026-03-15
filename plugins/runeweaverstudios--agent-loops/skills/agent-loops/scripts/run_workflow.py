#!/usr/bin/env python3
"""
Run prebuilt agent loop workflows. Loads a workflow YAML/JSON, executes each
step via the claude CLI (or agent-swarm router for model selection), captures
real outputs, and chains them between steps. Supports sequential and parallel steps.

Usage:
    # Dry-run (print what would happen)
    python3 run_workflow.py ship_feature "Add dark mode to settings"

    # Actually run agents
    python3 run_workflow.py ship_feature "Add dark mode to settings" --apply

    # With a specific model override
    python3 run_workflow.py bug_fix "Fix login crash" --apply --model sonnet

    # List available workflows
    python3 run_workflow.py --list
"""
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", str(Path.home() / ".openclaw")))
ROUTER = OPENCLAW_HOME / "workspace" / "skills" / "agent-swarm" / "scripts" / "router.py"
WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / "workflows"
RUNS_DIR = OPENCLAW_HOME / "workspace" / "skills" / "agent-loops" / "runs"
CLAUDE_BIN = shutil.which("claude") or "claude"


# ---------------------------------------------------------------------------
# Workflow loading
# ---------------------------------------------------------------------------

def load_workflow(workflow_id: str) -> dict:
    """Load a workflow definition from YAML or JSON."""
    for ext in (".yaml", ".json"):
        path = WORKFLOWS_DIR / f"{workflow_id}{ext}"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                if ext == ".json":
                    return json.load(f)
                try:
                    import yaml
                    return yaml.safe_load(f)
                except ImportError:
                    raise RuntimeError("PyYAML required for YAML workflows: pip install pyyaml")
    raise FileNotFoundError(f"Workflow not found: {workflow_id} (looked in {WORKFLOWS_DIR})")


def list_workflows() -> List[dict]:
    """List all available workflow definitions."""
    workflows = []
    seen = set()
    for path in sorted(WORKFLOWS_DIR.iterdir()):
        if path.suffix in (".yaml", ".json"):
            wf_id = path.stem
            if wf_id in seen:
                continue
            seen.add(wf_id)
            try:
                wf = load_workflow(wf_id)
                workflows.append({
                    "id": wf_id,
                    "name": wf.get("name", wf_id),
                    "description": wf.get("description", ""),
                    "steps": len(wf.get("steps", [])),
                })
            except Exception as e:
                workflows.append({"id": wf_id, "name": wf_id, "description": f"(error: {e})", "steps": 0})
    return workflows


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

def render_template(template: str, context: Dict[str, str]) -> str:
    """Replace {{ key }} placeholders with context values."""
    result = template
    for key, value in context.items():
        result = result.replace("{{ " + key + " }}", str(value))
    return result


# ---------------------------------------------------------------------------
# Router integration
# ---------------------------------------------------------------------------

def route_task(task: str, agent_hint: Optional[str] = None) -> dict:
    """Get model/spawn params from agent-swarm router."""
    if not ROUTER.exists():
        return {"task": task, "model": "sonnet", "sessionTarget": "isolated"}
    try:
        result = subprocess.run(
            [sys.executable, str(ROUTER), "spawn", "--json", task],
            capture_output=True, text=True, timeout=30,
            cwd=str(OPENCLAW_HOME),
            env={**os.environ, "OPENCLAW_HOME": str(OPENCLAW_HOME)},
        )
        if result.returncode == 0 and result.stdout.strip():
            params = json.loads(result.stdout.strip())
            params["task"] = task
            return params
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        pass
    return {"task": task, "model": "sonnet", "sessionTarget": "isolated"}


# ---------------------------------------------------------------------------
# Agent execution via claude CLI
# ---------------------------------------------------------------------------

def run_claude(task: str, model: Optional[str] = None, timeout_sec: int = 600,
               system_prompt: Optional[str] = None, cwd: Optional[str] = None) -> dict:
    """
    Run a task via `claude -p` and capture the result.
    Returns {"ok": True, "output": "...", "duration": N} or {"ok": False, "error": "..."}.
    """
    cmd = [CLAUDE_BIN, "-p", task, "--output-format", "json"]
    if model:
        cmd.extend(["--model", model])
    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            timeout=timeout_sec,
            cwd=cwd or str(OPENCLAW_HOME),
            env={**os.environ, "OPENCLAW_HOME": str(OPENCLAW_HOME)},
        )
        elapsed = round(time.time() - start, 1)

        if result.returncode != 0:
            return {"ok": False, "error": result.stderr.strip() or f"exit code {result.returncode}", "duration": elapsed}

        # claude --output-format json returns a JSON object with a "result" field
        stdout = result.stdout.strip()
        try:
            data = json.loads(stdout)
            output = data.get("result", stdout)
        except json.JSONDecodeError:
            output = stdout

        return {"ok": True, "output": output, "duration": elapsed}

    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"Timed out after {timeout_sec}s", "duration": timeout_sec}
    except OSError as e:
        return {"ok": False, "error": str(e), "duration": 0}


# ---------------------------------------------------------------------------
# Step execution
# ---------------------------------------------------------------------------

# Agent role → system prompt mapping
AGENT_PROMPTS = {
    "pm": (
        "You are a product manager. Break down features into clear, actionable tasks. "
        "Output a structured task list with priorities and acceptance criteria. Be concise."
    ),
    "dev": (
        "You are a senior developer. Implement code changes, write tests, and ensure quality. "
        "Output working code and a summary of changes made. Be thorough but focused."
    ),
    "editor": (
        "You are a technical editor. Write clear user-facing documentation and changelog entries. "
        "Output polished docs ready for users. Be precise and readable."
    ),
    "reviewer": (
        "You are a code reviewer. Analyze code for bugs, security issues, performance problems, "
        "and style violations. Output a structured review with severity levels."
    ),
    "researcher": (
        "You are a researcher. Find relevant information, synthesize sources, and produce "
        "a clear summary with citations. Be thorough and factual."
    ),
    "tester": (
        "You are a QA engineer. Design test cases, run tests, and report results. "
        "Output a structured test report with pass/fail status."
    ),
    "architect": (
        "You are a software architect. Design systems, evaluate trade-offs, and produce "
        "clear architectural decisions. Output diagrams (ASCII) and rationale."
    ),
}


def execute_step(step: dict, context: Dict[str, str], model_override: Optional[str] = None,
                 dry_run: bool = True, timeout: int = 600, verbose: bool = False) -> dict:
    """
    Execute a single workflow step.
    Returns {"step_id": ..., "ok": ..., "output": ..., "model": ..., "duration": ...}
    """
    step_id = step["id"]
    task_tpl = step.get("task_template", step.get("task", ""))
    task = render_template(task_tpl, context)
    agent = step.get("agent", "default")
    step_timeout = step.get("timeout", timeout)

    # Route to get model
    routed = route_task(task, agent)
    model = model_override or step.get("model") or routed.get("model", "sonnet")
    system_prompt = AGENT_PROMPTS.get(agent)

    result = {
        "step_id": step_id,
        "agent": agent,
        "model": model,
        "task": task[:200] + ("..." if len(task) > 200 else ""),
        "ok": False,
        "output": "",
        "duration": 0,
    }

    if dry_run:
        print(f"  [{step_id}] {agent} via {model}")
        print(f"    Task: {task[:100]}{'...' if len(task) > 100 else ''}")
        result["ok"] = True
        result["output"] = f"[dry-run output of {step_id}]"
        return result

    # Live execution
    print(f"  [{step_id}] spawning {agent} via {model}...")
    if verbose:
        print(f"    Task: {task[:150]}{'...' if len(task) > 150 else ''}")

    run_result = run_claude(task, model=model, timeout_sec=step_timeout, system_prompt=system_prompt)
    result["ok"] = run_result["ok"]
    result["output"] = run_result.get("output", run_result.get("error", ""))
    result["duration"] = run_result.get("duration", 0)

    status = "done" if run_result["ok"] else "FAILED"
    print(f"  [{step_id}] {status} ({result['duration']}s)")
    if not run_result["ok"]:
        print(f"    Error: {run_result.get('error', 'unknown')}")

    return result


def execute_parallel_steps(steps: List[dict], context: Dict[str, str],
                           model_override: Optional[str] = None, dry_run: bool = True,
                           timeout: int = 600, verbose: bool = False) -> List[dict]:
    """Execute multiple steps in parallel using threads."""
    if dry_run:
        results = []
        for step in steps:
            results.append(execute_step(step, context, model_override, dry_run, timeout, verbose))
        return results

    results = []
    with ThreadPoolExecutor(max_workers=len(steps)) as executor:
        futures = {
            executor.submit(execute_step, step, context, model_override, dry_run, timeout, verbose): step
            for step in steps
        }
        for future in as_completed(futures):
            results.append(future.result())

    # Sort by original step order
    step_order = {s["id"]: i for i, s in enumerate(steps)}
    results.sort(key=lambda r: step_order.get(r["step_id"], 999))
    return results


# ---------------------------------------------------------------------------
# Run persistence
# ---------------------------------------------------------------------------

def save_run(workflow_id: str, user_input: str, steps_output: List[dict], dry_run: bool) -> Optional[Path]:
    """Save a run record to disk for auditing."""
    if dry_run:
        return None
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = f"{workflow_id}_{int(time.time())}"
    run_file = RUNS_DIR / f"{run_id}.json"
    record = {
        "id": run_id,
        "workflow": workflow_id,
        "input": user_input,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "steps": steps_output,
        "success": all(s.get("ok") for s in steps_output),
        "total_duration": sum(s.get("duration", 0) for s in steps_output),
    }
    with open(run_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return run_file


# ---------------------------------------------------------------------------
# Main workflow runner
# ---------------------------------------------------------------------------

def run_workflow(workflow_id: str, user_input: str, dry_run: bool = True,
                 model_override: Optional[str] = None, timeout: int = 600,
                 verbose: bool = False) -> List[dict]:
    """
    Run a workflow end-to-end. Supports sequential steps, parallel groups,
    and chaining real outputs between steps.
    """
    wf = load_workflow(workflow_id)
    steps = wf.get("steps", [])
    context = {"user_input": user_input}
    all_outputs = []

    mode = "dry-run" if dry_run else "LIVE"
    print(f"\n{'='*60}")
    print(f"Workflow: {wf.get('name', workflow_id)} [{mode}]")
    print(f"Input: {user_input[:80]}{'...' if len(user_input) > 80 else ''}")
    print(f"{'='*60}\n")

    for i, step in enumerate(steps):
        # Check if this is a parallel group
        if "parallel" in step:
            parallel_steps = step["parallel"]
            group_id = step.get("id", f"parallel_{i}")
            print(f"  [{group_id}] parallel group ({len(parallel_steps)} steps)")
            results = execute_parallel_steps(
                parallel_steps, context, model_override, dry_run, timeout, verbose
            )
            all_outputs.extend(results)
            # Add all parallel outputs to context
            for r in results:
                context[f"{r['step_id']}_output"] = r["output"]
            # Also create a combined output for the group
            combined = "\n\n---\n\n".join(
                f"[{r['step_id']}]:\n{r['output']}" for r in results
            )
            context[f"{group_id}_output"] = combined
        else:
            result = execute_step(step, context, model_override, dry_run, timeout, verbose)
            all_outputs.append(result)
            context[f"{result['step_id']}_output"] = result["output"]

        # Abort on failure (unless step is marked optional)
        last = all_outputs[-1] if all_outputs else None
        if last and not last["ok"] and not step.get("optional", False):
            print(f"\n  Step '{last['step_id']}' failed — aborting workflow.")
            break

    # Summary
    ok_count = sum(1 for s in all_outputs if s.get("ok"))
    total = len(all_outputs)
    total_time = sum(s.get("duration", 0) for s in all_outputs)
    print(f"\n{'='*60}")
    print(f"Result: {ok_count}/{total} steps succeeded", end="")
    if not dry_run:
        print(f" in {total_time:.1f}s")
    else:
        print()

    # Save run
    run_file = save_run(workflow_id, user_input, all_outputs, dry_run)
    if run_file:
        print(f"Run saved: {run_file}")
    print(f"{'='*60}\n")

    return all_outputs


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    p = argparse.ArgumentParser(
        description="Run agent loop workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s ship_feature \"Add dark mode\"\n"
               "  %(prog)s bug_fix \"Fix login crash\" --apply\n"
               "  %(prog)s --list\n",
    )
    p.add_argument("workflow", nargs="?", help="Workflow id (e.g. ship_feature)")
    p.add_argument("input", nargs="?", default="", help="User input for the workflow")
    p.add_argument("--list", action="store_true", help="List available workflows")
    p.add_argument("--apply", action="store_true", help="Actually run agents (default: dry-run)")
    p.add_argument("--model", default=None, help="Override model for all steps")
    p.add_argument("--timeout", type=int, default=600, help="Per-step timeout in seconds (default: 600)")
    p.add_argument("--verbose", "-v", action="store_true", help="Show full task text per step")
    p.add_argument("--json", action="store_true", help="Output results as JSON")

    args = p.parse_args()

    if args.list:
        workflows = list_workflows()
        if args.json:
            print(json.dumps(workflows, indent=2))
        else:
            print("\nAvailable workflows:\n")
            for wf in workflows:
                print(f"  {wf['id']:20s} {wf['description']} ({wf['steps']} steps)")
            print()
        return

    if not args.workflow:
        p.print_help()
        sys.exit(1)

    if not args.input:
        print("Error: input is required (describe what you want the workflow to do)")
        sys.exit(1)

    dry_run = not args.apply
    outputs = run_workflow(
        args.workflow, args.input,
        dry_run=dry_run,
        model_override=args.model,
        timeout=args.timeout,
        verbose=args.verbose,
    )

    if args.json:
        print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
