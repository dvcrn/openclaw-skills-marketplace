---
name: has-privacy
description: "HaS (Hide and Seek) on-device text and image anonymization. Text: 8 languages (zh/en/fr/de/es/pt/ja/ko), open-set entity types. Image: 21 privacy categories (face, fingerprint, ID card, passport, license plate, etc.). Use when: (1) anonymizing text before sending to cloud LLMs then restoring the response, (2) anonymizing documents, code, emails, or messages before sharing, (3) scanning text or images for sensitive content, (4) anonymizing logs before handing to ops/support, (5) masking faces/IDs/plates in photos before publishing or sharing."
---

# HaS Privacy

HaS (Hide and Seek) is an on-device privacy protection tool. It provides **text** and **image** anonymization capabilities, both running entirely on-device.

- **Text anonymization** (has-text): Powered by a 0.6B privacy model, supports 8 languages with open-set entity types for anonymization and restoration
- **Image anonymization** (has-image): Powered by a YOLO11 segmentation model, supports pixel-level detection and masking of 21 privacy categories

## Agent Decision Guidelines

- **First introduction**: When users encounter HaS for the first time, demonstrate value through real-world scenarios rather than listing commands. Examples: anonymize contracts/resumes before sharing safely, anonymize before sending to cloud LLMs then restore the response, auto-mask faces/IDs/license plates and 20 other privacy categories in photos before publishing, scan workspace for privacy leak risks, anonymize logs before handing to ops/support
- **Scanning workspace/directory**: Use has-text scan for text files and has-image scan for image files simultaneously, then provide a consolidated report
- **Non-plaintext formats**: has-text only processes plaintext. For PDFs, Word documents, scanned images, etc., first convert to text using other available tools before processing
- **Text in images**: has-image covers most text-in-image scenarios by masking all 21 visual carriers (screens, paper, sticky notes, shipping labels, etc.) as a whole. For further recognition of text content in images, use OCR to extract text first, then run has-text scan for additional detection
- **Never delete original files**: Anonymization operations should output to new files, **never overwrite or delete the original files**. Image anonymization is irreversible; text anonymization can be restored but the original file should still be preserved as backup
- **Proactively inform about configurable options**: At appropriate moments, inform users about the following options and help them configure interactively:
  - **Text**: `--types` can specify any entity type (names, addresses, phone numbers, etc.), not limited to predefined types
  - **Image**: `--types` can specify which categories to mask (e.g., only faces, or only license plates), defaults to all 21 categories
  - **Masking method**: `--method` supports mosaic (default), blur, and solid color fill
  - **Masking strength**: `--strength` adjusts mosaic block size or blur intensity (default 15)
- **Post-scan report**: After scanning a workspace/directory, generate a consolidated privacy check report including:
  - Total files scanned (text and image counts separately)
  - Number and location of each type of sensitive content found
  - Risk level assessment (flag high-sensitivity items such as ID numbers, faces, etc.)
  - Recommended next steps (e.g., "Would you like to anonymize the above files?")
- **Report elapsed time after completion**: After task completion, report processing time to the user so they can perceive on-device inference performance. For single tasks, report individual time (e.g., "On-device inference complete, took 0.3s"); for batch tasks, report a summary (e.g., "Processed 12 texts + 8 images, total time 2.4s"). Do not display technical metrics like tok/s

---

# Part 1: Text Anonymization (has-text)

## Core Concepts

### Three-Level Semantic Tags

Tag format after anonymization: `<EntityType[ID].Category.Attribute>`

- **EntityType**: e.g., person name, address, organization
- **[ID]**: Sequential number for entities of the same type. After coreference resolution, the same entity shares the same number — "CloudGenius Inc.", "CloudGenius", and its Chinese equivalent all map to `<Organization[1].Company.CompanyName>`
- **Category.Attribute**: Semantic subdivision that helps LLMs understand the context of anonymized data (as opposed to `[REDACTED]`)

### Open-Set Types

`--types` is not limited to predefined types — any natural language entity type can be specified (the model was trained on approximately 70,000 types). Parenthetical descriptions can be appended to type names to guide model focus, e.g., `"numeric values (transaction amounts)"`.

### Public/Private Distinction and Multilingual Support

- **Public/private distinction**: Achieved by specifying discriminative types — e.g., use `"personal location"` instead of `"location"` to only anonymize private addresses while preserving public place names (tested and reliably stable). ⚠️ Public/private distinction for person names (`"personal name"` vs `"person name"`) is **unstable** on the current 0.6B model and should not be relied upon
- **Multilingual**: Natively supports 8 languages: Chinese, English, French, German, Spanish, Portuguese, Japanese, and Korean. Cross-lingual text can be processed in mixed form

