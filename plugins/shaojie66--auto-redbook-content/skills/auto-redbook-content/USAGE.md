# auto-redbook-content 使用说明

## 快速开始

### 1. 安装 skill

```bash
# 从 ClawHub 安装
clawhub install auto-redbook-content

# 或手动克隆
git clone https://clawhub.com/skills/auto-redbook-content ~/.openclaw/skills/auto-redbook-content
```

### 2. 配置环境

```bash
cd ~/.openclaw/skills/auto-redbook-content
cp .env.example .env
```

编辑 `.env` 填入配置：

**单 agent 模式（推荐）：**
```env
# 飞书配置（必需）
FEISHU_APP_TOKEN=bascn_your_app_token_here
FEISHU_TABLE_ID=tblxxxxxx

# 抓取配置
XHS_MAX_RESULTS=3

# 改写模式
REWRITE_MODE=direct

# AI 配置
AI_PROVIDER=openai
AI_MODEL=gpt-4
AI_API_KEY=your_openai_key
```

**多 agent 模式（高级）：**
```env
# 飞书配置（必需）
FEISHU_APP_TOKEN=bascn_your_app_token_here
FEISHU_TABLE_ID=tblxxxxxx

# 抓取配置
XHS_MAX_RESULTS=3

# 改写模式
REWRITE_MODE=agent

# Agent 配置
AGENT_ID=libu
```

### 3. 安装依赖工具

```bash
# macOS
brew install tesseract

# Linux (Fedora/RHEL)
sudo dnf install tesseract

# Linux (Ubuntu/Debian)
sudo apt-get install tesseract-ocr
```

### 4. 创建飞书表格

在飞书多维表格中创建以下字段：

| 字段名 | 类型 | 必需 |
|--------|------|------|
| 原标题 | 文本 | ✅ |
| 原文链接 | URL | ✅ |
| 作者 | 文本 | ✅ |
| 点赞数 | 数字 | ✅ |
| 评论数 | 数字 | ✅ |
| 收藏数 | 数字 | ✅ |
| 图片分析 | 多行文本 | 推荐 |
| 图片文字 | 多行文本 | 推荐 |
| 改写后标题 | 文本 | ✅ |
| 改写后正文 | 多行文本 | ✅ |
| 提取标签 | 文本 | 可选 |
| 抓取时间 | 日期时间 | ✅ |
| 状态 | 单选 | ✅ |

**状态字段选项：** 待审核、已发布、已归档

### 5. 测试运行

```bash
# 测试抓取功能
node ~/.openclaw/skills/auto-redbook-content/scripts/fetch.js 3

# 预期输出：
# [抓取] 开始抓取小红书笔记，数量: 3
# [抓取] 成功获取 3 条笔记
# [图片识别] 处理笔记 xxx 的图片...
```

## 使用方式

### 单 agent 模式

适用于只有一个 OpenClaw agent 的用户。

**配置：**
```env
REWRITE_MODE=direct
AI_PROVIDER=openai
AI_MODEL=gpt-4
AI_API_KEY=your_openai_key
```

**使用：**
```
请执行 auto-redbook-content 流程，抓取 3 条小红书笔记
```

你的 agent 会：
1. 读取 SKILL.md
2. 调用抓取脚本获取笔记
3. 直接调用 AI API 进行改写
4. 将结果写入飞书表格

### 多 agent 模式

适用于有多个 agent 协作的架构（如司礼监 + 礼部）。

**配置：**
```env
REWRITE_MODE=agent
AGENT_ID=libu
```

**使用：**
```
请执行 auto-redbook-content 流程，抓取 3 条小红书笔记
```

主 agent 会：
1. 读取 SKILL.md
2. 调用抓取脚本获取笔记
3. 使用 sessions_spawn 调用指定 agent 改写
4. 将结果写入飞书表格

### 手动测试

```bash
# 仅测试抓取（不改写、不写入）
node ~/.openclaw/skills/auto-redbook-content/scripts/fetch.js 3
```

## 工作流程

### 单 agent 模式流程

```
1. 抓取笔记
   ↓
   使用 xiaohongshu MCP 或模拟数据
   获取标题、内容、作者、互动数据、图片

2. 图片识别
   ↓
   Vision 分析：描述图片内容、风格、元素
   OCR 提取：识别图片中的文字

3. AI 改写
   ↓
   直接调用 AI API（OpenAI/Anthropic/Local）
   参考原文 + 图片分析结果

4. 写入表格
   ↓
   使用 feishu_bitable_create_record
   状态设为"待审核"
```

