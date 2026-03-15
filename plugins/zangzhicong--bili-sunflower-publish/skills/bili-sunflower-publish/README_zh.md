# bili-sunflower-publish

将 HTML 内容一键发布到 Bilibili，支持 **专栏**（Article）和 **小站**（Tribee）两种目标。

## 功能

- 🔐 自动检测登录状态，未登录时提示手动登录
- 📝 智能标题处理：过长自动缩短、无意义标题自动生成建议
- 📋 通过 macOS 系统剪贴板（NSPasteboard）粘贴富文本 HTML
- 🚀 一键发布，支持专栏发布设置（封面、定时、原创声明等）
- 🔄 粘贴失败时自动回退 CDP WebSocket 注入方案

## 支持的发布目标

| 目标 | 说明 |
|------|------|
| **专栏 (Article)** | `member.bilibili.com` 长文章 |
| **小站 (Tribee)** | `bilibili.com/bubble` 社区帖子 |

## 前置条件

- **macOS**（依赖 Swift NSPasteboard 设置 HTML 剪贴板）
- **OpenClaw** 的 `openclaw` 浏览器 profile（Playwright 管理的浏览器）

## 触发词

以下关键词会自动激活此 Skill：

> 发布文章到B站 / 上传专栏 / 发B站文章 / 发小站帖子 / tribee发帖 / publish to Bilibili

## 工作流程

1. **导航 & 登录检查** — 打开对应编辑器页面，检测登录状态
2. **标题处理** — 用户指定或自动推断，异常时提供候选
3. **粘贴文章正文** — Swift 脚本设置 HTML 剪贴板 → 编辑器内 `⌘V` 粘贴
4. **发布** — 应用用户设置后点击发布按钮

## 文件结构

```
bili-sunflower-publish/
├── SKILL.md                         # Skill 定义与详细流程
├── README.md                        # English README
├── README_zh.md                     # 本文件（中文说明）
└── scripts/
    └── set_html_clipboard.swift     # macOS 剪贴板 HTML 写入工具
```

## 作者

**Vicky**
