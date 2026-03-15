---
name: social-publisher
description: "同时发布内容到微博和小红书，使用真实 Chrome 浏览器绕过反机器人检测。支持文字、图片、预览模式和实际发布。当用户需要发布微博、发微博、weibo post、发布小红书、发小红书、xiaohongshu post 时使用此 skill。"
---

# 社交平台发布工具

使用真实 Chrome 浏览器同时发布到微博和小红书，支持文字和图片。

## 脚本目录

所有脚本位于 scripts/ 子目录。

## 前置要求

- Google Chrome 或 Chromium 已安装
- bun 已安装
- 首次运行：在打开的浏览器窗口中登录各平台

## 发布到微博

```bash
# 预览模式（不发布）
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "你好，微博！"

# 带图片
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "看这张图！" --image ./photo.png

# 实际发布
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "发布微博！" --image ./photo.png --submit
```

## 发布到小红书

```bash
# 预览模式（不发布）
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --xhs "你好，小红书！" --image ./photo.png

# 实际发布
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --xhs "发布小红书！" --image ./photo.png --submit
```

## 同时发布到微博和小红书

```bash
# 预览模式
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "你好！" --xhs "你好！" --image ./photo.png

# 实际发布
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "同时发布！" --xhs "同时发布！" --image ./photo.png --submit
```

## 参数说明

| 参数 | 描述 |
|------|------|
| `--weibo <text>` | 微博内容 |
| `--xhs <text>` | 小红书内容 |
| `--image <path>` | 图片路径（可重复） |
| `--submit` | 实际发布（默认：仅预览） |
| `--profile <dir>` | 自定义 Chrome 配置目录 |

## 注意事项

- 首次运行需要手动登录各平台（会话会保存）
- 总是先用预览模式确认，再使用 --submit
- 小红书至少需要 1 张图片
- 微博普通帖子限制 2000 字
- 支持 macOS、Linux 和 Windows
