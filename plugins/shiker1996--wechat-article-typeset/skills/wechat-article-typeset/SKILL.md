---
name: wechat-article-typeset
description: "公众号文章排版--用户提供 Markdown，返回两个预览链接：AI 结构化版 + 预设主题渲染版"
---

# 公众号文章排版

当用户需要进行**公众号文章排版**、**生成可复制到公众号的预览链接**时：**输入是用户的 Markdown 文件**，本技能会返回 **两个预览链接**：

- **AI 结构化版**：Markdown →（自由模式生成初稿HTML）→（按 `SPEC.md` 改写 HTML）→ `html-to-wechat-copy.js` → 预览链接
- **预设主题版**：Markdown →（预设主题渲染）→ 预览链接

## When to Use

- 用户提到「公众号排版」「复制到公众号」「生成公众号预览链接」「edit.shiker.tech」「文章转公众号」。
- **用户提供一篇 Markdown 文章**（如 `article.md`），需要得到**可复制到公众号的预览链接**时。

## 输入与输出

- **输入**：用户的 **Markdown 文件**（如 `article.md` 或用户指定的 .md 路径）。
- **输出**：两个**文章预览链接**（`https://edit.shiker.tech/copy.html?id=xxx`）：
  - `AI:`（AI 结构化版）
  - `PRESET:`（预设主题版）

## 1. 整体流程（Md → 两个预览链接）

1. **读取用户的 Markdown 文件**（用户提供的 .md 路径）。
2. **生成 AI 结构化版 HTML**（推荐两段式）：先让 AI 基于 Markdown 内容生成 `article.ai.draft.html`（初稿），再让 AI 按 `SPEC.md`（自由模式/统一格式）严格改写为 `article.ai.html`，保证自由度同时输出稳定可复制的公众号排版。
3. **生成预设主题版 HTML**：使用预设（`--preset`）对 Markdown 做主题渲染，得到一份 HTML（无需满足 SPEC）。
4. **分别请求复制页**：对两份 HTML 分别请求 `edit.shiker.tech/api/copy`，得到两条预览链接。
5. **将两条链接交给用户**：以脚本标准输出或同目录写入的链接文件为准（勿让 AI 自行"转述"链接，否则长 id 易漏数字导致链接错误）；用户浏览器打开 → 点击「复制到剪贴板」→ 粘贴到公众号后台。

HTML 生成规范（必读）：**`SPEC.md`** 是 Markdown →（AI 结构化版）HTML 的**唯一约定**。生成 AI 结构化版 HTML 时必须严格按 SPEC 输出，脚本才能稳定产出 AI 版预览链接。

## 2. 脚本入口

- `html-to-wechat-copy.js`：将"输入 HTML"转为公众号兼容 HTML 并请求复制页，输出单条预览链接（同时写入 `wechat-preview-url.txt`）。
- **`wechat-dual-copy.js`（推荐）**：输入一个 `.md`，一次输出两条预览链接（`AI:` / `PRESET:`），并写入 `wechat-preview-urls.txt`。

## 3. 文章类型与推荐格式（便于从 Md 选格式）

| 文章类型 | 推荐格式 | 说明 |
|----------|----------|------|
| 大厂早报 | 格式一 | 多条资讯 + 每条有「影响」+ 今日思考。 |
| AI 职场文 / 单厂深度 / 轻松吃瓜 / 下周职场预警 | 格式二 | 多段落、引用块、表格，用 section + table。 |
| 技术摸鱼周报 / 一周速读 | 格式一或二 | 多条 item+影响→格式一；自由小节+表格→格式二。 |

## 4. API 说明（edit.shiker.tech）

- **接口**：`POST https://edit.shiker.tech/api/copy`
- **请求体**：`Content-Type: application/json`，`{ "html": "完整 HTML 字符串" }`
- **响应**：`{ success: true, data: { id, url } }`；`url` 即为预览页地址。

## 5. 注意点

- 图片：内容中的图片需为可公网访问的 URL，否则公众号内无法显示。
- 公众号粘贴时，仅**引用（blockquote）**和**表格**会保留背景色与边框；脚本已按此规则将需强调的块转为 blockquote。
- **预览链接勿以 AI 转述为准**：长 id 容易被 AI 抄错或漏数字，导致链接失效。请以**脚本标准输出**或**同目录下生成的 `wechat-preview-url.txt`** 中的链接为准；若 AI 提供了链接，请与上述两者核对。

## 6. 兼容策略（HTML 未严格按 SPEC 时）

若生成的 HTML 未完全符合 SPEC，脚本会尽量兼容并仍尝试产出预览链接：

| 情况 | 脚本行为 |
|------|----------|
| 有 `<div class="article">` 且内含至少一个 `.item`（含 .item-title/.item-content/.item-impact） | 按格式一解析。 |
| 有 `.article` 但无 `.item`（如 section + 表格混合） | 按格式二处理：section → blockquote，表格保留。 |
| 无 `.article` 但有 `<body>` | 取 body 内内容，按格式二处理。 |
| 无 `<body>` | 取 `</head>` 后或整文件，按格式二处理。 |

仍建议生成 HTML 时尽量严格按 SPEC，以保证排版效果稳定。

---

## 7. 🌟 一步完成模式（推荐由 AI 编排）

> 目标：**让 AI 先按你文章的气质自由排版，再按 `SPEC.md` 规范收敛成公众号安全格式，最后自动生成预览链接**。  
> 脚本只负责「把 HTML 送去 edit.shiker.tech」，**不再由固定 JS 模板死板生成样式**。

在对话里，一步完成模式建议由 AI 直接串联以下步骤：

1. **从 Markdown 理解内容结构**  
   - AI 读取用户提供的 `.md`，识别标题、小节、列表、表格、重点提示等。
2. **按「自由模式」生成第一版精美 HTML，并保存**  
   - 严格遵守 `SPEC.md` 第 2 节的 6 条硬约束（完整 HTML5、用 `<section style>`、表格用 `<table>` 等）。  
   - 这里可以充分发挥设计感：多种卡片、配色、表格样式都可以，只要用 `<section style="...">` 表达高亮块即可。
   - **保存路径约定**：在原 Markdown 同目录写入 `article.ai.draft.html`，便于用户单独预览初稿排版。
3. **按「统一格式」做第二次规范化改写（可选但推荐），并保存**  
   - 在保持视觉风格的前提下，进一步贴近 `SPEC.md` 第 3 节（通用长文）：  
     - 检查是否误用了 `.article` 壳；  
     - 列表加粗是否符合「列表加粗规范」；  
     - 需要背景/边框的块是否都已经是 `<section style>`。
   - 得到一份**最终 HTML**，并在原 Markdown 同目录写入 `article.ai.html`，作为后续生成预览链接的唯一输入源。
4. **调用技能脚本生成预览链接**  
   - AI 在本技能目录执行：  
     ```bash
     node html-to-wechat-copy.js <path-to-article.ai.html>
     ```
   - 读出脚本输出的链接 / `wechat-preview-url.txt` 中的链接，返回给用户。

> 对话中的“一步完成”含义是：**用户只提供 Markdown，AI 自动完成「两版 HTML + 预览链接」整个流程**，而不是让用户自己手动跑多条命令。
