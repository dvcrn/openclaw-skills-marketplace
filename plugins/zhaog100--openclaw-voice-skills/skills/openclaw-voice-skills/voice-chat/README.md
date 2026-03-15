# Voice Chat - 语音对话技能

**完全本地化的语音对话功能，无需第三方API**

---

## 📦 安装

### 1. 安装系统依赖
```bash
sudo apt install -y ffmpeg espeak
```

### 2. 安装Python依赖
```bash
pip install openai-whisper pyttsx3
```

### 3. 可选：录音功能
```bash
pip install sounddevice soundfile
```

---

## 🚀 使用

### 语音识别
识别音频文件中的语音：
```bash
python3 ~/.openclaw/skills/voice-chat/scripts/recognize.py audio.mp3
```

### 语音合成
将文字转换为语音：
```bash
# 直接播放
python3 ~/.openclaw/skills/voice-chat/scripts/speak.py "你好，我是米粒儿"

# 保存为文件
python3 ~/.openclaw/skills/voice-chat/scripts/speak.py "你好" output.mp3
```

### 完整对话
```bash
# 单次对话
python3 ~/.openclaw/skills/voice-chat/scripts/chat.py

# 持续对话
python3 ~/.openclaw/skills/voice-chat/scripts/chat.py continuous
```

---

## 🔧 配置

**语音识别：**
- 模型：base（74MB）
- 语言：zh（中文）
- 设备：CPU

**语音合成：**
- 引擎：pyttsx3
- 语速：150
- 音量：1.0

---

## 🎯 功能特点

✅ 完全本地部署
✅ 无第三方API
✅ 数据隐私保护
✅ CPU友好
✅ 中文优化

---

## 📚 技术栈

- **语音识别：** OpenAI Whisper
- **语音合成：** pyttsx3
- **音频处理：** ffmpeg
- **录音功能：** sounddevice

---

## 🔗 集成

### QQ Bot集成（待开发）

**接收语音消息：**
1. QQ Bot接收语音消息
2. 保存音频文件
3. 调用recognize.py识别

**发送语音消息：**
1. AI生成文字回复
2. 调用speak.py生成语音
3. 通过QQ Bot发送

---

## ⚠️ 注意事项

1. **模型下载：** 首次使用会自动下载Whisper模型（74MB）
2. **CPU模式：** VMware环境无GPU加速，使用CPU模式
3. **中文优化：** 指定language="zh"以提高中文识别率
4. **隐私保护：** 完全本地处理，数据不上传

---

## 🐛 故障排除

**问题：找不到whisper命令**
```bash
pip install openai-whisper
```

**问题：找不到ffmpeg**
```bash
sudo apt install ffmpeg
```

**问题：没有中文语音**
```bash
sudo apt install espeak
```

---

## 📋 待办

- [x] 技能框架
- [x] 语音识别脚本
- [x] 语音合成脚本
- [x] 完整对话脚本
- [ ] QQ Bot集成
- [ ] 实时对话优化
- [ ] 中文模型优化

---

**版本：** 1.0.0
**创建时间：** 2026-03-03
**作者：** 米粒儿
