# 配置示例

本文档展示不同使用场景的配置方式。

## 1. 基础配置（使用内置凭据）

直接使用，无需任何配置：

```bash
python3 ../scripts/transcribe.py audio.wav
```

## 2. 使用自己的凭据

### 方式 A：修改脚本默认值

编辑 `../scripts/transcribe.py`：

```python
@dataclass
class ASRConfig:
    appkey: str = "your_appkey_here"      # 修改这里
    secret: str = "your_secret_here"      # 修改这里
    userid: str = "your_userid_here"      # 修改这里
    base_url: str = "https://your-api.com"  # 可选：修改API地址
```

### 方式 B：使用环境变量

```bash
# 设置环境变量
export UNISOUND_APPKEY="your_appkey"
export UNISOUND_SECRET="your_secret"
export UNISOUND_USERID="your_userid"

# 运行脚本
python3 ../scripts/transcribe.py audio.wav
```

### 方式 C：使用 .env 文件

创建 `.env` 文件：

```bash
UNISOUND_APPKEY=your_appkey
UNISOUND_SECRET=your_secret
UNISOUND_USERID=your_userid
```

加载并运行：

```bash
set -a && source .env && set +a
python3 ../scripts/transcribe.py audio.wav
```

## 3. 不同音频格式

### MP3 文件
```bash
python3 ../scripts/transcribe.py audio.mp3 --format mp3
```

### M4A 文件
```bash
python3 ../scripts/transcribe.py audio.m4a --format m4a
```

### FLAC 文件
```bash
python3 ../scripts/transcribe.py audio.flac --format flac
```

## 4. 不同业务场景

### 金融领域（默认）
```bash
python3 ../scripts/transcribe.py audio.wav --domain finance
```

### 通用领域
```bash
python3 ../scripts/transcribe.py audio.wav --domain general
```

### 客服领域
```bash
python3 ../scripts/transcribe.py audio.wav --domain customerservice
```

## 5. 输出选项

### 保存为文本文件
```bash
python3 ../scripts/transcribe.py audio.wav --out result.txt
```

### 保存为 JSON 文件（包含完整结果）
```bash
python3 ../scripts/transcribe.py audio.wav --json --out result.json
```

### 关闭标点符号处理
```bash
python3 ../scripts/transcribe.py audio.wav --no-punction
```

## 6. 批量处理示例

创建批处理脚本 `batch_transcribe.sh`：

```bash
#!/bin/bash

for file in audio/*.wav; do
    echo "Processing: $file"
    python3 ../scripts/transcribe.py "$file" --out "results/$(basename $file .wav).txt"
done
```

## 7. Python 集成示例

```python
from scripts.transcribe import ASRClient, ASRConfig

# 使用默认配置
config = ASRConfig()

# 或自定义配置
config = ASRConfig(
    appkey="your_appkey",
    secret="your_secret",
    userid="your_userid",
)

# 创建客户端并转写
with ASRClient(config) as client:
    result = client.transcribe("audio.wav")
    text = client.extract_text(result)
    print(text)
```

## 8. 常见参数组合

### 快速转写（默认设置）
```bash
python3 ../scripts/transcribe.py audio.wav
```

### 完整转写（保存JSON结果）
```bash
python3 ../scripts/transcribe.py audio.wav --json --out result.json
```

### 指定格式和领域
```bash
python3 ../scripts/transcribe.py audio.mp3 --format mp3 --domain finance --out result.txt
```

### 无标点符号
```bash
python3 ../scripts/transcribe.py audio.wav --no-punction
```

## 9. 错误处理示例

```bash
# 检查文件是否存在
if [ ! -f "audio.wav" ]; then
    echo "Error: audio.wav not found"
    exit 1
fi

# 执行转写并检查错误
python3 ../scripts/transcribe.py audio.wav || {
    echo "Transcription failed"
    exit 1
}
```

## 10. 日志记录

```bash
# 保存标准错误输出到日志文件
python3 ../scripts/transcribe.py audio.wav 2> transcript.log

# 同时保存输出和错误
python3 ../scripts/transcribe.py audio.wav --out result.txt 2>&1 | tee full.log
```
