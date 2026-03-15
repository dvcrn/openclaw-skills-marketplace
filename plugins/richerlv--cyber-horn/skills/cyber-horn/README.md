# CyberHorn —— 一个让龙虾开口说话的SKILL

将文本通过 **ElevenLabs** 克隆语音合成（TTS），转成 Opus 后以**飞书原生语音条**发送到指定群聊或会话。

## 作用

- 输入一段文字 → 调用 ElevenLabs 生成语音（可指定克隆音色）
- 转码为飞书支持的 Opus 格式并上传
- 在飞书群/会话中发送为语音消息（非文件，可点击播放）

适合通知播报、机器人语音回复、OpenClaw 技能等场景。

## 环境要求

- Python 3.x
- 环境变量（可用 `.env`）：
  - `ELEVEN_API_KEY` — ElevenLabs API Key
  - `VOICE_ID` — 使用的音色 ID
  - `FEISHU_APP_ID` / `FEISHU_APP_SECRET` — 飞书应用凭证

## 安装与运行

```bash
pip install -r requirements.txt
python main.py "要说的内容" "飞书群/会话的 CHAT_ID" [receive_id_type]
```

`receive_id_type` 默认 `chat_id`，按飞书文档可改为 `open_id` 等。

## 作为 OpenClaw 技能

本项目提供 `skill.yaml`，可被 OpenClaw 以「环境变量 + 命令行参数」方式调用：  
第 1 个参数为语音文本，第 2 个为 `receive_id`（如 `oc_xxxx_chat_id`），第 3 个可选 `receive_id_type`。
