---
name: venus-ble-vibrator
description: "Control a Venus (Cachito) BLE vibrator from natural language. Calls a local HTTP server that broadcasts BLE commands to the toy via macOS CoreBluetooth. Requires hardware setup — see the ToyBridge repo before installing."
---

# Venus BLE Vibrator Control

Control a **Venus / Cachito (小猫爪) BLE vibrator** using natural language through OpenClaw.

> This is a device-specific skill for Cachito-protocol toys. If your device is supported by [Buttplug.io](https://iostindex.com), use the `intiface-control` skill instead — no reverse-engineering needed.

> **macOS only.** The server uses CoreBluetooth.

---

## Setup

Follow the [ToyBridge setup guide](https://github.com/AmandaClarke61/toybridge) — complete Steps 1–3 (discover device ID, configure, verify locally), then start the server:

```bash
uv run 4-bridge/server.py
```

Leave this terminal open. The server runs on **port 8888**.

---

## Commands the agent will use

### Vibrate at intensity

```bash
curl -s -X POST http://host.docker.internal:8888/vibrate \
  -H "Content-Type: application/json" \
  -d '{"intensity": 60}'
```

`intensity`: 0–100 (0 = stop)

### Stop immediately

```bash
curl -s -X POST http://host.docker.internal:8888/stop
```

### Check status

```bash
curl -s http://host.docker.internal:8888/status
```

> If OpenClaw runs natively (not in Docker), replace `host.docker.internal` with `localhost`.

---

## Intensity guide

| Range  | Feel    |
|--------|---------|
| 1–20   | Gentle  |
| 30–50  | Medium  |
| 60–80  | Strong  |
| 90–100 | Maximum |

---

## Preset patterns

| Pattern | What it does |
|---------|-------------|
| `pulse` | Bursts of 80%, 5 times |
| `wave`  | Ramp up 20→100%, then back down, x2 |
| `tease` | 30% → 70% → 100%, escalating, then stop |

Example: *"Run the wave pattern"* or *"Give me a 30-second tease session"*

---

## Agent rules

- Always stop (intensity 0) after a timed session unless user says to keep going
- Do **not** use the `notify` tool — use `bash` with `curl`
- Replace `host.docker.internal` with `localhost` if OpenClaw is not in Docker

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `BT not ready` error | Check Bluetooth is on, grant permission in System Settings → Privacy |
| `connection refused` | Make sure `uv run 4-bridge/server.py` is running |
| Device doesn't respond | Double-check `DEVICE_ID` in `4-bridge/ble_worker.py` matches your Cachito controller |
| Wrong intensity | Values are clamped to 0–100 |