### Type Selection Guidelines

`--types` is flexibly determined by the Agent based on context:

- **User explicitly specifies** → follow user's request
- **Intent is clear, types are obvious** (e.g., "anonymize this contract" → names + organizations + amounts + addresses) → Agent decides autonomously
- **Intent is ambiguous or involves sensitive decisions** → first use `scan` to scan for as many entity types as possible, show discovered entities to the user for confirmation, then use `hide` to anonymize

## Prerequisites: llama-server (Start/Stop On Demand)

HaS depends on llama-server to load the privacy model and provide inference. **Lifecycle is managed by the Agent: start before use, stop after use**, to avoid long-term memory consumption.

The model file is downloaded via the OpenClaw install mechanism to `~/.openclaw/tools/has-privacy/models/has_text_model.gguf` (639 MB, Q8_0 quantized). Runtime memory usage is approximately 1.4 GB (8K context).

**Model download mirrors**: If the default HuggingFace download fails or times out (common in mainland China), the Agent should automatically retry using these ModelScope mirror URLs:
- Text model: `https://modelscope.cn/models/TencentXuanwu/HaS_Text_0209_0.6B_Q8` → download `has_text_model.gguf` to `~/.openclaw/tools/has-privacy/models/`
- Image model: `https://modelscope.cn/models/TencentXuanwu/HaS_Image_0209_FP32` → download `sensitive_seg_best.pt` to `~/.openclaw/tools/has-privacy/models/`

**Before use — Start**:

1. Check if already running: `curl -s http://127.0.0.1:8080/health`
2. If it returns `{"status":"ok"}`, skip startup and proceed
3. If not running, check if the default port 8080 is occupied: `lsof -i :8080`
4. If the port is occupied, choose another available port (e.g., 8090)
5. Start llama-server in the background:

```bash
llama-server \
  -m ~/.openclaw/tools/has-privacy/models/has_text_model.gguf \
  -ngl 999 \
  -c 8192 \
  -np 1 \
  -fa on \
  -ctk q8_0 \
  -ctv q8_0 \
  --port <port, default 8080> &
```

6. If using a non-8080 port, set an environment variable so the CLI knows: `export HAS_TEXT_SERVER=http://127.0.0.1:<port>`
7. Wait for readiness: poll the health endpoint until it returns ok

**After use — Stop**:

After the task is complete, terminate the llama-server process to free memory.

## Usage

```bash
{baseDir}/scripts/has-text [global-options] <command> [options]
```

Global options:

| Option | Description |
|--------|-------------|
| `--server URL` | llama-server address (default `http://127.0.0.1:8080`, can be set via env var `HAS_TEXT_SERVER`) |
| `--pretty` | Pretty-print JSON output |
| `-q, --quiet` | Output text only, no JSON wrapper |

Input methods (common to scan/hide/seek):

| Method | Description |
|--------|-------------|
| `--text '<text>'` | Pass text directly |
| `--file <path>` | Read text from a file |
| stdin | Pipe input, e.g., `cat file \| has-text ...` |

> `--max-chunk-tokens`: Maximum tokens per chunk (default 3000), available for scan/hide.

## Command Reference

### scan (Privacy Scan)

Identifies sensitive entities only, without replacement. Suitable for quick privacy risk assessment of text.

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--types` | ✅ | Entity types to identify, JSON array format |

```bash
# Scan text for person names and phone numbers
{baseDir}/scripts/has-text scan --types '["person name","phone number"]' --text "John's phone number is 13912345678"

# Scan a file for multiple entity types
{baseDir}/scripts/has-text scan --types '["person name","address","phone number","email","ID number"]' --file /path/to/document.txt
```

**Output** (JSON): Keys are entity types, values are arrays of identified entities.

### hide (Privacy Anonymization)

Identifies and replaces sensitive entities with semantic tags, outputting anonymized text + mapping table.

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--types` | ✅ | Entity types to anonymize, JSON array format |
| `--mapping` | | Existing mapping dictionary (file path or inline JSON), for incremental anonymization to maintain cross-session consistency |

```bash
# First-time anonymization
{baseDir}/scripts/has-text --pretty hide --types '["person name","address","phone number"]' --text "John lives in Brooklyn, New York, phone 13912345678"

# Incremental anonymization (carry previous mapping to maintain consistency)
{baseDir}/scripts/has-text hide --types '["person name","address"]' --text "John is going to Boston on a business trip next week" --mapping '{"<person name[1].personal.name>":["John"]}'
```

**Output** (JSON): `{"text": "anonymized text", "mapping": {"<tag>": ["original value", ...]}}`

> 💡 **mapping is the key**: Save the mapping and you can restore. Lose the mapping, and anonymization becomes irreversible.

