---
name: bark-push
description: "智能 Bark 推送助手，支持多用户管理、智能内容识别、历史记录追踪和消息更新功能"
homepage: https://bark.day.app
---

# Bark Push Skill

🔔 智能 Bark 推送助手，为您提供便捷、灵活的消息推送服务。

## 功能特性

### 🎯 智能内容识别
自动识别您发送的内容类型，以最优方式推送：
- **纯图片**：直接推送图片 URL（使用 `image` 参数）
- **纯链接**：直接推送链接（使用 `url` 参数）
- **纯文本**：推送文本内容（使用 `body` 参数）
- **混合内容**：自动整理为 Markdown 格式

### 👥 多用户管理
- 支持单用户推送：`--user alice`
- 支持多用户推送：`--user alice,bob,charlie`
- 支持全员推送：`--user all`
- 使用别名简化操作，无需记忆复杂的 device_key
- 未指定用户时智能提示可用用户列表

### 📝 智能标题生成
- 用户未输入标题时，自动根据内容生成 title 和 subtitle
- 用户指定标题时，优先使用用户提供的标题

### 📂 分组管理
- 支持查询和使用 Bark 分组功能
- 可指定消息分组或使用默认分组
- 分组不存在时自动使用默认分组

### 🔄 历史记录与更新
- 保存推送历史记录（推送 ID、用户、参数等）
- 支持查询历史并更新已推送的消息内容
- 支持删除已推送的消息
- 历史记录自动管理，超过限制自动删除最旧记录

### ⚙️ 灵活参数配置
通过 JSON 配置文件管理默认推送参数：
- **level**：消息级别（passive/active/time-sensitive/critical）
- **volume**：警告通知音量（0-10）
- **badge**：应用角标数字
- **sound**：通知声音
- **icon**：自定义图标 URL
- **call**：是否呼叫
- **autoCopy**：是否自动复制
- **copy**：复制到剪贴板的内容
- **isArchive**：是否自动归档
- **action**：自定义动作

用户指定的参数优先于默认配置。

### 📊 智能结果反馈
根据操作结果返回清晰的信息：
- **推送成功**：显示推送 ID、成功用户列表、参数摘要、内容简要
- **推送失败**：显示失败原因、失败用户列表、参数摘要、内容简要
- **指令错误**：显示错误原因、解析的参数列表、内容简要

## 快速开始

### 配置文件

首次使用前，创建配置文件 `config.json`：

```json
{
  "default_push_url": "https://api.day.app",
  "ciphertext": "",
  "users": {
    "alice": "your_device_key_1",
    "bob": "your_device_key_2"
  },
  "defaults": {
    "level": "active",
    "volume": 10,
    "badge": 1,
    "sound": "bell",
    "icon": "",
    "group": "default",
    "call": false,
    "autoCopy": false,
    "copy": "",
    "isArchive": true,
    "action": ""
  },
  "groups": ["work", "personal", "urgent"],
  "history_limit": 100,
  "enable_update": true
}
```

### 基本使用

```bash
# 推送简单文本消息
bark-push --user alice --content "Hello, World!"

# 推送带标题的消息
bark-push --user alice --title "重要通知" --content "会议将在10分钟后开始"

# 推送图片
bark-push --user bob --content "https://example.com/photo.jpg"

# 推送给多个用户
bark-push --user alice,bob --title "团队通知" --content "项目已上线"

# 推送给所有用户
bark-push --user all --title "系统公告" --content "服务器维护通知"

# 指定消息级别
bark-push --user alice --content "紧急事件" --level critical

# 指定分组
bark-push --user alice --content "工作提醒" --group work

# 更新已推送的消息
bark-push --update abc123 --user alice --content "会议时间改为15分钟后"

# 删除已推送的消息
bark-push --delete abc123 --user alice

# 查看历史记录
bark-push --list-history --history-limit 20

# 查看用户列表
bark-push --list-users

# 查看帮助信息
bark-push --help-skill
```

## 命令行参数

### 基本参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--config` | 配置文件路径 | `--config ./config.json` |
| `--user, -u` | 指定推送用户（别名或 device_key） | `--user alice` |
| `--title, -t` | 消息标题 | `--title "重要通知"` |
| `--subtitle` | 消息副标题 | `--subtitle "10分钟后"` |
| `--content, -c` | 消息内容 | `--content "消息内容"` |
| `--group` | 指定分组 | `--group work` |
| `--help-skill` | 显示帮助信息 | `--help-skill` |

