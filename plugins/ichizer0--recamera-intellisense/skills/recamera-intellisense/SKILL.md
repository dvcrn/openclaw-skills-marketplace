---
name: recamera-intellisense
description: "Registers reCamera devices, configures AI detection models/rules/schedules, monitors and clears detection events, fetches event snapshots, and runs manual image/video capture. Uses local Python CLI scripts with JSON I/O. Triggers on camera onboarding, detection setup, event polling, snapshot capture, or reCamera automation tasks."
---

# reCamera Intellisense

## Requirements

- `python3` (no external packages)
- Reachable reCamera HTTP API (default port `80`)
- Credentials stored in `~/.recamera/devices.json` (created automatically; declared in skill metadata)

## Security considerations

- **Credential storage**: Device tokens are stored in `~/.recamera/devices.json`. Protect this file with appropriate permissions (`chmod 600`) and do not place unrelated secrets there.
- **Plain HTTP transport**: Communication to devices uses HTTP (port 80) by default — data including images and tokens travels unencrypted. Configure HTTPS on your devices if operating on untrusted networks.
- **Trusted networks only**: The skill polls devices and downloads snapshot/image files. Only use it with cameras on networks you trust.
- **Camera-specific tokens**: Use dedicated per-camera tokens (`sk_xxx`). Do not reuse tokens shared with cloud services.
- **Source review**: The bundle includes full Python sources under `scripts/`. Review them to verify behavior matches your expectations before granting autonomous execution.

## Scripts

All scripts live under `{baseDir}/scripts` and accept **one JSON object** as CLI argument (optional for `detect_local_device` and `list_devices`).

- **`device_manager.py`**: add/update/remove/list/get device credentials, file download
- **`detection_manager.py`**: models, schedule, rules, events, event-image fetch
- **`capture_manager.py`**: capture status/start/stop, one-shot image capture

**Full API signatures and CLI schemas**: See [REFERENCE.md](REFERENCE.md)

## Agent rules

1. Always pass complete JSON; never use interactive prompts.
2. Use exactly one of `device_name` (preferred) or inline `device`.
3. Auth token format: `sk_xxx` (from Web Console → Device Info → Connection Settings → HTTP/HTTPS Settings).
4. To detect by label name: call `get_detection_models_info`, map name → label index, use index in `label_filter`.
5. Poll `get_detection_events` every 1–10s; pass `start_unix_ms` for incremental reads.
6. Prefer event metadata first; fetch images only when needed.
7. CLI output: success = JSON on stdout (mutating commands may produce no stdout, check exit code `0`); failure = actionable stderr. On error, surface stderr and provide one concrete fix.

## Execution checklist

Copy and track for multi-step tasks:

```text
reCamera Task Progress
- [ ] Resolve device (device_name or inline device)
- [ ] Validate JSON arguments
- [ ] Run CLI command
- [ ] If polling, checkpoint start_unix_ms
- [ ] Handle errors with one fix suggestion
```

## CLI quickstart

Run from `{baseDir}`:

```bash
python3 scripts/device_manager.py add_device '{"name":"cam1","host":"192.168.1.100","token":"sk_xxxxxxxx"}'
python3 scripts/device_manager.py list_devices
python3 scripts/detection_manager.py get_detection_models_info '{"device_name":"cam1"}'
python3 scripts/detection_manager.py set_detection_model '{"device_name":"cam1","model_id":0}'
python3 scripts/detection_manager.py get_detection_events '{"device_name":"cam1"}'
python3 scripts/detection_manager.py clear_detection_events '{"device_name":"cam1"}'
python3 scripts/detection_manager.py fetch_detection_event_image '{"device_name":"cam1","snapshot_path":"/mnt/.../event.jpg","local_save_path":"./event.jpg"}'
python3 scripts/capture_manager.py capture_image '{"device_name":"cam1","local_save_path":"./capture.jpg"}'
```

## Python pattern (long-running automation)

```python
from datetime import datetime, timezone
import sys
sys.path.append("./scripts")

from device_manager import get_device
from detection_manager import get_detection_events

device = get_device("cam1")
events = get_detection_events(device, start_unix_ms=int(datetime.now(timezone.utc).timestamp() * 1000))
```

Use a loop with checkpointed `start_unix_ms` for incremental polling.

## Workflows

### Onboard a device

1. `add_device` with host + token.
2. `list_devices` to verify.

### Configure object detection by name

1. `get_detection_models_info` → map object name to label index.
2. `set_detection_model`.
3. `set_detection_rules` with `label_filter` containing the index.
4. `clear_detection_events` to start fresh.

### Monitor events

1. Poll `get_detection_events` with `start_unix_ms` every 1–10s.
2. Track last timestamp for next poll.
3. Fetch images only when needed via `fetch_detection_event_image`.

### On-demand snapshot

- **CLI**: `capture_image` with `local_save_path` → returns `{capture, saved_path, bytes}`.
- **Python**: `capture_image` → persist returned `content` bytes.
- **Alternative**: `fetch_detection_event_image` with `local_save_path`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| 401/403 auth error | Re-copy token from Web Console |
| Timeout / connection refused | Verify host, network path, device power |
| Schedule rejected | Use `Day HH:MM:SS` format |
| Empty rules or events | Enable rule/storage prerequisites; check region filter; poll more frequently |
| Image fetch failed | Use fresh `snapshot_path`; data may rotate out |
| Import errors in Python mode | Run from `{baseDir}`; append `./scripts` to `sys.path` |
