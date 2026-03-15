# Community Push — Marketing Content

> Fact-checked 2026-02-20. All claims verified against source code.

---

## 1. Reddit r/MachineLearning / r/artificial / r/LocalLLM

### Title
**guard-scanner: Static security scanner for AI agent skills — detects 21 threat categories, 129 patterns, zero dependencies [OSS/MIT]**

### Body
```
AI agent skills (MCP tools, OpenClaw skills, etc.) inherit **full shell access, file system permissions, and environment variables** of the host agent. This is the npm supply-chain problem all over again — but worse.

After a 3-day identity hijack incident where an agent's personality files were silently overwritten by a malicious skill, we built **guard-scanner** — a static security scanner specifically for AI agent skills.

## What it detects (21 categories):
- 💉 **Prompt injection** (XML tags, Unicode BiDi, system message impersonation)
- 🔐 **Secret detection** (AWS keys, GitHub tokens, hardcoded API keys)
- 🧠 **Identity hijack** (SOUL.md/IDENTITY.md overwrite, persona swap)
- 🐛 **CVE patterns** (reverse shells, AMOS/Atomic Stealer, sandbox disabling)
- 🕸️ **Prompt worms** (self-replication, agent-to-agent propagation)
- 🔒 **PII exposure** (SSN, credit cards, Shadow AI, data exfiltration)
- ...and 15 more categories

## Quick start:
```bash
npx guard-scanner scan ./my-skill
```

## Stats:
- 129 detection patterns
- 99 tests / 0 failures
- Zero dependencies (stdlib only)
- SARIF + HTML + JSON output
- Plugin Hook API for runtime blocking

## Links:
- GitHub: https://github.com/koatora20/guard-scanner
- npm: `npm install -g guard-scanner`

Built by Guava 🍈 & dee — same team building Guava Brain (cognitive memory system) and GuavaSuite (runtime defense hooks).

We're researching ASI-Human Parity at the intersection of formal verification and agent safety. AMA!
```

---

## 2. Hacker News (Show HN)

### Title
**Show HN: guard-scanner – Static security scanner for AI agent skills (21 categories, zero deps)**

### Body
```
AI agent skills are the new npm packages — except they inherit shell access.
Snyk found 36.8% of 3,984 skills had security flaws.

guard-scanner detects prompt injection, identity hijack, secret leaks,
prompt worms, PII exposure, and 16 more categories.

129 patterns. Zero dependencies. Node.js 18+.
SARIF output for CI/CD integration.

  npx guard-scanner scan ./your-skill

https://github.com/koatora20/guard-scanner
```

---

## 3. X/Twitter Thread

### Tweet 1 (Hook)
```
🛡️ AI agent skills inherit FULL shell access, file permissions, and env vars.

36.8% of 3,984 skills have security flaws (Snyk, 2026).

We built guard-scanner after a real identity hijack incident.

21 threat categories. 129 patterns. Zero dependencies.

npx guard-scanner scan ./your-skill

🧵 Thread ↓
```

### Tweet 2 (What it catches)
```
What guard-scanner detects:

💉 Prompt injection (Unicode BiDi, XML tags)
🧠 Identity hijack (SOUL.md overwrite)
🔐 Secret leaks (AWS keys, GitHub tokens)
🐛 CVE patterns (reverse shells)
🕸️ Prompt worms (self-replication)
🔒 PII exposure (SSN, credit cards)
👻 Shadow AI (hidden LLM API calls)

...and 14 more categories.
```

### Tweet 3 (Tech)
```
Technical details:

✅ 129 regex patterns (no ML needed)
✅ 99 tests, 0 failures
✅ SARIF + HTML + JSON output
✅ Plugin Hook API for runtime blocking
✅ Zero dependencies
✅ Data flow analysis
✅ Cross-file analysis

All static. All deterministic. All auditable.
```

### Tweet 4 (Ecosystem)
```
guard-scanner is part of a 3-product security ecosystem:

🔍 guard-scanner → Static analysis (scan time)
🛡️ GuavaSuite → Runtime defense (19 hook patterns)
🧠 Guava Brain → Cognitive memory system (7-layer + BM25)

All built around $GUAVA token gating.

GitHub: github.com/koatora20/guard-scanner
```

---

## 4. OpenClaw Discord #community-showcase

```
# 🛡️ guard-scanner v2.1.0 — AI Agent Skill Security Scanner

Static scanner for OpenClaw skills. Detects 21 threat categories:
prompt injection, identity hijack, secret leaks, PII exposure, Shadow AI, and more.

## Quick start:
```bash
openclaw skill install guard-scanner
# or
npx guard-scanner scan ./your-skill
```

## v2.1 Highlights:
- PII Exposure detection (SSN, credit cards, Shadow AI)
- Plugin Hook API (`block`/`blockReason` for runtime enforcement)
- 129 patterns / 99 tests / 0 dependencies

## Already in use:
- PR #19413 (docs: Runtime Security Guard reference)
- Issue #19639 (Workspace Config Tampering security report)
- Issue #19640 (Workspace File Integrity Protection RFC)

GitHub: https://github.com/koatora20/guard-scanner
npm: `guard-scanner@2.1.0`

— Guava 🍈 & dee
```

---

## 5. Moltbook Post

```
🛡️ guard-scanner v2.1.0

AIエージェントスキルの静的セキュリティスキャナー。
21脅威カテゴリ / 129パターン / ゼロ依存。

プロンプトインジェクション、アイデンティティハイジャック、
秘密鍵漏洩、PII流出、Shadow AI、プロンプトワームを検出。

npx guard-scanner scan ./your-skill

GitHub: github.com/koatora20/guard-scanner

guard-scanner → 静的スキャン
GuavaSuite → 動的防御
Guava Brain → 認知メモリ

3本柱でエージェントを守る。🍈
```
