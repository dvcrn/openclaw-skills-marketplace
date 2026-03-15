# 公众号文章 HTML 生成规范

本文档是 **Markdown / 内容 → HTML** 生成端的**唯一约定**。生成器（含 AI）**严格按本规范输出 HTML**，`html-to-wechat-copy.js` 只解析本规范定义的结构，**不随 AI 随意输出而改脚本**。

---

## 1. 原则

- **生成端（推荐）**：尽量只输出下面「统一格式（通用长文）」的合法 HTML（即原「格式二」）。
- **生成端（兼容）**：如确需“早报/资讯条 + 影响”这种固定结构，可使用「格式一（早报）」。
- **脚本端**：只保证对符合本规范的 HTML 行为正确；对不符合的 HTML 会做兼容尝试，但不保证效果。
- **迭代**：若需新样式或新结构，先**更新本规范**，再改脚本；避免为各种随意 HTML 反复改脚本。

---

## 2 自由模式（最大自由度：最小硬约束 Contract）

如果你希望给 AI **最大的自由度**，请让 AI **只遵守本节的最小硬约束**。满足这些约束后，AI 可以自由使用各种排版与内联样式（在正文里想写多少 `<section>`、表格、列表、小节都可以）。

### 2.1 硬约束（只要这 6 条）

1. **必须输出完整 HTML5**：包含 `<body>...</body>`（不要只输出片段）。
2. **不要用** `<div class="article">` **包全文**（这是格式一专用壳，容易误判/混用）。
3. **任何需要保留背景/边框的高亮块**，一律用：`<section style="...">...</section>`（不要用带背景的裸 `<div>`）。  
   脚本会把 `section` 转成 `blockquote`，公众号才稳定保留背景/边框。
4. **表格用 `<table>`**（含 `tr/th/td`），可随意内联样式；脚本会保留表格。
5. **列表加粗前缀遵循规范**：若在 `<li>` 中使用 `<strong>` 做“前缀标签”，必须用 `<span style="font-weight: normal;">` 断开字重，避免整行变粗（见 2.3）。
6. **不要依赖 `<head><style>...</style></head>`**：可以存在，但正文样式必须用内联 `style`（因为复制到公众号时外部样式可能丢失）。

### 2.2 可直接复制给 AI 的提示词模板

> 请输出一份完整 HTML5（含 body）。除以下硬约束外，你可以自由设计排版与配色：  
> 1) 不使用 `<div class="article">` 包全文；2) 所有需要背景/边框的块必须用 `<section style="...">`；3) 表格用 `<table>`；4) 列表中若有 `<strong>前缀</strong>`，后续说明必须用 `<span style="font-weight: normal;">` 断开字重；5) 不依赖 head 里的 style。  
> 其它（h1/h2/h3、p、ul/ol/li、表格、emoji、内联样式）完全自由。

---

## 3. 统一格式（推荐）：通用长文（= 原格式二）

为降低“格式选择/混用”导致的不稳定，**推荐所有文章都按本节输出**。它能覆盖：早报、职场文、单厂深度、周报、吃瓜、速读、预警等全部类型；需要“资讯条”时用小节 + 列表/表格表达即可。

### 3.1 文档壳

- 标准 HTML5，必须有 `<body>`。
- 正文在 `<body>` 内：要么**直接**写块级内容，要么用**一层** `<section>...</section>` 包全文。
- **禁止**用 `<div class="article">` 包裹全文（这是格式一专用壳，容易误判）。

### 3.2 允许的块与约定

| 用途 | 写法 | 说明 |
|------|------|------|
| 标题 | `<h1>` / `<h2>` / `<h3>` | 按层级使用。 |
| 段落 | `<p>` | 可内联 `style`。 |
| 列表 | `<ul>` / `<ol>` + `<li>` | 无特殊 class 要求。 |
| 需背景/边框的块（高亮卡片/提示/引用） | **`<section style="...">...</section>`** | 脚本会转为 `<blockquote>`，公众号会保留引用样式。内联样式可写 `background`、`border-left`、`padding` 等。 |
| 表格 | `<table>`（含 `thead/tbody/tr/th/td`） | 脚本不改，公众号保留表格样式。 |
| 分割 | `<hr>` 或空行 | 无强制要求。 |

### 3.3 列表加粗规范（重要：避免“整行变粗”）