### 多 agent 模式流程

```
1. 抓取笔记
   ↓
   使用 xiaohongshu MCP 或模拟数据
   获取标题、内容、作者、互动数据、图片

2. 图片识别
   ↓
   Vision 分析：描述图片内容、风格、元素
   OCR 提取：识别图片中的文字

3. AI 改写
   ↓
   通过 sessions_spawn 调用其他 agent
   参考原文 + 图片分析结果

4. 写入表格
   ↓
   使用 feishu_bitable_create_record
   状态设为"待审核"
```

## 配置说明

### 飞书配置

**获取 App Token：**
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 进入你的应用 > 凭证与基础信息
3. 复制 App Token（格式：`bascn...` 或 `cli_...`）

**获取 Table ID：**
1. 打开飞书多维表格
2. 复制浏览器地址栏中的 `table_id`（格式：`tblxxxxxx`）

### 改写模式配置

**单 agent 模式（direct）：**
- `AI_PROVIDER`：AI 提供商，支持 `openai` / `anthropic` / `local`
- `AI_MODEL`：AI 模型名称
- `AI_API_KEY`：AI API 密钥
- `AI_BASE_URL`：（可选）自定义 API 端点

**多 agent 模式（agent）：**
- `AGENT_ID`：要调用的 agent ID（如 `libu`）

### 抓取配置

- `XHS_MAX_RESULTS`：每次抓取的笔记数量，建议 3-5 条
- 数量过多会导致改写时间过长

### 图片识别配置

- `ENABLE_IMAGE_ANALYSIS`：是否启用图片识别，默认 `true`
- `IMAGE_ANALYSIS_TIMEOUT`：单张图片处理超时时间（秒），默认 30

**禁用图片识别：**
```env
ENABLE_IMAGE_ANALYSIS=false
```

这样可以加快处理速度，但改写时不会参考图片信息。

## AI 提供商配置示例

### OpenAI

```env
AI_PROVIDER=openai
AI_MODEL=gpt-4
AI_API_KEY=sk-...
# AI_BASE_URL=https://api.openai.com/v1  # 可选
```

### Anthropic

```env
AI_PROVIDER=anthropic
AI_MODEL=claude-3-opus-20240229
AI_API_KEY=sk-ant-...
# AI_BASE_URL=https://api.anthropic.com/v1  # 可选
```

### 本地模型（Ollama）

```env
AI_PROVIDER=local
AI_MODEL=llama2
# AI_BASE_URL=http://localhost:11434  # 可选
```

## 常见问题

### Q1: 抓取失败怎么办？

**症状：** `[抓取] 失败: ECONNREFUSED`

**解决方案：**
- 不影响使用，会自动切换到模拟数据
- 如需真实数据，配置 xiaohongshu MCP：
  ```bash
  mcporter config xiaohongshu
  mcporter start xiaohongshu
  ```

### Q2: 图片识别失败？

**症状：** `[OCR] 文字提取失败: tesseract: command not found`

**解决方案：**
```bash
# macOS
brew install tesseract

# Linux
sudo dnf install tesseract  # 或 apt-get install tesseract-ocr
```

### Q3: 飞书写入失败？

**症状：** `Error: Invalid app_token or table_id`

**解决方案：**
1. 检查 `.env` 配置格式
2. 验证表格字段是否完整
3. 检查应用权限（需要"多维表格"权限）

### Q4: AI 改写失败？

**单 agent 模式症状：** `AI_API_KEY 未配置`

**解决方案：**
- 检查 `.env` 中的 `AI_API_KEY` 是否正确
- 验证 API Key 是否有效
- 检查网络连接和 API 端点

**多 agent 模式症状：** `Agent not found: libu`

**解决方案：**
- 检查 `AGENT_ID` 配置是否正确
- 确认目标 agent 已启动
- 验证 agent 是否支持改写功能

### Q5: 改写质量不满意？

**解决方案：**
- 单 agent 模式：修改 `scripts/rewrite.js` 中的提示词
- 多 agent 模式：调整被调用 agent 的行为
- 增加风格要求（如"轻松活泼"）
- 增加长度要求（如"控制在 500 字以内"）

### Q6: 如何选择改写模式？

**建议：**
- **单 agent 用户**：使用 `REWRITE_MODE=direct`
  - 优点：配置简单，响应快，成本可控
  - 缺点：需要 API Key
