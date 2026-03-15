---
name: bailian-studio
description: "Call Aliyun Bailian via DashScope; OCR text extraction first."
---

# Bailian Studio

First feature: OCR text extraction via DashScope.

## Requirements

- Python 3
- `dashscope` (>=1.22.2)
- `oss2`

Install:
```bash
pip install dashscope oss2
```

## Config

**API Key (priority order):**
1. `DASHSCOPE_API_KEY` env
2. `secrets/bailian.env`

**OSS (priority order):**
1. `OSS_ACCESS_KEY`, `OSS_SECRET_KEY`, `OSS_BUCKET`, `OSS_ENDPOINT`, `OSS_REGION` env
2. `secrets/bailian.env`

Example `secrets/bailian.env`:
```env
DASHSCOPE_API_KEY=sk-xxx
OSS_ACCESS_KEY=ak-xxx
OSS_SECRET_KEY=sk-xxx
OSS_BUCKET=your-bucket
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
OSS_REGION=cn-beijing
```

**Defaults:**
- Region/base URL: Beijing (`https://dashscope.aliyuncs.com/api/v1`)

**Optional overrides:**
- `DASHSCOPE_BASE_URL`

## Usage

### OCR (text)

From local image (uploads to OSS):
```bash
python3 {baseDir}/scripts/ocr_text.py --image /path/to.png
```

From URL:
```bash
python3 {baseDir}/scripts/ocr_text.py --url https://example.com/image.png
```
