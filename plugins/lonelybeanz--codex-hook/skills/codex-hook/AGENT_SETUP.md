# Codex Hook - Agent Workspace Setup

This file documents the codex-hook setup for this agent workspace.

## Installation

1. Copy scripts to `~/bin`:
```bash
mkdir -p ~/bin
cp /path/to/skills/codex-hook/scripts/* ~/bin/
chmod +x ~/bin/*
```

2. Ensure agent exists:
```bash
openclaw agents add codex --workspace "$(pwd)" --model openai-codex/gpt-5.2 --non-interactive
```

## Configuration

Create `~/.config/codex-hook/config.json`:

```json
{
  "result_dir": "/tmp/codex-results",
  "pending_wake_file": "/tmp/codex-results/pending-wake.json",
  "latest_result_file": "/tmp/codex-results/latest.json",
  "default_channel": "telegram",
  "default_group": "YOUR_GROUP_ID_HERE",
  "default_webhook_url": "",
  "poll_interval": 5,
  "max_concurrent": 4,
  "heartbeat_integration": true,
  "archive_days": 30,
  "output_max_chars": 4000
}
```

### Required settings

- **`default_group`**: Set to your Telegram group ID for notifications
- **`result_dir`**: Where task data is stored (ensure this is writable)
- `heartbeat_integration`: Set `true` if AGI heartbeat integration is needed

### Optional settings

- `default_webhook_url`: For webhook callbacks
- `poll_interval`: How often (seconds) watcher checks task status
- `output_max_chars`: Max output to store/notify (default 4000)

## Usage

### Dispatch a task

```bash
dispatch-codex.sh \
  -t "Task description" \
  -n "task-name" \
  -w "$(pwd)" \
  --timeout 3600
```

### Monitor tasks

```bash
codex-tasks list
codex-tasks status <task_id>
```

### Enable daemon (optional)

For automatic processing of completions:

```bash
start-codex-daemon.sh  # Start watcher
stop-codex-daemon.sh   # Stop watcher
```

Daemon logs: `/tmp/codex-results/logs/daemon.log`

## Integration with AGI Heartbeat

If your AGI uses heartbeat, call `process-codex-callbacks` regularly to process task completions.

Example heartbeat snippet:
```bash
process-codex-callbacks --no-mark  # Check without marking
process-codex-callbacks            # Check and mark as processed
```

## Git Integration

When task completes, notifications include:
- Recent commit messages (last 3 commits)
- Modified files list (up to 10 files)

Ensure workspace is a git repository for this feature.

## Troubleshooting

**No Telegram notifications?**
- Check `default_group` is set in config
- Verify OpenClaw Telegram channel is configured

**Tasks not completing?**
- Verify agent `codex` exists: `openclaw agents list`
- Check watcher is running (if using daemon)
- Inspect task output: `cat /tmp/codex-results/tasks/<task_id>/output.txt`

**Permission errors?**
- Ensure result_dir is writable: `mkdir -p /tmp/codex-results && chmod 700 /tmp/codex-results`

## Files

- Scripts: `~/bin/` (dispatch-codex.sh, codex-tasks, runner.py, watcher.py, process-codex-callbacks)
- Config: `~/.config/codex-hook/config.json`
- Data: `/tmp/codex-results/` (tasks, latest.json, pending-wake.json)
- Logs: `/tmp/codex-results/logs/`

## See Also

- Full documentation: `skills/codex-hook/README.md` (in skill repo)
- OpenClaw docs: https://docs.openclaw.ai
