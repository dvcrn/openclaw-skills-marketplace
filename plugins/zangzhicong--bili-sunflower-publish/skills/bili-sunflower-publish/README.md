# bili-sunflower-publish

One-click publishing of HTML content to Bilibili, supporting both **Article** (专栏) and **Tribee** (小站) targets.

## Features

- 🔐 Auto-detects login status; prompts manual login when needed
- 📝 Smart title handling: auto-shortens long titles, generates suggestions for meaningless ones
- 📋 Rich HTML paste via macOS system clipboard (NSPasteboard)
- 🚀 One-click publish with full control over article settings (cover, scheduling, originality declaration, etc.)
- 🔄 Automatic fallback to CDP WebSocket injection if clipboard paste fails

## Supported Targets

| Target | Description |
|--------|-------------|
| **Article (专栏)** | Long-form articles on `member.bilibili.com` |
| **Tribee (小站)** | Community posts on `bilibili.com/bubble` |

## Prerequisites

- **macOS** (requires Swift NSPasteboard for HTML clipboard)
- **OpenClaw** with the `openclaw` browser profile (Playwright-managed browser)

## Trigger Keywords

This skill activates when the user mentions:

> 发布文章到B站 / 上传专栏 / 发B站文章 / 发小站帖子 / tribee发帖 / publish to Bilibili

## Workflow

1. **Navigate & Login Check** — Opens the target editor page and verifies login status
2. **Title Handling** — Uses user-provided title or infers from filename; offers alternatives if problematic
3. **Paste Article Body** — Swift script sets HTML clipboard → `⌘V` paste into the editor
4. **Publish** — Applies user-requested settings and clicks the publish button

## File Structure

```
bili-sunflower-publish/
├── SKILL.md                         # Skill definition & detailed workflow
├── README.md                        # This file (English)
├── README_zh.md                     # 中文说明
└── scripts/
    └── set_html_clipboard.swift     # macOS clipboard HTML writer
```

## Author

**Vicky**
