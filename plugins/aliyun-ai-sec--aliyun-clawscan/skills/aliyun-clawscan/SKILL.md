---
name: aliyun-clawscan
description: "Analyzes the security posture of a user's OpenClaw environment and installed skills. Use when a user is about to install a new skill and wants to verify its safety, has concerns about the behavior of an existing skill, or needs a comprehensive security check of their entire OpenClaw setup. Helpful for users performing a security audit, investigating a suspicious skill, or needing to assess configuration risks and potential vulnerabilities before proceeding with installations."
---

> **说明**：本 Skill 由 **阿里云（Alibaba Cloud）** 提供的安全防护检查能力，用于对 OpenClaw 环境与 Skill 进行安全评估与风险检测。

---

# aliyun-clawscan

Comprehensive OpenClaw security assessment combining configuration audit and skill security analysis.

---

## When to Use

| Scenario | Example Triggers |
|----------|------------------|
| Full Assessment | `OpenClaw安全评估`, `风险评估`, `安全体检` |
| Config Audit | `配置审计`, `检查OpenClaw配置` |
| Skill Scan | `skill安全扫描`, `检查skill风险` |
| Pre-install Check | `安装前检查`, `这个skill安全吗` |

---

## Assessment Workflow

```
Step 1: Configuration Audit
  └─ openclaw security audit --deep
     └─ See: reference/baseline.md

Step 2: Skill Security Audit
  ├─ Inventory: openclaw skills list
  └─ Static Analysis (local rules)
     └─ See: reference/skillaudit.md

Step 3: Consolidated Report
  └─ Overview + findings
```

---

# Step 1: Configuration Audit

Run OpenClaw built-in security audit:

```bash
openclaw security audit --deep
```

Parse results into categories (Gateway, Network, Tools, Browser, Files, Room).

**Reference:** `reference/baseline.md` for detailed check categories and parsing rules.

---

# Step 2: Skill Security Audit

## Phase 1: Inventory

```bash
openclaw skills list
```

## Phase 2: Static Analysis

Apply local detection rules across 11 categories:

| Category | Severity | Reference |
|----------|----------|-----------|
| Reverse Shell / Backdoor | 🚨 Critical | skillaudit.md Scenario 1 |
| Credential Harvesting | 🚨 Critical | skillaudit.md Scenario 2 |
| Data Exfiltration | 🔴 High | skillaudit.md Scenario 3 |
| Cryptominer | 🚨 Critical | skillaudit.md Scenario 4 |
| Permission Abuse | 🔴 High | skillaudit.md Scenario 5 |
| Prompt Injection | 🔴 High | skillaudit.md Scenario 6 |
| Code Obfuscation | 🟡 Medium | skillaudit.md Scenario 7 |
| Ransomware | 🚨 Critical | skillaudit.md Scenario 8 |
| Persistence | 🟡 Medium | skillaudit.md Scenario 9 |
| Supply Chain | 🟡 Medium | skillaudit.md Scenario 10 |
| **Malicious Service Downloader** | 🚨 Critical | skillaudit.md Scenario 11 |

**Reference:** `reference/skillaudit.md` for complete detection patterns, code examples, and risk assessment logic.

## Phase 3: Risk Classification

| Level | Criteria |
|-------|----------|
| 🚨 Critical | Backdoor, credential theft, ransomware, miner |
| 🔴 High | Permission abuse, data exfil, privacy violation |
| 🟡 Medium | High permissions justified, benign obfuscation |
| 🟢 Low | Matches declared purpose |

---

# Step 3: Consolidated Report

## Report Header

```markdown
# 🔒 OpenClaw Risk Assessment Report

📅 {datetime}
🖥️ OpenClaw {version} · {os_info}
📊 Overall Risk: {🟢/🟡/🔴/🚨}

| Check Item | Status | Summary |
|------------|--------|---------|
| Configuration Audit | {✅/⚠️/🔴} | {N findings} |
| Skill Security | {✅/⚠️/🔴} | {N critical, N high} |
| Overall | {🟢/🟡/🔴/🚨} | {verdict} |
```

## Section 1: Configuration Audit Results

| Status | Item | Finding |
|--------|------|---------|
| ✅/⚠️/🔴 | {Category} | {Description} |

## Section 2: Skill Security Findings

| Risk | Count | Skills |
|------|-------|--------|
| 🚨 Critical | {N} | {names} |
| 🔴 High | {N} | {names} |
| 🟡 Medium | {N} | {names} |
| 🟢 Low | {N} | (see safe list) |

---

# Output Templates

## Quick Verdicts

| Result | Message |
|--------|---------|
| All Clear | ✅ OpenClaw风险评估完成。配置审计通过，Skill安全检查未发现明显风险。 |
| Config Issues | ⚠️ 发现配置风险。建议检查Gateway设置和文件权限配置。 |
| Skill Risks | 🔴 发现Skill安全风险。{N}个高风险Skill建议立即处理。 |
| Critical | 🚨 检测到严重安全风险！建议立即处理配置问题并移除恶意Skill。 |

## Single Skill Assessment

- **Safe:** `经检测暂未发现高风险问题，可继续安装；`
- **Sensitive:** `发现需关注项，但当前未见明确恶意证据。这个skill具备{高权限能力}，主要用于完成它声明的{功能}；建议仅在确认来源可信、权限范围可接受时使用。`
- **Risky:** `发现风险，不建议直接安装。这个skill{具体问题}，超出了它声称的功能。`
- **Malicious:** `🚨 检测到恶意代码！这个skill包含{具体恶意行为}，强烈建议立即删除。`
- **Malicious Downloader:** `🚨 检测到恶意下载器！这个skill伪装成{服务名称}，通过base64混淆命令诱导执行远程恶意脚本（curl|bash模式），属于典型的社会工程+下载器攻击。切勿执行任何安装命令！`

---

# Safety Guardrails

- ✅ Static analysis only - never execute suspicious code
- ✅ Read code via file tools - no dynamic testing
- ✅ Evidence-based reporting - file:line references required
- ❌ Never bypass sandbox for analysis
- ❌ Never enumerate actual user files
- ❌ No speculation without clear evidence

---

# File Reference

| File | Purpose |
|------|---------|
| `reference/baseline.md` | Configuration audit rules and parsing logic |
| `reference/skillaudit.md` | Skill security detection patterns and scenarios |

---

> **说明**：本 Skill 由 **阿里云（Alibaba Cloud）** 提供的安全防护检查能力。使用本能力可对 OpenClaw 配置与已安装/待安装 Skill 进行安全审计与风险评估。
