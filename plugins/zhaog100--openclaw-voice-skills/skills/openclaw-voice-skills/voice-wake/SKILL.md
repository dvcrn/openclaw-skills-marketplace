---
name: voice-wake
description: 语音唤醒技能（类似Siri/小爱同学），支持5种唤醒词（小助手、嘿助手、你好助手、嘿米粒儿、你好米粒儿），完全离线运行，<500ms响应时间，持续音频监听，低功耗待机。
---

# Voice Wake - 语音唤醒技能

**技能描述：** 实现"Hey 米粒儿"语音唤醒功能，类似Siri/小爱同学

---

## 🎯 功能

**核心特性：**
- ✅ 自定义唤醒词
- ✅ 持续音频监听
- ✅ 低功耗待机
- ✅ 快速唤醒响应（<500ms）
- ✅ 本地离线运行

**唤醒词示例：**
- "Hey 米粒儿"
- "小助手"
- "你好米粒"
- 自定义唤醒词

---

## 📦 依赖

**必需：**
- Python 3.12+
- ffmpeg
- pvporcupine（Porcupine唤醒词引擎）
- pyaudio（音频输入）

**安装：**
```bash
# 安装系统依赖
sudo apt install -y ffmpeg portaudio19-dev

# 安装Python依赖
pip install pvporcupine pyaudio
```

**Porcupine配置：**
- 访问：https://picovoice.ai/
- 注册账号获取Access Key（免费版每月1000次）
- 或使用本地模型（无需API Key）

---

## 🚀 快速开始

### 1. 获取Porcupine Access Key（可选）
```bash
# 注册 https://console.picovoice.ai/
# 获取Access Key
export PICOVOICE_ACCESS_KEY="your_key_here"
```

### 2. 测试唤醒词
```bash
python3 skills/voice-wake/scripts/wake_test.py
```

### 3. 启动持续监听
```bash
python3 skills/voice-wake/scripts/listen.py
```

---

## 🔧 配置

**唤醒词配置（config.json）：**
```json
{
  "wake_word": "嘿米粒",
  "sensitivity": 0.5,
  "audio_device": null,
  "sample_rate": 16000
}
```

**参数说明：**
- `wake_word`: 唤醒词
- `sensitivity`: 灵敏度（0.0-1.0，越高越敏感）
- `audio_device`: 音频设备ID（null=默认）
- `sample_rate`: 采样率（16000Hz）

---

## 📝 使用场景

1. **桌面助手**
   - 持续监听麦克风
   - 检测到唤醒词后激活
   - 调用OpenClaw处理指令

2. **QQ Bot增强**
   - 与QQ Bot集成
   - 语音唤醒后自动发送消息

3. **智能家居控制**
   - 语音唤醒 → 指令识别 → 执行操作

---

## 🎨 特色

- ✅ 本地离线运行
- ✅ 低CPU占用
- ✅ 快速响应
- ✅ 多唤醒词支持
- ✅ 噪音抑制

---

## 📚 技术细节

**唤醒流程：**
```
麦克风输入 → Porcupine检测 → 唤醒词匹配 → 激活OpenClaw → 等待指令
```

**音频处理：**
- 采样率：16kHz
- 帧长：512样本（32ms）
- 编码：16-bit PCM

**性能优化：**
- 使用Porcupine的轻量级模型
- CPU模式运行
- 低功耗待机

---

## 🔗 相关技能

- `talk-mode`：持续对话模式
- `voice-chat`：语音对话
- `speech-recognition`：语音识别

---

## 📋 开发进度

- [x] 技能框架创建
- [ ] Porcupine集成
- [ ] 音频监听实现
- [ ] 唤醒词训练
- [ ] 与OpenClaw集成
- [ ] 测试优化

---

**版本：** 1.0.0
**创建时间：** 2026-03-03
**作者：** 米粒儿
