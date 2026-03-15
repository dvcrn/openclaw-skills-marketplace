# References

此文件夹包含 ASR skill 的参考文件。

## 文件说明

### audio_example.txt
音频文件示例说明

### config_examples.md
配置示例，展示不同使用场景的配置方式

## 使用示例音频

如果你想测试这个 skill，可以使用以下方式准备测试音频：

1. **使用自己的音频文件**
   ```bash
   python3 ../scripts/transcribe.py /path/to/your/audio.wav
   ```

2. **支持的音频格式**
   - WAV - 推荐，无损格式
   - MP3 - 通用格式
   - M4A - Apple 设备常用
   - FLAC - 无损压缩
   - OGG - 开源格式

3. **音频要求**
   - 最大文件大小：100MB
   - 最长时长：2小时
   - 采样率：建议 16kHz 或以上
   - 声道：支持单声道和立体声

## 配置示例

参考 `config_examples.md` 查看不同场景的配置方法。
