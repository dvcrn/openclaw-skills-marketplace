<p align="center">
  <h1 align="center">privacy-mask</h1>
  <p align="center">
    <strong>Detect and redact sensitive information in images — 100% local, 100% offline.</strong>
  </p>
  <p align="center">
    <a href="https://github.com/fullstackcrew-alpha/privacy-mask/actions/workflows/ci.yml"><img src="https://github.com/fullstackcrew-alpha/privacy-mask/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://pypi.org/project/privacy-mask/"><img src="https://img.shields.io/pypi/v/privacy-mask" alt="PyPI version"></a>
    <a href="https://pypi.org/project/privacy-mask/"><img src="https://img.shields.io/pypi/pyversions/privacy-mask" alt="Python 3.10+"></a>
    <a href="https://github.com/fullstackcrew-alpha/privacy-mask/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  </p>
</p>

> **Your images never leave your machine.** privacy-mask intercepts screenshots before they are sent to AI services, automatically detecting and masking phone numbers, ID cards, API keys, and 40+ other sensitive patterns.

**[🇨🇳 中文文档 / Chinese Documentation](README.zh.md)**

---

## Demo

<p align="center">
  <img src="https://raw.githubusercontent.com/fullstackcrew-alpha/privacy-mask/main/examples/demo.gif" alt="privacy-mask demo" width="700">
</p>

---

## Before / After

