# 多平台收藏词复活计划

**面向 OpenClaw 的 browser-first 收藏词同步与每日单词推送工具**  
**支持 Google / 有道｜每天 1 词，不让收藏吃灰**

这个项目用于把已经收藏过的词重新转化为可持续复习的输入。
它不替代记忆或背词系统，而是负责完成以下链路：

1. 打开收藏页并确认登录状态
2. 抓取当前页面内容，必要时补充更多页面缓存
3. 写入平台词库并聚合为统一词库
4. 每天选择一个词并生成消息
5. 按需发送或交由定时任务触发发送

## 当前版本范围

当前版本已经提供：

- Google / 有道页面缓存 → 本地词库同步
- 聚合去重 → 每日 1 词选择 → 消息预览 / 发送
- `doctor` / `status` / `test-message` 等本地检查命令

当前版本**尚未将“浏览器自动翻页并抓完整个平台词库”封装为仓库内的一键命令**。
这一部分仍然属于推荐的 Agent 工作流：先通过 OpenClaw 浏览器抓取页面内容，再由本地脚本执行同步与推送。

## 界面示例

下图展示了典型使用流程：发起同步、完成同步，以及每日单词推送效果。

<table>
  <tr>
    <td align="center">
      <img src="docs/images/sync-google-start.png" alt="开始同步 Google 收藏词示例" width="260" />
      <br />
      <sub>同步入口</sub>
    </td>
    <td align="center">
      <img src="docs/images/sync-google-success.png" alt="Google 收藏词同步完成示例" width="260" />
      <br />
      <sub>同步完成</sub>
    </td>
    <td align="center">
      <img src="docs/images/daily-word-message.png" alt="每日单词推送示例" width="260" />
      <br />
      <sub>每日推送</sub>
    </td>
  </tr>
</table>

## 支持平台

- Google Translate Saved
- 有道单词本 / 收藏页

## 安装

### 方式 A：通过 ClawHub 安装

```bash
npm i -g clawhub
clawhub --workdir ~/.openclaw/workspace install word-vault-revival
openclaw skills info word-vault-revival
```

如需安装指定版本：

```bash
clawhub --workdir ~/.openclaw/workspace install word-vault-revival --version 0.1.0
```

安装后可进一步检查：

```bash
openclaw skills check --json
openclaw skills info word-vault-revival --json
```

### 方式 B：从 GitHub 安装

```bash
git clone https://github.com/zhonghanwen/word-vault-revival.git ~/.openclaw/workspace/skills/word-vault-revival
openclaw skills info word-vault-revival
```

## 快速开始

1. 安装 Node.js 18+ 和 OpenClaw
2. 运行 `npm run doctor`
3. 用 OpenClaw 打开支持的平台收藏页并抓取页面内容
4. 运行 `npm run sync:google` 或 `npm run sync:youdao`
5. 运行 `npm run test-message`
6. 确认无误后运行 `npm run send`

如果 `PUSH_TARGET` 留空，`npm run send` 不会发送到固定目标，可作为正式发送前的检查步骤。

## 使用方法

### 1. 准备环境

需要：

- Node.js 18+
- OpenClaw 浏览器 / Agent 工作流

如需覆盖默认配置，复制 `.env.example` 为 `.env`，再调整推送目标、时区或启用词源。

首次使用建议先运行：

```bash
npm run doctor
```

该命令会检查 Node 版本、OpenClaw CLI、配置文件、缓存文件和当前词库状态。

### 2. 准备页面内容

先用 OpenClaw 打开目标收藏页：

- Google：`https://translate.google.com/saved?sl=en&tl=zh-CN&op=translate`
- 有道：`https://dict.youdao.com/webwordbook/wordlist`

建议流程：

1. 打开页面
2. 确认登录状态
3. 如未登录，先完成登录
4. 抓取当前页；如果已有稳定的浏览器翻页工作流，再继续补充更多页面
5. 将抓取结果写入 `data/cache/<platform>-page.txt`

如需先查看当前状态：

```bash
npm run doctor
npm run status
```

### 3. 同步词库

```bash
npm run sync:google
npm run sync:youdao
```

如果多个平台缓存都已准备好：

```bash
npm run status
npm run sync
```

同步完成后，会更新本地词库并生成用于每日推送的聚合结果。

### 4. 预览今日单词

```bash
npm run test-message
```

### 5. 发送今日单词

```bash
npm run send
```

如果推送目标已经配置完成，`npm run send` 会尝试直接发送今日单词；如果环境尚未配置完整，则会停留在可检查状态，便于先验证输出是否符合预期。

### 6. 配置每日定时推送

当前版本**支持定时推送**，但**不会在安装时自动注册循环任务**。

这意味着：

- `npm run send` 已经可以作为定时任务的执行目标
- “每天几点自动运行”仍需额外配置调度器

推荐顺序：

1. 先运行 `npm run sync`
2. 再运行 `npm run test-message`
3. 确认 `.env` 或 `config/platforms.json` 中已配置有效的推送目标
4. 再配置循环任务调用 `npm run send`

推荐调度方式：

- **OpenClaw cron**：最适合 OpenClaw 工作流
- **OpenClaw heartbeat**：适合与其他周期检查合并
- **系统级调度器**：如 macOS `launchd`、Linux `cron`

进一步说明见：

- `docs/cron-heartbeat-guide.md`

### 在 OpenClaw 中配置定时推送

以下自然语言示例适合用于让 OpenClaw 代为创建调度：

- `每天早上 9 点从收藏词里给我推一个单词`
- `帮我设置每日 09:00 自动发送今日单词`
- `每天上午九点发一个今日单词到 Telegram`
- `帮我定时运行这个 skill，每天推送 1 个词`

创建调度前，请先确认：

1. 已完成至少一次 `npm run sync`
2. 已检查过 `npm run test-message` 的输出
3. 已配置 `PUSH_TARGET` 或 `push.target`

## 常用命令

```bash
npm run doctor
npm run status
npm run sync
npm run sync:google
npm run sync:youdao
npm run test-message
npm run send
```

## 配置

主配置文件：

- `config/platforms.json`

`.env` 用作覆盖层。

关键字段包括：

- `timezone`
- `dailyPush.time`
- `dailyPush.dedupeSameDay`
- `platforms.google.pageTextFile`
- `platforms.youdao.pageTextFile`
- `push.channel`
- `push.target`
- `push.sendCommand`

默认示例：

```json
{
  "title": "多平台收藏词复活计划",
  "subtitle": "支持 Google / 有道｜每天 1 词，不让收藏吃灰",
  "timezone": "Asia/Shanghai",
  "dailyPush": {
    "enabled": true,
    "time": "09:00",
    "count": 1,
    "dedupeSameDay": true
  },
  "platforms": {
    "google": {
      "enabled": true,
      "savedUrl": "https://translate.google.com/saved?sl=en&tl=zh-CN&op=translate",
      "pageTextFile": "./data/cache/google-page.txt"
    },
    "youdao": {
      "enabled": true,
      "savedUrl": "https://dict.youdao.com/webwordbook/wordlist",
      "pageTextFile": "./data/cache/youdao-page.txt"
    }
  },
  "push": {
    "channel": "telegram",
    "target": "",
    "sendCommand": ""
  }
}
```

## 进一步阅读

- `docs/browser-workflow.md`：浏览器侧工作流
- `docs/adapters.md`：平台解析说明
- `docs/cron-heartbeat-guide.md`：定时调度建议
