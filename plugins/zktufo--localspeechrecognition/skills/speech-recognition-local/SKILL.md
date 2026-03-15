---
name: speech-recognition-local
description: "本地语音转文字。使用 faster-whisper 在本地运行 Whisper 模型，无需 API 费用。"
---

# 本地语音识别

## 触发

- 用户发送语音消息 (.ogg, .m4a, .mp3)

## 转录命令

```bash
python3 ~/.openclaw/workspace/scripts/transcribe.py <audio_file> [language]
```

- language: zh (中文默认) / en (英文)

## 首次使用

首次运行时会自动下载模型 (~75MB for small 模型)

## 模型

- **small**: 推荐，速度和准确度平衡好 (~75MB)
- **base**: 更快但准确度稍低 (~75MB)  
- **medium**: 更准确但更慢 (~800MB)

可修改脚本中的 `model_size` 切换模型。

## 费用

免费（本地运行）

## 已配置

✅ faster-whisper 已安装
✅ small 模型可自动下载
