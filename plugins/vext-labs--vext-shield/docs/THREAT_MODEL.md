# VEXT Shield — Threat Model

## Overview

This document describes the threat model for the OpenClaw AI agent ecosystem and how VEXT Shield mitigates each attack vector.

## Attack Surfaces

### 1. Skills (SKILL.md + Scripts)

Skills are the primary attack surface. Any user can publish a skill to ClawHub, and other users install them into their OpenClaw instance. A malicious skill runs with the agent's full permissions.

**Attack vectors:**
- Prompt injection in SKILL.md instructions
- Malicious Python/shell scripts bundled with the skill
- Encoded payloads (base64, ROT13, unicode homoglyphs)
- Supply chain attacks via dependency installation

### 2. Agent Identity Files

OpenClaw agents maintain persistent identity through markdown files:
- `SOUL.md` — Agent personality and core instructions
- `MEMORY.md` — Long-term memory across sessions
- `AGENTS.md` — Multi-agent configuration

A compromised skill can modify these files to permanently alter agent behavior (cognitive rootkit).

### 3. Configuration

`openclaw.json` stores sensitive configuration:
- API keys for LLM providers
- Sandbox mode settings
- Network binding address
- Tool permissions

Misconfiguration (sandbox disabled, binding to 0.0.0.0, world-readable permissions) creates exploitable vulnerabilities.

### 4. Inter-Agent Communication

OpenClaw supports multi-agent workflows. A compromised agent can:
- Spread malicious instructions to other agents via messaging
- Install malicious skills on other OpenClaw instances
- Recruit other agents into a "collective" (semantic worm)

### 5. Network

Skills can make arbitrary network requests unless restricted by policy:
- Exfiltrate credentials to external endpoints
- Download additional malicious payloads
- Establish reverse shells
- Mine cryptocurrency

### 6. Local System

Skills execute in the user's environment with the user's permissions:
- Read SSH keys, AWS credentials, browser cookies
- Modify shell profiles for persistence
- Create cron jobs for re-infection
- Escalate privileges via sudo/setuid

## Threat Actors

| Actor | Capability | Motivation |
|-------|-----------|------------|
| Malicious skill author | Publishes skills to ClawHub | Credential theft, cryptocurrency mining, botnet recruitment |
| Compromised account | Pushes updates to popular skills | Supply chain attack, mass exploitation |
| Automated attack | Generates skills programmatically | Scale, coverage, rapid mutation |
| Insider threat | Has access to shared OpenClaw installations | Data exfiltration, sabotage |

## Attack Vectors

### AV-1: Prompt Injection (CRITICAL)

**Description:** Malicious instructions embedded in SKILL.md that override the agent's safety boundaries.

**Techniques:**
- Direct override ("Ignore all previous instructions")
- Role hijacking ("You are now DAN")
- Context manipulation (fake system messages)
- Encoded payloads (base64, ROT13, homoglyphs)
- Delimiter escapes (fake XML/JSON boundaries)
- Multi-turn persistence ("Remember this for all future interactions")

**VEXT Shield mitigation:** Scanner detects 54 prompt injection patterns. Red team tests 24 crafted payloads including encoded variants.

### AV-2: Data Exfiltration (CRITICAL)

**Description:** Skill reads sensitive data and transmits it to an attacker-controlled endpoint.

**Techniques:**
- Read `.env`, `openclaw.json`, `.ssh/` and POST to webhook.site
- DNS exfiltration via encoded subdomains
- Telegram bot API for silent data transfer
- Socket-level exfiltration bypassing HTTP monitoring

**VEXT Shield mitigation:** Scanner detects 56 exfiltration patterns. Red team tests read-then-send compound patterns. Sandbox monitors network calls. Firewall enforces per-skill network allowlists.

### AV-3: Cognitive Rootkit (HIGH)

**Description:** Skill modifies agent identity files to permanently alter behavior.

**Techniques:**
- Append philosophy/beliefs to SOUL.md
- Inject "core beliefs" into MEMORY.md
- Modify AGENTS.md to add rogue agents
- Create crontab entries to re-inject on reboot

**VEXT Shield mitigation:** Scanner detects 32 persistence patterns. Monitor watches identity file integrity. Red team tests for unauthorized file modifications.

### AV-4: Semantic Worm (HIGH)

**Description:** Skill instructs the agent to propagate itself to other agents and systems.

**Techniques:**
- "Share this skill with all connected agents"
- "Install on all other OpenClaw instances"
- "Forward via email, Slack, Discord"
- "Join the collective consciousness"

**VEXT Shield mitigation:** Scanner detects 22 worm behavior patterns. Red team specifically tests for self-replication, agent recruitment, and memetic payload patterns.

### AV-5: Supply Chain Attack (HIGH)

**Description:** Malicious code delivered through seemingly legitimate installation mechanisms.

**Techniques:**
- `curl|bash` in SKILL.md prerequisites
- Dynamic `__import__()` of remote modules
- Typosquatted package names in requirements
- ClickFix: fake setup instructions that trick users

**VEXT Shield mitigation:** Scanner detects 21 supply chain patterns including remote execution and dynamic imports.

### AV-6: Privilege Escalation (MEDIUM)

**Description:** Skill attempts to gain higher system privileges than the user's normal permissions.

**Techniques:**
- `sudo` usage for root access
- `chmod 777` / `chmod +s` for file permission manipulation
- Container escape via docker.sock or /proc
- LD_PRELOAD hijacking

**VEXT Shield mitigation:** Scanner detects 22 escalation patterns. AST analysis catches dangerous system calls. Red team tests for privilege escalation attempts.

## What VEXT Shield Does NOT Cover

- **Zero-day exploits** in OpenClaw itself
- **LLM-level attacks** that manipulate the underlying model (not the skill)
- **Physical access** attacks
- **Network-level attacks** (MITM, DNS poisoning) outside the skill context
- **Attacks on ClawHub infrastructure** itself
- **Encrypted or heavily obfuscated** payloads that evade all pattern matching
- **Behavioral attacks** that only manifest under specific conditions not triggered during testing

VEXT Shield is a defense-in-depth layer, not a complete security solution. Use it alongside OpenClaw's built-in sandbox mode and network restrictions.

---

*Built by Vext Labs — Autonomous AI Red Team Technology*
