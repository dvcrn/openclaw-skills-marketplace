---
name: moss-transcribe-diarize
description: "Comprehensive MOSS Transcribe Diarize workflow for high-confidence multi-speaker ASR. Use when users need (1) timestamped transcription, (2) speaker-labeled segments/diarization, (3) meeting or interview transcript extraction, or (4) ASR from URL/Base64/local audio-video files with structured post-processing outputs (raw JSON, segment timeline, and by-speaker summary)."
---

# MOSS Transcribe Diarize Skill

Call this skill when users want:
- 多人语音转写（带说话人）
- 带时间戳的会议纪要原文
- 从音视频 URL / 本地文件做 ASR + diarization

## Quick workflow

1. 准备音频来源（URL / 本地文件 / Base64）
2. 调用 `scripts/transcribe.py`
3. 用 `segments` 生成：逐段文本、按说话人汇总、会后纪要

## API assumptions (from docs page)
- 模型名固定：`moss-transcribe-diarize`
- 请求体核心字段：
  - `audio_data`（URL 或 data URL）
  - `model`
  - `sampling_params`（如 `max_new_tokens`, `temperature`）
  - `meta_info`（可选）
- 返回中重点看：
  - `text`
  - `meta_info`
  - `segments`（含时间戳、speaker、content）

> 官方文档入口：`https://studio.mosi.cn/docs/moss-transcribe-diarize`

## Run

```bash
# URL 音频
python scripts/transcribe.py \
  --audio-url "https://example.com/audio.mp3" \
  --api-key "$MOSS_API_KEY" \
  --out result.json

# 本地文件（自动转 data URL）
python scripts/transcribe.py \
  --file "/path/to/meeting.mp4" \
  --api-key "$MOSS_API_KEY" \
  --out result.json
```

## Endpoint

默认 endpoint：`https://studio.mosi.cn/v1/audio/transcriptions`

如果你的环境 endpoint 不同，用参数覆盖：

```bash
--endpoint "https://your-endpoint"
```

## Output handling

- 原始结果保存为 JSON
- 脚本会额外导出：
  - `*.segments.txt`（逐段）
  - `*.by_speaker.txt`（按说话人）
