---
name: giggle-generation-music
description: "Use when the user wants to create, generate, or compose music—whether from text description, custom lyrics, or instrumental background music. Triggers: generate music, write a song, compose, create music, AI music, background music, instrumental, beats."
homepage: https://github.com/storyclaw-official/storyclaw-skills
---

[简体中文](./SKILL.zh-CN.md) | English

# Giggle Music

**Source**: [storyclaw-official/storyclaw-skills](https://github.com/storyclaw-official/storyclaw-skills) · API: [giggle.pro](https://giggle.pro/)

Generates AI music via giggle.pro. Supports simplified and custom modes.

---

## ⚠️ Before Installing — You Must Accept

This skill uses **asynchronous polling**. Installation means you accept:

| Behavior | Details |
|----------|---------|
| **Writes** | `~/.openclaw/skills/giggle-generation-music/logs/` — task state for Cron deduplication |
| **Cron** | Registers 2min-interval poll; removed when task completes |
| **stdout** | Script output forwarded to user as-is (no filtering) |

**Requirements**: `python3`, `GIGGLE_API_KEY` (env), `requests` (pip). **Read and accept the above before installing.**

---

## Environment Setup

**API Key**: Set system environment variable `GIGGLE_API_KEY`. See [SETUP.md](SETUP.md).

---

## Interaction Guide

### Mode Selection (priority: high to low)

| User input | Mode | Description |
|------------|------|-------------|
| User provides full **lyrics** | Custom mode (B) | Must be lyrics, not description |
| User requests instrumental/background music | Instrumental mode (C) | No vocals |
| Other cases (description, style, vocals, etc.) | **Simplified mode (A)** | Use user description as prompt; AI composes |

> **Key rule**: If the user does not provide lyrics, always use **simplified mode A**. Use the user's description exactly as `--prompt`; **do not add or rewrite**. E.g. user says "female voice, 1 min, ancient romance", use `--prompt "female voice, 1 min, ancient romance"` directly.

### Guidance when info is lacking

Only when the user input is very vague (e.g. "generate music" with no description), ask:

```
Question: "What type of music would you like to generate?"
Options: AI compose (describe style) / Use my lyrics / Instrumental
```

---

## Execution Flow (Phase 1 Submit + Phase 2 Cron)

Music generation typically takes 1–3 minutes. Uses "fast submit + Cron poll" two-phase architecture.

> **Important**: **Never** pass `GIGGLE_API_KEY` in exec's `env` parameter. API Key is read from system environment variable. Run the following commands directly.

---

### Phase 1: Submit Task (exec completes in ~10 seconds)

**First send a message to the user**: "Music generation in progress, usually takes 1–3 minutes. Results will be sent automatically."

#### A: Simplified Mode
```bash
python3 scripts/giggle_music_api.py --prompt "user description" --no-wait
```

#### B: Custom Mode
```bash
python3 scripts/giggle_music_api.py --custom \
  --prompt "lyrics content" \
  --style "pop, ballad" \
  --title "Song Title" \
  --vocal-gender female \
  --no-wait
```

#### C: Instrumental
```bash
python3 scripts/giggle_music_api.py --prompt "user description" --instrumental --no-wait
```

Response example:
```json
{"status": "started", "task_id": "xxx", "log_file": "/path/to/log"}
```

**Immediately store task_id in memory** (`addMemory`):
```
giggle-generation-music task_id: xxx (submitted: YYYY-MM-DD HH:mm)
```

---

### Phase 2: Register Cron (2 minute interval, wakeMode: "now")

Use the `cron` tool to register the polling job. **Strictly follow the parameter format; do not modify field names or add extra fields**:

```json
{
  "action": "add",
  "job": {
    "name": "giggle-generation-music-<first 8 chars of task_id>",
    "schedule": {
      "kind": "every",
      "everyMs": 120000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "Music task poll: exec python3 scripts/giggle_music_api.py --query --task-id <full task_id>, handle stdout per Cron logic. If stdout is non-JSON plain text, forward to user as-is and remove Cron. If stdout is JSON, do not send message, keep waiting. If stdout is empty, remove Cron immediately."
    },
    "sessionTarget": "main"
  }
}
```

On each Cron trigger, run:
```bash
python3 scripts/giggle_music_api.py --query --task-id <task_id>
```

**Link return rule**: Audio links in stdout must be **full signed URLs** (with Policy, Key-Pair-Id, Signature query params). Correct: `https://assets.giggle.pro/...?Policy=...&Key-Pair-Id=...&Signature=...`. Wrong: do not return unsigned URLs with only the base path (no query params). The script handles `~` as `%7E`; keep as-is when forwarding.

**Cron trigger handling** (based on exec stdout; all paths exit 0):

| stdout pattern | Action |
|----------------|--------|
| Non-empty plain text (not starting with `{`) | **Forward stdout to user as-is** (no prefix, no changes), **remove Cron** |
| stdout empty | Already pushed, **remove Cron immediately, do not send message** |
| JSON (starts with `{`, has `"status"` field) | Do not send message, do not remove Cron, wait for next poll |

---

## Recovery After Gateway Restart

When the user asks about previous music progress:

1. **task_id in memory** → Run `--query --task-id xxx` directly. **Do not resubmit**
2. **No task_id in memory** → Tell the user, ask if they want to regenerate

---

## Parameter Reference

| Parameter | Description |
|-----------|-------------|
| `--prompt` | Music description or lyrics (required in simplified mode) |
| `--custom` | Enable custom mode |
| `--style` | Music style (required in custom mode) |
| `--title` | Song title (required in custom mode) |
| `--instrumental` | Generate instrumental |
| `--vocal-gender` | Vocal gender: male / female (custom mode only) |
| `--query` | Query task status (Cron poll and manual) |
| `--task-id` | Task ID (use with --query) |
