---
name: u2-tts
description: "U2-tts"
---

name: u2-tts

description: Text-to-speech conversion using UniSound's TTS WebSocket API for generating high-quality Chinese Mandarin audio from text. Supports multiple voices, adjustable parameters, and real-time streaming synthesis.

---

Text-to-speech conversion using UniSound's TTS WebSocket API for generating high-quality Chinese Mandarin audio from text.

Installation
------------
```bash
pip install websocket-client
```

Set your credentials as environment variables:
```bash
export UNISOUND_APPKEY='ce44uxf7g5eag2cv33qvlp5d22qrkgcezvgfp2q3'
export UNISOUND_SECRET='5c12231cd279b35873a3ccecf9439118'
```

Features
--------
* WebSocket-based streaming TTS API
* Multiple Chinese voice options (xiaofeng, xiaoyan, etc.)
* Adjustable speech parameters (speed, volume, pitch, brightness)
* Multiple output formats (mp3, wav, pcm)
* Multiple sample rates (8k, 16k)
* SHA256 signature authentication
* Automatic connection management

Activation
----------
This skill activates when the user:
* Requests Chinese text-to-speech: "把这段文字转成语音", "生成中文语音", "使用云知声TTS"
* Uses keywords: "unisound", "云知声", "hivoice", "ws-stts"
* Needs Chinese Mandarin speech synthesis
* Asks for streaming TTS or WebSocket-based TTS
* Specifies voice preferences: "xiaofeng", "xiaoyan"

Requirements
------------
* `UNISOUND_APPKEY` environment variable must be set
* `UNISOUND_SECRET` environment variable must be set
* Python 3.6+
* Dependencies: `websocket-client` (for WebSocket connection)

Quick Start
-----------
### Command Line (Recommended)
```bash
# Set credentials
export UNISOUND_APPKEY='ce44uxf7g5eag2cv33qvlp5d22qrkgcezvgfp2q3'
export UNISOUND_SECRET='5c12231cd279b35873a3ccecf9439118'

# Basic usage
python scripts/tts.py --text '今天天气怎么样'

# With custom voice and format
python scripts/tts.py --text '你好世界' --voice xiaofeng-base --format wav

# Adjust speech parameters
python scripts/tts.py --text '快速朗读' --speed 70 --volume 60
```

### Python API
```python
from scripts.tts import Ws_parms, do_ws, write_results
import os

# Simple TTS conversion
ws_parms = Ws_parms(
    url='wss://ws-stts.hivoice.cn/v1/tts',
    appkey=os.getenv('UNISOUND_APPKEY'),
    secret=os.getenv('UNISOUND_SECRET'),
    pid=1,
    vcn='xiaofeng-base',
    text='你好，欢迎使用云知声语音合成服务！',
    tts_format='mp3',
    tts_sample='16k',
    user_id='quick-demo',
)

do_ws(ws_parms)
write_results(ws_parms)
print('Audio saved to results/ directory!')
```

Voices
------
| Voice | Type | Description |
| --- | --- | --- |
| xiaofeng-base | Male | Standard male voice |
| xiaoyan | Female | Female voice options |
| xiaomei | Female | Alternative female voice |
| Custom voices | Various | Contact UniSound for more options |

Parameters
----------
| Parameter | Range | Default | Description |
| --- | --- | --- | --- |
| speed | 0-100 | 50 | Speech speed (50 = normal) |
| volume | 0-100 | 50 | Volume level (50 = normal) |
| pitch | 0-100 | 50 | Pitch level (50 = normal) |
| bright | 0-100 | 50 | Brightness/tone (50 = normal) |

Usage
-----
### Basic Usage

```python
from scripts.tts import Ws_parms, do_ws, write_results

# Set credentials
appkey = 'ce44uxf7g5eag2cv33qvlp5d22qrkgcezvgfp2q3'
secret = '5c12231cd279b35873a3ccecf9439118'
ws_url = 'wss://ws-stts.hivoice.cn/v1/tts'
user_id = 'unisound-python-demo'

# Configure TTS parameters
vcn = 'xiaofeng-base'  # Voice name
text = '今天天气怎么样？'  # Text to convert
tts_format = 'mp3'  # Output format: mp3, wav, pcm
tts_sample = '16k'  # Sample rate: 8k, 16k

# Create WebSocket parameters
ws_parms = Ws_parms(
    url=ws_url,
    appkey=appkey,
    secret=secret,
    pid=1,
    vcn=vcn,
    text=text,
    tts_format=tts_format,
    tts_sample=tts_sample,
    user_id=user_id,
)

# Execute TTS conversion
do_ws(wsP)

# Save result to file
write_results(wsP)
print('TTS conversion completed!')
```

