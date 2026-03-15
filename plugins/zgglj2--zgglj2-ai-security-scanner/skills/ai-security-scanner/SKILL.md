---
name: ai-security-scanner
description: "AI Agent 安全检测工具。扫描 OpenClaw 等 AI Agent 的安全风险，包括 API Key 泄露、Skill 投毒、敏感信息泄露、配置风险等。当用户询问 AI 安全、Agent 安全、API Key 泄露、Skill 风险、安全扫描、安全审计时触发。"
---

# AI Agent 安全检测

## 概述

对 AI Agent（OpenClaw、Claude Code、Cursor 等）进行安全扫描，检测潜在风险并提供修复建议。

## ⚠️ 首次使用必须安装

此 Skill 包含完整扫描器代码，首次使用需要安装依赖：

```bash
cd ~/.openclaw/skills/ai-security-scanner
./scripts/install.sh
```

安装完成后，扫描器即可使用。

## 核心能力

| 模块 | 功能 | 检测项 |
|------|------|--------|
| 资产发现 | 自动发现 AI Agent 安装 | OpenClaw、Claude Code、Cursor |
| API Key 检测 | 扫描凭证泄露 | OpenAI、Anthropic、Gemini 等 Key |
| Skill 风险扫描 | 检测恶意 Skill | 数据外传、权限滥用、恶意代码 |
| 敏感信息检测 | 扫描记忆/日志中的机密 | 密码、Token、密钥 |
| LLM 语义分析 | 智能风险识别 | 深度语义分析（可选） |

## 使用方式

### 1. 快速扫描

```bash
cd ~/.openclaw/skills/ai-security-scanner
source venv/bin/activate
aascan scan -v
```

### 2. 完整扫描（含报告）

```bash
# 生成 HTML 报告
aascan scan --html /tmp/scan-report.html -v

# 生成 JSON 报告
aascan scan -o /tmp/scan-report.json -v
```

### 3. 启用 LLM 语义分析

```bash
# 需要配置 LLM API Key (GLM 或 OpenAI)
export ZHIPU_API_KEY="your-key"  # 或 OPENAI_API_KEY
aascan scan --llm --llm-provider zhipu -v
```

### 4. 仅资产发现

```bash
aascan discover
```

### 5. 仅检测 API Key

```bash
aascan check-apikey
aascan check-apikey /path/to/project --verify
```

### 6. 检测单个 Skill

```bash
aascan check-skill /path/to/skill
```

## 工作流程

### 步骤 1: 确认安装状态

首次使用时，检查扫描器是否已安装：

```bash
cd ~/.openclaw/skills/ai-security-scanner
if [ ! -d "venv" ]; then
    ./scripts/install.sh
fi
```

### 步骤 2: 确认扫描范围

询问用户：
1. 扫描目标（本地 OpenClaw / 指定路径）
2. 是否启用 LLM 语义分析
3. 是否生成报告

### 步骤 3: 执行扫描

根据用户选择执行相应命令。

### 步骤 4: 结果解读

| 等级 | 说明 | 处理时限 |
|------|------|----------|
| 🔴 Critical | 严重风险，可能导致系统被控 | 立即处理 |
| 🟠 High | 高风险，可能导致数据泄露 | 24 小时内 |
| 🟡 Medium | 中风险，需要关注 | 7 天内 |
| ⚪ Low | 低风险，建议优化 | 30 天内 |
| ℹ️ Info | 提示信息，通常无需处理 | 按需 |

### 步骤 5: 修复建议

根据发现的风险类型，提供具体修复建议：

| 风险类型 | 修复建议 |
|----------|----------|
| API Key 泄露 | 轮换 Key、使用环境变量、从代码中移除 |
| 恶意 Skill | 卸载 Skill、检查来源、审计脚本 |
| 敏感信息 | 清理记忆文件、加密存储、权限控制 |
| 配置风险 | 绑定本地地址、启用认证、配置 TLS |

## 扫描器目录结构

```
~/.openclaw/skills/ai-security-scanner/
├── SKILL.md           # 本文件
├── README.md          # 详细说明
├── pyproject.toml     # Python 依赖
├── scanner/           # 扫描器核心代码
│   ├── discovery.py   # 资产发现
│   ├── apikey.py      # API Key 检测
│   ├── content.py     # 内容扫描
│   ├── models.py      # 数据模型
│   ├── report.py      # 报告生成
│   └── llm.py         # LLM 分析
├── rules/             # 规则库
├── config/            # 配置文件
├── scripts/
│   └── install.sh     # 安装脚本
└── venv/              # 虚拟环境（安装后生成）
```

## LLM 提供商配置

| 提供商 | 环境变量 | 说明 |
|--------|----------|------|
| zhipu | `ZHIPU_API_KEY` | 智谱 AI (GLM) |
| openai | `OPENAI_API_KEY` | OpenAI |

## 飞书报告配置（可选）

如需使用 `--feishu` 生成飞书文档报告，需配置以下环境变量：

| 环境变量 | 说明 | 获取方式 |
|----------|------|----------|
| `FEISHU_APP_ID` | 飞书应用 ID | 飞书开放平台创建应用 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 飞书开放平台 |
| `FEISHU_USER_OPENID` | 接收报告的用户 ID | 飞书用户信息 |

配置方式：

```bash
# 临时配置（当前终端）
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
export FEISHU_USER_OPENID="ou_xxx"

# 永久配置（添加到 ~/.bashrc）
echo 'export FEISHU_APP_ID="cli_xxx"' >> ~/.bashrc
echo 'export FEISHU_APP_SECRET="xxx"' >> ~/.bashrc
echo 'export FEISHU_USER_OPENID="ou_xxx"' >> ~/.bashrc
source ~/.bashrc
```

不配置这些环境变量时，`--feishu` 选项会生成 Markdown 报告，但不会自动上传飞书。

## 定期扫描建议

```bash
# 每日 09:00 扫描
openclaw cron add --name "ai-security-scan" --schedule "0 9 * * *" \
  --command "cd ~/.openclaw/skills/ai-security-scanner && source venv/bin/activate && aascan scan --html /var/log/aascan/daily.html"
```

## 安全最佳实践

1. **API Key 管理**: 使用环境变量、定期轮换、最小权限
2. **Skill 安全**: 仅从官方渠道安装、检查 VirusTotal
3. **配置安全**: Dashboard 绑定本地、启用认证、配置 HTTPS
4. **定期审计**: 建立定期扫描机制、监控异常行为

## 系统要求

- Python 3.10+
- 足够的磁盘空间（虚拟环境约 50MB）
- 网络连接（如需 LLM 分析或威胁情报查询）

## 故障排除

### 安装失败

```bash
# 手动安装
cd ~/.openclaw/skills/ai-security-scanner
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 找不到 aascan 命令

确保已激活虚拟环境：
```bash
source ~/.openclaw/skills/ai-security-scanner/venv/bin/activate
```

### LLM 分析不工作

检查环境变量是否设置：
```bash
echo $ZHIPU_API_KEY
echo $OPENAI_API_KEY
```

## 相关资源

- OpenClaw 文档: https://docs.openclaw.ai
- ClawHub: https://clawhub.com
- OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- MITRE ATLAS: https://atlas.mitre.org/