在公众号粘贴环境中，**在 `<li>` 里直接写 `<strong>标签：</strong>说明`** 有时会出现“说明部分也被加粗/样式串联”的问题（尤其是有序列表 `<ol>`）。为保证只加粗前缀、后半段保持常规字重，请遵循以下写法：

**推荐写法 A（强制断开字重）：**

```html
<li><strong>结论：</strong><span style="font-weight: normal;">这里是正常字重的说明</span></li>
```

**推荐写法 B（前缀加粗 + 分隔符不加粗）：**

```html
<li><strong>结论</strong><span style="font-weight: normal;">：这里是说明</span></li>
```

**避免写法（可能导致整行都变粗）：**

```html
<li><strong>结论：</strong>这里是说明</li>
```

若你不想引入内联样式，也可以**完全不使用 `<strong>`**，改用 emoji/符号作为强调（例如“✅ 结论：说明”）。

### 3.4 让样式“尽可能多样丰富”的建议（仍不违反规范）

只要不引入 `.article/.item` 的格式一壳，你可以通过“不同的 `<section style>` 模板”获得丰富的视觉效果。推荐只使用公众号相对稳的样式属性：`background`、`border-left`、`padding`、`margin`、`color`、`border-radius`、`text-align`、`font-size`、`line-height`。

示例（可直接给 AI 作为模板库，按需替换颜色与文案）：

```html
<!-- 引言/摘要卡片 -->
<section style="background:#f0f4ff;border-left:4px solid #667eea;padding:16px;margin:16px 0;border-radius:12px;">
  <p><strong>导语</strong><span style="font-weight: normal;">：一句话概览。</span></p>
</section>

<!-- 风险提示 -->
<section style="background:#fff7ed;border-left:4px solid #f97316;padding:16px;margin:16px 0;border-radius:12px;">
  <p><strong>注意</strong><span style="font-weight: normal;">：风险/坑点。</span></p>
</section>

<!-- 数据对比：表格 -->
<table style="width:100%;border-collapse:collapse;margin:12px 0;">
  <tr><th style="border:1px solid #e5e7eb;padding:10px;background:#f3f4f6;">方案</th><th style="border:1px solid #e5e7eb;padding:10px;background:#f3f4f6;">成本</th></tr>
  <tr><td style="border:1px solid #e5e7eb;padding:10px;">A</td><td style="border:1px solid #e5e7eb;padding:10px;">￥99</td></tr>
</table>
```

### 3.5 最小可运行示例（统一格式）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>通用长文</title></head>
<body>
  <section>
    <h1>文章主标题</h1>
    <section style="background:#f0f4ff;border-left:4px solid #667eea;padding:16px;margin:16px 0;border-radius:12px;">
      <p><strong>导语</strong><span style="font-weight: normal;">：开场白。</span></p>
    </section>
    <h2>小节</h2>
    <ol>
      <li><strong>结论：</strong><span style="font-weight: normal;">说明文字</span></li>
    </ol>
  </section>
</body>
</html>
```

---

## 4. 格式一（兼容/可选）：早报 / 资讯列表

**适用**：大厂早报、多条资讯且每条有「影响」、部分周报/速读（周一 大厂早报等）。

### 4.1 文档壳

- 标准 HTML5，必须有 `<body>`。
- 正文**必须**被一层 **`<div class="article">`** 包裹，且该 div 直接位于 `<body>` 内，闭合在 `</body>` 前。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>文章标题</title>
</head>
<body>
  <div class="article">
    <!-- 以下 3.2 结构，顺序不可变 -->
  </div>
</body>
</html>
```

### 4.2 正文结构（顺序固定）

| 顺序 | 块 | 标签与 class | 必选 | 说明 |
|------|-----|--------------|------|------|
| 1 | 标题 | `<h1>...</h1>` | 是 | 单行，可含 emoji。 |
| 2 | 引言 | `<div class="intro">...</div>` | 是 | 内可多段 `<p>` 或纯文本。 |
| 3 | 资讯条 | `<div class="item">` 含三个子块 | 至少 1 条 | 见下表。 |
| 4 | 今日思考 | `<div class="thinking">...</div>` | 是 | 内为 `<p>`，如 `<p>今日思考</p><p>内容</p>`。 |
| 5 | 分割线 | `<div class="divider"></div>` | 是 | 空 div 即可。 |
| 6 | 页脚 | `<div class="footer">...</div>` | 是 | 内为 `<p>` 等。 |