### Using Environment Variables

```python
import os
from scripts.tts import Ws_parms, do_ws, write_results

appkey = os.getenv('UNISOUND_APPKEY')
secret = os.getenv('UNISOUND_SECRET')

ws_parms = Ws_parms(
    url='wss://ws-stts.hivoice.cn/v1/tts',
    appkey=appkey,
    secret=secret,
    pid=1,
    vcn='xiaofeng-base',
    text='欢迎使用云知声语音合成服务',
    tts_format='mp3',
    tts_sample='16k',
    user_id='my-app',
)

do_ws(ws_parms)
write_results(ws_parms)
```

### Custom Speech Parameters

```python
from scripts.tts import Ws_parms, do_ws, write_results

ws_parms = Ws_parms(
    url='wss://ws-stts.hivoice.cn/v1/tts',
    appkey='ce44uxf7g5eag2cv33qvlp5d22qrkgcezvgfp2q3',
    secret='5c12231cd279b35873a3ccecf9439118',
    pid=1,
    vcn='xiaofeng-base',
    text='这是自定义参数的语音合成示例',
    tts_format='wav',
    tts_sample='16k',
    user_id='demo',
)

# Customize speech parameters
wsP.tts_speed = 60   # Faster speech (0-100)
wsP.tts_volume = 70  # Louder volume (0-100)
wsP.tts_pitch = 40   # Lower pitch (0-100)
wsP.tts_bright = 60  # Brighter tone (0-100)

do_ws(ws_parms)
write_results(ws_parms)
```

### Long Text Processing

```python
from scripts.tts import Ws_parms, do_ws, write_results

def long_text_tts(text, output_format='mp3'):
    ws_parms = Ws_parms(
        url='wss://ws-stts.hivoice.cn/v1/tts',
        appkey=os.getenv('UNISOUND_APPKEY'),
        secret=os.getenv('UNISOUND_SECRET'),
        pid=1,
        vcn='xiaofeng-base',
        text=text,
        tts_format=output_format,
        tts_sample='16k',
        user_id='long-text-demo',
    )
    do_ws(wsP)
    return write_results(wsP)

# Usage
long_text = """
这是一段很长的文本内容。
云知声TTS服务可以处理长文本合成。
支持多种输出格式和采样率。
语音自然流畅，适合各种应用场景。
"""

long_text_tts(long_text)
```

Output Formats
--------------
Supported formats: `mp3` (default), `wav`, `pcm`

Supported sample rates: `16k` (default), `8k`

| Format | Compression | Quality | File Size | Best For |
| --- | --- | --- | --- | --- |
| mp3 | Lossy | Good | Small | General use, web, streaming |
| wav | None | Excellent | Large | High-quality production |
| pcm | None | Excellent | Large | Raw audio processing |

# MP3 format (compressed, smaller file size)
ws_parms = Ws_parms(..., tts_format='mp3', tts_sample='16k')

# WAV format (uncompressed, higher quality)
ws_parms = Ws_parms(..., tts_format='wav', tts_sample='16k')

# PCM format (raw audio data)
ws_parms = Ws_parms(..., tts_format='pcm', tts_sample='16k')
```

Command Line
------------
```bash
# Set credentials as environment variables
export UNISOUND_APPKEY='ce44uxf7g5eag2cv33qvlp5d22qrkgcezvgfp2q3'
export UNISOUND_SECRET='5c12231cd279b35873a3ccecf9439118'

# Quick start - basic usage
python scripts/tts.py --text '今天天气怎么样'

# Common options
python scripts/tts.py --text '你好世界' --voice xiaofeng-base --format wav
python scripts/tts.py --text '测试' --speed 60 --volume 70 --pitch 50
python scripts/tts.py --text '高质量音频' --format wav --sample 16k

# View all options
python scripts/tts.py --help
```

Error Handling
--------------
```python
from scripts.tts import Ws_parms, do_ws, write_results
import os

