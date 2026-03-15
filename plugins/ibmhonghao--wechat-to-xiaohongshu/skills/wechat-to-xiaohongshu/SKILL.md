---
name: wechat-to-xiaohongshu
description: "Automatically migrate WeChat Official Account articles to Xiaohongshu (Little Red Book). Use when the user wants to (1) cross-post published WeChat articles to Xiaohongshu, (2) sync content between WeChat and Xiaohongshu platforms, (3) automate daily article distribution workflow."
---

# WeChat to Xiaohongshu Content Migration

**Automates cross-posting of WeChat Official Account articles to Xiaohongshu (Little Red Book)** — the leading Chinese content platform.

This skill handles the entire workflow: fetching latest articles from WeChat, importing them to Xiaohongshu with auto-formatting, adding relevant hashtags, and publishing — all without manual intervention on either platform.

## Quick Start

```
"把今天的微信文章搬到小红书"
或
"用 wechat-to-xiaohongshu 发布最新文章"
```

**Result:** Article imported, formatted, tagged, and published in ~50 seconds.

## Before You Start

✅ **See full requirements:** Read `REQUIREMENTS.md` for hardware, software, and account setup.

**Quick checklist:**
- ✅ WeChat OA account with published articles
- ✅ Xiaohongshu creator account with publish permission
- ✅ Both platforms logged in (browser tabs open)
- ✅ OpenClaw Browser Relay extension installed and **ON** on both tabs

---

## Using This Skill

**→ See `USAGE.md`** for:
- How to invoke the skill in conversation
- Common workflow scenarios
- Customization options
- Tips for better results

---

## Troubleshooting

**→ See `TROUBLESHOOTING.md`** for:
- Common error messages and fixes
- Network/connection issues
- Account/permission problems
- Browser relay troubleshooting

## Workflow

### 1. Prepare Browser Tabs

Ensure both platforms are open and the OpenClaw Browser Relay extension is attached (ON status):

- WeChat Official Account backend: `https://mp.weixin.qq.com`
- Xiaohongshu Creator Platform: `https://creator.xiaohongshu.com/publish/publish?from=menu&target=article`

Check tabs:
```
browser(action="tabs", profile="chrome")
```

### 2. Find the Latest Article

Navigate to WeChat backend and identify the most recent published article:

```
browser(action="snapshot", profile="chrome", targetId="<wechat-tab-id>")
```

Look for the "近期发表" (Recent Posts) section. The latest article will be at the top with today's timestamp.

### 3. Get Article URL

The article URL is in the link element. Format: `https://mp.weixin.qq.com/s/<article-id>`

Extract the URL from the snapshot (check the link href in recent posts).

### 4. Import to Xiaohongshu

Switch to Xiaohongshu tab and use the "导入链接" (Import Link) feature:

a. Click "导入链接" button:
```
browser(action="act", profile="chrome", targetId="<xiaohongshu-tab-id>", 
        request={"kind": "click", "ref": "<import-button-ref>"})
```

b. Paste the WeChat article URL:
```
browser(action="act", profile="chrome", targetId="<xiaohongshu-tab-id>",
        request={"kind": "type", "ref": "<input-field-ref>", "text": "<article-url>"})
```

c. Click "一键排版" (Auto Format):
```
browser(action="act", profile="chrome", targetId="<xiaohongshu-tab-id>",
        request={"kind": "click", "ref": "<format-button-ref>"})
```

Wait 30 seconds for import to complete.

### 5. Add Topics and Publish

a. Take snapshot to find the description field:
```
browser(action="snapshot", profile="chrome", targetId="<xiaohongshu-tab-id>")
```

b. Add relevant hashtags to description:
```
browser(action="act", profile="chrome", targetId="<xiaohongshu-tab-id>",
        request={"kind": "type", "ref": "<description-ref>", 
                 "text": "#小龙虾 #OpenClaw #AI工具 #自动化办公 #效率工具 #人工智能"})
```

Customize hashtags based on article content.

c. Click "下一步" (Next) if needed to proceed to publish settings.

d. Click "发布" (Publish):
```
browser(action="act", profile="chrome", targetId="<xiaohongshu-tab-id>",
        request={"kind": "click", "ref": "<publish-button-ref>"})
```

## Error Handling

**Extension disconnected**: If you get "tab not found" error:
- Ask user to re-click the OpenClaw extension icon on the relevant tab
- Wait for "ON" badge to appear
- Retry the operation

**Import failed**: If "一键排版" times out or fails:
- Verify the WeChat article URL is publicly accessible
- Check if article contains unsupported media types
- Try manual copy-paste as fallback

**Publish button disabled**: Usually means:
- Content hasn't fully loaded yet (wait longer)
- Required fields missing (check title/description)
- Image processing still in progress

## Customization

Adjust hashtags based on article topic. Common categories:

- **AI/Tech**: #人工智能 #AI工具 #科技 #效率工具
- **Programming**: #程序员 #编程 #开发者工具
- **Business**: #职场 #效率 #自动化办公
- **Tutorial**: #教程 #干货分享 #实用技巧

## Notes

- Import preserves formatting, images, and text structure
- Cover images are auto-generated (7 options provided)
- Character count is displayed after import
- Auto-save activates every few minutes
- Published articles appear in "笔记管理" (Note Management)
