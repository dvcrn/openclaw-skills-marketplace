<p align="center">
  <h1 align="center">🧠 MLX Local Inference Stack</h1>
  <p align="center">
    Give your Apple Silicon Mac the power to hear, see, read, speak, think — all locally.
  </p>
  <p align="center">
    <a href="https://clawhub.ai/skills/mlx-local-inference"><img src="https://img.shields.io/badge/ClawHub-mlx--local--inference-FF5A36?style=flat-square" alt="ClawHub"></a>
    <a href="#"><img src="https://img.shields.io/badge/platform-macOS%20Apple%20Silicon-000?style=flat-square&logo=apple&logoColor=white" alt="Platform"></a>
    <a href="#"><img src="https://img.shields.io/badge/runtime-MLX-blue?style=flat-square" alt="MLX"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
  </p>
  <p align="center">
    <a href="README_CN.md"><b>中文</b></a> · English
  </p>
</p>

---

## One-Line Install

If you're running [OpenClaw](https://github.com/openclaw/openclaw) (or any agent with ClawHub support), just say:

> **"Install the mlx-local-inference skill"**

Your agent will run `clawhub install mlx-local-inference` and pick it up on the next session. That's it — your Mac gains local AI superpowers.

Or install manually:

```bash
clawhub install mlx-local-inference
```

Or clone directly:

```bash
git clone https://github.com/bendusy/mlx-local-inference.git
```

## Why This Exists

Your M-series Mac has a powerful Neural Engine and unified memory sitting right there — yet most AI workflows still send every request to the cloud. That's wasteful, slow, and unnecessary for a huge number of tasks.

**MLX Local Inference Stack** turns your Mac into a fully self-contained AI workstation. We've tested and curated the best-performing MLX models across every modality — speech recognition, text generation, OCR, text-to-speech, and embeddings — so you don't have to. One install, and your Mac can **hear, see, read, speak, and think**, entirely offline.

