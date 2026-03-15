---
name: xiaohongshu
description: "小红书自动化操作 - 发布笔记、管理账号、数据爬取、定时发布。使用浏览器自动化模拟真人操作。"
homepage: https://github.com/openclaw/skills/xiaohongshu
---

# 小红书 Skill (Xiaohongshu)

通过浏览器自动化操作小红书，支持发布笔记、管理账号、数据爬取等功能。

## ⚠️ 使用须知

1. **账号安全**：自动化操作可能触发风控，建议先用小号测试
2. **登录状态**：首次使用需手动登录，会话状态本地存储
3. **合规使用**：请遵守小红书社区规范，不要用于 spam 或违规内容

## 命令列表

### 发布笔记
```bash
/xhs-publish --title "标题" --content "内容" --images "/path/to/img1.jpg,/path/to/img2.jpg" --tags "标签 1,标签 2"
```

### 查看草稿
```bash
/xhs-drafts --list
/xhs-drafts --delete --id <draft_id>
```

### 查看数据
```bash
/xhs-stats --note-id <note_id>
/xhs-stats --account
```

### 评论管理
```bash
/xhs-comments --list --note-id <note_id>
/xhs-comments --reply --comment-id <comment_id> --text "回复内容"
```

### 内容爬取
```bash
/xhs-scrape --note <note_url>
/xhs-scrape --topic "话题名称" --limit 10
```

### 定时发布
```bash
/xhs-schedule --title "标题" --content "内容" --time "2026-03-14 10:00"
/xhs-schedule --list
/xhs-schedule --cancel --id <schedule_id>
```

### 登录检查
```bash
/xhs-login --check
/xhs-login --logout
```

## 配置

在 `~/.openclaw/openclaw.json` 中配置：

```json5
{
  skills: {
    entries: {
      xiaohongshu: {
        enabled: true,
        env: {
          XHS_BROWSER_HEADLESS: "false",  // 是否无头模式
          XHS_SESSION_PATH: "~/.openclaw/xiaohongshu/session.json",  // 会话存储路径
        },
      },
    },
  },
}
```

## 技术实现

- 使用 Playwright 进行浏览器自动化
- 会话状态加密存储
- 模拟真人操作间隔，降低风控风险

## 常见问题

**Q: 登录后还是提示未登录？**
A: 检查会话文件是否存在，尝试 `/xhs-login --logout` 后重新登录

**Q: 发布失败怎么办？**
A: 检查图片格式（支持 jpg/png/webp），标题不超过 20 字，内容不超过 1000 字

**Q: 触发验证码怎么处理？**
A: 浏览器会显示验证码页面，手动完成验证后继续操作