| Original | Masked |
|----------|--------|
| ![before](https://raw.githubusercontent.com/fullstackcrew-alpha/privacy-mask/main/examples/demo_form_before.png) | ![after](https://raw.githubusercontent.com/fullstackcrew-alpha/privacy-mask/main/examples/demo_before_after_form.png) |
| ![before](https://raw.githubusercontent.com/fullstackcrew-alpha/privacy-mask/main/examples/demo_terminal_before.png) | ![after](https://raw.githubusercontent.com/fullstackcrew-alpha/privacy-mask/main/examples/demo_terminal_masked.png) |
| ![before](https://raw.githubusercontent.com/fullstackcrew-alpha/privacy-mask/main/examples/demo_chat_before.png) | ![after](https://raw.githubusercontent.com/fullstackcrew-alpha/privacy-mask/main/examples/demo_chat_masked.png) |

---

## Why?

When you share screenshots with AI assistants, you might accidentally expose:

- **Personal IDs** — national ID numbers, passports, social security numbers
- **Phone numbers & emails** — yours or your users'
- **API keys & tokens** — AWS, GitHub, Stripe, database credentials
- **Financial data** — bank card numbers, IBAN codes

Cloud-based redaction services require uploading your images — defeating the purpose. **privacy-mask processes everything locally before any data leaves your machine**, making it the only approach that truly protects your privacy.

This matters for compliance too: **GDPR**, **HIPAA**, and other regulations require that sensitive data be protected at the point of origin.

---

## Quick Start

```bash
# Install (regex engine only)
pip install privacy-mask

# Install with NER engine (recommended)
pip install privacy-mask[ner]

# Mask a screenshot
privacy-mask mask screenshot.png

# One-time setup: auto-mask all images before AI upload
privacy-mask install
```

That's it. After `privacy-mask install`, every image you share with your AI coding assistant is automatically masked before upload.

```bash
# Toggle masking on/off
privacy-mask off       # Temporarily disable
privacy-mask on        # Re-enable
privacy-mask status    # Check current state
```

---

## Agent Integration

privacy-mask follows the [agentskills.io](https://agentskills.io) SKILL.md standard and works with **20+ AI coding tools** that run locally:

| Platform | How it works |
|----------|-------------|
| **Claude Code** | `pip install privacy-mask && privacy-mask install` or `/plugin marketplace add fullstackcrew-alpha/privacy-mask` then `/plugin install privacy-mask@privacy-mask` |
| **Cursor** | SKILL.md auto-detected in project |
| **VS Code Copilot** | SKILL.md auto-detected in project |
| **Gemini CLI** | SKILL.md auto-detected in project |
| **OpenHands** | CLI available via shell |
| **Goose** | SKILL.md auto-detected |
| **Roo Code** | SKILL.md auto-detected |
| **aider** | CLI available via shell |
| **Cline** | SKILL.md auto-detected |
| **Windsurf** | SKILL.md auto-detected |
| **OpenClaw** | `clawhub install privacy-mask` or SKILL.md auto-detected |

> **Note:** privacy-mask only works with **local agents**. Web-based AI (ChatGPT Web, Gemini Web) uploads images to cloud servers before processing — local masking cannot help there. This tool is designed for agents that run on your machine.

---

## Detection Engines

privacy-mask supports two detection engines, switchable via config or CLI:

| Engine | Description | Install |
|--------|-------------|---------|
| **NER** (default) | Zero-shot Named Entity Recognition via [GLiNER](https://github.com/urchade/GLiNER). Detects person names, addresses, organizations, dates of birth, medical conditions, and more — without regex. | `pip install privacy-mask[ner]` |
| **Regex** | 47 hand-tuned regex rules covering 15+ countries. No extra dependencies. | `pip install privacy-mask` |

```bash
# Default: NER engine (requires privacy-mask[ner])
privacy-mask mask screenshot.png

# Switch to regex engine
privacy-mask mask screenshot.png --detection-engine regex
```

You can also set the default engine in `config.json`:

```json
{
  "detection": { "engine": "ner" }
}
```

---

## What It Detects

### NER Engine

Configurable entity types (zero-shot, no training needed):
- Person names, street addresses, organization names
- Dates of birth, medical conditions, license plate numbers
- Custom entity types via `config.json` `ner.entity_types`

### Regex Engine

**47 regex rules** covering **15+ countries**:

| Category | Rules |
|----------|-------|
| **IDs** | Chinese ID card & passport, HK/TW ID, US SSN, UK NINO, Canadian SIN, Indian Aadhaar & PAN, Korean RRN, Singapore NRIC, Malaysian IC |
| **Phone** | Chinese mobile & landline, US phone, international (+prefix) |
| **Financial** | Bank card (UnionPay/Visa/MC), Amex, IBAN, SWIFT/BIC |
| **Developer Keys** | AWS access key, GitHub token, Slack token, Google API key, Stripe key, JWT, database connection strings, generic API keys, SSH/PEM private keys |
| **Crypto** | Bitcoin address (legacy + bech32), Ethereum address |
| **Other** | Email, birthday, IPv4/IPv6, MAC address, UUID, Chinese license plate, passport MRZ, URL auth tokens, WeChat/QQ IDs |

---

## How It Works

<p align="center">
  <img src="https://raw.githubusercontent.com/fullstackcrew-alpha/privacy-mask/main/examples/architecture.svg" alt="Architecture" width="700">
</p>

1. **OCR** — Dual-engine: Tesseract + RapidOCR extract text with bounding boxes. Multi-strategy preprocessing (grayscale, binarization, contrast enhancement) with confidence-based merge for maximum accuracy.

2. **Line Grouping** — OCR results are grouped into logical text lines using vertical overlap analysis.

3. **Detect** — Switchable engine:
   - **NER** (default) — GLiNER zero-shot NER identifies entities (names, addresses, etc.) without regex
   - **Regex** — 47 compiled regex rules scan for structured patterns (IDs, phone numbers, API keys)

4. **Mask** — Matched regions are blurred (default) or filled with solid color. Output is saved as a new file or overwrites the original.

---

## CLI Usage

```bash
# Basic: mask → screenshot_masked.png
privacy-mask mask screenshot.png

# Overwrite original
privacy-mask mask screenshot.png --in-place

# Detection only, no masking
privacy-mask mask screenshot.png --dry-run

# Black fill instead of blur
privacy-mask mask screenshot.png --method fill

# Choose OCR engine (tesseract, rapidocr, or combined)
privacy-mask mask screenshot.png --engine tesseract

# Choose detection engine (ner or regex)
privacy-mask mask screenshot.png --detection-engine regex

# Custom config
privacy-mask mask screenshot.png --config my_rules.json

# Output path
privacy-mask mask screenshot.png -o /tmp/safe.png
```

Output is JSON:
```json
{
  "status": "success",
  "input": "screenshot.png",
  "output": "screenshot_masked.png",
  "detections": [
    {"label": "PHONE_CN", "text": "***", "bbox": [10, 20, 100, 30]},
    {"label": "EMAIL", "text": "***", "bbox": [10, 50, 200, 30]}
  ],
  "summary": "Masked 2 regions: 1 PHONE_CN, 1 EMAIL"
}
```

---

## Configuration

Rules are defined in `config.json`. You can pass a custom config:

```bash
privacy-mask mask image.png --config my_config.json
```

Each rule has a `name`, `pattern` (regex), and optional `flags`. Example:

```json
{
  "rules": [
    {
      "name": "MY_CUSTOM_ID",
      "pattern": "CUSTOM-\\d{8}",
      "flags": ["IGNORECASE"]
    }
  ]
}
```

See the [bundled config.json](mask_engine/data/config.json) for all 47 rules.

---

## Requirements

- **Python 3.10+**
- **Tesseract OCR**
  - macOS: `brew install tesseract`
  - Ubuntu: `sudo apt install tesseract-ocr`
  - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

MIT

