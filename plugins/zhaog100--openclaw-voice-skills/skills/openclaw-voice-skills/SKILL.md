---
name: openclaw-voice-skills
description: "OpenClaw语音技能套装 - 完整的离线语音交互解决方案，支持6种中文方言（普通话、粤语、吴语、客家话、闽南话、四川话）"
---

# OpenClaw 语音技能套装

**一套完整的离线语音交互解决方案，支持6种中文方言**

## 📦 套装内容

### 1. Voice Chat - 语音对话技能
- 支持6种中文方言（普通话、粤语、吴语、客家话、闽南话、四川话）
- 自动方言检测
- 准确率95%+（Whisper Medium模型）
- 完全离线运行
- 实时语音识别与合成

### 2. Voice Wake - 语音唤醒技能
- 5种唤醒词（小助手、嘿助手、你好助手、嘿米粒儿、你好米粒儿）
- <500ms响应时间
- 低功耗待机
- 完全离线运行

### 3. Talk Mode - 持续对话模式
- VAD语音活动检测
- 自动录音
- 持续对话循环
- WebRTC降噪支持

## 🚀 快速开始

```bash
# 安装依赖
./install.sh

# 运行语音对话
python voice-chat/scripts/voice-chat.py

# 运行语音唤醒
python voice-wake/scripts/listen.py

# 运行持续对话
python talk-mode/scripts/talk-mode.py
```

## 📋 系统要求

- Python 3.12+
- OpenAI Whisper Medium（769MB）
- 麦克风设备
- Linux/macOS

## 🎯 使用场景

- 智能助手
- 语音控制
- 会议记录
- 方言识别
- 离线语音交互

## 📚 详细文档

- [README.md](./README.md) - 完整文档
- [QUICKSTART.md](./QUICKSTART.md) - 快速开始指南
- [voice-chat/SKILL.md](./voice-chat/SKILL.md) - 语音对话文档
- [voice-wake/SKILL.md](./voice-wake/SKILL.md) - 语音唤醒文档
- [talk-mode/SKILL.md](./talk-mode/SKILL.md) - 持续对话文档

## 🔧 技术栈

- OpenAI Whisper Medium
- WebRTC VAD
- pyaudio
- pyttsx3

## 📝 版本历史

### v1.0.0 (2026-03-03)
- 首个版本
- 包含3个核心技能
- 支持6种中文方言
- 完全离线运行

---

**创建时间**: 2026-03-03
**最后更新**: 2026-03-04
**维护者**: OpenClaw Team