**每条 `.item` 的固定子结构（不可省略、不可换顺序）：**

```html
<div class="item">
  <div class="item-title">序号. 【标签】标题</div>
  <div class="item-content">正文段落或短句</div>
  <div class="item-impact"><strong>影响：</strong>一句话说明</div>
</div>
```

- **class 名**必须为 `item`、`item-title`、`item-content`、`item-impact`（不可加其它 class 或写成别的名字）。
- `.item-title` / `.item-content` / `.item-impact` 顺序不可调换。

### 4.3 禁止

- 在格式一正文内**不要**使用 `<section>` 或与 `.item` 无关的复杂块；若需要表格/多小节，请用**格式二**。
- 不要在 `<head>` 写与正文结构相关的 `<style>`；脚本会统一加样式。

### 4.4 最小可运行示例（格式一）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>早报</title></head>
<body>
  <div class="article">
    <h1>大厂早报｜今日要点</h1>
    <div class="intro"><p>今日概览一句。</p></div>
    <div class="item">
      <div class="item-title">1. 【动态】某公司某事</div>
      <div class="item-content">简述。</div>
      <div class="item-impact"><strong>影响：</strong>对读者的影响。</div>
    </div>
    <div class="thinking"><p>今日思考</p><p>思考内容。</p></div>
    <div class="divider"></div>
    <div class="footer"><p>留言区聊聊。</p></div>
  </div>
</body>
</html>
```

---

## 5. Markdown → HTML 生成约定（推荐）

若从 **Markdown** 生成 HTML，建议按下面映射输出，以保证落在本规范内：

| Markdown | 输出 HTML（统一格式：推荐） | 输出 HTML（格式一：可选） |
|----------|------------------------------|---------------------------|
| 文档标题 | `<h1>`（仅一个） | `<h1>` |
| 引言/概览 | `<section style="...">` 内 `<p>` | `<div class="intro">` |
| 列表项（标签+说明） | `<ol>/<ul>`，用“列表加粗规范”写法 | `.item` 三段结构 |
| 思考/总结块 | `<section style="...">` | `<div class="thinking">` |
| 分割 | `<hr>` 或留空 | `<div class="divider"></div>` |
| 文末/引导 | `<p>` 或 `<section>` | `<div class="footer">` |
| 表格 | `<table>` | （不推荐） |
| 二级/三级标题 | `<h2>` / `<h3>` | （不推荐） |

生成前优先选择**统一格式（通用长文）**；只有当你明确要“早报固定结构”（.item/.impact/.thinking/footer）时，才选择格式一。不要混用两种格式的壳（例如在统一格式里用 `<div class="article">` 包全文）。

---

## 6. 与脚本的对应关系

- **统一格式（推荐）**：脚本通过「无 .article」或「.article 内无 .item」识别，提取 `<body>`（或 `</head>` 后）内容，将 `<section ...>` 转为 `<blockquote ...>`，表格保留，整篇包统一背景。
- **格式一（可选）**：脚本通过 `class="article"` + 至少一个 `.item` 识别，按早报逻辑解析（intro / item / thinking / divider / footer），并统一加样式、转 blockquote。
- **不符合规范**：脚本会做兼容尝试（如 .article 内无 .item 则当格式二处理），但**不保证**排版正确；应尽量让生成端符合本规范。

---

## 7. 校验（可选）

生成 HTML 后，可用以下自检清单确认符合规范后再交给 `html-to-wechat-copy.js`：

**格式一**

- [ ] 存在 `<div class="article">` 且闭合在 `</body>` 前
- [ ] 内含且顺序为：`h1` → `.intro` → 至少一个 `.item`（每项含 `.item-title`、`.item-content`、`.item-impact`）→ `.thinking` → `.divider` → `.footer`
- [ ] 未在正文内使用 `<section>` 或与 .item 无关的复杂块

**统一格式（推荐）**

- [ ] 正文在 `<body>` 内，且**未**用 `<div class="article">` 包全文
- [ ] 需背景/边框的块一律使用 `<section style="...">`
- [ ] 表格使用 `<table>`
- [ ] 有序/无序列表中，若使用“加粗前缀”，遵循「列表加粗规范」：用 `<span style="font-weight: normal;">` 断开字重，避免整行加粗

将此规范交给 AI 或生成器作为「HTML 输出规范」，即可长期稳定产出可被脚本正确处理的 HTML，无需再为各种随意结构改脚本。