def safe_tts_conversion(text, max_retries=3):
    appkey = os.getenv('UNISOUND_APPKEY')
    secret = os.getenv('UNISOUND_SECRET')

    for attempt in range(max_retries):
        try:
            ws_parms = Ws_parms(
                url='wss://ws-stts.hivoice.cn/v1/tts',
                appkey=appkey,
                secret=secret,
                pid=1,
                vcn='xiaofeng-base',
                text=text,
                tts_format='mp3',
                tts_sample='16k',
                user_id='safe-demo',
            )

            do_ws(wsP)

            # Check if audio data was received
            if len(wsP.tts_stream) > 0:
                write_results(wsP)
                print(f"Success! Generated {len(wsP.tts_stream)} bytes")
                return True
            else:
                print("No audio data received")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff

    return False

# Usage
success = safe_tts_conversion("测试错误处理")
```

Examples
--------
### Audiobook Chapter Converter

```python
from scripts.tts import Ws_parms, do_ws, write_results
import os

def convert_chapter(chapter_text, chapter_num, voice='xiaofeng-base'):
    """Convert a book chapter to audio file"""
    filename = f'chapter_{chapter_num:02d}.mp3'

    # Add chapter announcement
    intro = f"第{chapter_num}章。"
    full_text = intro + chapter_text

    ws_parms = Ws_parms(
        url='wss://ws-stts.hivoice.cn/v1/tts',
        appkey=os.getenv('UNISOUND_APPKEY'),
        secret=os.getenv('UNISOUND_SECRET'),
        pid=chapter_num,
        vcn=voice,
        text=full_text,
        tts_format='mp3',
        tts_sample='16k',
        user_id=f'audiobook-ch{chapter_num}',
    )

    # Slower, clearer reading for books
    wsP.tts_speed = 45
    wsP.tts_pitch = 50

    do_ws(wsP)
    write_results(wsP)
    print(f"Chapter {chapter_num} converted to {filename}")

# Usage
chapter = """这是第一章的内容。在一个阳光明媚的早晨，
主人公开始了他的冒险之旅。这个故事将带我们
走进一个充满奇迹的世界。"""
convert_chapter(chapter, 1)
```

### Chat Message Reader

```python
from scripts.tts import Ws_parms, do_ws, write_results
import os

def read_messages(messages, output_file='chat_audio.mp3'):
    """Convert chat messages to audio for hands-free listening"""
    formatted_text = []

    for msg in messages:
        speaker = msg.get('speaker', '未知')
        content = msg.get('content', '')
        formatted_text.append(f"{speaker}说：{content}")

    full_text = "。".join(formatted_text) + "。"

    ws_parms = Ws_parms(
        url='wss://ws-stts.hivoice.cn/v1/tts',
        appkey=os.getenv('UNISOUND_APPKEY'),
        secret=os.getenv('UNISOUND_SECRET'),
        pid=1,
        vcn='xiaofeng-base',
        text=full_text,
        tts_format='mp3',
        tts_sample='16k',
        user_id='chat-reader',
    )

    do_ws(wsP)
    write_results(wsP)
    print(f"Chat messages saved to {output_file}")

# Usage
messages = [
    {'speaker': '小明', 'content': '你好，最近怎么样？'},
    {'speaker': '小红', 'content': '我很好，谢谢关心！你呢？'},
    {'speaker': '小明', 'content': '我也不错，周末有空吗？'},
]
read_messages(messages)
```

### Accessibility Helper

```python
from scripts.tts import Ws_parms, do_ws, write_results
import os

def accessibility_reader(text, speed='normal', voice='xiaofeng-base'):
    """
    Text-to-speech for accessibility (visually impaired users)
    with customizable reading speed
    """
    speed_map = {
        'slow': 35,
        'normal': 50,
        'fast': 65
    }

    ws_parms = Ws_parms(
        url='wss://ws-stts.hivoice.cn/v1/tts',
        appkey=os.getenv('UNISOUND_APPKEY'),
        secret=os.getenv('UNISOUND_SECRET'),
        pid=1,
        vcn=voice,
        text=text,
        tts_format='mp3',
        tts_sample='16k',
        user_id='accessibility',
    )

    wsP.tts_speed = speed_map.get(speed, 50)
    wsP.tts_volume = 70  # Higher volume for accessibility

    do_ws(wsP)
    write_results(wsP)
    return wsP.tts_stream

# Usage
article = "这是一篇重要的新闻文章。"
accessibility_reader(article, speed='slow')
```

### Batch Text to Speech

```python
from scripts.tts import Ws_parms, do_ws, write_results
import os

