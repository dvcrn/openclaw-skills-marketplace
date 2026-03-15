---
name: openclaw-optimizer
description: "OpenClaw token cost reduction, performance tuning, and security hardening guide. Use when asked to optimize OpenClaw, reduce token costs, fix missing capabilities, tune model/cache/search settings, or harden security (firewall, permissions, credential audit)."
---

# OpenClaw Optimizer

Battle-tested optimizations for OpenClaw instances. Reduce token costs, fix capability gaps, tune performance, harden security.

## The Token Cost Formula
`Token spend = (input + output) × calls/day × model price`

Every workspace file loaded at session start multiplies across every call. Keep them lean.

---

## Step 1 — Audit Current State

```bash
# Check workspace file token usage (macOS/Linux)
for f in AGENTS.md SOUL.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md MEMORY.md; do
  p="$HOME/.openclaw/workspace/$f"
  [ -f "$p" ] && echo "$f : ~$(($(wc -c < "$p") / 4)) tokens"
done
cat ~/.openclaw/openclaw.json
```

---

## Step 2 — SOUL.md Core Constraints

Ensure these principles are present in `SOUL.md`. They are system-level behavioral guarantees, not style preferences:

| Constraint | Rule |
|---|---|
| **脚本优先** | 有现成脚本能解决的，必须调脚本，不允许用提示词绕过脚本自己手写 API 或手拼数据结构。只有脚本真的无法覆盖的场景，才用提示词驱动 LLM，且要在执行前说明原因。 |
| **API 优先** | 能用 API 的情况下优先用 API，不要直接操作浏览器。只有 API 走不通时才考虑浏览器，且要先询问用户。 |
| **做完才说完** | 说"完成了"之前先验证结果，不只是文字改了。 |
| **死磕到底** | 遇到问题试 10 种方法再说放弃。**例外**：当前任务有硬约束（SOP 铁律、安全规则）时，遇到阻塞必须立即停止并上报，禁止自行变通绕过约束。 |

Add to `SOUL.md` if missing:
```bash
grep -q "脚本优先" ~/.openclaw/workspace/SOUL.md || cat >> ~/.openclaw/workspace/SOUL.md << 'EOF'
- **脚本优先**：有现成脚本能解决的，必须调脚本，不允许用提示词绕过脚本自己手写 API 或手拼数据结构。脚本是确定性保证，提示词是不可靠的。只有脚本真的无法覆盖的场景，才用提示词驱动 LLM 处理，且要在执行前说明原因。
EOF
```

---

## Step 3 — Slim Down Workspace Files

Target: AGENTS.md ≤ 200 tokens · SOUL.md ≤ 200 tokens · MEMORY.md ≤ 2000 tokens

- AGENTS.md — keep only: session startup flow, memory structure, WAL protocol, safety rules. Remove duplicates already covered by system prompt (group chat, proactive work, etc.)
- SOUL.md — compress to concise bullet points
- MEMORY.md — remove outdated entries
- Periodically clean `memory/YYYY-MM-DD.md` logs older than 30 days

Saving 1000 tokens = ~$45/month at Sonnet × 100 calls/day.

---

## Step 3 — Key `openclaw.json` Settings

| Setting | Value | Why |
|---------|-------|-----|
| `cacheRetention` | `"long"` | Prompt Caching — saves up to 90% on repeated context |
| `contextPruning` | `cache-ttl / 55m` | Auto-clears history; align ttl with heartbeat interval |
| `compaction.memoryFlush` | enabled | Auto-saves key content before compaction |
| `heartbeat.every` | `"55m"` | Keeps cache warm between sessions |
| `memorySearch.provider` | `"gemini"` + `gemini-embedding-001` | Best semantic recall, especially for non-English |
| Web Search | `gemini-2.5-flash` | Free tier, replaces Brave |
| `tools.profile` | `"full"` | Unlocks web_search, browser, nodes and all tools |

**Get a free Gemini API Key:** https://aistudio.google.com/apikey (1500 requests/day free)

> ⚠️ `heartbeat.quiet` is not supported — throws `Unrecognized key` error. Do not add it.  
> ⚠️ `tools.profile` must be `"full"`. Defaults (`coding` / `messaging`) silently disable most tools.  
> ⚠️ Set `contextPruning.ttl` to match `heartbeat.every` (both `"55m"`) to keep cache warm.

---

## Step 4 — Security Hardening

### Checklist

| Item | Command / Location | Expected |
|------|-------------------|----------|
| gateway.bind | `openclaw.json` | `"loopback"` (not `"0.0.0.0"`) |
| gateway.auth.mode | `openclaw.json` | `"token"` |
| gateway.auth.token length | check config | ≥ 32 chars |
| openclaw.json permissions | `ls -la ~/.openclaw/openclaw.json` | `-rw-------` |
| macOS firewall | see below | Enabled |
| tailscale | `tailscale status` | Off unless intentional |

### Enable macOS Application Firewall

```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
# Verify:
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

**Trade-off:** First run of any new app that listens on a port will trigger a system dialog. Allow or deny as needed. Can be disabled anytime:
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
```

### Fix config file permissions if needed

```bash
chmod 600 ~/.openclaw/openclaw.json
chmod 700 ~/.openclaw/credentials
```

---

## Step 5 — Essential Skills

```bash
# Proactive behavior + self-improvement
npx skills add halthelobster/proactive-agent@proactive-agent -g -y
```

**Avoid:**
- `bdi-mental-states` — academic only, not useful for personal assistants
- `autonomous-agents` — reference manual, limited practical value

**Optional (after memory files exceed 5000+ tokens):**
```bash
npm install -g https://github.com/tobi/qmd
```

---

## Step 6 — Model Switching

```
/model opus    # Switch to Opus (complex / reasoning tasks)
/model sonnet  # Switch back to Sonnet (daily use)
```

Set model aliases in `openclaw.json`:
```json
"agents": {
  "defaults": {
    "models": {
      "amazon-bedrock/global.anthropic.claude-opus-4-6-v1": { "alias": "opus", "params": { "cacheRetention": "long" } },
      "amazon-bedrock/global.anthropic.claude-sonnet-4-6": { "alias": "sonnet", "params": { "cacheRetention": "long" } }
    }
  }
}
```

---

## Step 7 — Verify

```bash
# macOS/Linux
node -e "const fs=require('fs'); eval('('+fs.readFileSync(process.env.HOME+'/.openclaw/openclaw.json','utf8')+')'); console.log('Config valid ✅')"
```

Check Prompt Cache hit rate after a few conversations with `/status`.

---

## Priority Order (highest impact first)

1. **tools.profile → full** (broken without this)
2. **SOUL.md core constraints** (脚本优先 / API 优先 / 做完才说完)
3. Slim workspace files
4. Prompt Caching (`cacheRetention: long`)
5. Gemini web search (fixes search)
6. Gemini embeddings (fixes non-English memory recall)
7. **Security hardening** (firewall + permissions audit)
8. Context Pruning + Compaction (ttl aligned to heartbeat)
9. Install proactive-agent
10. qmd (after files accumulate)
