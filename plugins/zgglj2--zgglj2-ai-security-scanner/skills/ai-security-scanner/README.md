# AI Agent Security Scanner

🛡️ AI Agent 安全检测工具 - 扫描 OpenClaw 等 AI Agent 的安全风险

## 功能

- **资产发现**: 自动发现 OpenClaw、Claude Code、Cursor 等 AI Agent
- **API Key 检测**: 扫描配置文件、环境变量中的 API Key 泄露
- **Skill 风险扫描**: 检测恶意 Skill、数据外传、权限滥用
- **敏感信息检测**: 扫描记忆文件、日志中的机密
- **LLM 语义分析**: 智能风险识别（可选）

## 快速开始

### 安装

```bash
cd ~/.openclaw/skills/ai-security-scanner
./scripts/install.sh
```

### 使用

```bash
# 激活环境
source venv/bin/activate

# 执行扫描
aascan scan

# 详细输出
aascan scan -v

# 生成 HTML 报告
aascan scan --html report.html

# 启用 LLM 分析
aascan scan --llm --llm-provider zhipu

# 仅资产发现
aascan discover

# 检测 API Key
aascan check-apikey
```

## 风险等级

| 等级 | 说明 | 处理时限 |
|------|------|----------|
| 🔴 Critical | 严重风险 | 立即处理 |
| 🟠 High | 高风险 | 24 小时内 |
| 🟡 Medium | 中风险 | 7 天内 |
| ⚪ Low | 低风险 | 30 天内 |
| ℹ️ Info | 提示信息 | 按需 |

## 依赖

- Python 3.10+
- typer, rich, pydantic, pyyaml, requests, httpx, zhipuai

## 环境变量配置（可选）

### LLM 语义分析

```bash
export ZHIPU_API_KEY="your-key"    # 智谱 AI
# 或
export OPENAI_API_KEY="your-key"   # OpenAI
```

### 飞书报告（可选）

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
export FEISHU_USER_OPENID="ou_xxx"
```

## 许可证

MIT
