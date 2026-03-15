---
name: bili-sunflower-publish
description: "Publish HTML content to Bilibili — supports both 专栏 (article) and 小站 (tribee) targets. Handles login check, title input, HTML paste via clipboard, and direct publish. Trigger when user asks to publish to B站专栏/小站, or mentions 发布文章到B站/上传专栏/发B站文章/发小站帖子/tribee发帖."
---

# bili-sunflower-publish

Unified publish pipeline for Bilibili: HTML file → editor → publish.

Supports two targets:

- **专栏 (Article)**: long-form articles on `member.bilibili.com`
- **小站 (Tribee)**: community posts on `bilibili.com/bubble`

## Prerequisites

- **macOS** (uses Swift NSPasteboard for HTML clipboard)
- **Browser tool** with `openclaw` profile (Playwright-managed browser)

## Input

- **HTML file path** (article body)
- **Target type**: `article` (专栏) or `tribee` (小站) — infer from user intent
- **Title** (optional — see Phase 2)
- For tribee: **tribee name or ID** (required)
- For tribee: **分区** (category, optional — user can specify or choose during publish)

---

## Phase 1: Navigate & Login Check

### Article mode

Navigate to `https://member.bilibili.com/york/read-editor` and take a snapshot.

- **Logged in**: editor loads with title textbox `"请输入标题（建议30字以内）"`
- **Not logged in**: redirects to login page

### Tribee mode

Publish URL: `https://www.bilibili.com/bubble/publish?tribee_id={id}&tribee_name={name}`

Both `tribee_id` and `tribee_name` are required for the publish URL. Resolve missing params:

| User provides | Resolution                                                                                                                                            |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| id + name     | Direct → publish URL                                                                                                                                  |
| id only       | Navigate to `https://www.bilibili.com/bubble/home/{id}`, extract tribee name from the page, then → publish URL                                        |
| name only     | Search `https://search.bilibili.com/all?keyword={name}`, find the card linking to `bilibili.com/bubble/home/{id}`, extract `{id}`, then → publish URL |

After navigating to the publish URL:

- **Logged in + member**: editor loads with title and body area
- **Not logged in**: redirects to login page
- **Not a member**: may show join prompt — tell user to join the tribee first

If not logged in, **stop and tell the user** to log in manually in the openclaw browser profile, then retry.

---

## Phase 2: Title Handling

Determine the title:

1. If user provided a title → use it
2. If not → use HTML filename (sans `.html` extension)

After resolving, validate:

- **Title > 50 characters**: present 2-3 shortened alternatives, let user choose
- **Title looks meaningless** (e.g. `output`, `untitled`, `temp`, or clearly unrelated to the HTML content): read the first few hundred chars of HTML body, generate 2-3 title suggestions, let user choose

Do NOT silently use a bad title. Wait for user selection before proceeding.

Enter the title: click the title textbox and type.

---

## Phase 3: Paste Article Body

Both editors share the same rich-text editor component.

### 3a. Set HTML clipboard (macOS NSPasteboard)

```bash
swift {SKILL_DIR}/scripts/set_html_clipboard.swift <html-file>
```

Sets `text/html` + `text/plain` on the system clipboard.

### 3b. Focus editor body and paste

1. Click the body contenteditable area
2. Press `Meta+v` to paste

**Note:** The `openclaw` Playwright browser profile on macOS correctly routes `Meta+v` through the system clipboard. This does NOT work with the Chrome extension relay profile.

### 3c. Verify paste

Evaluate JS to confirm content was pasted:

```javascript
// DOM selector for the editor's contenteditable area
(function () {
  const e = document.querySelector(".eva3-editor");
  return { chars: e.textContent.length, first80: e.textContent.substring(0, 80) };
})();
```

Expected: `chars > 100` and `first80` matches the article opening.

---

## Phase 4: Publish

### Article mode

Editor bottom has a "发布设置" panel (usually already visible) with defaults that work out of the box:

- 可见范围: 所有人可见 (default)
- 封面: auto-generated from body text (default)
- 评论: enabled (default)

If the user has specific publishing preferences, adjust before publishing:

| 设置          | 操作                                  | 说明                            |
| ------------- | ------------------------------------- | ------------------------------- |
| 可见范围      | 选 radio: "所有人可见" / "仅自己可见" | 仅自己可见不支持分享和商业推广  |
| 自定义封面    | 勾选 checkbox → 上传图片              | 不设则自动抓正文开头文字        |
| 评论开关      | 勾选/取消 checkbox                    | 关闭后无法评论                  |
| 精选评论      | 勾选 checkbox                         | 开启后需手动筛选评论才展示      |
| 定时发布      | 勾选 checkbox → 选择时间              | 范围: 当前+2h ~ 7天内，北京时间 |
| 创作声明-原创 | 勾选 checkbox                         | 声明原创，禁止转载              |
| 创作声明-AI   | 勾选 checkbox                         | 标识使用 AI 合成技术            |
| 话题          | 点击"添加话题"按钮                    | 可选                            |
| 文集          | 点击"选择文集"按钮                    | 可选                            |

Steps:

1. Scroll down to confirm the "发布设置" panel is visible; if collapsed, click "发布设置" button to expand
2. Apply any user-requested settings from the table above
3. Click **"发布"** button (next to "保存为草稿", at the bottom right)
4. If a confirmation dialog appears, confirm
5. Verify publish succeeded (URL changes or success toast)

### Tribee mode

Bottom bar appears after content is entered, with defaults that work out of the box:

- 分区: 未选择 (some tribees may require)
- 同步至动态: enabled (default)

If the user has specific preferences, adjust before publishing:

| 设置       | 操作                          | 说明                         |
| ---------- | ----------------------------- | ---------------------------- |
| 分区       | 点击"选择分区"下拉 → 选择分区 | 部分小站可能必选             |
| 同步至动态 | 取消勾选 checkbox             | 默认开启，取消后不同步到动态 |

#### 分区自动选择（Tribee only）

When the user **did not specify** a 分区:

1. Click "选择分区" dropdown to reveal available options
2. Read the list of 分区 names from the dropdown (snapshot)
3. Based on the **article title + first ~200 chars of body content**, pick the most relevant 分区:
   - Match by keyword/topic similarity (e.g. tutorial content → "经验分享", questions → "提问求助")
   - If no option is a clear fit, pick the most general/catch-all option
   - If the tribee only has 1-2 generic options, just pick the best one without overthinking
4. Click the chosen 分区
5. Do **not** ask the user to confirm — just pick and proceed (they can always re-publish if wrong)

If the user **did specify** a 分区, use it directly (skip auto-selection).

Steps:

1. Handle 分区 (user-specified or auto-selected per above)
2. Apply any other user-requested settings
3. Click **"发布"** button (blue, bottom right)
4. Verify publish succeeded

---

## Fallback: CDP WebSocket Injection

If `Meta+v` paste fails (clipboard not recognized), use direct CDP injection:

1. Split HTML into ~1500-char chunks
2. Connect via CDP WebSocket to inject chunks into `window.__hp` array
3. Join and dispatch a synthetic ClipboardEvent with `text/html`

```javascript
// DOM selector for the editor's contenteditable area
// After all chunks pushed to window.__hp:
(function () {
  const e = document.querySelector(".eva3-editor");
  e.focus();
  const html = window.__hp.join("");
  const dt = new DataTransfer();
  dt.setData("text/html", html);
  const pe = new ClipboardEvent("paste", { bubbles: true, cancelable: true, clipboardData: dt });
  e.dispatchEvent(pe);
  return e.textContent.length;
})();
```

CDP WebSocket URL pattern: `ws://127.0.0.1:18800/devtools/page/{targetId}`

Locate the `ws` module dynamically:

```bash
node -e "console.log(require.resolve('ws', {paths:[require.resolve('openclaw')]}))"
```

Use `Runtime.evaluate` to inject each chunk. Keep each evaluate payload under 6KB.

---

## Execution

Default: execute Phase 1 → 4 directly in the main session (supports user interaction for login/title).

Only delegate to subagent if the user explicitly requests it.