def batch_tts(text_list, output_dir='results'):
    """Convert multiple texts to audio files"""
    appkey = os.getenv('UNISOUND_APPKEY')
    secret = os.getenv('UNISOUND_SECRET')

    for i, text in enumerate(text_list):
        ws_parms = Ws_parms(
            url='wss://ws-stts.hivoice.cn/v1/tts',
            appkey=appkey,
            secret=secret,
            pid=i,
            vcn='xiaofeng-base',
            text=text,
            tts_format='mp3',
            tts_sample='16k',
            user_id=f'batch-{i}',
        )

        do_ws(wsP)
        write_results(wsP)
        print(f"Generated: {text[:30]}...")

# Usage
texts = [
    "第一段文字",
    "第二段文字",
    "第三段文字"
]
batch_tts(texts)
```

### News Article Reader

```python
from scripts.tts import Ws_parms, do_ws, write_results

def news_to_audio(title, content, voice='xiaofeng-base'):
    """Convert news article to audio with intro and outro"""
    intro = f"欢迎收听新闻。{title}。"
    outro = "感谢您的收听。"

    full_text = f"{intro}\n{content}\n{outro}"

    ws_parms = Ws_parms(
        url='wss://ws-stts.hivoice.cn/v1/tts',
        appkey=os.getenv('UNISOUND_APPKEY'),
        secret=os.getenv('UNISOUND_SECRET'),
        pid=1,
        vcn=voice,
        text=full_text,
        tts_format='mp3',
        tts_sample='16k',
        user_id='news-reader',
    )

    do_ws(wsP)
    return write_results(wsP)

# Usage
title = "今日科技新闻"
content = "人工智能技术正在快速发展，为各行各业带来创新变革。"
news_to_audio(title, content)
```

### Custom Voice Preset

```python
from scripts.tts import Ws_parms, do_ws, write_results

def create_voice_preset(preset_name):
    """Create different voice presets"""
    presets = {
        'narrator': {'speed': 45, 'volume': 55, 'pitch': 50, 'bright': 50},
        'announcer': {'speed': 55, 'volume': 60, 'pitch': 55, 'bright': 60},
        'gentle': {'speed': 40, 'volume': 45, 'pitch': 45, 'bright': 45},
    }

    return presets.get(preset_name, presets['narrator'])

def tts_with_preset(text, preset='narrator'):
    params = create_voice_preset(preset)

    ws_parms = Ws_parms(
        url='wss://ws-stts.hivoice.cn/v1/tts',
        appkey=os.getenv('UNISOUND_APPKEY'),
        secret=os.getenv('UNISOUND_SECRET'),
        pid=1,
        vcn='xiaofeng-base',
        text=text,
        tts_format='mp3',
        tts_sample='16k',
        user_id=f'preset-{preset}',
    )

    wsP.tts_speed = params['speed']
    wsP.tts_volume = params['volume']
    wsP.tts_pitch = params['pitch']
    wsP.tts_bright = params['bright']

    do_ws(wsP)
    return write_results(wsP)

# Usage
tts_with_preset("这是一个主播风格的语音示例", preset='announcer')
tts_with_preset("这是一个温柔风格的语音示例", preset='gentle')
```

Authentication
--------------
The UniSound TTS API uses SHA256 signature-based authentication:

```python
# Signature is automatically generated by Ws_parms class
# Format: SHA256(appkey + timestamp + secret).upper()

# Manual signature example (if needed):
import hashlib
import time

def generate_signature(appkey, secret):
    timestamp = str(int(time.time() * 1000))
    hs = hashlib.sha256()
    hs.update((appkey + timestamp + secret).encode('utf-8'))
    signature = hs.hexdigest().upper()
    return timestamp, signature
```

Links
-----
* [UniSound/HiVoice Official Site](https://www.unisound.com/)
* [WebSocket Client Documentation](https://websocket-client.readthedocs.io/)
* [TTS API Documentation](https://www.unisound.com/tts-api)

Tips
----
* For better audio quality, use `wav` format with `16k` sample rate
* Adjust `tts_speed` between 45-55 for natural speech
* Use batch processing for converting multiple texts to improve efficiency
* Check the `logs/` directory for detailed operation logs
* Generated audio files are saved in `results/` directory with timestamp filenames
