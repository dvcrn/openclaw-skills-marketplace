---
name: wander-monitor
description: "Guides users on using Wander to monitor GitHub Actions workflows. Use when user asks how to watch CI/CD runs, avoid polling Actions page, get notified when workflows complete, or integrate Wander with a project. Covers smart-push, foreground/background/detached modes, edge cases, and project integration."
---

# Wander — CI/CD Monitor Skill

**Don't watch. Wander.** Elegant automation for monitoring GitHub Actions without polling.

## When to use this skill

- User wants to monitor a GitHub Actions workflow after push
- User asks how to get notified when CI completes
- User wants to avoid refreshing the Actions page
- User integrates CI monitoring into a project (e.g. ClawHub publish)

---

## Install

```bash
git clone https://github.com/ERerGB/wander.git
cd wander
chmod +x *.sh
```

**Prerequisites**: `gh` CLI (authenticated), `jq`, macOS (for notifications)

---

## Usage patterns

### 1. Smart push (recommended for Wander's own repo)

```bash
cd wander
./smart-push.sh
```

Recommends smoke / e2e / skip based on changed files. Pushes and monitors.

### 2. Manual control (any repo)

```bash
# From target repo (e.g. openclaw-uninstall)
git push

# Choose monitoring mode:
../wander/watch-workflow.sh publish.yml      # Foreground, block until done
../wander/watch-workflow-bg.sh publish.yml  # Background, macOS notify when done
../wander/watch-workflow-detached.sh publish.yml  # Detached, can close terminal
```

### 3. Project integration

Add a wrapper script in the project:

```bash
#!/bin/bash
# scripts/watch-publish.sh
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WANDER_DIR="${WANDER_DIR:-$(dirname "$REPO_ROOT")/wander}"
cd "$REPO_ROOT"
exec "$WANDER_DIR/watch-workflow-bg.sh" publish.yml "$@"
```

Then: `git push && ./scripts/watch-publish.sh`

---

## Edge cases (from experience)

| Scenario | Behavior | Tip |
|----------|----------|-----|
| Workflow finishes in &lt; 30s | "Already completed" + immediate notify | Use `watch-workflow-bg`; it detects recent completion |
| Push then monitor immediately | Workflow may not start for 5–10s | Script waits up to 30s for workflow to appear |
| Wrong branch | No workflow after 30s | Ensure workflow is configured for current branch |
| No lock file in repo | setup-node `cache: npm` fails | Remove `cache: "npm"` from workflow if no package-lock.json |

---

## Workflow registry

For custom `check_window` / `expected_duration`, add `.workflows.yml` in project root or set `WORKFLOW_REGISTRY_FILE`:

```yaml
workflows:
  - name: "publish.yml"
    description: "Publish to ClawHub"
    check_window: 120
    expected_duration: 30
    category: "publish"
```

Default: `check_window=300` when workflow not in registry.

---

## Reference

- [Wander README](https://github.com/ERerGB/wander)
- [EDGE_CASES.md](https://github.com/ERerGB/wander/blob/main/EDGE_CASES.md)
- [COFFEE_BREAK.md](https://github.com/ERerGB/wander/blob/main/COFFEE_BREAK.md)
