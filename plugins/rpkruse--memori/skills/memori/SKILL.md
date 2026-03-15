---
name: memori
description: "Memori"
---

# Memori - Automatic Long-term Memory for OpenClaw

Persistent memory integration that works automatically in the background. No commands, no manual management - just install and your agent remembers.

## Core Workflow

Memori operates automatically via OpenClaw lifecycle hooks:

### Before Each Response (Intelligent Recall)
Memori automatically:
1. Searches for relevant past conversations
2. Injects matching context into the agent's prompt
3. Enables continuity across sessions - **no search command needed**

### After Each Response (Advanced Augmentation)
Memori automatically:
1. Captures the conversation turn (user + assistant)
2. Sends to Memori backend for intelligent processing
3. Extracts facts, deduplicates, and indexes - **no storage command needed**

**You don't manage memory - it just works.**

## Installation

```bash
openclaw plugins install @memorilabs/openclaw-memori
```

## Configuration

Add to your `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "openclaw-memori": {
        "enabled": true,
        "config": {
          "apiKey": "${MEMORI_API_KEY}",
          "entityId": "openclaw-user"
        }
      }
    }
  }
}
```

### Configuration Options

- **apiKey** (required): Your Memori API key from [memorilabs.ai](https://app.memorilabs.ai/signup)
- **entityId** (required): Unique identifier for this user's memories

Get your API key: https://app.memorilabs.ai/signup

## How It Works

Memori uses OpenClaw lifecycle hooks for automatic operation:

```javascript
before_prompt_build → intelligent-recall (inject relevant memories)
agent_end → advanced-augmentation (store conversation turn)
```

**Zero commands needed** - memory works automatically in the background.

## What Memori Does Automatically

**Backend Intelligence** (handled by Memori SDK):
- Intelligent fact extraction from conversations
- Automatic deduplication and merging
- Semantic ranking by relevance
- Temporal decay (older memories fade)
- Privacy filtering (no secrets stored)

**Plugin Role** (what runs in OpenClaw):
- Pipes conversations to Memori backend
- Injects recalled memories into prompts
- Zero configuration after setup

**You don't configure what to capture - the backend handles it.**

## Verification

Check that the plugin is working:

```bash
# Verify plugin is installed
openclaw plugins list

# Check for Memori logs in gateway output
# Look for "[Memori]" prefixed entries
```

## Quota Management

Check your current API quota:

```bash
memori quota
```

**Example output:**
```
 __  __                           _
|  \/  | ___ _ __ ___   ___  _ __(_)
| |\/| |/ _ \ '_ ` _ \ / _ \| '__| |
| |  | |  __/ | | | | | (_) | |  | |
|_|  |_|\___|_| |_| |_|\___/|_|  |_|
                  perfectam memoriam
                       memorilabs.ai

+ Maximum # of Memories: 100
+ Current # of Memories: 0

+ You are not currently over quota.
```

Use this to monitor usage and upgrade if needed.

## Performance

- **Automatic deduplication** prevents memory bloat  
- **Semantic ranking** ensures relevant memories surface first
- **Zero manual commands** - always-on background operation

## Privacy & Data Handling

**Transparent data flow:**
- ✅ Conversations sent to Memori backend (https://api.memorilabs.ai)
- ✅ Data encrypted in transit and at rest
- ✅ You control data via your API key and entityId
- ✅ Delete memories anytime via Memori dashboard
- ✅ No third-party sharing
- ⚠️ Only install if you trust Memori with conversation data

Backend automatically filters sensitive data (API keys, passwords, secrets).

For details: [Memori Privacy Policy](https://memorilabs.ai/privacy)

## Memory Persistence

Memories persist across:
- Session restarts
- Gateway restarts
- System reboots
- OpenClaw upgrades

All storage handled by Memori backend - no local database needed.

## Troubleshooting

**Plugin not loading:**
- Verify `enabled: true` in openclaw.json
- Check API key: `echo $MEMORI_API_KEY`
- Restart gateway: `openclaw gateway restart`

**No memories captured:**
- Check gateway logs for `[Memori]` errors
- Verify API endpoint reachable
- Test API key: `memori quota`

**Memories not recalled:**
- Ensure `entityId` is consistent across sessions
- Verify memories exist: `memori quota` shows count > 0
- Check logs for recall errors

**Quota exceeded:**
- Run `memori quota` to check usage
- Upgrade at [memorilabs.ai](https://app.memorilabs.ai/)
- Or clear old memories via dashboard

## Learn More

- **npm Package**: https://www.npmjs.com/package/@memorilabs/openclaw-memori
- **GitHub**: https://github.com/MemoriLabs/Memori
- **Documentation**: https://memorilabs.ai/docs/memori-cloud/openclaw/overview/
- **API Dashboard**: https://app.memorilabs.ai/
- **Support**: [GitHub Issues](https://github.com/MemoriLabs/Memori/issues)

## Notes

This skill teaches the agent about the Memori plugin. The plugin must be installed separately via npm. Once installed, memory capture and recall happen automatically - no commands needed.