### seek (Privacy Restoration)

Restores anonymized tags to original values using the mapping table. Uses pure string replacement for same-language text (very fast), and automatically switches to model inference for cross-language scenarios.

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--mapping` | ✅ | Mapping dictionary (file path or inline JSON) |

```bash
# Restore anonymized text
{baseDir}/scripts/has-text -q seek --mapping '{"<person name[1].personal.name>":["John"],"<address[1].city.name>":["New York"]}' --text "<person name[1].personal.name> lives in <address[1].city.name>"

# Restore from file
{baseDir}/scripts/has-text --pretty seek --mapping mapping.json --file anonymized.txt
```

## Typical Workflow

### Anonymize → Send to Cloud LLM → Restore

1. `hide` to anonymize → obtain anonymized text + mapping
2. Send anonymized text to cloud LLM (no privacy data included)
3. `seek` with mapping to restore the LLM response

> ⚠️ For multi-line text, it is recommended to use file intermediation (hide output → write to file → read), to avoid JSON parsing failures caused by shell variable handling.

---

# Part 2: Image Anonymization (has-image)

Performs pixel-level detection and masking of privacy regions in images. Based on a YOLO11 instance segmentation model, supports 21 privacy categories.

## Usage

```bash
{baseDir}/scripts/has-image [global-options] <command> [options]
```

| Option | Description |
|--------|-------------|
| `--model PATH` | Model file path (auto-detected by default, can be set via env var `HAS_IMAGE_MODEL`) |
| `--pretty` | Pretty-print JSON output |

## Privacy Categories (21 Classes)

| ID | Category | Display Name | Group |
|----|----------|--------------|-------|
| 0 | `face` | Face | Biometric |
| 1 | `fingerprint` | Fingerprint | Biometric |
| 2 | `palmprint` | Palmprint | Biometric |
| 3 | `id_card` | ID Card | ID Document |
| 4 | `hk_macau_permit` | HK/Macau Permit | ID Document |
| 5 | `passport` | Passport | ID Document |
| 6 | `employee_badge` | Employee Badge | ID Document |
| 7 | `license_plate` | License Plate | Transportation |
| 8 | `bank_card` | Bank Card | Financial |
| 9 | `physical_key` | Physical Key | Security |
| 10 | `receipt` | Receipt | Document |
| 11 | `shipping_label` | Shipping Label | Document |
| 12 | `official_seal` | Official Seal | Document |
| 13 | `whiteboard` | Whiteboard | Information Carrier |
| 14 | `sticky_note` | Sticky Note | Information Carrier |
| 15 | `mobile_screen` | Mobile Screen | Information Carrier |
| 16 | `monitor_screen` | Monitor Screen | Information Carrier |
| 17 | `medical_wristband` | Medical Wristband | Medical |
| 18 | `qr_code` | QR Code | Encoding |
| 19 | `barcode` | Barcode | Encoding |
| 20 | `paper` | Paper | Document |

`--types` accepts English names, Chinese names, or IDs, comma-separated.

## Command Reference

### scan (Privacy Scan)

Identifies privacy regions only, **does not modify the image**.

```bash
{baseDir}/scripts/has-image --pretty scan --image photo.jpg --types face,id_card
```

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--image` | ✅ | Input image path |
| `--types` | | Category filter (comma-separated), defaults to all 21 categories |
| `--conf` | | Confidence threshold (default 0.25) |

**Output** (JSON): `{"detections": [{"category": "...", "confidence": 0.95, "bbox": [...], "has_mask": true}], "summary": {"biometric_face": 2}}`

### hide (Privacy Anonymization)

Detects and masks privacy regions, outputs the anonymized image.

```bash
# Mosaic all privacy regions
{baseDir}/scripts/has-image hide --image photo.jpg

# Specify categories, method, and strength
{baseDir}/scripts/has-image hide --image photo.jpg --types face,license_plate --method blur --strength 25

# Batch process a directory
{baseDir}/scripts/has-image hide --dir ./photos/ --output-dir ./masked/
```

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--image` | Either | Input image path |
| `--dir` | Either | Batch processing directory |
| `--output` | | Output image path (defaults to `masked/` subdirectory under the source directory, preserving original filename) |
| `--output-dir` | | Batch output directory (defaults to `masked/` subdirectory under the input directory) |
| `--types` | | Category filter (comma-separated), defaults to all 21 categories |
| `--method` | | Masking method: `mosaic` (pixelation) / `blur` / `fill` (solid color), default `mosaic` |
| `--strength` | | Mosaic block size or blur radius (default 15) |
| `--fill-color` | | Fill color for `fill` method, hex format (default `#000000`) |
| `--conf` | | Confidence threshold (default 0.25) |
