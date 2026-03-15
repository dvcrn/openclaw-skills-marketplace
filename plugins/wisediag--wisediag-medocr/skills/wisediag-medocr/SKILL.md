---
name: wisediag-medocr
description: "PDF OCR — Convert PDF to Markdown via WiseDiag cloud API. Supports table recognition, multi-column layouts, and high-accuracy text extraction. Usage: Upload a PDF and say Use WiseOCR to OCR this."
---

# ⚠️ Privacy Warning

**IMPORTANT - READ BEFORE INSTALLING:**

This skill **uploads your files to WiseDiag's cloud servers** for OCR processing.

**Do NOT use with sensitive or confidential documents** unless:
- You trust WiseDiag's data handling policies
- You accept that file contents will be transmitted and processed remotely

**For sensitive documents, use offline/local OCR tools instead.**

---

# WiseOCR Skill (powered by WiseDiag)

A high-accuracy OCR tool that converts PDF files into Markdown format. After processing, the Markdown result is automatically saved to disk — no additional saving is needed.

## Installation

```bash
pip install -r requirements.txt
```

## 🔑 API Key Setup (Required)

**Get your API key:** 👉 [https://console.wisediag.com/apiKeyManage](https://s.wisediag.com/xsu9x0jq)

The API key MUST be set as an environment variable. The script reads it automatically.

```bash
export WISEDIAG_API_KEY=your_api_key
```

## How to Process a PDF (Step-by-Step)

**NEVER call any API or HTTP endpoint directly. ONLY use the script below.**

Step 1: Set the API key (if not already set):

```bash
export WISEDIAG_API_KEY=your_api_key
```

Step 2: Run the script with the input PDF file:

```bash
cd scripts
python3 wiseocr.py -i "/path/to/input_filename.pdf"
```

**IMPORTANT:** If the input file has been copied or renamed (e.g. to a temp path), always pass `-n` with the original filename (without extension) so the output file is named correctly:

```bash
python3 wiseocr.py -i "/tmp/ocr_input.pdf" -n "my_report"
# Output saved to: ~/.openclaw/workspace/WiseOCR/my_report.md
```

The Markdown result is saved to `~/.openclaw/workspace/WiseOCR/{name}.md` automatically. No additional saving is needed.

## Arguments

| Flag | Description |
|------|-------------|
| `-i, --input` | Input PDF file path (required) |
| `-n, --name` | Original filename without extension for output (recommended when input file is renamed/copied) |
| `-o, --output` | Output directory (default: ~/.openclaw/workspace/WiseOCR) |
| `--dpi` | PDF rendering DPI, 72-600 (default: 200) |

## Data Privacy

**What happens to your files:**
1. Files are uploaded to WiseDiag's OCR API
2. Files are processed on WiseDiag servers
3. Processing results are returned to you
4. Files are not permanently stored on WiseDiag servers

**For sensitive documents, use offline/local OCR tools instead.**

## License

MIT
