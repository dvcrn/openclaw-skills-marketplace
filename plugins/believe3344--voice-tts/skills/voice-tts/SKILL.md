---
name: voice-tts
description: "语音处理技能 - 完整的语音输入输出解决方案。功能：(1) 语音识别 ASR - 将用户语音转录为文字（使用 Whisper）(2) 语音合成 TTS - 将文字转换为语音（使用 Edge TTS）。触发场景：用户发送语音消息、主动要求\"用语音读...\"、\"语音回复\"等。支持平台：Telegram、Discord、WhatsApp、飞书/Lark。确保每次语音回复都同时发送文字和语音。"
---

> ⚠️ 安装后请将 scripts/ 目录下的 .txt 文件名后缀去掉（去掉 .txt）才能正常使用！

# Voice 语音处理技能

完整的语音输入输出解决方案，同时支持语音识别（ASR）和语音合成（TTS）。

## 功能概述

| 方向 | 技术 | 说明 |
|------|------|------|
| 语音→文字 | Whisper (本地) | 用户发语音时自动转录 |
| 文字→语音 | Edge TTS | 生成语音回复 |

## 安装依赖

```bash
# 必须安装的包
pip install edge-tts whisper torch click

# 如果没有 ffmpeg（音频处理需要）
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

## OpenClaw 配置

要在 OpenClaw 中使用语音识别，需要修改 `openclaw.json`：

```json
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "models": [
          {
            "type": "cli",
            "command": "python3",
            "args": [
              "{{SkillPath}}/voice-tts/scripts/whisper",
              "--model",
              "base",
              "{{MediaPath}}"
            ]
          }
        ]
      }
    }
  }
}
```

**说明**：
- `{{SkillPath}}` 会自动替换为 skill 安装路径
- `--model base` 可以改为 `turbo` 等其他模型
- 修改后执行 `openclaw gateway restart` 重启生效

## 触发场景

### 场景一：用户发送语音消息（ASR）

当用户发送**语音消息**时：
1. 系统会自动转录为文字（transcript）
2. 你需要理解用户意图并回复
3. **用语音+文字回复**用户

### 场景二：用户主动要求语音回复（TTS）

当用户说以下话术时：
- "用语音读..."
- "语音回复"
- "读给我听"
- "说出来"
- "text to speech"
- "TTS"
- "飞书语音"
- 或任何明确要求语音输出的请求

## 脚本说明

Skill 自带两个脚本：

### 1. 语音识别 - whisper

位置：`{{SkillPath}}/scripts/whisper`

```bash
# 基本用法
python3 {{SkillPath}}/scripts/whisper audio.mp3

# 指定模型（默认 base）
python3 {{SkillPath}}/scripts/whisper audio.mp3 --model turbo

# 输出 JSON（带语言检测）
python3 {{SkillPath}}/scripts/whisper audio.mp3 --json

# 带时间戳
python3 {{SkillPath}}/scripts/whisper audio.mp3 --timestamps
```

**可用模型**：

| 模型 | 大小 | 速度 | 精度 |
|------|------|------|------|
| tiny | 39M | 最快 | 较低 |
| base | 74M | 快 | 中等 |
| small | 244M | 中等 | 较好 |
| turbo | 809M | 快 | 较好 |
| large-v3 | 1.5GB | 慢 | 最高 |

**推荐**：首次使用下载 `base` 或 `turbo` 模型，后续可直接使用。

### 2. 语音合成 - edge_tts

位置：`{{SkillPath}}/scripts/edge_tts`

```bash
# 基本用法
python3 {{SkillPath}}/scripts/edge_tts "要说的内容" -f output.mp3

# 指定声音
python3 {{SkillPath}}/scripts/edge_tts "你好" -v zh-CN-XiaoxiaoNeural -f output.mp3

# 调整语速
python3 {{SkillPath}}/scripts/edge_tts "你好" -r +10% -f output.mp3
```

**推荐声音**：
- `zh-CN-XiaoxiaoNeural` - 中文女声（默认推荐）
- `zh-CN-YunxiNeural` - 中文男声
- `en-US-JennyNeural` - 英文女声

### 3. 自动语音检查 - auto_voice_check（可选）

自动检查未处理的语音消息并批量处理。

```bash
python3 {{SkillPath}}/scripts/auto_voice_check
```

功能：
- 检查 `~/.openclaw/media/inbound/` 下的新音频
- 自动转写（使用 whisper）
- 移动到已处理目录

### 4. 语音回复钩子 - voice_reply_hook（可选）

用于自动合成语音回复的钩子。

```bash
# 设置环境变量
export REPLY_TEXT="你好，我是AI助手"
export MEDIA_OUT="{{Workspace}}/media/outbound"

