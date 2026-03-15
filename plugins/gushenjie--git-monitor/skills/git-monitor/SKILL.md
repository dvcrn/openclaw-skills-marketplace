---
name: git-monitor
description: "通用 Git 项目监控工具。支持 GitHub、GitLab、Gitee 等所有 Git 平台。可以添加、删除、检查任意 Git 仓库的更新，自动拉取代码并生成变更摘要。当用户询问\"监控项目\"、\"检查更新\"、\"添加仓库\"、\"代码有什么变化\"、\"拉取最新代码\"、\"仓库更新通知\"、\"自动同步代码\"、\"追踪项目变更\"时使用此技能。即使用户没有明确说\"监控\"，只要涉及跟踪代码仓库的变化、获取更新通知、或需要定期检查项目状态，都应该使用此技能。"
---

# Git 项目监控技能

自动监控 Git 项目更新（支持 GitHub、GitLab、Gitee 等所有 Git 平台），拉取最新代码并生成变更摘要。

## 首次使用配置（必读）

### 1. 配置飞书通知（可选）

如果你需要推送通知到飞书，需要配置以下信息：

1. 打开 `config.json` 文件
2. 替换以下占位符为你的飞书配置：

```json
"feishu": {
  "appId": "你的飞书应用ID",
  "appSecret": "你的飞书应用密钥",
  "chatId": "你的群聊ID"
}
```

**如何获取飞书配置：**
- 登录飞书开放平台：https://open.feishu.cn/
- 创建企业自建应用
- 获取 App ID 和 App Secret
- 在应用权限中开启 `im:chat:read:chat_id` 和 `im:message:send_as_bot`
- 将应用添加到群聊，获取群聊 ID

### 2. 配置监控仓库

在 `config.json` 的 `repositories` 数组中添加你想监控的仓库：

```json
{
  "url": "https://github.com/owner/repo.git",
  "name": "my-project",
  "platform": "github",
  "owner": "owner",
  "repo": "repo",
  "localPath": "/path/to/local/clone",
  "branch": "main"
}
```

## 功能

1. **初始化监控** - 克隆目标仓库到本地
2. **检查更新** - 对比本地和远程的 commit 差异
3. **拉取代码** - 自动更新本地仓库
4. **生成摘要** - 分析 commit 信息和代码变更，生成可读的更新摘要
5. **通知推送** - 通过 Feishu 推送更新通知

## 使用方法

### 添加监控项目（支持多种平台）
```
监控 GitHub 项目 anthropics/skills
监控 https://github.com/openai/openai-python
监控 GitLab 项目 gitlab-org/gitlab
监控 https://gitlab.com/gitlab-org/gitlab-runner
监控 Gitee 项目 openharmony/docs
监控 https://gitee.com/mindspore/mindspore
添加仓库 https://git.example.com/my-org/my-project
```

### 查看监控列表
```
查看监控列表
列出所有监控的仓库
```

### 检查更新
```
检查所有更新
检查 anthropics/skills 的更新
```

### 拉取最新代码
```
拉取最新代码
更新所有仓库
```

### 删除监控
```
删除监控 anthropics/skills
取消监控 openai/openai-python
```

## 命令行用法

```bash
# 添加监控
node helper.js add https://github.com/owner/repo

# 列出监控
node helper.js list

# 检查更新
node helper.js check

# 拉取代码
node helper.js pull

# 删除监控
node helper.js remove owner/repo
```
