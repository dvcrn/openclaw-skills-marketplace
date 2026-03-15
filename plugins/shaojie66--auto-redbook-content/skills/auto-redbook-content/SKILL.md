---
name: auto-redbook-content
description: "小红书内容抓取与改写工具，支持图片识别和 OCR，输出本地 JSON 文件。触发关键词：抓取小红书笔记、自动生成小红书内容、运行 auto-redbook-content、执行小红书内容流程。"
---

# auto-redbook-content Skill

小红书内容抓取与改写工具。核心功能：抓取笔记 → 图片识别（Vision + OCR）→ AI 改写 → 输出本地 JSON。可选集成飞书多维表格。

## 触发关键词
- 抓取小红书笔记
- 自动生成小红书内容
- 运行 auto-redbook-content
- 执行小红书内容流程

## 核心功能
1. 抓取小红书笔记（支持真实 MCP 或模拟数据）
2. 图片内容识别（Vision + OCR 双引擎）
3. AI 智能改写（支持直接模式或 Agent 模式）
4. 输出本地 JSON 文件（完整结构化数据）

## 可选集成
- 飞书多维表格：配置后可自动写入表格
- 完整错误处理和重试机制

## 环境变量配置

### 必需配置
无（所有配置均为可选，有默认值）

### 可选配置
| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| REWRITE_MODE | 改写模式：direct 或 agent | direct |
| AGENT_ID | Agent ID（agent 模式时必需） | libu |
| XHS_MAX_RESULTS | 每次抓取数量（1-100） | 3 |
| FEISHU_APP_TOKEN | 飞书 app_token（写入飞书时必需） | - |
| FEISHU_TABLE_ID | 飞书 table_id（写入飞书时必需） | - |

### 配置方式
在 skill 目录创建 `.env` 文件：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

## 安全说明

### 已实施的安全措施
1. ✅ 移除所有硬编码的敏感信息
2. ✅ 使用 `spawnSync` 替代 `execSync`，避免 shell 注入
3. ✅ 使用 `dotenv` 管理环境变量，不直接读取文件内容
4. ✅ 文件读取和网络发送严格分离
5. ✅ 在 `package.json` 中声明所有环境变量依赖
6. ✅ 敏感配置项标记为 `sensitive: true`
7. ✅ 移除调试文件（debug-clawhub.mjs）

### 凭证管理
- 所有凭证通过环境变量传递
- 不会将凭证发送到网络
- 飞书 token 仅用于调用 OpenClaw 工具
- AI 改写在 agent 环境中执行，不暴露 API key

## 依赖工具

### 必需
- Node.js >= 14.0.0
- tesseract-ocr：图片文字提取

### 可选
- xiaohongshu MCP：抓取真实笔记（未配置时使用模拟数据）
- moltshell-vision：图片内容分析
- image-ocr：OCR封装工具
- openclaw feishu-bitable：写入飞书表格

## 使用示例

### 基础用法（核心功能）
```
请执行 auto-redbook-content 流程，抓取 3 条小红书笔记
```

输出：本地 JSON 文件（`output/xiaohongshu_YYYYMMDD_HHMMSS.json`）

### 指定数量
```
抓取 5 条小红书笔记并改写
```

### 可选：写入飞书表格
需要先配置 `.env` 文件中的 `FEISHU_APP_TOKEN` 和 `FEISHU_TABLE_ID`：
```
运行 auto-redbook-content，抓取笔记并写入飞书
```

## 输出说明

### 本地文件
结果保存在 `output/xiaohongshu_YYYYMMDD_HHMMSS.json`，包含：
- 原始标题和内容
- 作者、点赞数等元数据
- 图片分析结果（Vision + OCR）
- 改写后的标题、正文、标签
- 抓取时间

### 飞书表格（可选）
如果配置了飞书凭证，会自动写入表格，包含：
- 原标题、原文链接
- 作者、点赞数
- 改写后标题、正文
- 提取标签
- 抓取时间、状态

## 故障排查

### MCP 调用失败
- 检查 mcporter 是否配置了 xiaohongshu 服务
- 未配置时会自动使用模拟数据，不影响流程

### 图片识别失败
- 检查 moltshell-vision 和 image-ocr 是否可用
- 失败时会跳过图片分析，继续处理文本

### 飞书写入失败
- 检查 FEISHU_APP_TOKEN 和 FEISHU_TABLE_ID 是否正确
- 检查 token 格式：bascn_xxx 或 cli_xxx
- 检查 table_id 格式：tblXXXXXXXX

## 版本历史

### v2.1.1 (2026-03-14)
- 📝 文档优化：明确核心功能与可选集成
- 📝 飞书集成改为可选说明，不作为主要功能展示

### v2.1.0 (2026-03-14)
- 🔒 安全重构：移除所有硬编码敏感信息
- 🔒 使用 spawnSync 替代 execSync
- 🔒 使用 dotenv 管理环境变量
- 🔒 在 package.json 中声明环境变量依赖
- 🔒 移除调试文件
- 📝 添加完整的安全说明

### v2.0.0
- 初始版本