This is especially useful when paired with AI agents like [OpenClaw](https://github.com/openclaw/openclaw). Instead of routing every tool call through cloud APIs, the agent can leverage your local hardware for transcription, text correction, document reading, voice output, and semantic search — making interactions faster, cheaper, and more private.

## What Your Mac Gains

| Ability | What It Does | Curated Model |
|:--------|:-------------|:--------------|
| 👂 **Hear** | Transcribe speech — Cantonese, Mandarin, English, or any mix; 99 languages total | Qwen3-ASR-1.7B · Whisper-v3-turbo |
| 👁️ **See** | Extract text from photos, screenshots, receipts, documents | PaddleOCR-VL-1.5 |
| 🧠 **Think** | Chat, reason, write code, translate, summarize | Qwen3-14B · Gemma3-12B |
| 🗣️ **Speak** | Generate natural speech with custom voice cloning | Qwen3-TTS-1.7B |
| 📐 **Understand** | Vectorize text for semantic search, RAG, and document indexing | Qwen3-Embedding 0.6B · 4B |
| 📝 **Transcribe** | Drop an audio file, get corrected transcripts automatically | ASR + LLM correction pipeline |

Every model was selected through hands-on testing for quality, speed, and memory efficiency on Apple Silicon. They're packaged together as one coherent stack — not a collection of random tools, but an integrated local AI runtime.

## How It Fits Together

```
                        ┌─────────────────┐
                        │   Your Agent    │
                        │  (OpenClaw etc) │
                        └────────┬────────┘
                                 │ OpenAI-compatible API
                 ┌───────────────┼───────────────┐
                 ▼               ▼               ▼
          ┌────────────┐  ┌───────────┐  ┌────────────┐
          │  Port 8787 │  │ Port 8788 │  │    CLI     │
          │  always-on │  │ on-demand │  │  on-demand │
          │            │  │           │  │            │
          │ · LLM      │  │ · ASR     │  │ · OCR      │
          │ · Whisper  │  │ · TTS     │  │            │
          │ · Embed    │  │           │  │            │
          └────────────┘  └───────────┘  └────────────┘
                 │               │               │
                 └───────────────┴───────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   Apple Silicon (MLX)   │
                    │   Unified Memory GPU    │
                    └─────────────────────────┘
```

### Keep-Alive & On-Demand Loading

Not everything needs to run all the time. The stack uses a hybrid strategy:

- **Always-on (Port 8787):** The main service stays resident as a launchd daemon. LLM and Whisper models are kept warm in memory for instant response. This is where your agent sends most requests.
- **On-demand (Port 8788):** Qwen3-ASR and TTS models load into memory only when called, then can be unloaded to free RAM. This is ideal for models you use less frequently.
- **CLI-only:** OCR runs as a one-shot Python command — no daemon, no memory cost when idle.

The transcription daemon coordinates this intelligently: it loads ASR for transcription, unloads it when done, then loads the LLM for correction — avoiding memory contention on 16 GB machines.

You can unload any on-demand model manually:

```bash
# Free ASR model memory
curl -X DELETE "http://localhost:8788/models?model_name=mlx-community/Qwen3-ASR-1.7B-8bit"
```

## Requirements

- Apple Silicon Mac (M1 / M2 / M3 / M4)
- macOS 14+
- Python 3.10+
- 32 GB+ RAM recommended (16 GB works with keep-alive/on-demand strategy)

## Usage

### 🧠 Think — LLM Chat

```bash
curl http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-14b",
    "messages": [{"role": "user", "content": "Explain quantum computing briefly"}]
  }'
```

<details>
<summary>Python</summary>

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8787/v1", api_key="unused")
r = client.chat.completions.create(
    model="qwen3-14b",
    messages=[{"role": "user", "content": "Hello"}],
)
print(r.choices[0].message.content)
```

</details>

Two LLMs are included: **Qwen3-14B** (strongest Chinese + reasoning with built-in chain-of-thought) and **Gemma3-12B** (fast English + code). Pick based on your task.

### 👂 Hear — Speech Recognition

```bash
# Cantonese / Mandarin / Chinese-English mix → Qwen3-ASR
curl http://localhost:8788/v1/audio/transcriptions \
  -F file=@audio.wav -F model=mlx-community/Qwen3-ASR-1.7B-8bit -F language=zh

# English or any of 99 languages → Whisper
curl http://localhost:8787/v1/audio/transcriptions \
  -F file=@audio.wav -F model=whisper-large-v3-turbo
```

**Multi-language support:** Real conversations aren't monolingual. If you mix Cantonese, English, and Mandarin in the same audio (as many people do), Qwen3-ASR handles it natively. For pure non-Chinese audio, Whisper covers 99 languages. Set the `language` parameter to guide recognition, or omit it for auto-detection.

Supported formats: `wav`, `mp3`, `m4a`, `flac`, `ogg`, `webm`

### 👁️ See — OCR

```bash
python -m mlx_vlm.generate \
  --model mlx-community/PaddleOCR-VL-1.5-6bit \
  --image document.jpg --prompt "OCR:" --max-tokens 512 --temp 0.0
```

### 🗣️ Speak — Text-to-Speech

```bash
curl http://localhost:8788/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit","input":"Hello world"}' \
  -o speech.wav
```

### 📐 Understand — Embeddings

```bash
curl http://localhost:8787/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-embedding-0.6b", "input": ["document 1", "document 2"]}'
```

Two sizes: **0.6B** for fast retrieval, **4B** for high-accuracy semantic matching.

### 📝 Transcribe — Auto Pipeline

Drop audio files into `~/transcribe/` and walk away:

1. Qwen3-ASR transcribes → `filename_raw.md`
2. Qwen3-14B corrects errors, adds punctuation → `filename_corrected.md`
3. Results archived to `~/transcribe/done/`

The correction LLM adapts to the source language — it preserves Cantonese characters (嘅/唔/咁/喺) when the audio is Cantonese, uses standard Mandarin for Mandarin input, and handles mixed-language content naturally. You can customize the correction prompt in the daemon script to match your language preferences.

## Model Selection

Every model was chosen for the best balance of quality and efficiency on Apple Silicon:

| Modality | Model | Why This One |
|:---------|:------|:-------------|
| LLM (Chinese) | Qwen3-14B 4bit | Best bilingual performance at this size; native chain-of-thought |
| LLM (English) | Gemma3-12B 4bit | Fast, strong code generation, lean memory footprint |
| ASR (Chinese) | Qwen3-ASR-1.7B 8bit | Superior Cantonese/Mandarin/mixed accuracy, on-demand loading |
| ASR (Multi) | Whisper-v3-turbo | 99 languages, always loaded, battle-tested |
| Embedding (Fast) | Qwen3-Embedding-0.6B 4bit | Low latency, good enough for most retrieval |
| Embedding (Accurate) | Qwen3-Embedding-4B 4bit | High-precision semantic matching |
| OCR | PaddleOCR-VL-1.5 6bit | ~185 tokens/s, 3.3 GB, best accuracy-to-speed ratio |
| TTS | Qwen3-TTS-1.7B 8bit | Custom voice cloning, ~2 GB |

## Upgrading Models

The MLX ecosystem moves fast — new and better quantized models appear regularly. When you want to swap in a newer model:

1. **Download the new model:**
   ```bash
   huggingface-cli download mlx-community/<new-model-name>
   ```

2. **Update the server config** (`~/.mlx-server/config.yaml`):
   ```yaml
   models:
     - model: mlx-community/<new-model-name>
       model_id: qwen3-14b  # keep the same alias for compatibility
   ```

3. **Restart the service:**
   ```bash
   launchctl kickstart -k gui/$(id -u)/com.mlx-server
   ```

Your agent and all API calls continue using the same model ID — zero client-side changes. The `references/` docs in this repo list the exact models we've tested; check [mlx-community](https://huggingface.co/mlx-community) on Hugging Face for newer releases.

**Tip:** When a major new model drops (e.g., Qwen4, Gemma4), we'll publish an updated version of this skill via ClawHub. Update with:

```bash
clawhub update mlx-local-inference
```

Or just tell your agent: **"Update the mlx-local-inference skill."**

## Service Management

```bash
# Main service (LLM + Whisper + Embedding) — always-on
launchctl kickstart -k gui/$(id -u)/com.mlx-server

# ASR + TTS service — on-demand models
launchctl kickstart -k gui/$(id -u)/com.mlx-audio-server

# Auto-transcription daemon
launchctl kickstart gui/$(id -u)/com.mlx-transcribe-daemon
```

## Project Structure

```
mlx-local-inference/
├── SKILL.md              # OpenClaw skill definition
├── README.md             # English (this file)
├── README_CN.md          # 中文
├── LICENSE
└── references/           # Detailed per-model documentation
    ├── asr-qwen3.md
    ├── asr-whisper.md
    ├── embedding-qwen3.md
    ├── llm-qwen3-14b.md
    ├── llm-gemma3-12b.md
    ├── llm-models-reference.md
    ├── ocr.md
    ├── transcribe-daemon.md
    └── tts-qwen3.md
```

## Contributing

Issues and PRs welcome. See `references/` for detailed technical documentation on each model.

## License

[MIT](LICENSE)
