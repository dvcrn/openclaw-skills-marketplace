# 音频文件指南

## 支持的音频格式

| 格式 | 扩展名 | 推荐场景 |
|------|--------|----------|
| WAV | `.wav` | 最佳质量，推荐使用 |
| MP3 | `.mp3` | 通用格式，文件较小 |
| M4A | `.m4a` | Apple 设备录制 |
| FLAC | `.flac` | 无损压缩，高保真 |
| OGG | `.ogg` | 开源格式 |

## 音频参数建议

### 推荐参数
- **采样率**: 16kHz 或以上
- **位深度**: 16-bit 或以上
- **声道**: 单声道（mono）或立体声（stereo）

### 不同场景的建议

#### 电话通话录音
- 格式: WAV 或 MP3
- 采样率: 8kHz - 16kHz
- 声道: 单声道

#### 会议录音
- 格式: WAV 或 FLAC
- 采样率: 16kHz - 44.1kHz
- 声道: 单声道或立体声

#### 高质量音频
- 格式: WAV 或 FLAC
- 采样率: 44.1kHz - 48kHz
- 声道: 立体声

## 文件限制

- **最大文件大小**: 100MB
- **最长时长**: 2小时

## 音频质量对识别效果的影响

### 良好质量的音频特征
✓ 清晰的人声，无明显背景噪音
✓ 适当的音量（不要过小或过大）
✓ 稳定的采样率
✓ 完整的音频文件（未损坏）

### 可能影响识别效果的因素
✗ 强烈的背景噪音（音乐、交通噪音等）
✗ 多人同时说话且重叠
✗ 音量过小或失真
✓ 低采样率（低于 8kHz）
✗ 损坏的音频文件

## 音频转换

### 使用 ffmpeg 转换音频格式

#### MP3 转 WAV
```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```

#### M4A 转 WAV
```bash
ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav
```

#### 调整采样率
```bash
ffmpeg -i input.wav -ar 16000 output_16k.wav
```

#### 转换为单声道
```bash
ffmpeg -i input.wav -ac 1 output_mono.wav
```

#### 优化音频质量
```bash
ffmpeg -i input.wav -ar 16000 -ac 1 -b:a 64k output_optimized.wav
```

### 在线转换工具

如果不想使用命令行工具，可以使用：
- **在线转换**: cloudconvert.com, convertio.co
- **桌面软件**: Audacity（免费，开源）

## 测试音频

### 获取测试音频

1. **使用自己录制的音频**
   ```bash
   # Linux/Mac
   arecord -d 10 -r 16000 -f S16_LE test.wav

   # Windows (使用 PowerShell)
   $soundRecorder = New-Object -ComObject SoundRecorder
   ```

2. **下载公开数据集**
   - Common Voice (Mozilla)
   - LibriSpeech
   - AISHELL (中文语音数据集)

3. **使用示例音频**
   确保你有测试音频文件：
   ```bash
   ls -lh audio.wav
   ```

### 测试命令

```bash
# 基础测试
python3 ../scripts/transcribe.py test_audio.wav

# 查看详细输出
python3 ../scripts/transcribe.py test_audio.wav --json --out result.json
cat result.json
```

## 常见音频问题

### 问题：文件过大
**解决方案**：降低采样率或使用压缩格式
```bash
ffmpeg -i large.wav -ar 16000 -b:a 64k output.mp3
```

### 问题：识别不准确
**可能原因**：
- 背景噪音过大
- 音量过小
- 采样率过低
- 音频格式不兼容

**解决方案**：
```bash
# 提高音量并降噪
ffmpeg -i input.wav -af "volume=2.0" output.wav

# 转换为标准格式
ffmpeg -i input.wav -ar 16000 -ac 1 output.wav
```

### 问题：音频文件损坏
**检查方法**：
```bash
# 使用 ffmpeg 检查
ffmpeg -v error -i input.wav -f null -
```

**解决方案**：重新录制或获取音频文件

## 音频录制建议

### 录音环境
- 选择安静的场所
- 避免回声和混响
- 远离噪音源（空调、电脑风扇等）

### 麦克风位置
- 距离说话者 20-30cm
- 避免直接对着麦克风吹气
- 使用防风罩（如果在户外）

### 录音设置
- 格式: WAV（无损）
- 采样率: 44.1kHz 或 48kHz
- 位深度: 16-bit 或 24-bit
- 声道: 单声道

## 批量处理

### 批量转换格式
```bash
for file in *.mp3; do
    ffmpeg -i "$file" -ar 16000 -ac 1 "${file%.mp3}.wav"
done
```

### 批量转写
```bash
for file in audio/*.wav; do
    python3 ../scripts/transcribe.py "$file" --out "results/$(basename "$file" .wav).txt"
done
```
