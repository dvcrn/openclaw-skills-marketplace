# OpenClaw 中使用本技能

## 加载方式

本技能放在**工作区**目录 `.openclaw/skills/wechat-article-typeset/` 下，在 OpenClaw 中打开本仓库（`wework`）时，会按工作区技能优先加载。

- 若未自动加载：确认 OpenClaw 的「工作区」或「当前目录」为本项目根目录。
- 全局使用：可把整个 `wechat-article-typeset` 目录复制到 `~/.openclaw/skills/`，则任意工作区都会加载。

## 触发方式

`SKILL.md` 中已配置 `trigger`，当用户输入包含以下关键词时会激活本技能：

- 公众号排版  
- 复制到公众号  
- edit.shiker.tech  
- 公众号文章  

也可在对话中直接说「帮我排成公众号格式并生成复制链接」等。

## 可选配置（Gate / 专属 Agent）

若希望仅在某些场景或某个 Agent 下启用，可在 OpenClaw 配置中为该技能设置 gate 或 agents，例如：

```yaml
skills:
  wechat-article-typeset:
    enabled: true
    # gate:
    #   keywords: ["公众号", "排版"]
    # agents: ["your-agent-name"]
```

## 流程（输入 = 用户 Md，输出 = 两个预览链接）

1. **输入**：用户提供的 **Markdown 文件**（如 article.md）。
2. 在技能目录下执行（推荐用纯英文参数，避免终端对中文参数的兼容问题）：  
   - **推荐**：`node wechat-dual-copy.js <input.md> --theme <themeId> --layout <layoutId> [--ai-html path]`  
   - 可选：`node wechat-dual-copy.js <input.md> --preset <预设名> [--ai-html path]`
3. 脚本会输出两条链接：`AI:`（AI 结构化版）与 `PRESET:`（预设主题版），并在 md 同目录写入 `wechat-preview-urls.txt`。
4. 将链接交给用户，浏览器打开后复制再粘贴到公众号。

> `--ai-html`：可选（**推荐使用**）。让 AI 先生成一份 HTML 初稿，再按 `SPEC.md`（自由模式/统一格式）改成第二版 `article.ai.html`，用该参数指定它；这样自由度最高、且排版最稳定。
>
> 说明：若你不提供 `--ai-html`，脚本会用公共库 **markdown-it** 把 md 转成一份基础 HTML 作为兜底（能跑通，但样式不如 AI 结构化版可控）。
>
> 注意：轻量转换默认**不允许** Markdown 内嵌原始 HTML（安全/一致性考虑）。如果你希望 AI 生成带 `<section style="...">` 的丰富卡片样式，请走 `--ai-html`，让 AI 直接按 `SPEC.md` 的「自由模式」输出 HTML。

### 如何让公众号预览达到「AI 单独生成 HTML」那种好看效果

**做法**：直接用那份好看的 AI HTML 作为输入即可，无需改脚本。

- **单链接**：在技能目录执行  
  `node html-to-wechat-copy.js <path-to-你的AI生成的.html>`  
  会得到一条预览链接，并写入同目录的 `wechat-preview-url.txt`。
- **双链接（AI + 预设）**：  
  `node wechat-dual-copy.js <input.md> --ai-html <path-to-你的AI生成的.html> --theme <themeId> --layout <layoutId>`  
  其中 `AI:` 那条链接就是用你这份 HTML 生成的，预览效果与本地打开该 HTML 一致（渐变、表格、引用块等都会保留）。

**原理**：脚本在「通用模式」下只做两件事：把 `<section>` 改成 `<blockquote>`（以便公众号保留背景/边框），表格和所有内联样式**原样保留**，再包一层统一背景。因此 AI 生成的内联样式（颜色、圆角、间距等）都会体现在公众号预览里。

### 推荐工作流：AI 先出初稿 HTML，再按规范改第二版

为了同时获得**自由度**与**稳定性**，建议这样用：

1. 让 AI **直接基于 Markdown 内容生成一份 HTML 初稿**（例如 `article.ai.draft.html`）。这份初稿允许风格随意，但应尽量接近 `SPEC.md` 的自由模式硬约束。
2. 再让 AI 按 `SPEC.md`（自由模式/统一格式）把初稿**严格改写**为第二版 `article.ai.html`（重点：高亮块用 `<section style>`；列表加粗按规范断字重；不要用 `.article` 壳等）。
3. 再运行：  
   `node wechat-dual-copy.js <input.md> --ai-html <path-to-article.ai.html> --theme <themeId> --layout <layoutId>`  
   这时 `AI:` 链接会以你改写后的结构化 HTML 为准，效果更可控。

> 可选辅助：如果你不想让 AI 从零生成 HTML，可用 `--emit-ai-draft` 让脚本先把 md 兜底渲染成 `article.ai.draft.html`，再交给 AI 做第二版改写。

常用等价示例：

- `墨色下划线` ≈ `--theme ink-seri --layout underline`

## 技能目录内的文件

- **SPEC.md**：**《公众号文章 HTML 生成规范》**，用于 AI 结构化版：Markdown → HTML 的**唯一约定**（格式一或格式二）。
- **html-to-wechat-copy.js**：将“输入 HTML”转为公众号兼容 HTML 并 POST 到 edit.shiker.tech，输出单条预览链接（并写入 `wechat-preview-url.txt`）。
- **wechat-dual-copy.js**：输入一个 md，一次生成两条预览链接（AI / PRESET），并写入 `wechat-preview-urls.txt`。

## 依赖

- Node.js（支持 ES Module）。
- 网络：需能请求 `https://edit.shiker.tech/api/copy` 以获取复制页链接。
- 首次运行请在技能目录执行 `npm install`（安装 markdown-it）。
