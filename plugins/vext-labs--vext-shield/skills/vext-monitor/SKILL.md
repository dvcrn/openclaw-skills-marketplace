---
name: vext-monitor
description: Runtime behavioral monitor that watches for unauthorized file access, network egress, memory manipulation, and suspicious process activity by OpenClaw skills. Built by Vext Labs.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🛡️"
    requires:
      bins: ["python3"]
---

# VEXT Monitor

Real-time behavioral monitoring for your OpenClaw installation. Watches for unauthorized file access, suspicious network activity, identity file tampering, and rogue processes.

## Usage

- "Monitor my skills for suspicious activity"
- "Check if any skills have modified my SOUL.md"
- "Run a security monitor check"
- "Watch for unauthorized changes"

## How It Works

1. Hashes SOUL.md, MEMORY.md, AGENTS.md, and openclaw.json at startup
2. Monitors for file modifications to identity and config files
3. Checks for sensitive file access (.env, SSH keys, cookies, keychains)
4. Scans for suspicious network connections
5. Detects new background processes that may have been spawned by skills
6. Logs all findings to ~/.openclaw/vext-shield/monitor.log

## Rules

- Only perform read-only monitoring — never modify monitored files
- Log all findings with timestamps
- Do not interfere with legitimate skill operations
- Do not transmit monitoring data externally

## Safety

- This skill only reads files and system state — no modifications
- No network requests are made
- Monitoring data stays local in ~/.openclaw/vext-shield/
- Can be run as a one-shot check or on a schedule