### 推送参数

| 参数 | 说明 | 取值范围 |
|------|------|----------|
| `--level` | 消息级别 | passive, active, time-sensitive, critical |
| `--volume` | 音量 | 0-10 |
| `--badge` | 角标数字 | 整数 |
| `--sound` | 通知声音 | bell, chime, glass 等 |
| `--icon` | 图标 URL | 完整的 HTTPS URL |
| `--call` | 是否呼叫 | 1/0/true/false |
| `--autoCopy` | 自动复制 | 1/0/true/false |
| `--copy` | 复制内容 | 字符串 |
| `--isArchive` | 自动归档 | 1/0/true/false |
| `--action` | 自定义动作 | JSON 字符串 |
| `--ciphertext` | 加密密文 | 字符串 |

### 操作参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--update` | 更新已推送的消息 | `--update abc123` |
| `--delete` | 删除已推送的消息 | `--delete abc123` |
| `--list-users` | 列出所有用户 | `--list-users` |
| `--list-groups` | 列出所有分组 | `--list-groups` |
| `--list-history` | 列出历史记录 | `--list-history --history-limit 20` |
| `--history-limit` | 历史列表条数 | `--history-limit 20` |

## 配置说明

### 用户别名配置

在 `config.json` 的 `users` 字段中配置用户别名：

```json
{
  "users": {
    "alice": "device_key_alice_123",
    "bob": "device_key_bob_456",
    "charlie": "device_key_charlie_789"
  }
}
```

### 默认参数配置

在 `config.json` 的 `defaults` 字段中配置默认推送参数：

```json
{
  "defaults": {
    "level": "active",
    "volume": 10,
    "badge": 1,
    "sound": "bell",
    "group": "default"
  }
}
```

### 分组配置

在 `config.json` 的 `groups` 字段中定义可用分组：

```json
{
  "groups": ["work", "personal", "urgent", "family"]
}
```

### 历史记录限制

在 `config.json` 的 `history_limit` 字段中设置历史记录保存数量：

```json
{
  "history_limit": 100
}
```

### 加密密文配置
```json
{
  "ciphertext": "your_encryption_key"
}
```

## 使用场景

### 场景 1：日常提醒
```bash
bark-push --user alice --content "别忘了下午3点的会议"
```

### 场景 2：系统监控告警
```bash
bark-push --user all --title "服务器告警" --content "CPU使用率超过90%" --level critical --sound alarm
```

### 场景 3：团队协作通知
```bash
bark-push --user alice,bob,charlie --title "项目进度" --content "前端开发已完成，请开始测试" --group work
```

### 场景 4：图片分享
```bash
bark-push --user bob --content "https://example.com/screenshot.png"
```

### 场景 5：消息更新
```bash
# 首次推送
bark-push --user alice --content "会议将在10分钟后开始"
# 返回推送 ID：abc123

# 更新消息
bark-push --update abc123 --user alice --content "会议时间改为15分钟后"
```

## 故障排查

### 配置文件找不到
如果提示配置文件不存在，请在当前目录或 `~/.bark-push/` 目录下创建 `config.json` 文件。

### 推送失败
1. 检查网络连接是否正常
2. 验证 device_key 是否正确
3. 确认 Bark 服务地址是否可访问
4. 查看错误日志获取详细信息

### 用户不存在
如果提示用户不存在，使用 `--list-users` 命令查看可用用户列表，并在 `config.json` 中添加用户配置。

### 历史记录不可用
确保 `~/.bark-push/` 目录具有写入权限，历史记录文件会自动创建。

## 高级功能

### 加密推送
如果配置了 `ciphertext`，所有推送将使用加密方式发送：

```json
{
  "ciphertext": "your_encryption_key"
}
```

### 自定义动作
支持 Bark 的自定义动作功能，可以在通知中添加交互按钮：

```bash
bark-push --user alice --content "是否同意?" --action '{"action":"confirm","text":"同意"}'
```

### 批量推送
使用脚本批量推送消息：

```bash
#!/bin/bash
for user in alice bob charlie; do
  bark-push --user $user --content "批量通知消息"
done
```

## 贡献指南

欢迎提交问题和改进建议！

## 许可证

MIT License

## 相关链接

- [Bark 官方网站](https://bark.day.app)
- [Bark API 文档](https://bark.day.app/#/tutorial)
- [ClawHub 项目](https://clawhub.ai)
