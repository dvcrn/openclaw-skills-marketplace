# auto-redbook-content

小红书内容抓取与改写工具，支持图片识别和 OCR，输出本地 JSON 文件。

## 功能特性

- ✅ 自动抓取小红书热门笔记
- ✅ 智能图片识别（Vision + OCR）
- ✅ AI 改写（由 OpenClaw agent 处理）
- ✅ 输出本地 JSON 文件
- ✅ 支持模拟数据测试
- ✅ 完整错误处理和重试机制

## 什么是"改写"

**改写**是指基于原文生成新的表达方式，保留核心信息但改变表述。本工具通过 AI 技术辅助内容改写，但请注意：

- 改写后的内容仍需人工审核和二次创作
- 不建议直接发布改写内容
- 应尊重原作者版权，获得授权后使用

## 快速开始

### 1. 安装依赖

```bash
# 安装 tesseract（OCR 依赖）
# macOS
brew install tesseract

# Linux
sudo dnf install tesseract  # Fedora/RHEL
sudo apt install tesseract-ocr  # Debian/Ubuntu
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env`，最小配置：

```env
# 改写模式（可选，默认 direct）
REWRITE_MODE=direct

# Agent 模式时需要配置
# AGENT_ID=libu
```

### 3. 使用

对 OpenClaw agent 说：

```
请执行 auto-redbook-content 流程，抓取 3 条小红书笔记
```

Agent 会：
1. 调用抓取脚本获取笔记
2. 处理图片识别和 OCR
3. 将结果保存到 `output/xiaohongshu_YYYYMMDD_HHMMSS.json`
4. 调用 AI 进行内容改写
5. 更新 JSON 文件中的改写内容

## 输出格式

输出文件：`output/xiaohongshu_YYYYMMDD_HHMMSS.json`

每条笔记包含：

```json
{
  "original_title": "原标题",
  "original_content": "原正文",
  "author": "作者",
  "likes": 1234,
  "image_analysis": ["图片描述1", "图片描述2"],
  "ocr_text": ["图片文字1", "图片文字2"],
  "rewritten_title": "改写后标题",
  "rewritten_content": "改写后正文",
  "tags": ["标签1", "标签2"],
  "url": "https://www.xiaohongshu.com/explore/...",
  "fetch_time": "2024-03-14T03:00:00.000Z"
}
```

## 改写模式

### Direct 模式（推荐）

由 OpenClaw agent 直接处理改写。

**配置：**
```env
REWRITE_MODE=direct
```

**使用：**
```
请执行 auto-redbook-content 流程，抓取 3 条小红书笔记
```

### Agent 模式（高级）

通过 `sessions_spawn` 调用其他 agent 处理改写。

**配置：**
```env
REWRITE_MODE=agent
AGENT_ID=libu
```

**使用：**
```
请执行 auto-redbook-content 流程，抓取 3 条小红书笔记
```

## 依赖工具

### 必需
- **Node.js** >= 14.0.0
- **tesseract-ocr**：图片文字提取

### 可选
- **xiaohongshu MCP**：抓取真实笔记（未配置时使用模拟数据）
- **moltshell-vision**：图片内容分析
- **image-ocr**：OCR 封装工具

## 法律风险提示

### ⚠️ 版权声明

本工具涉及内容改写，使用前请务必了解相关法律风险：

1. **版权问题**
   - 小红书笔记内容受《著作权法》保护
   - 即使经过 AI 改写，仍可能构成"演绎作品"，需获得原作者授权
   - 未经授权的改写和发布可能侵犯原作者的著作权

2. **使用建议**
   - **仅用于学习和研究**：建议将本工具用于学习内容创作技巧，而非直接发布
   - **人工审核**：改写后的内容必须经过人工审核和二次创作，确保原创性
   - **获得授权**：如需使用他人内容，应先获得原作者明确授权
   - **标注来源**：如使用参考内容，应明确标注原始来源

3. **禁止行为**
   - ❌ 批量抓取并发布他人内容
   - ❌ 用于商业目的而未获授权
   - ❌ 冒充原创发布改写内容
   - ❌ 侵犯他人知识产权

### 免责声明

- 本工具仅供学习和研究使用
- 使用者应自行承担因使用本工具产生的法律责任
- 开发者不对任何侵权行为负责

## 常见问题

### Q1: 抓取失败？

**检查：**
- xiaohongshu MCP 是否配置正确
- 网络连接是否正常
- 未配置 MCP 时会自动使用模拟数据

### Q2: 图片识别失败？

**检查：**
- moltshell-vision 是否可用
- image-ocr 和 tesseract 是否安装
- 图片 URL 是否可访问

### Q3: 改写失败？

**检查：**
- OpenClaw agent 是否正常运行
- Agent 模式下 AGENT_ID 是否配置正确
- 查看 agent 日志获取详细错误信息

### Q4: 输出文件在哪里？

输出文件保存在 `output/` 目录下，文件名格式：`xiaohongshu_YYYYMMDD_HHMMSS.json`

### Q5: 如何提高改写质量？

- 确保图片识别成功，提供更多上下文
- 在 agent 提示词中明确改写要求
- 人工审核并二次创作

## 安全建议

1. **配置文件**
   - `.env` 文件包含敏感信息，不要提交到版本控制
   - 使用 `.env.example` 作为配置模板

2. **权限控制**
   - 定期检查输出文件的访问权限
   - 避免在公共网络环境下执行

3. **定期维护**
   - 定期清理 `/tmp/xhs-images/` 临时文件
   - 检查输出目录存储空间
   - 更新依赖工具版本

## 许可证

MIT License