- **多 agent 用户**：使用 `REWRITE_MODE=agent`
  - 优点：复用现有 agent，风格统一
  - 缺点：需要多 agent 架构

### Q7: 如何调整抓取数量？

修改 `.env`：
```env
XHS_MAX_RESULTS=5  # 改为 5 条
```

### Q8: 如何禁用图片识别？

在 `.env` 中添加：
```env
ENABLE_IMAGE_ANALYSIS=false
```

## 进阶使用

### 自定义改写提示词（单 agent 模式）

编辑 `scripts/rewrite.js`，修改 prompt：

```javascript
const prompt = `请帮我改写以下小红书笔记，要求：
1. 保持原意，但用不同的表达方式
2. 风格轻松活泼，适合年轻人阅读  // 修改这里
3. 标题控制在 30 字以内，正文控制在 500 字以内
4. 使用 emoji 增加趣味性
5. 参考图片分析结果（如有），确保内容与图片一致
6. 提取 3-5 个相关标签

原标题：${note.title}
原内容：${note.content}
...`;
```

### 集成到其他工作流

```javascript
// 在其他 skill 中调用
const { fetchNotes } = require('~/.openclaw/skills/auto-redbook-content/scripts/fetch.js');
const { rewriteNote } = require('~/.openclaw/skills/auto-redbook-content/scripts/rewrite.js');

async function myWorkflow() {
  // 抓取笔记
  const notes = await fetchNotes(5);
  
  // 改写
  for (const note of notes) {
    const rewritten = await rewriteNote(note);
    // 你的逻辑
  }
}
```

### 自定义飞书字段映射

如果你的飞书表格字段名称不同，可以在调用时自定义映射：

```javascript
const fields = {
  '标题': note.title,           // 你的字段名
  '链接': note.url,
  '作者名': note.author,
  // ...
};
```

## 监控与维护

### 查看执行日志

```bash
# 查看 OpenClaw 日志
tail -f ~/.openclaw/logs/agent.log

# 查看心跳日志（如果配置了定时任务）
tail -f ~/.openclaw/agents/your-agent/workspace/logs/heartbeat/$(date +%Y-%m-%d).log
```

### 清理临时文件

```bash
# 清理图片临时目录
rm -rf /tmp/xhs-images/*
```

### 检查飞书表格

定期检查飞书表格：
- 存储空间是否充足
- 数据是否正常写入
- 状态字段是否正确

## 故障排查

### 完整测试流程

```bash
# 1. 测试抓取
node ~/.openclaw/skills/auto-redbook-content/scripts/fetch.js 1

# 2. 测试 Vision 分析
moltshell-vision "https://picsum.photos/800/600" "描述这张图片"

# 3. 测试 OCR 提取
image-ocr /path/to/image.jpg --lang chi_sim+eng

# 4. 测试飞书连接（在 OpenClaw agent 中）
feishu_bitable_list_fields app_token table_id
```

### 启用调试日志

```bash
DEBUG=* node ~/.openclaw/skills/auto-redbook-content/scripts/fetch.js 3
```

## 更新与升级

### 更新到最新版本

```bash
clawhub update auto-redbook-content
```

### 查看更新日志

```bash
clawhub info auto-redbook-content
```

## 版本历史

### v1.1.0（当前版本）
- ✅ 支持单 agent 模式（直接调用 AI API）
- ✅ 支持多 agent 模式（通过 sessions_spawn）
- ✅ 新增 `scripts/rewrite.js` 改写模块
- ✅ 支持 OpenAI / Anthropic / 本地模型
- ✅ 文档通用化，删除多 agent 术语
- ✅ 更新配置示例和使用指南

### v1.0.0
- ✅ 初始版本
- ✅ 支持小红书笔记抓取
- ✅ 集成图片识别（Vision + OCR）
- ✅ 多 agent 架构（司礼监 + 礼部）
- ✅ 飞书表格写入

## 技术支持

- **ClawHub 页面：** https://clawhub.com/skills/auto-redbook-content
- **Skill ID：** k97ekbxcm4tpq7xzf7ze34820x82teh9
- **版本：** 1.1.0

## 相关资源

- [SKILL.md](./SKILL.md) - 技能详细说明
- [README.md](./README.md) - 项目介绍
- [.env.example](./.env.example) - 配置模板
- [TEST_REPORT.md](./TEST_REPORT.md) - 测试报告
