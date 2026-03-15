---
name: qqbot-multi-bind
description: "快速配置 OpenClaw 多 QQBot 账号绑定到不同 Agent。用于首次安装 QQBot、新增 QQBot 账号、创建 agent 绑定关系、重启 gateway 使配置生效。当用户需要安装 QQBot 插件、添加新的 QQBot 机器人或配置多账号路由时使用此技能。"
---

# QQBot 多账号绑定配置

## 首次安装 QQBot（从零开始）

### Step 1 — 在 QQ 开放平台创建机器人

1. 访问 [QQ 开放平台](https://bot.q.qq.com/)，用手机 QQ 扫码登录
2. 点击「创建机器人」
3. 记录 **AppID** 和 **AppSecret**（AppSecret 只显示一次，务必保存好）

⚠️ 注意：创建后机器人会自动出现在你的 QQ 消息列表，但会回复"机器人去火星了"，需要完成下面配置才能正常使用。

### Step 2 — 安装插件

**方式 A：npm 安装（推荐）**
```bash
openclaw plugins install @tencent-connect/openclaw-qqbot
```

**方式 B：源码一键安装**
```bash
git clone https://github.com/tencent-connect/openclaw-qqbot.git && cd openclaw-qqbot
bash ./scripts/upgrade-via-source.sh --appid YOUR_APPID --secret YOUR_SECRET
```

**方式 C：手动安装**
```bash
git clone https://github.com/tencent-connect/openclaw-qqbot.git && cd openclaw-qqbot
npm install --omit=dev
openclaw plugins install .
```

### Step 3 — 配置 OpenClaw

**方式 1：CLI 向导（推荐）**
```bash
openclaw channels add --channel qqbot --token "AppID:AppSecret"
```

**方式 2：手动编辑配置文件**

编辑 `~/.openclaw/openclaw.json`：
```json
{
  "channels": {
    "qqbot": {
      "enabled": true,
      "appId": "Your AppID",
      "clientSecret": "Your AppSecret"
    }
  }
}
```

### Step 4 — 启动测试
```bash
openclaw gateway
```

---

## 多账号绑定配置（已有 QQBot，新增第二个）

### 前置条件

- 已有 OpenClaw 安装并运行
- 已有 qqbot 插件安装
- 已有至少一个 agent（如 `main`）
- 新的 QQBot AppID 和 ClientSecret

## 快速配置步骤

### 1. 创建新 Agent（如需要）

```bash
openclaw agents add <agent-name>
```

示例：
```bash
openclaw agents add coding
```

### 2. 编辑配置文件

修改 `~/.openclaw/openclaw.json`：

#### 2.1 在 `channels.qqbot.accounts` 中添加新账号

```json
"channels": {
  "qqbot": {
    "enabled": true,
    "allowFrom": ["*"],
    "accounts": [
      {
        "accountId": "main",
        "appId": "1903000001",
        "clientSecret": "your-secret-here"
      },
      {
        "accountId": "coding",
        "appId": "1903000002",
        "clientSecret": "your-secret-here"
      }
    ]
  }
}
```

#### 2.2 在 `bindings` 中添加路由规则

```json
"bindings": [
  {
    "agentId": "main",
    "match": {
      "channel": "qqbot",
      "accountId": "main"
    }
  },
  {
    "agentId": "coding",
    "match": {
      "channel": "qqbot",
      "accountId": "coding"
    }
  }
]
```

### 3. 重启 Gateway

```bash
openclaw gateway restart
```

### 4. 验证配置

```bash
openclaw agents list --bindings
```

## 配置模板

### 添加第 N 个 QQBot 的完整步骤

1. **获取新 QQBot 信息**：
   - AppID: `1903xxxxxx`（从 QQ 开放平台获取）
   - ClientSecret: `your-secret-here`（从 QQ 开放平台获取）
   - 确定 accountId（如 `work`, `game`, `notify`）
   - 确定绑定哪个 agent（如 `main`, `coding` 或新建）

2. **编辑 `~/.openclaw/openclaw.json`**：

   在 `channels.qqbot.accounts` 数组末尾添加：
   ```json
   {
     "accountId": "<account-id>",
     "appId": "<app-id>",
     "clientSecret": "<client-secret>"
   }
   ```

   在 `bindings` 数组末尾添加：
   ```json
   {
     "agentId": "<agent-id>",
     "match": {
       "channel": "qqbot",
       "accountId": "<account-id>"
     }
   }
   ```

3. **重启并验证**：
   ```bash
   openclaw gateway restart
   openclaw agents list --bindings
   ```

## 常见问题

### Q: 一个 agent 可以绑定多个 QQBot 吗？
A: 可以！只需添加多个 bindings 指向同一个 agentId。

### Q: 一个 QQBot 可以发给多个 agent 吗？
A: 不可以，一个消息只能路由到一个 agent。

### Q: 如何删除某个 QQBot？
A: 从 `accounts` 和 `bindings` 中删除对应条目，然后重启 gateway。

## 示例配置

```json
{
  "agents": {
    "list": [
      { "id": "main", "model": "bailian/kimi-k2.5" },
      { "id": "coding", "model": "bailian/kimi-k2.5" },
      { "id": "notify", "model": "bailian/kimi-k2.5" }
    ]
  },
  "channels": {
    "qqbot": {
      "enabled": true,
      "allowFrom": ["*"],
      "accounts": [
        { "accountId": "main", "appId": "1903000001", "clientSecret": "your-secret-here" },
        { "accountId": "coding", "appId": "1903000002", "clientSecret": "your-secret-here" },
        { "accountId": "notify", "appId": "1903000003", "clientSecret": "your-secret-here" }
      ]
    }
  },
  "bindings": [
    { "agentId": "main", "match": { "channel": "qqbot", "accountId": "main" } },
    { "agentId": "coding", "match": { "channel": "qqbot", "accountId": "coding" } },
    { "agentId": "notify", "match": { "channel": "qqbot", "accountId": "notify" } }
  ]
}
```
