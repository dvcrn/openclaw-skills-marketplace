---
name: bitaxe-skills
description: "Discover, inspect, and manage solo miners on the same local network, with support for Bitaxe and Nerd or NerdAxe devices. Use when Codex or OpenClaw needs to scan a LAN for miner IPs via /api/system/info, extract and record core status fields, answer questions about miner metrics such as best difficulty, hashrate, temperature, pool settings, or uptime, update basic settings via PATCH /api/system, or restart devices via POST /api/system/restart."
---

# Bitaxe Skills

## Overview

Use the bundled CLI to discover miners on the same subnet, normalize their mixed Bitaxe and Nerd payloads, and safely perform common read and write actions.

Prefer the script over handwritten `curl` when the task involves discovery, field extraction, comparisons, or repeated updates.

## Primary Tool

Use [`scripts/bitaxe_skills.py`](./scripts/bitaxe_skills.py) as the default interface.

Quick examples:

```bash
# Discover miners on the local LAN and save a normalized inventory
python3 scripts/bitaxe_skills.py discover --save /tmp/solo-miners.json

# Probe a specific device and return one metric
python3 scripts/bitaxe_skills.py show 192.168.28.89 --field bestSessionDiff

# Query the raw JSON from one device
python3 scripts/bitaxe_skills.py show luckyminer001 --format raw

# Update a common setting and immediately restart
python3 scripts/bitaxe_skills.py set luckyminer001 fanspeed=95 --restart

# Restart a device
python3 scripts/bitaxe_skills.py restart 192.168.4.1
```

## Workflow

1. Discover first unless the user already supplied a confirmed IP or hostname.
2. Save the normalized discovery result when the user needs the miner list to be reused later.
3. For a question about one metric, run `show` with `--field` instead of dumping the whole payload.
4. For a comparison across miners, run `discover --format json`, then compare the normalized fields.
5. Before writing settings, read the current payload or at least state the target device and intended keys.
6. Restart after writes when the user wants the new configuration applied immediately.

## Field Semantics

Use the normalized fields from the script unless the user explicitly asks for raw JSON keys.

- "本轮最佳难度" or "current round best" maps to `best_session_diff` / raw `bestSessionDiff`.
- "历史最佳难度" or "best ever" maps to `best_diff` / raw `bestDiff`.
- "当前算力" maps to `hash_rate_ghs` / raw `hashRate`.
- "1 分钟算力", "10 分钟算力", "1 小时算力" map to the corresponding normalized rolling fields.
- "池难度" maps to `pool_difficulty`.
- "温度" maps to `temp_c`, while VR temperature maps to `vr_temp_c`.

If the user says only “最佳难度” and does not clarify whether they mean current round or lifetime best, return both values.

## Discovery Rules

- By default, discover on the local private `/24` networks detected from the current machine and also probe `192.168.4.1`.
- If the user gives a specific CIDR, use that instead of guessing.
- Treat success on `GET /api/system/info` as the source of truth for device presence.
- Record at least the normalized IP, type, hostname, model, ASIC model, firmware, pool target, hashrate, temperature, power, and difficulty fields.

## Write Safety

- Use `set` for common settings such as `hostname`, `fanspeed`, `autofanspeed`, `temptarget`, `frequency`, `coreVoltage`, pool URL, pool port, pool user, and display settings.
- The script has a safe allowlist for documented common keys and a small Nerd-specific observed allowlist.
- If the requested key is outside that set, inspect the current payload first and use `--allow-unknown` only when the field is already visible on the device or the user provided firmware-specific evidence.
- Tell the user when a write was sent and whether a restart was also sent.

## References

Read [`references/api-map.md`](./references/api-map.md) when you need the cross-model field map, query heuristics, or update safety notes.
