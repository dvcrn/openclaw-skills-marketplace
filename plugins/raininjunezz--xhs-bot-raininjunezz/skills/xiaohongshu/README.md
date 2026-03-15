# 📕 小红书自动化 Skill

通过浏览器自动化操作小红书，支持发布笔记、管理账号、数据爬取等功能。

## ⚠️ 重要提示

1. **账号安全**：自动化操作可能触发小红书风控系统
2. **先用小号测试**：确认稳定后再使用主号
3. **遵守社区规范**：不要用于 spam 或违规内容
4. **登录态本地存储**：密码不会上传到任何服务器

## 安装

```bash
cd ~/.openclaw/workspace/skills/xiaohongshu
npm install
```

## 快速开始

### 1. 登录

```bash
./xhs login
```

会在浏览器中打开小红书登录页面，手动完成登录后按回车。

### 2. 检查登录状态

```bash
./xhs login --check
```

### 3. 发布笔记

```bash
./xhs publish \
  --title "我的第一篇自动化笔记" \
  --content "这是通过 OpenClaw Skill 自动发布的内容！" \
  --images "/path/to/image1.jpg,/path/to/image2.jpg" \
  --tags "AI,自动化，OpenClaw"
```

### 4. 查看笔记数据

```bash
./xhs stats --note-id "笔记 ID"
```

### 5. 查看评论

```bash
./xhs comments --list --note-id "笔记 ID"
```

### 6. 回复评论

```bash
./xhs comments --reply --comment-id "评论 ID" --text "谢谢支持！"
```

### 7. 爬取笔记内容

```bash
./xhs scrape --note "https://www.xiaohongshu.com/explore/笔记 ID"
```

### 8. 爬取话题笔记

```bash
./xhs scrape --topic "AI" --limit 10
```

### 9. 退出登录

```bash
./xhs login --logout
```

## 配置

在 `~/.openclaw/openclaw.json` 中添加：

```json5
{
  skills: {
    entries: {
      xiaohongshu: {
        enabled: true,
        env: {
          XHS_BROWSER_HEADLESS: "false",  // 生产环境可设为 true
          XHS_SESSION_PATH: "~/.openclaw/xiaohongshu/session.json",
        },
      },
    },
  },
}
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `login` | 登录小红书 |
| `login --check` | 检查登录状态 |
| `login --logout` | 退出登录 |
| `publish` | 发布笔记 |
| `stats` | 查看数据统计 |
| `comments --list` | 查看评论列表 |
| `comments --reply` | 回复评论 |
| `scrape --note` | 爬取单篇笔记 |
| `scrape --topic` | 爬取话题笔记 |

## 常见问题

### Q: 提示未找到命令？
A: 确保脚本有执行权限：`chmod +x xhs`

### Q: 登录后还是提示未登录？
A: 删除会话文件重试：`rm ~/.openclaw/xiaohongshu/session.json`

### Q: 发布失败？
A: 检查图片格式（jpg/png/webp），标题不超过 20 字

### Q: 触发验证码？
A: 在浏览器中手动完成验证，后续操作会自动使用会话

## 技术实现

- **浏览器自动化**：Playwright
- **会话管理**：本地加密存储
- **风控规避**：模拟真人操作间隔

## 更新日志

### v1.0.0 (2026-03-13)
- 初始版本
- 支持发布笔记、查看数据、评论管理、内容爬取

## 许可证

MIT
