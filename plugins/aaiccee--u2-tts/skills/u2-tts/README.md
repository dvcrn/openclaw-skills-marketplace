# U2-TTS

> UniSound Text-to-Speech - Convert Chinese text to natural audio using WebSocket API

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your credentials
export UNISOUND_APPKEY='your_appkey'
export UNISOUND_SECRET='your_secret'

# 3. Convert text to speech
python scripts/tts.py --text '今天天气怎么样'
```

## Features

- **Real-time Streaming**: WebSocket-based TTS API
- **Multiple Voices**: Support for various Chinese voices (xiaofeng, xiaoyan, etc.)
- **Flexible Parameters**: Adjust speed, volume, pitch, and brightness
- **Multiple Formats**: Output in MP3, WAV, or PCM
- **High Quality**: 16kHz sample rate support

## Usage

### Command Line

```bash
# Basic usage
python scripts/tts.py --text '你好世界'

# Custom voice and format
python scripts/tts.py --text '测试' --voice xiaofeng-base --format wav

# Adjust speech parameters
python scripts/tts.py --text '快速朗读' --speed 70 --volume 60

# View all options
python scripts/tts.py --help
```

### Python API

```python
from scripts.tts import Ws_parms, do_ws, write_results
import os

ws_parms = Ws_parms(
    url='wss://ws-stts.hivoice.cn/v1/tts',
    appkey=os.getenv('UNISOUND_APPKEY'),
    secret=os.getenv('UNISOUND_SECRET'),
    pid=1,
    vcn='xiaofeng-base',
    text='你好，欢迎使用云知声语音合成服务！',
    tts_format='mp3',
    tts_sample='16k',
    user_id='demo',
)

do_ws(ws_parms)
write_results(ws_parms)
```

## Available Voices

| Voice | Type | Description |
|-------|------|-------------|
| xiaofeng-base | Male | Standard male voice |
| xiaoyan | Female | Female voice |
| xiaomei | Female | Alternative female voice |

## Speech Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `--speed` | 0-100 | 50 | Speech speed |
| `--volume` | 0-100 | 50 | Volume level |
| `--pitch` | 0-100 | 50 | Pitch level |
| `--bright` | 0-100 | 50 | Tone brightness |

## Output Formats

- **mp3** - Compressed, smaller file size (default)
- **wav** - Uncompressed, higher quality
- **pcm** - Raw audio data

## Configuration

Credentials can be set via environment variables or command line arguments:

```bash
# Environment variables (recommended)
export UNISOUND_APPKEY='your_appkey'
export UNISOUND_SECRET='your_secret'

# Or pass as arguments
python scripts/tts.py --appkey 'your_appkey' --secret 'your_secret' --text '测试'
```

## Output

Audio files are saved in the `results/` directory with timestamp filenames:

```
results/
├── 1773288318.mp3
├── 1773288450.wav
└── ...
```

## Examples

```bash
# News article to audio
python scripts/tts.py --text '欢迎收听今日新闻。人工智能技术正在快速发展。' --voice xiaofeng-base

# Audiobook chapter (slower, clearer)
python scripts/tts.py --text '第一章开始。在一个阳光明媚的早晨...' --speed 45 --format wav

# Quick notification (faster)
python scripts/tts.py --text '您有新的消息' --speed 65 --volume 60
```

## Requirements

- Python 3.6+
- websocket-client
- Valid UniSound AppKey and Secret

## Documentation

See [SKILL.md](SKILL.md) for complete API documentation and advanced usage examples.

## License

MIT License

## Links

- [UniSound Official Site](https://www.unisound.com/)
- [SKILL.md](SKILL.md) - Complete skill documentation
