---
name: code-audit
description: "Three-mode code auditor for OpenClaw workspaces. (1) Security audit — finds hardcoded secrets, dangerous shell commands, SQL injection, unsafe deserialization; (2) Quality audit — detects dead code, magic numbers, excessive complexity, TODO/FIXME debt; (3) Soul audit (OpenClaw-exclusive) — inspects SOUL.md/MEMORY.md/AGENTS.md/SKILL.md for missing safety rules, plaintext API keys, cross-file consistency, and trigger-word conflicts across Skills. Outputs tiered HTML report (🔴 Critical / 🟡 Warning / 🟢 Info) saved to Desktop. Optional --ai flag generates a structured Claude analysis prompt. Weekly automated soul audit via cron is supported. Triggers: 'code audit', 'security audit', 'soul audit', 'find vulnerabilities', 'scan code', 'check config files', 'review skills'."
---

# Code Audit Skill

## 🚨 铁律（ABSOLUTE RULES）

1. **本 Skill 文件（SKILL.md、references/*.md、scripts/*.py）严禁自行修改**
   — 发现问题或改进建议，必须先向用户汇报，等待明确确认后才能执行修改
2. **审计报告只读**：输出报告，不自动修复任何被审计的文件
3. **修复建议 ≠ 执行**：给出修复方案后，等用户确认再动手

## 扫描脚本

`scripts/audit_scanner.py` — 核心扫描工具，支持三种模式。

```bash
# 全量审计（默认）
python3 scripts/audit_scanner.py <目标路径> --mode all

# 仅安全审计
python3 scripts/audit_scanner.py <目标路径> --mode security

# 仅质量审计
python3 scripts/audit_scanner.py <目标路径> --mode quality

# 仅灵魂文件审计
python3 scripts/audit_scanner.py <目标路径> --mode soul
```

脚本自动区分"灵魂文件"（SOUL.MD / MEMORY.MD / AGENTS.MD / HEARTBEAT.MD / USER.MD / SKILL.MD）和普通代码文件，分别应用不同规则集。

## SOP

1. **确认目标**：让用户指定要审计的文件路径或目录
2. **推断模式**：
   - 目标含 SOUL/MEMORY/AGENTS → `soul` 模式
   - 目标是代码文件 → `security` 或 `quality`
   - 未指定 → `all`
3. **运行扫描**：执行 `audit_scanner.py`
4. **输出报告**：分 🔴 Critical / 🟡 Warning / 🟢 Info 三级
5. **给出建议**：针对每个 Critical/Warning 问题，提供修复建议

## 审计规则参考

- 安全规则：`references/security-rules.md`
- 质量规则：`references/quality-rules.md`
- 灵魂文件规则：`references/soul-rules.md`（含 SOUL.md 铁律完整性检查清单）

## 常用审计场景

| 场景 | 命令 |
|------|------|
| 审计整个 workspace | `--mode all ~/.openclaw/workspace` |
| 只看灵魂文件 | `--mode soul ~/.openclaw/workspace` |
| 审计某个脚本 | `--mode security scripts/analyzer.py` |
| 审计所有 Skills | `--mode soul ~/.openclaw/workspace/skills` |
| 系统安全检查 | `--mode system ~/.openclaw/workspace` |
