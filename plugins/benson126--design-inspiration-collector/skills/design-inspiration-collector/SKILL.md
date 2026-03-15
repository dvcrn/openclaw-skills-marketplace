---
name: design-inspiration-collector
description: "多平台设计灵感收集技能。当用户需要设计参考、UI灵感、视觉创意时触发。用户提出设计方向（如\"医疗App\"、\"移动端UI\"、\"金融Dashboard\"等），技能负责：(1) 使用Tavily搜索Behance、Dribbble、Pinterest三个平台的相关内容 (2) 整理内容并附上链接 (3) 生成飞书文档，文档命名为\"关键词+日期时间\"格式 (4) 发送文档链接给用户 (5) 推荐其他相关方向（不带链接）。触发词：找灵感、收集灵感、设计参考、UI参考、视觉灵感、设计趋势、Behance、Dribbble、Pinterest。"
---

# 多平台设计灵感收集器

帮助用户从 Behance、Dribbble、Pinterest 三个平台高效收集设计灵感，并生成飞书文档。

## 功能特点

1. **多平台搜索**：自动搜索 Behance、Dribbble、Pinterest 三个设计平台
2. **飞书文档**：自动生成飞书文档，命名为"关键词+日期时间"格式
3. **趋势分析**：提取 AI 设计趋势摘要
4. **推荐相关**：推荐相关设计方向供进一步探索

## 工作流程

### Step 1: 理解需求

当用户提出设计方向时，确认：
- 具体领域（App类型、设计风格、平台等）
- 是否有细分要求（如"只看移动端"、"只要Dashboard"）

### Step 2: 多平台搜索

使用 Tavily API 搜索三个平台：

```python
# Pinterest
query = f"site:pinterest.com {主题} ui ux design 2026"

# Dribbble
query = f"site:dribbble.com {主题} ui design 2026"

# Behance
query = f"site:behance.net {主题} ui ux design 2026"
```

### Step 3: 生成飞书文档

使用 feishu_doc 工具创建飞书文档：

```python
# 1. 创建文档，命名为：关键词+日期时间
feishu_doc action=create title="{关键词}_{YYYYMMDD_HHMMSS}"

# 2. 写入 Markdown 内容
feishu_doc action=write doc_token=xxx content="markdown内容"
```

**文档命名格式**：`{关键词}_{YYYYMMDD_HHMMSS}`

示例：
- `医疗App设计灵感_20260311_170245`
- `金融Dashboard_20260311_143022`

### Step 4: 发送文档链接

将飞书文档链接发送给用户，格式如下：

```
# {主题} 设计灵感收集

> 来源：Behance、Dribbble、Pinterest

---

## 📊 趋势概览

{AI 分析的设计趋势}

---

## 🎨 Pinterest 精选 (5条)

1. **{标题}** ⭐⭐⭐⭐⭐
   - 链接：{URL}
   - 内容：{描述}

2. **{标题}** ⭐⭐⭐⭐
   - 链接：{URL}
   - 内容：{描述}

...（共5条）

---

## 🎯 Dribbble 精选 (5条)

...

---

## 💎 Behance 精选 (5条)

...

---

## 🔍 搜索关键词

- `{主题} ui design`
- `{主题} app ui`
- `{主题} dashboard`
- `{主题} mobile`

---

## 📌 相关方向推荐

需要我帮你搜索以下细分主题吗？

1. **{方向1}** - {简短描述}
2. **{方向2}** - {简短描述}
3. **{方向3}** - {简短描述}
```

---

**飞书文档链接**：https://feishu.cn/docx/xxx

---

## 依赖工具

| 工具 | 用途 | 安装 |
|------|------|------|
| Tavily API | 搜索三个设计平台 | `pip install tavily-python` |
| feishu_doc | 创建飞书文档 | 系统内置 |

## 配置说明

### Tavily API Key

在环境中设置：
```bash
export TAVILY_API_KEY="tvly-你的key"
```

或修改脚本中的默认值。

## 使用方法

### 基本用法

当用户说"帮我收集 XXX 的设计灵感"时：

1. 使用 Tavily 搜索三个平台
2. 每个平台取前 5 条结果
3. 整理成 Markdown 格式
4. 直接在聊天窗口发送
5. 推荐相关方向

### 示例对话

**用户：** 帮我收集医疗App的设计灵感

**执行：**
1. 搜索三个平台：`healthcare app ui design`
2. 整理 15 条内容（每个平台 5 条）
3. 创建飞书文档：`医疗App设计灵感_20260311_170245`
4. 发送文档链接给用户
5. 推荐相关方向：AI问诊、健康追踪、远程医疗

**回复：**
```
✅ 飞书文档已创建！

**文档名称**：医疗App设计灵感_20260311_170245
**文档链接**：https://feishu.cn/docx/xxx

共收集 15 条设计灵感（Pinterest 5条、Dribbble 5条、Behance 5条）

---

## 📌 相关方向推荐

1. **AI 问诊助手** - 智能问诊、症状分析
2. **健康追踪** - 运动记录、睡眠监测
3. **远程医疗** - 视频问诊、处方管理
```

## 搜索技巧

### 热门设计方向

| 方向 | 关键词 |
|------|--------|
| 移动 App | mobile app, ios, android, app ui |
| 网页设计 | web design, landing page, website |
| 仪表盘 | dashboard, admin panel, data viz |
| 电商 | ecommerce, shop, checkout |
| 金融 | fintech, banking, crypto, payment |
| 健康 | health, medical, fitness, wellness |
| 风格 | glassmorphism, neumorphism, minimal |

## 注意事项

1. **三个平台都要搜**：Pinterest、Dribbble、Behance，每个平台至少 5 条
2. **飞书文档命名**：必须按 `{关键词}_{YYYYMMDD_HHMMSS}` 格式命名
3. **按平台分类**：文档中清晰标注 Pinterest、Dribbble、Behance
4. **推荐内容**：最后推荐 3-5 个相关方向（不带链接）
5. **星级评分**：按相关度给出 1-5 星评分
6. **发送链接**：必须发送飞书文档链接给用户
