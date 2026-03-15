# 配置指南

本文档详细说明 openqq 的配置选项。

---

## 📁 配置文件位置

**主配置文件：** `~/.openclaw/workspace/open-qq-config.json`

---

## ⚡ 快速配置（推荐）

对于大多数用户，只需配置 QQ 凭据即可：

```json
{
  "qq": {
    "appId": "你的 APP ID",
    "token": "你的 Token",
    "appSecret": "你的 App Secret"
  }
}
```

其他配置会使用默认值，通常不需要修改。

---

## 📝 配置项详解

### QQ 凭据（必需）

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `appId` | string | ✅ | QQ 机器人应用 ID，从 QQ 开放平台获取 |
| `token` | string | ✅ | QQ Bot Token，从 QQ 开放平台获取 |
| `appSecret` | string | ✅ | QQ 应用密钥，从 QQ 开放平台获取 |

**获取方式：**
1. 访问 [QQ 开放平台](https://bot.q.qq.com/)
2. 登录并创建机器人应用
3. 在应用详情页面获取凭据

---

### 日志配置（可选）

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `logDir` | string | `/root/.openclaw/workspace/logs/qq-bot` | 日志文件存储目录 |
| `maxLogSize` | string | `10MB` | 单个日志文件最大大小（支持 B/KB/MB/GB） |
| `maxLogFiles` | number | `7` | 保留的日志文件数量 |
| `timezone` | string | `Asia/Shanghai` | 日志时间戳时区 |
| `logLevel` | string | `debug` | 日志级别：`debug`/`info`/`error` |
| `sanitizeSensitive` | boolean | `true` | 是否自动过滤敏感数据（token、密码等） |

**日志级别说明：**
- `debug` - 记录所有日志（包括调试信息），适合开发环境
- `info` - 只记录信息和错误，适合生产环境
- `error` - 只记录错误，适合高负载生产环境

---

### 机器人配置（可选）

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `intents` | number | `33554433` | QQ 事件订阅权限（私域完整权限） |
| `shard` | array | `[0, 1]` | WebSocket 分片配置 |
| `heartbeatInterval` | number | `30000` | 心跳间隔（毫秒） |
| `reconnectDelay` | number | `5000` | 断线重连延迟（毫秒） |

**intents 说明：**
- `33554433` = `(1 << 0) | (1 << 25)` - 私域完整权限（QQ 群 + 私聊）
- 一般不需要修改，除非需要订阅其他事件

**heartbeatInterval 建议：**
- 默认 `30000`（30 秒）即可
- 不要设置过小（<5000），可能被服务器断开
- 不要设置过大（>60000），可能被判定为离线

---

## 🔒 安全提示

### 1. 保护配置文件

```bash
# 设置文件权限（只有所有者可读写）
chmod 600 ~/.openclaw/workspace/open-qq-config.json

# 验证权限
ls -l ~/.openclaw/workspace/open-qq-config.json
# 应该显示：-rw------- 1 user user ...
```

### 2. 不要提交到版本控制

```bash
# 添加到 .gitignore
echo "open-qq-config.json" >> ~/.openclaw/workspace/.gitignore
```

### 3. 备份配置

```bash
# 备份配置文件（不要分享真实凭据！）
cp ~/.openclaw/workspace/open-qq-config.json \
   ~/.openclaw/workspace/open-qq-config.json.backup

# 编辑备份文件，删除真实凭据后再分享
vim ~/.openclaw/workspace/open-qq-config.json.backup
```

---

## 📋 配置示例

### 最小配置（推荐）

```json
{
  "qq": {
    "appId": "123456789",
    "token": "your_token",
    "appSecret": "your_secret"
  }
}
```

### 生产环境配置

```json
{
  "qq": {
    "appId": "123456789",
    "token": "your_token",
    "appSecret": "your_secret"
  },
  "logger": {
    "logLevel": "info",
    "maxLogFiles": 14
  },
  "bot": {
    "heartbeatInterval": 30000,
    "reconnectDelay": 5000
  }
}
```

### 开发环境配置

```json
{
  "qq": {
    "appId": "123456789",
    "token": "your_token",
    "appSecret": "your_secret"
  },
  "logger": {
    "logLevel": "debug"
  }
}
```

### 高负载环境配置

```json
{
  "qq": {
    "appId": "123456789",
    "token": "your_token",
    "appSecret": "your_secret"
  },
  "logger": {
    "logLevel": "error",
    "maxLogFiles": 30
  }
}
```

---

## 🔍 配置验证

### 检查配置文件格式

```bash
# 使用 node 验证 JSON 格式
node -e "JSON.parse(require('fs').readFileSync('~/.openclaw/workspace/open-qq-config.json'))" && echo "✅ JSON 格式正确"
```

### 检查必需配置

确保配置文件包含以下字段：
- ✅ `qq.appId`
- ✅ `qq.token`
- ✅ `qq.appSecret`

### 测试配置

```bash
# 启动机器人，检查是否有配置错误
cd ~/.openclaw/workspace/skills/openqq
npm start
```

如果配置正确，会看到：
```
🚀 正在启动 QQ Bot...
✅ QQ Bot 已就绪，可以接收消息了！
```

---

## ❓ 常见问题

### Q: 配置文件在哪里？
A: `~/.openclaw/workspace/open-qq-config.json`

### Q: 如何重置配置？
A: 
```bash
cp ~/.openclaw/workspace/skills/openqq/open-qq-config.json.example \
   ~/.openclaw/workspace/open-qq-config.json
```

### Q: 配置修改后需要重启吗？
A: 是的，修改配置后需要重启机器人：
```bash
# 停止
pkill -f "node qq-bot.js"

# 启动
npm start
```

### Q: 可以使用环境变量吗？
A: 推荐使用配置文件。环境变量作为备选方案，参考 `.env.example`。

---

## 📚 相关文件

| 文件 | 说明 |
|------|------|
| `open-qq-config.json` | 主配置文件 |
| `open-qq-config.json.example` | 简化配置模板 |
| `open-qq-config.full.example` | 完整配置模板 |
| `.env.example` | 环境变量模板 |
| `CONFIG.md` | 本文档 |

---

**最后更新：** 2026-02-26 | **版本：** 0.0.3
