#!/usr/bin/env python3
import base64
import json
import os
import shlex
import sys
from typing import Any


def parse_payload(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("wake payload must be a JSON object")
    return data


def pending_tasks(payload: dict[str, Any]) -> list[dict[str, Any]]:
    pending = payload.get("pending")
    if not isinstance(pending, dict):
        return []
    tasks = pending.get("tasks")
    if not isinstance(tasks, list):
        return []
    return [task for task in tasks if isinstance(task, dict)]


def review_tasks(payload: dict[str, Any]) -> list[dict[str, Any]]:
    review = payload.get("review")
    if not isinstance(review, dict):
        return []
    tasks = review.get("tasks")
    if not isinstance(tasks, list):
        return []
    return [task for task in tasks if isinstance(task, dict)]


def stuck_tasks(payload: dict[str, Any]) -> list[dict[str, Any]]:
    stuck = payload.get("stuck")
    if not isinstance(stuck, dict):
        return []
    tasks = stuck.get("tasks")
    if not isinstance(tasks, list):
        return []
    return [task for task in tasks if isinstance(task, dict)]


def task_workspace(payload: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    workspace = task.get("workspace")
    if isinstance(workspace, dict):
        return workspace

    pending = payload.get("pending")
    if isinstance(pending, dict):
        fallback = pending.get("workspace")
        if isinstance(fallback, dict):
            return fallback

    return {}


def build_branch(task: dict[str, Any]) -> str:
    branch = task.get("branch")
    if isinstance(branch, str) and branch.strip():
        return branch.strip()
    task_id = str(task.get("_id") or "").strip()
    return f"task/{task_id}" if task_id else "task/unknown"


def json_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def shell_quote(value: Any) -> str:
    return shlex.quote(json_string(value))


def build_direct_task_prompt(task: dict[str, Any], workspace: dict[str, Any]) -> str:
    agent = task.get("agent") if isinstance(task.get("agent"), dict) else {}
    task_id = json_string(task.get("_id"))
    agent_id = json_string(agent.get("_id") or task.get("assignedAgentId"))
    agent_name = json_string(agent.get("name")) or "assigned agent"
    acp_agent = (os.environ.get("SC_WAKE_ACP_AGENT") or "codex").strip() or "codex"
    branch = build_branch(task)
    title = json_string(task.get("title")) or "(untitled task)"
    description = json_string(task.get("description"))
    review_iteration = int(task.get("reviewIteration") or 0)
    review_comments = json_string(task.get("lastReviewComments"))
    workspace_name = json_string(workspace.get("name"))
    repo_url = json_string(workspace.get("repoUrl"))
    github_token = json_string(workspace.get("githubToken"))
    soul_md = json_string(agent.get("soulMd"))
    sc_api_url = os.environ.get("SC_API_URL", "")
    sc_api_key = os.environ.get("SC_API_KEY", "")
    sc_api_url_sh = shell_quote(sc_api_url)
    sc_api_key_sh = shell_quote(sc_api_key)
    task_id_sh = shell_quote(task_id)
    agent_id_sh = shell_quote(agent_id)
    branch_sh = shell_quote(branch)
    workspace_name_sh = shell_quote(workspace_name)
    repo_url_sh = shell_quote(repo_url)
    github_token_sh = shell_quote(github_token)

    return f"""# Identity
{soul_md}

Execute this Squad Control task directly. You are already the assigned worker agent for this task.
Assigned agent: {agent_name}
ACP harness agent: {acp_agent}

Hard requirements:
- Do NOT call sessions_spawn. Do NOT delegate to another dispatcher or sub-agent.
- Do NOT stop after calling /api/tasks/pickup or after posting the pickup thread message.
- After pickup, you must actually do the task work in the repository and drive it to completion yourself.
- If you open a PR, you must call /api/tasks/set-review with the PR deliverable.
- If anything fails, you must call /api/tasks/fail with the error details.

# Initialize environment (run these exports before any curl/git commands)
export SC_API_URL={sc_api_url_sh}
export SC_API_KEY={sc_api_key_sh}
export TASK_ID={task_id_sh}
export AGENT_ID={agent_id_sh}
export BRANCH={branch_sh}

# Repository
export WORKSPACE_NAME={workspace_name_sh}
export REPO_URL={repo_url_sh}
export GITHUB_TOKEN={github_token_sh}  # may be empty for public repos

# First step (required immediately)
curl -sL -X POST "${{SC_API_URL}}/api/tasks/pickup" \\
  -H "x-api-key: ${{SC_API_KEY}}" \\
  -H "Content-Type: application/json" \\
  -d '{{"taskId": "{task_id}", "agentId": "{agent_id}", "branch": "{branch}"}}'

# Second step (required immediately after pickup)
curl -sL -X POST "${{SC_API_URL}}/api/threads/send" \\
  -H "x-api-key: ${{SC_API_KEY}}" -H "Content-Type: application/json" \\
  -d '{{"taskId": "{task_id}", "agentId": "{agent_id}", "content": "Picking up task. Starting work now."}}'

# Task
**{title}**
{description}

# Review context
Review iteration: {review_iteration}
Previous review comments:
{review_comments or "(none)"}

# Work expectations
- Clone the repo after pickup (use credential helper — do NOT embed the token in the URL):
  if [ -n "$GITHUB_TOKEN" ]; then
    git -c "credential.helper=!f() {{ echo username=x-access-token; echo password=${{GITHUB_TOKEN}}; }}; f" clone "$REPO_URL" /tmp/task-repo
  else
    git clone "$REPO_URL" /tmp/task-repo
  fi
  cd /tmp/task-repo
  git checkout -b {branch}
- Clone the repo, create or reuse the task branch, and make the requested changes.
- Run the most relevant verification available before finishing.
- Keep the change focused to this task only.
- You are the worker. After the pickup message, continue until the work is actually done or failed.

# When Done — follow these steps EXACTLY, do not skip any

## 1. Commit and push
git add -A && git commit -m "feat: {title}"
git push origin {branch}

## 2. Create GitHub PR
Create the pull request against the default branch and save the PR number and URL.

## 3. Post summary to thread
curl -sL -X POST "${{SC_API_URL}}/api/threads/send" \\
  -H "x-api-key: ${{SC_API_KEY}}" -H "Content-Type: application/json" \\
  -d '{{"taskId": "{task_id}", "agentId": "{agent_id}", "content": "Work complete. PR #N: ${{PR_URL}}\\n\\n${{SUMMARY}}"}}'

## 4. Hand off for review (REQUIRED when a PR exists)
curl -sL -X POST "${{SC_API_URL}}/api/tasks/set-review" \\
  -H "x-api-key: ${{SC_API_KEY}}" -H "Content-Type: application/json" \\
  -d '{{"taskId": "{task_id}", "agentId": "{agent_id}", "result": "${{SUMMARY}}", "deliverables": [{{"type": "pr", "name": "PR #N", "url": "${{PR_URL}}"}}]}}'

If no PR is needed, call /api/tasks/complete directly instead of /api/tasks/set-review.

## If anything fails
curl -sL -X POST "${{SC_API_URL}}/api/tasks/fail" \\
  -H "x-api-key: ${{SC_API_KEY}}" -H "Content-Type: application/json" \\
  -d '{{"taskId": "{task_id}", "agentId": "{agent_id}", "error": "description of what went wrong"}}'
"""


def encode_text(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def command_pending_launches(payload: dict[str, Any]) -> int:
    acp_agent = (os.environ.get("SC_WAKE_ACP_AGENT") or "codex").strip() or "codex"

    for task in pending_tasks(payload):
        workspace = task_workspace(payload, task)
        task_id = json_string(task.get("_id"))
        if not task_id:
            continue

        prompt = build_direct_task_prompt(task, workspace)
        fields = [
            task_id,
            encode_text(acp_agent),
            encode_text(prompt),
        ]
        print("\t".join(fields))

    return 0


def command_residual_payload(payload: dict[str, Any]) -> int:
    if not review_tasks(payload) and not stuck_tasks(payload):
        return 0

    residual = dict(payload)
    pending = residual.get("pending")
    if isinstance(pending, dict):
        pending = dict(pending)
        pending["tasks"] = []
        residual["pending"] = pending

    counts = residual.get("counts")
    if isinstance(counts, dict):
        counts = dict(counts)
        counts["pending"] = 0
        residual["counts"] = counts

    print(json.dumps(residual))
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: wake-dispatch-plan.py <pending-launches|residual-payload>", file=sys.stderr)
        return 2

    payload = parse_payload(sys.stdin.read())
    command = sys.argv[1]
    if command == "pending-launches":
        return command_pending_launches(payload)
    if command == "residual-payload":
        return command_residual_payload(payload)

    print(f"Unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
