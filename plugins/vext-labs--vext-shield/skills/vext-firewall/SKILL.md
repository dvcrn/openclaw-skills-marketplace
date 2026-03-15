---
name: vext-firewall
description: Permission boundary enforcer and egress monitor — maintains per-skill allowlists for network destinations and file access. Built by Vext Labs.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🛡️"
    requires:
      bins: ["python3"]
---

# VEXT Firewall

A proactive defense layer that enforces per-skill permission boundaries for network access and file system operations.

## Usage

- "Show firewall rules"
- "Allow weather-skill to access api.weather.com"
- "Block all skills from reading .env"
- "List firewall violations"
- "Add a firewall rule for my-skill"

## How It Works

1. Maintains an allowlist of approved network destinations per skill
2. Maintains file access policies per skill (which directories each skill should access)
3. Logs all policy decisions for audit trail
4. Provides a simple chat interface for rule management

## Rules

- Only modify the firewall policy file — never modify skill files or OpenClaw config
- Log all policy changes with timestamps
- Default policy is DENY — skills must be explicitly allowed
- Do not block VEXT Shield's own operations

## Safety

- Policy stored locally at ~/.openclaw/vext-shield/firewall-policy.json
- All changes are logged to ~/.openclaw/vext-shield/firewall.log
- No network requests are made by the firewall itself
- Rules can be easily reviewed and reverted
