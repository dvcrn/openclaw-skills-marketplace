---
name: talk-mode
description: 持续对话模式技能，自动检测说话开始/结束（VAD），无需手动触发，智能静音检测，流畅的对话体验，支持实时语音对话循环。
---

# Talk Mode - 持续对话模式

**技能描述：** 实现持续的语音对话模式，自动检测说话结束并回复

---

## 🎯 功能

**核心特性：**
- ✅ 自动检测说话开始/结束
- ✅ 持续对话循环
- ✅ 无需手动触发
- ✅ 智能静音检测
- ✅ 流畅的对话体验

**工作流程：**
1. 检测到说话开始 → 自动录音
2. 检测到说话结束 → 停止录音
3. 语音识别 → AI处理 → 语音回复
4. 循环等待下一次说话

---

## 📦 依赖

**必需：**
- Python 3.12+
- ffmpeg
- webrtcvad（语音活动检测）
- pyaudio（音频输入）
- openai-whisper（语音识别）
- pyttsx3（语音合成）

**安装：**
```bash
# 安装系统依赖
sudo apt install -y ffmpeg portaudio19-dev espeak

# 安装Python依赖
pip install webrtcvad pyaudio openai-whisper pyttsx3
```

---

## 🚀 快速开始

### 1. 测试VAD检测
```bash
python3 skills/talk-mode/scripts/vad_test.py
```

### 2. 启动持续对话
```bash
python3 skills/talk-mode/scripts/start_talk.py
```

### 3. 退出对话
- 说"退出"或"再见"
- 或按Ctrl+C

---

## 🔧 配置

**对话配置（config.json）：**
```json
{
  "vad_mode": 3,
  "silence_duration": 1.0,
  "max_recording_time": 30,
  "sample_rate": 16000,
  "reply_speed": 150
}
```

**参数说明：**
- `vad_mode`: VAD灵敏度（0-3，3最敏感）
- `silence_duration`: 静音判定时长（秒）
- `max_recording_time`: 最大录音时长（秒）
- `sample_rate`: 采样率（16000Hz）
- `reply_speed`: 回复语速

---

## 📝 使用场景

1. **实时对话**
   - 持续监听并对话
   - 无需每次点击或唤醒
   - 流畅的交互体验

2. **会议助手**
   - 自动记录会议内容
   - 实时转写和总结
   - 语音指令控制

3. **电话客服**
   - 自动接听电话
   - 持续对话直到挂断
   - 语音转文字记录

---

## 🎨 特色

- ✅ 智能静音检测
- ✅ 自动录音剪辑
- ✅ 流畅对话体验
- ✅ 低延迟响应
- ✅ 支持打断回复

---

## 📚 技术细节

**VAD检测流程：**
```
音频流 → WebRTC VAD → 判断是否有人说话 → 触发录音
```

**对话循环：**
```
监听 → 检测说话 → 录音 → 识别 → AI处理 → 合成语音 → 播放 → 循环
```

**静音检测算法：**
- 使用WebRTC VAD
- 连续N帧静音判定为说话结束
- 可配置静音时长阈值

**性能优化：**
- 音频缓冲区优化
- 异步处理
- 实时流式识别

---

## 🔗 相关技能

- `voice-wake`：语音唤醒
- `voice-chat`：语音对话
- `speech-recognition`：语音识别

---

## 📋 开发进度

- [x] 技能框架创建
- [ ] VAD检测实现
- [ ] 自动录音逻辑
- [ ] 对话循环实现
- [ ] 与OpenClaw集成
- [ ] 测试优化

---

**版本：** 1.0.0
**创建时间：** 2026-03-03
**作者：** 米粒儿
