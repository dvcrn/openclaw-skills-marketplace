# 🎬 Video Pusher — 多平台视频一键发布工具

**[English](#english) | [中文](#chinese)**

> 用 AI 驱动的自动化工具，将视频/图文内容一键同步发布到抖音、小红书、微信视频号、Threads、Instagram。
>
> AI-powered automation tool to publish videos and posts to Douyin, Xiaohongshu, WeChat Channels, Threads, and Instagram — all at once.

![platforms](https://img.shields.io/badge/platforms-抖音%20·%20小红书%20·%20视频号%20·%20Threads%20·%20Instagram-blue)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

---

<a name="chinese"></a>

## 📖 简介

**Video Pusher** 是一套运行在 [Claude Code](https://claude.ai/code) 或 [OpenClaw](https://openclaw.ai) 上的 Skills，让 AI 替你操控浏览器完成多平台发布——你只需要最后检查并点一下"发布"。

**核心优势：**
- 🚀 **一次操作，五平台同步** — 抖音、小红书、微信视频号、Threads、Instagram
- 🔐 **登录一次，永久复用** — Session 保存在本地，无需每次扫码
- 🤖 **AI 全程协助** — 告诉  AI 要发什么，它帮你检查状态、依次完成发布
- 🛡️ **半自动设计** — 脚本填好内容，你来确认后点发布，避免误操作
- 💻 **Mac / Windows / Linux 全平台支持**

---

## ✨ 功能演示

```
你：发布 /Users/me/video.mp4 到抖音和小红书，A组账号，标题「春季护肤指南」，标签 护肤 医美

Claude：
  ✅ 抖音 已登录
  ✅ 小红书 已登录
  📤 正在打开抖音创作者平台...
  ✏️  标题、正文、标签已填写
  ✅ 内容填写完毕！请检查后点击【发布】按钮
  （用户点击发布，关闭浏览器）
  📤 正在打开小红书创作者平台...
  ...
```

---

## 🚀 快速开始

### 安装

**方式一：Claude Code**

```bash
git clone https://github.com/your-username/video-pusher
cd video-pusher
uv sync
uv run playwright install chromium   # 首次必须，约 150MB
```

**方式二：OpenClaw / ClawHub**

```bash
clawhub install your-username/video-pusher
uv run playwright install chromium
```

### 使用步骤

**1. 创建账号组**

```bash
uv run python skills/vp-accounts/vp_accounts.py add "我的账号"
```

**2. 登录各平台**（浏览器弹出，完成登录后关闭窗口即自动保存）

```bash
uv run python skills/vp-accounts/vp_accounts.py login "我的账号" douyin
uv run python skills/vp-accounts/vp_accounts.py login "我的账号" xhs
uv run python skills/vp-accounts/vp_accounts.py login "我的账号" shipinhao
uv run python skills/vp-accounts/vp_accounts.py login "我的账号" threads
uv run python skills/vp-accounts/vp_accounts.py login "我的账号" ins
```

**3. 查看登录状态**

```bash
uv run python skills/vp-accounts/vp_accounts.py list
```

**4. 发布内容**

```bash
# 抖音
uv run python skills/vp-publish-douyin/publish_douyin.py \
  --file /path/to/video.mp4 --title "标题" --tags "护肤 医美" --group "我的账号"

# 小红书（视频/图片均支持）
uv run python skills/vp-publish-xhs/publish_xhs.py \
  --file /path/to/video.mp4 --title "标题" --group "我的账号"

# 微信视频号
uv run python skills/vp-publish-shipinhao/publish_shipinhao.py \
  --file /path/to/video.mp4 --title "短标题" --description "描述" --group "我的账号"

# Threads（--file 可选，支持纯文字）
uv run python skills/vp-publish-threads/publish_threads.py \
  --title "正文内容" --tags "护肤" --group "我的账号"

# Instagram
uv run python skills/vp-publish-ins/publish_ins.py \
  --file /path/to/photo.jpg --title "Caption" --group "我的账号"
```

**5. 让 Claude 一键多平台发布**

在 Claude Code / OpenClaw 中直接说：

> 发布 `/path/to/video.mp4` 到抖音和小红书，使用「我的账号」，标题「xxx」，正文「yyy」，标签 护肤 医美

---

## 📦 Skills 列表

| Skill | 功能 |
|-------|------|
| `vp-accounts` | 账号组管理：创建/删除账号组，登录各平台，查询登录状态 |
| `vp-publish` | 多平台编排：一次指令，依次发布到多个平台 |
| `vp-publish-douyin` | 抖音发布：上传视频，自动填写标题/正文/标签 |
| `vp-publish-xhs` | 小红书发布：支持视频和图片，自动切换模式 |
| `vp-publish-shipinhao` | 微信视频号发布：微信扫码登录，单独填写短标题 |
| `vp-publish-threads` | Threads 发布：支持纯文字或带媒体 |
| `vp-publish-ins` | Instagram 发布：自动完成裁剪/滤镜多步骤流程 |

---

## ⚙️ 参数说明

所有发布脚本共用：

| 参数 | 必填 | 说明 |
|------|------|------|
| `--file` | 抖音/小红书/视频号必填 | 媒体文件绝对路径 |
| `--title` | 必填 | 标题 / Caption / 帖子正文开头 |
| `--description` | 否 | 正文内容（视频号为描述字段） |
| `--tags` | 否 | 标签，空格分隔，自动加 `#` 前缀 |
| `--group` | 必填 | 账号组名称 |

---

## 🔧 工作原理

1. 打开 Chromium，加载本地已保存的登录 Session
2. 自动填写标题、正文、标签，上传媒体文件
3. **你来检查内容，手动点击发布按钮**
4. 关闭浏览器窗口，脚本自动退出，继续下一个平台

Session 保存在 `profile/` 目录（已加入 `.gitignore`，不会上传到 Git）。

---

## 🛠️ 开发

```bash
uv run pytest tests/ -v          # 运行全部测试
uv run pytest tests/test_vp_accounts.py -v   # 运行单个测试文件
```

---

<a name="english"></a>

## 📖 Overview

**Video Pusher** is a collection of AI Skills for [Claude Code](https://claude.ai/code) / [OpenClaw](https://openclaw.ai) that automates multi-platform video publishing. The AI controls the browser to fill in titles, descriptions, tags, and upload files — you just review and click "Publish".

**Key Features:**
- 🚀 **One command, five platforms** — Douyin (TikTok China), Xiaohongshu (RED), WeChat Channels, Threads, Instagram
- 🔐 **Login once, reuse forever** — Sessions saved locally, no repeated QR scanning
- 🤖 **AI-assisted workflow** — Tell Claude what to publish, it handles the rest
- 🛡️ **Semi-automatic by design** — Script fills content, you confirm before publishing
- 💻 **Mac / Windows / Linux support**

---

## 🚀 Quick Start

### Installation

**Option 1: Claude Code**

```bash
git clone https://github.com/your-username/video-pusher
cd video-pusher
uv sync
uv run playwright install chromium   # Required on first run (~150MB)
```

**Option 2: OpenClaw / ClawHub**

```bash
clawhub install your-username/video-pusher
uv run playwright install chromium
```

### Usage

**1. Create an account group**

```bash
uv run python skills/vp-accounts/vp_accounts.py add "MyGroup"
```

**2. Log in to each platform** (browser opens, log in, close window to save session)

```bash
uv run python skills/vp-accounts/vp_accounts.py login "MyGroup" douyin
uv run python skills/vp-accounts/vp_accounts.py login "MyGroup" xhs
uv run python skills/vp-accounts/vp_accounts.py login "MyGroup" shipinhao
uv run python skills/vp-accounts/vp_accounts.py login "MyGroup" threads
uv run python skills/vp-accounts/vp_accounts.py login "MyGroup" ins
```

**3. Check login status**

```bash
uv run python skills/vp-accounts/vp_accounts.py list
```

**4. Publish content**

```bash
# Douyin
uv run python skills/vp-publish-douyin/publish_douyin.py \
  --file /path/to/video.mp4 --title "My Title" --tags "skincare beauty" --group "MyGroup"

# Xiaohongshu (video or image)
uv run python skills/vp-publish-xhs/publish_xhs.py \
  --file /path/to/video.mp4 --title "My Title" --group "MyGroup"

# WeChat Channels
uv run python skills/vp-publish-shipinhao/publish_shipinhao.py \
  --file /path/to/video.mp4 --title "Short Title" --description "Description" --group "MyGroup"

# Threads (--file optional, text-only supported)
uv run python skills/vp-publish-threads/publish_threads.py \
  --title "Post content" --tags "skincare" --group "MyGroup"

# Instagram
uv run python skills/vp-publish-ins/publish_ins.py \
  --file /path/to/photo.jpg --title "Caption text" --group "MyGroup"
```

**5. Let Claude publish to multiple platforms at once**

In Claude Code / OpenClaw, just say:

> Publish `/path/to/video.mp4` to Douyin and Xiaohongshu using "MyGroup", title "Spring Skincare Guide", tags: skincare beauty

---

## 📦 Skills

| Skill | Description |
|-------|-------------|
| `vp-accounts` | Account group management: create/delete groups, log in to platforms, check login status |
| `vp-publish` | Multi-platform orchestration: one command to publish everywhere |
| `vp-publish-douyin` | Publish to Douyin: upload video, auto-fill title/body/tags |
| `vp-publish-xhs` | Publish to Xiaohongshu: supports video and images |
| `vp-publish-shipinhao` | Publish to WeChat Channels: WeChat QR login, separate short title field |
| `vp-publish-threads` | Publish to Threads: text-only or with media |
| `vp-publish-ins` | Publish to Instagram: auto-navigates crop/filter/caption steps |

---

## ⚙️ Parameters

All publish scripts share these parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--file` | Yes (Douyin/XHS/Channels) | Absolute path to media file |
| `--title` | Yes | Title / Caption / Post opening text |
| `--description` | No | Body text (description field for WeChat Channels) |
| `--tags` | No | Hashtags, space-separated, `#` added automatically |
| `--group` | Yes | Account group name |

---

## 🔧 How It Works

1. Opens Chromium with a saved local session (no login needed)
2. Automatically fills in title, body, tags and uploads media
3. **You review the content and manually click Publish**
4. Close the browser window — script exits and moves to the next platform

Sessions are stored in `profile/` (gitignored, never committed).

---

## 🛠️ Development

```bash
uv run pytest tests/ -v
```

---

## 📄 License

MIT
