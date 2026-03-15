---
name: context-compression
description: "Prevent context overflow with automatic session truncation and memory preservation. Never lose important conversations again. Features: token-based trimming, AI fact extraction, preference lifecycle management. Use when: (1) context window exceeds limit (2) setting up memory hierarchy (3) managing user preferences with expiry."
---

# Memory Compression

**Prevent context overflow. Never lose important conversations.**

## The Problem

OpenClaw sessions grow indefinitely. When context exceeds the model's limit:
- New sessions fail to load
- Important information is lost
- Cron tasks inherit huge context and crash

## The Solution

Automatic session truncation + hierarchical memory preservation:
1. **Trim sessions** before they exceed limits
2. **Extract facts** (preferences, decisions, tasks) before trimming
3. **Preserve memory** through layered storage (MEMORY.md, daily notes, summaries)

---

## 🚀 Quick Start

### Step 1: Check Configuration

```bash
cat ~/.openclaw/workspace/.context-compression-config.json 2>/dev/null
```

### Step 2: Configure (Interactive)

When this skill loads, it guides you through:

| Question | Options | Recommended |
|----------|---------|-------------|
| Context preservation | 20k/40k/60k tokens | 40k |
| Truncation frequency | 10min/30min/1h | 10min |
| Skip active sessions | Yes/No | Yes |
| Daily summaries | Yes/No | No |

### Step 3: Verify

```bash
ls -la ~/.openclaw/workspace/.context-compression-config.json
ls -la ~/.openclaw/workspace/skills/context-compression/scripts/truncate-sessions-safe.sh
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Context Budget: ~80k tokens              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  L4: MEMORY.md (~5k)      ← User preferences, key facts    │
│  L3: Daily summaries (~10k) ← Compressed older sessions    │
│  L2: Recent sessions (~25k) ← Last N session files         │
│  L1: Current session (~40k) ← Active conversation          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key principle**: L4 > L3 > L2 in priority. Always preserve MEMORY.md.

---

## 🔧 How It Works

### Session Truncation
- Runs in background (independent of agent)
- Trims to last N tokens per session
- Skips active sessions (.lock files)
- Preserves JSONL line integrity

### Fact Extraction
- Detects keywords: 重要/决定/TODO/偏好, important/decision/must
- Extracts to MEMORY.md before truncation
- Categories: [偏好], [决策], [任务], [时间], [关系], [重要]

### Preference Lifecycle
- **Short-term** (1-7 days): Tag with `@YYYY-MM-DD`
- **Mid-term** (1-4 weeks): Auto-expire via daily check
- **Long-term**: Permanent in MEMORY.md

---

## 📜 Scripts

| Script | Purpose |
|--------|---------|
| `truncate-sessions-safe.sh` | Trim session files safely |
| `extract-facts-enhanced.sh` | AI-powered fact extraction |
| `check-preferences-expiry.sh` | Remove expired preferences |
| `check-context-health.sh` | Report context status |

---

## ⚙️ Configuration File

`~/.openclaw/workspace/.context-compression-config.json`:

```json
{
  "version": "2.3",
  "maxTokens": 40000,
  "frequencyMinutes": 10,
  "skipActive": true,
  "enableSummaries": false,
  "strategy": "priority-first",
  "priorityKeywords": [
    "重要", "决定", "记住", "TODO", "偏好",
    "important", "remember", "must", "deadline", "decision"
  ]
}
```

---

## ✅ Verification Checklist

- [ ] Config file exists
- [ ] Scripts are executable
- [ ] MEMORY.md exists and is current
- [ ] Truncation log shows recent runs: `tail ~/.openclaw/logs/truncation.log`

---

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| Context still exceeded | Reduce maxTokens, check truncation log |
| Memory not persisting | Verify real-time writing in AGENTS.md |
| Summaries not generated | Check daily notes exist in memory/ |

---

## 📚 Related

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Hierarchical Memory Architecture](references/memory-architecture.md)
