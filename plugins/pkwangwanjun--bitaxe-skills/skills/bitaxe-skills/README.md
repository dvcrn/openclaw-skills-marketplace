# bitaxe-skills

## 🚀 One-Line Install (OpenClaw)

```bash
npx skills add https://github.com/pkwangwanjun/bitaxe-skills --skill bitaxe-skills
```

`bitaxe-skills` is a Codex skill for discovering, inspecting, and managing Bitaxe, Nerd, and NerdAxe solo miners on a local network.

## What It Does

- Discovers miners on the current LAN with `GET /api/system/info`
- Normalizes mixed Bitaxe and Nerd payloads into one common schema
- Reads a single metric, a normalized record, or the raw JSON payload from a device
- Updates common settings with `PATCH /api/system`
- Restarts miners with `POST /api/system/restart`

## Repository Layout

- `SKILL.md`: Skill metadata and operational workflow
- `agents/openai.yaml`: UI-facing skill metadata
- `scripts/bitaxe_skills.py`: Main CLI entrypoint
- `references/api-map.md`: Field mapping and writable setting notes

## Requirements

- Python 3
- Network access to the miner subnet
- Devices that expose the Bitaxe-compatible REST API

## Usage

```bash
# Discover miners on the LAN
python3 scripts/bitaxe_skills.py discover --save /tmp/solo-miners.json

# Show one field from one miner
python3 scripts/bitaxe_skills.py show 192.168.28.89 --field bestSessionDiff

# Query the raw JSON payload
python3 scripts/bitaxe_skills.py show luckyminer001 --format raw

# Update a setting and restart
python3 scripts/bitaxe_skills.py set luckyminer001 fanspeed=95 --restart

# Restart a miner
python3 scripts/bitaxe_skills.py restart 192.168.4.1
```

## Skill Name

The canonical skill trigger name is `$bitaxe-skills`.

## Notes

- The CLI uses only the Python standard library.
- The discovery command auto-detects private local networks and also probes `192.168.4.1` by default.
- Normalized and raw fields are documented in `references/api-map.md`.