# 执行钩子
python3 {{SkillPath}}/scripts/voice_reply_hook
```

## 使用流程

### 语音输入处理流程

```
用户发送语音 → 系统转录 → 你理解内容 → 语音+文字回复
```

1. 用户语音消息到达时，系统会提供 `transcript` 字段（转录文字）
2. 直接读取理解用户意图
3. 用 Edge TTS 合成语音回复
4. 同时发送文字和语音

### 语音输出流程

```
文字内容 → Edge TTS 合成 → 发送语音消息
```

1. 确定要语音回复的内容
2. 创建输出目录：`mkdir -p {{Workspace}}/media/outbound/`
3. 合成语音：`python3 {{SkillPath}}/scripts/edge_tts "内容" -f {{Workspace}}/media/outbound/voice.mp3`
4. 发送语音消息（见下方多平台说明）

## 配置

### 音频目录

- 输入音频：`~/.openclaw/media/inbound/`（系统自动存放）
- 输出音频：`{{Workspace}}/media/outbound/`

### 环境变量（飞书需要）

- `FEISHU_APP_ID` - 飞书应用 ID
- `FEISHU_APP_SECRET` - 飞书应用密钥
- `FEISHU_CHAT_ID` - 群聊 ID

## 多平台支持

### Telegram（推荐）

```python
message(
    action="send",
    channel="telegram",
    media="{{Workspace}}/media/outbound/voice.mp3",
    asVoice=True,
    message="这里是文字说明"
)
```

| 参数 | 说明 |
|------|------|
| `asVoice=True` | 关键！设为 True 显示为语音消息 |

### Discord

```python
message(action="send", channel="discord", media=voice_path, message=text)
```

### WhatsApp

```python
message(action="send", channel="whatsapp", media=voice_path, message=text)
```

### 飞书/Lark

飞书不支持直接发语音，用文件消息：

```bash
# 1. 获取 token
TENANT_TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\": \"${FEISHU_APP_ID}\", \"app_secret\": \"${FEISHU_APP_SECRET}\"}" | \
  python3 -c "import json,sys; print(json.load(sys.stdin).get('tenant_access_token',''))")

# 2. 上传音频
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -F "file_type=mp3" \
  -F "file=@{{Workspace}}/media/outbound/voice.mp3" | \
  python3 -c "import json,sys; print(json.load(sys.stdin).get('data',{}).get('file_key',''))")

# 3. 发送
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\": \"${FEISHU_CHAT_ID}\", \"msg_type\": \"file\", \"content\": \"{\\\"file_key\\\": \\\"${FILE_KEY}\\\"}\"}"
```

或用卡片发文字说明：

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{"msg_type": "interactive", "card": {"header": {"title": {"tag": "plain_text", "content": "🎙️ 语音消息"}, "template": "blue"}, "elements": [{"tag": "markdown", "content": "**文字内容：**\n\n要说的内容"}]}}'
```

## 重要规则

1. **语音输入**：用户发语音 → 必须用语音+文字双回复
2. **语音输出**：用户要求语音 → 必须合成语音发送
3. **同时发送**：语音消息必须附带文字，确保兼容所有平台
4. **检查文件**：合成后确认文件存在再发送

## 示例

### 示例一：用户语音问天气

用户语音："今天天气怎么样？"

处理：
1. 读取 transcript（系统已转录）
2. 回答：今天天气晴朗，20-28度
3. 合成语音
4. 发送：文字+语音双回复

### 示例二：用户要求读文章

用户："用语音读一下这段话：AI正在改变世界"

处理：
1. 提取要读的内容
2. 合成语音：AI正在改变世界
3. 发送：语音消息 + 文字"已经读给你听了"

## 故障排除

### Whisper 转录失败
- 确认 ffmpeg 已安装：`ffmpeg -version`
- 确认音频文件存在：`ls -la ~/.openclaw/media/inbound/`

### Edge TTS 生成失败
- 检查 Python 包：`python3 -c "import edge_tts"`
- 检查输出目录权限

### 语音发送失败
- Telegram：文件需 < 20MB
- 飞书：需要配置 App ID/Secret

---

**提示**：这个技能可以自动和天气、新闻、日程等技能结合，用语音播报信息。
