# OpenClaw OneBot 11 Channel Plugin 🐧

[中文](#中文) | [English](#english)

---

## 中文

> ⚠️ **ClawHub 安全扫描说明**：本 skill 在 ClawHub 上可能被标记为 "Suspicious"，这是因为 `.ts` (TypeScript) 文件的扩展名被自动识别为 `video/mp2t` (MPEG-2 视频流) MIME 类型触发了误报。所有源码均为标准 TypeScript，可在 [GitHub](https://github.com/xucheng/openclaw-onebot) 审查。


OpenClaw 的 **OneBot 11 协议通道插件**，让 QQ 成为 OpenClaw 一等消息通道。

支持 [NapCat](https://github.com/NapNeko/NapCatQQ)、[go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 等所有兼容 OneBot 11 协议的 QQ 机器人框架。

### 功能

- 🔌 **原生通道插件** — QQ 与 Discord / Telegram / WhatsApp 同级
- 📨 私聊和群聊收发消息
- 🎤 **语音完整链路** — QQ 语音 (SILK/AMR) → MP3 → STT → TTS → 发送 QQ 语音
- 📦 **消息聚合** — 连续多条消息 1.5s 内自动合并（类似 Telegram 风格）
- 🖼️ 图片、语音、文件附件发送
- 🔄 WebSocket 自动重连（指数退避）
- 🔒 可选 access token 鉴权
- 🎯 `allowFrom` 消息来源过滤（私聊/群聊/用户级别）
- ✅ 58 个测试用例全部通过

### 与其他方案对比

| | **openclaw-onebot** (本项目) | **方案 A** | **方案 B** |
|---|---|---|---|
| **协议** | OneBot 11 (NapCat/go-cqhttp) | QQ 官方 Bot API | OneBot 11 (NapCat) |
| **集成方式** | ✅ **ChannelPlugin 原生集成** | ❌ 独立 Python 脚本 + 文件队列 | ❌ 独立 Python 脚本 |
| **消息路由** | OpenClaw 自动路由，`message` tool 直接用 | 文件队列读写，需手动桥接 | 手动调 Python API |
| **语音支持** | ✅ SILK/AMR → MP3 → STT/TTS 全自动 | ❌ 无 | ❌ 无 |
| **消息聚合** | ✅ 1.5s 智能合并 | ❌ 无 | ❌ 无 |
| **自动重连** | ✅ WebSocket 指数退避 | daemon 脚本重启 | ❌ 无 |
| **测试** | ✅ 58 tests | ❌ 无 | ❌ 无 |
| **语言** | TypeScript | Python | Python |
| **需要额外进程** | ❌ 随 gateway 启动 | ✅ 需独立运行 daemon | ✅ 需独立运行 listener |

**核心区别**：本项目是 OpenClaw **原生通道插件**，安装后 QQ 就和 Discord / Telegram 一样使用，不需要额外的桥接脚本或消息队列。其他方案都是外挂式的独立进程，需要自己处理消息路由和会话管理。

### 架构

```
QQ 机器人框架 (NapCat / go-cqhttp)
  ├── WebSocket → 接收消息 (含语音 SILK/AMR 自动转 MP3)
  └── HTTP API  → 发送消息 (文字/图片/语音)
      ↕
OpenClaw OneBot Plugin (ChannelPlugin)
  ├── 消息聚合 (1.5s debounce)
  ├── 语音处理 (SILK → pilk → PCM → ffmpeg → MP3)
  └── allowFrom 过滤
      ↕
OpenClaw Gateway (统一消息管线)
  ├── STT (语音转文字)
  ├── Agent 对话
  └── TTS (文字转语音) → sendRecord → QQ 语音
```

### 快速开始

#### 1. 安装插件

```bash
# 自动安装
bash scripts/install.sh

# 或手动
cp -r src index.ts package.json tsconfig.json ~/.openclaw/plugins/onebot/
cd ~/.openclaw/plugins/onebot && npm install && npm run build
```

#### 2. 配置

在 `openclaw.json` 中添加：

```json
{
  "channels": {
    "onebot": {
      "enabled": true,
      "wsUrl": "ws://your-host:3001",
      "httpUrl": "http://your-host:3001"
    }
  }
}
```

也支持环境变量：

```bash
ONEBOT_WS_URL=ws://your-host:3001
ONEBOT_HTTP_URL=http://your-host:3001
ONEBOT_ACCESS_TOKEN=your_token  # 可选
```

#### 3. 重启 Gateway

```bash
openclaw gateway restart
```

### 高级配置

```json
{
  "channels": {
    "onebot": {
      "enabled": true,
      "wsUrl": "ws://your-host:3001",
      "httpUrl": "http://your-host:3001",
      "accessToken": "your_token",
      "allowFrom": ["private:12345", "group:67890"],
      "users": ["12345"]
    }
  }
}
```

| 参数 | 说明 |
|------|------|
| `allowFrom` | 消息来源白名单 — `private:<QQ号>`、`group:<群号>`、或 `*`（允许所有） |
| `users` | 允许触发机器人的 QQ 用户白名单 |
| `accessToken` | HTTP API 用 Bearer token，WebSocket 用 query 参数 |

### 语音支持（可选）

支持 QQ 语音消息的完整自动处理链路：

- **入站**：QQ 语音 (SILK/AMR) → 下载 → 转 MP3 → OpenClaw STT 转文字 → Agent 生成回复
- **出站**：Agent 回复 → TTS 生成音频 → `sendRecord` 发送 QQ 语音

**依赖**：
- `ffmpeg` — 音频格式转换
- `uv` — 运行 `pilk` 解码 SILK 格式（AMR 仅需 ffmpeg）

不需要语音功能时可以跳过这些依赖。

### 消息目标格式

- `private:<QQ号>` — 私聊消息
- `group:<群号>` — 群聊消息
- `<QQ号>` — 自动识别为私聊

### NapCat 部署参考

推荐使用 Docker 部署 [NapCat](https://github.com/NapNeko/NapCatQQ)：

```yaml
# docker-compose.yml
services:
  napcat:
    image: mlikiowa/napcat-docker:latest
    restart: always
    ports:
      - "3001:3001"   # OneBot 11 WS + HTTP
      - "6099:6099"   # WebUI
    volumes:
      - ./napcat-data:/app/.config/QQ
      - ./shared:/shared   # 文件共享目录
```

### 开发

```bash
npm install
npm test          # 58 tests
npm run build     # 编译 TypeScript
npm run coverage  # 覆盖率报告
```

---

## English

> ⚠️ **ClawHub Security Note**: This skill may be flagged as "Suspicious" on ClawHub because `.ts` (TypeScript) files are auto-detected as `video/mp2t` (MPEG-2 Transport Stream) MIME type, triggering a false positive. All source code is standard TypeScript — review it on [GitHub](https://github.com/xucheng/openclaw-onebot).


An [OpenClaw](https://github.com/openclaw/openclaw) **native channel plugin** that connects to [NapCat](https://github.com/NapNeko/NapCatQQ), [go-cqhttp](https://github.com/Mrs4s/go-cqhttp), or any OneBot 11 compatible QQ bot framework.

### Features

- 🔌 **Native channel plugin** — QQ on par with Discord / Telegram / WhatsApp
- 📨 Private & group chat (inbound + outbound)
- 🎤 **Full voice pipeline** — QQ voice (SILK/AMR) → MP3 → STT → TTS → send QQ voice
- 📦 **Message batching** — auto-merge rapid messages within 1.5s (Telegram-style)
- 🖼️ Image, audio, and file attachments
- 🔄 WebSocket auto-reconnect with exponential backoff
- 🔒 Optional access token authentication
- 🎯 `allowFrom` filtering (private/group/user-level)
- ✅ 58 tests passing

### Comparison with Alternatives

| | **openclaw-onebot** (this) | **方案 A** | **方案 B** |
|---|---|---|---|
| **Protocol** | OneBot 11 (NapCat/go-cqhttp) | QQ Official Bot API | OneBot 11 |
| **Integration** | ✅ **Native ChannelPlugin** | ❌ Standalone Python + file queue | ❌ Standalone Python scripts |
| **Message routing** | Auto via OpenClaw `message` tool | Manual file I/O bridge | Manual Python API calls |
| **Voice** | ✅ SILK/AMR → MP3 → STT/TTS auto | ❌ None | ❌ None |
| **Batching** | ✅ 1.5s smart merge | ❌ None | ❌ None |
| **Auto-reconnect** | ✅ Exponential backoff | Daemon restart | ❌ None |
| **Tests** | ✅ 58 tests | ❌ None | ❌ None |
| **Language** | TypeScript | Python | Python |
| **Extra process** | ❌ Runs with gateway | ✅ Separate daemon | ✅ Separate listener |

**Key difference**: This is a **native OpenClaw channel plugin** — once installed, QQ works just like Discord or Telegram. No bridge scripts, no message queues, no extra processes.

### Quick Start

#### 1. Install

```bash
bash scripts/install.sh
```

#### 2. Configure

Add to `openclaw.json`:

```json
{
  "channels": {
    "onebot": {
      "enabled": true,
      "wsUrl": "ws://your-host:3001",
      "httpUrl": "http://your-host:3001"
    }
  }
}
```

Or via environment variables:

```bash
ONEBOT_WS_URL=ws://your-host:3001
ONEBOT_HTTP_URL=http://your-host:3001
ONEBOT_ACCESS_TOKEN=your_token  # optional
```

#### 3. Restart Gateway

```bash
openclaw gateway restart
```

### Voice Support (Optional)

End-to-end voice flow:
- **Inbound**: QQ voice (SILK/AMR) → download → MP3 → OpenClaw STT → Agent reply
- **Outbound**: Agent reply → TTS audio → `sendRecord` → QQ voice

**Dependencies**: `ffmpeg` + `uv` (for SILK decoding via `pilk`). Skip if text/image only.

### Configuration

| Option | Description |
|--------|-------------|
| `allowFrom` | Whitelist — `private:<qq>`, `group:<id>`, or `*` (allow all) |
| `users` | QQ user ID whitelist |
| `accessToken` | Bearer token for HTTP, query param for WebSocket |

### Target Format

- `private:<qq_number>` — Private message
- `group:<group_id>` — Group message
- `<qq_number>` — Auto-detected as private

### Development

```bash
npm install
npm test          # Run 58 tests
npm run build     # Compile TypeScript
npm run coverage  # Coverage report
```

## License

MIT
