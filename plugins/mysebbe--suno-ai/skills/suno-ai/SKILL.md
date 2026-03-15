---
name: suno-ai
description: "Generate music via Suno with the local browser-backed flow. Use when the user wants Suno songs, instrumental tracks, lyric-based songs, Suno credit checks, or Suno session recovery."
---

# Suno AI

Use this skill directly from the chat agent when the user wants music generation or a Suno credit check. Do not delegate ordinary Suno generation to a coding agent.

## Default flow

Run the skill from its own directory:

```bash
cd /home/sebbe/.openclaw/workspace-chat/skills/suno-ai
./run_generate_song.sh ...
```

The generator uses:

- the runtime Python environment in `~/.suno/venv`
- the persistent browser profile in `~/.suno/chrome_gui_profile`
- the normalized cookie header in `~/.suno/suno_cookie.txt`
- raw cookies in `~/.suno/cookies.json`
- the browser-backed `v2-web` Suno flow with hCaptcha solving
- output files in `/home/sebbe/.openclaw/workspace-chat/output_mp3`
- debug logs and screenshots in `~/.suno/debug`

## Common commands

Simple prompt:

```bash
./run_generate_song.sh \
  --prompt "short synthwave instrumental with bright arpeggios" \
  --instrumental \
  --json
```

Lyrics + style:

```bash
./run_generate_song.sh \
  --lyrics "In the wires, in the code..." \
  --tags "cyberpunk, dark synth" \
  --title "Digital Soul" \
  --json
```

Credits only:

```bash
./run_generate_song.sh --credits-only --json
```

Validate imported cookies:

```bash
./run_generate_song.sh \
  --import-cookies /path/to/export.txt \
  --validate-session \
  --json
```

## Session recovery

If generation fails because the Suno browser session is stale:

1. Make sure the local cookie receiver service is running at `http://127.0.0.1:8765/suno/cookies`.
2. Export fresh cookies from the local Suno extension while logged in.
3. Retry the generation command.

Do not rebuild the login flow unless the user explicitly asks to repair the skill.

Runtime cookies, logs, screenshots, and other session artifacts must stay under `~/.suno`, not inside the skill folder.

## Reply format

When generation succeeds, report:

- track title
- clip ids
- saved MP3 paths
- remaining Suno credits
