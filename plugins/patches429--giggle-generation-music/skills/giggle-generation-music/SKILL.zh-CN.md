---
name: giggle-generation-music
description: 当用户希望创建、生成或创作音乐时使用此技能——无论是文字描述、自定义歌词，还是纯乐器背景音乐。触发词：生成音乐、写歌、创作歌曲、制作音乐、做一首歌、AI 音乐、背景音乐、为我作曲、带歌词的音乐、纯音乐、做 beats。
version: "0.0.7"
license: MIT
author: storyclaw-official
homepage: https://github.com/storyclaw-official/storyclaw-skills
requires:
  bins: [python3]
  env: [GIGGLE_API_KEY]
  pip: [requests]
metadata:
  openclaw:
    emoji: "📂"
    requires:
      bins: [python3]
      env: [GIGGLE_API_KEY]
      pip: [requests]
    primaryEnv: GIGGLE_API_KEY
    runtimeBehaviors:
      writes: ["~/.openclaw/skills/giggle-generation-music/logs/"]
      cron: "用户发起音乐生成时注册轮询任务（2分钟间隔）"
    installNotice: "需用户确认。写入 logs/；注册 Cron；原样转发 stdout。安装前请阅读 SKILL.md。"
---

简体中文 | [English](./SKILL.md)

# Giggle 音乐

**来源**：[storyclaw-official/storyclaw-skills](https://github.com/storyclaw-official/storyclaw-skills) · API：[giggle.pro](https://giggle.pro/)

通过 giggle.pro 平台生成 AI 音乐。支持简化模式和自定义模式。

---

## ⚠️ 安装前 — 须确认并接受

本技能使用**异步轮询**。安装即表示您接受：

| 行为 | 说明 |
|------|------|
| **写入** | `~/.openclaw/skills/giggle-generation-music/logs/` — 任务状态，用于 Cron 去重 |
| **Cron** | 注册 2 分钟间隔轮询；任务完成后移除 |
| **stdout** | 脚本输出原样呈现给用户（不经过滤） |

**依赖要求**：`python3`、`GIGGLE_API_KEY`（环境变量）、`requests`（pip）。**安装前须阅读并确认上述内容。**

---

## 环境配置

**API Key**：设置系统环境变量 `GIGGLE_API_KEY`。详见 [SETUP.md](SETUP.md)。

---

## 交互指引

### 模式选择（优先级从高到低）

| 用户输入 | 模式 | 说明 |
|------------|------|-------|
| 用户提供完整**歌词文本** | 自定义模式 (B) | 必须是歌词，而非描述 |
| 用户要求纯音乐/背景音乐 | 纯音乐模式 (C) | 无人声 |
| 其他情况（描述、风格、人声等） | **简化模式 (A)** | 将用户描述原样作为 prompt，AI 作曲 |

> **关键规则**：若用户未提供歌词，始终使用**简化模式 A**。将用户描述原样作为 `--prompt`；**不要补充或改写**。例如用户说「女声、1 分钟、古风爱情」，则直接使用 `--prompt "女声，1 分钟，古风爱情"`。

### 信息不足时的引导

仅当用户输入非常模糊时（例如只说「生成音乐」无任何描述），可询问：

```
问题：「您想生成什么类型的音乐？」
选项：AI 作曲（描述风格）/ 使用我的歌词 / 纯音乐
```

---

## 执行流程（阶段 1 提交 + 阶段 2 Cron）

音乐生成通常需要 1–3 分钟。采用「快速提交 + Cron 轮询」两阶段架构。

> **重要**：**切勿**在 exec 的 `env` 参数中传递 `GIGGLE_API_KEY`。API Key 从系统环境变量读取。直接执行以下命令即可。

---

### 阶段 1：提交任务（exec 在 10 秒内完成）

**先向用户发送消息**：「音乐生成进行中，通常需要 1–3 分钟，结果将自动发送。」

#### A：简化模式
```bash
python3 scripts/giggle_music_api.py --prompt "用户描述" --no-wait
```

#### B：自定义模式
```bash
python3 scripts/giggle_music_api.py --custom \
  --prompt "歌词内容" \
  --style "pop, ballad" \
  --title "歌曲标题" \
  --vocal-gender female \
  --no-wait
```

#### C：纯音乐
```bash
python3 scripts/giggle_music_api.py --prompt "用户描述" --instrumental --no-wait
```

响应示例：
```json
{"status": "started", "task_id": "xxx", "log_file": "/path/to/log"}
```

**立即将 task_id 存入记忆**（`addMemory`）：
```
giggle-generation-music task_id: xxx (submitted: YYYY-MM-DD HH:mm)
```

---

### 阶段 2：注册 Cron（2 分钟间隔，wakeMode: "now"）

使用 `cron` 工具注册轮询任务。**必须严格遵循参数格式；不得修改字段名或添加额外字段**：

```json
{
  "action": "add",
  "job": {
    "name": "giggle-generation-music-<task_id 前 8 位>",
    "schedule": {
      "kind": "every",
      "everyMs": 120000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "音乐任务轮询：执行 exec python3 scripts/giggle_music_api.py --query --task-id <完整 task_id>，按 Cron 逻辑处理 stdout。若 stdout 为非 JSON 纯文本，原样发送给用户并移除 Cron。若 stdout 为 JSON，不发送消息，继续等待。若 stdout 为空，立即移除 Cron。"
    },
    "sessionTarget": "main"
  }
}
```

每次 Cron 触发时执行：
```bash
python3 scripts/giggle_music_api.py --query --task-id <task_id>
```

**链接返回规范**：stdout 中的音频链接必须为**完整签名 URL**（含 Policy、Key-Pair-Id、Signature 等查询参数）。正确示例：`https://assets.giggle.pro/...?Policy=...&Key-Pair-Id=...&Signature=...`。错误：不要返回仅含基础路径的未签名 URL（无查询参数）。脚本已自动处理 `~` 编码为 `%7E`，转发时保持原样。

**Cron 触发处理**（根据 exec stdout 判断；以下路径均 exit 0）：

| stdout 模式 | 动作 |
|----------------|--------|
| 非空纯文本（不以 `{` 开头） | **将 stdout 原样转发给用户**（不加前缀、不修改），**移除 Cron** |
| stdout 为空 | 已推送，**立即移除 Cron，不发送消息** |
| JSON（以 `{` 开头，含 `"status"` 字段） | 不发送消息，不移除 Cron，等待下次轮询 |

---

## 网关重启后的恢复

当用户询问之前的音乐进度时：

1. **记忆中有 task_id** → 直接执行 `--query --task-id xxx`，**切勿重新提交**
2. **记忆中无 task_id** → 告知用户，询问是否要重新生成

---

## 参数速查

| 参数 | 说明 |
|-----------|-------------|
| `--prompt` | 音乐描述或歌词（简化模式必填） |
| `--custom` | 启用自定义模式 |
| `--style` | 音乐风格（自定义模式必填） |
| `--title` | 歌曲标题（自定义模式必填） |
| `--instrumental` | 生成纯音乐 |
| `--vocal-gender` | 人声性别：male / female（仅自定义模式） |
| `--query` | 查询任务状态（Cron 轮询及手动查询） |
| `--task-id` | 任务 ID（与 --query 配合使用） |
