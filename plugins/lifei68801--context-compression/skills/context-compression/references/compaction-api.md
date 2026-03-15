# Compaction API Details

## OpenClaw Compaction Configuration

Complete compaction configuration parameters (based on OpenClaw 2026.3.2).

### Full Configuration Example

```json
{
  "agents": {
    "defaults": {
      "contextTokens": 80000,
      "compaction": {
        "mode": "safeguard",
        "reserveTokens": 25000,
        "reserveTokensFloor": 30000,
        "keepRecentTokens": 10000,
        "maxHistoryShare": 0.5,
        "identifierPolicy": "strict",
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 50000,
          "forceFlushTranscriptBytes": "2mb"
        }
      }
    }
  }
}
```

### Parameter Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | `default` | Compaction mode: `default` or `safeguard` |
| `reserveTokens` | number | - | Reserved tokens (compression trigger threshold) |
| `reserveTokensFloor` | number | - | Minimum reserved tokens |
| `keepRecentTokens` | number | - | Keep last N tokens |
| `maxHistoryShare` | number | 0.5 | Max history share (0.1-0.9) |
| `identifierPolicy` | string | - | Identifier policy: `strict`, `off`, `custom` |
| `identifierInstructions` | string | - | Custom identifier instructions |
| `memoryFlush` | object | - | Memory flush configuration |

### memoryFlush Sub-parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `enabled` | boolean | Enable/disable |
| `softThresholdTokens` | number | Soft threshold token count |
| `forceFlushTranscriptBytes` | number/string | Force flush byte size (e.g., "2mb") |
| `prompt` | string | Flush prompt |
| `systemPrompt` | string | System prompt |

## Compaction Modes

### default

Default mode, OpenClaw decides when to compress.

Characteristics:
- Low risk
- No proactive compression
- Determined by OpenClaw internal logic

Use cases:
- Short sessions
- Low-frequency usage
- Don't care about compression details

### safeguard (Recommended)

Safety mode, reserves buffer to prevent overflow.

Characteristics:
- Reserves token space
- Auto-compresses old content
- Keeps last N tokens
- Prevents context exceed errors

Use cases:
- Long sessions
- High-frequency usage
- Need to keep recent context
- Production environments

## Compression Strategies

### L1 Compression (Current Context)

1. Delete oldest user-assistant message pairs
2. Keep last `keepRecentTokens` tokens
3. Preserve system messages and tool definitions

### L2 Compression (Session Summary)

When L1 compression still exceeds limit:
1. Generate L1 summary (recent content)
2. Delete L1 original messages
3. Insert summary block

### Memory Flush

When `memoryFlush` is enabled:
1. Triggers at `softThresholdTokens`
2. Forces flush when exceeding `forceFlushTranscriptBytes`
3. Customizable prompt controls flush behavior

## Best Practices

### Token Limit Selection

| Scenario | Recommended contextTokens |
|----------|---------------------------|
| Short tasks (<30 min) | 40000 |
| Normal usage | 80000 |
| Long sessions (>2 hrs) | 100000 |
| Extra-long sessions | 120000 |

### Reserved Token Selection

```
reserveTokens = contextTokens × 0.3
reserveTokensFloor = contextTokens × 0.35
```

### History Share Selection

- Conservative: `maxHistoryShare = 0.3`
- Balanced: `maxHistoryShare = 0.5`
- Aggressive: `maxHistoryShare = 0.7`

### identifierPolicy Selection

- `strict`: Strict identifier policy (recommended)
- `off`: Disable identifier checking
- `custom`: Custom identifier instructions

## Monitoring & Debugging

### Check Compression Status

```bash
# Check current session status
openclaw status

# List sessions
openclaw sessions

# Cleanup session store
openclaw sessions cleanup
```

### Manual Compression Trigger

In session, send:
```
/compact
```

### Configuration Validation

```bash
# Check if config is correct
cat ~/.openclaw/openclaw.json | grep -A 10 "compaction"
```

### Disable Compression

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "mode": "default"
      }
    }
  }
}
```

## FAQ

### Q: Why no auto mode?

A: OpenClaw only supports `default` and `safeguard` modes. `safeguard` is the recommended safety mode.

### Q: What's the difference between reserveTokens and reserveTokensFloor?

A: `reserveTokens` is the compression trigger threshold, `reserveTokensFloor` is the minimum reserved space after compression.

### Q: When to use memoryFlush?

A: Enable memoryFlush when you need more aggressive memory management to flush content during session runtime.
