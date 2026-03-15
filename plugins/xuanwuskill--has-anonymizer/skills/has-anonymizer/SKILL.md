---
name: has-anonymizer
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

## Prerequisites: llama-server (Auto-managed, Local-Only)

HaS depends on llama-server to load the privacy model and provide inference. `has-text` auto-reuses or auto-starts a **local loopback** `llama-server` when a command needs the model. Non-loopback server URLs are rejected to ensure all data stays on-device. Same-language `seek` avoids starting the server when deterministic restoration succeeds. **Only stop a server if this task started it. Never terminate a pre-existing server that you merely detected on the same port.**

The model file is downloaded via the OpenClaw install mechanism to `~/.openclaw/tools/has-anonymizer/models/has_text_model.gguf` (639 MB, Q8_0 quantized). Runtime memory usage is approximately 1.4 GB (8K context).

**Platform notes**:
- macOS: OpenClaw can surface bundled install actions for `uv` and `llama.cpp` via Homebrew.
- Linux / WSL: install `uv` and `llama-server` manually first, then use OpenClaw's download install actions for the HaS model files.

**Model download mirrors**: OpenClaw's built-in install metadata currently points at HuggingFace. If that download fails or times out, use these ModelScope mirror URLs as a manual fallback instead of assuming automatic retry:
- Text model: `https://modelscope.cn/models/TencentXuanwu/HaS_Text_0209_0.6B_Q8` → download `has_text_model.gguf` to `~/.openclaw/tools/has-anonymizer/models/`
- Image model: `https://modelscope.cn/models/TencentXuanwu/HaS_Image_0209_FP32` → download `sensitive_seg_best.pt` to `~/.openclaw/tools/has-anonymizer/models/`

**Auto-managed local runtime**:

- Server URL: `http://127.0.0.1:8080` (hardcoded loopback; non-local URLs are rejected)
- Default model path: `~/.openclaw/tools/has-anonymizer/models/has_text_model.gguf`
- Override the auto-start model path with env var `HAS_TEXT_MODEL_PATH=/abs/path/to/has_text_model.gguf`
- Override the parallel request cap with env var `HAS_TEXT_MAX_PARALLEL_REQUESTS` (default 4, max 4)
- Auto-start slot count is workload-aware: `has-text` only starts as many slots as the current command can actually use, capped by `--max-parallel-requests` and a fixed local ceiling of 4
- Auto-start keeps each slot at the full 8K context budget by scaling `-c` with `-np` (`np=1 -> c=8192`, `np=2 -> c=16384`, ..., `np=4 -> c=32768`)
- If a healthy local HaS server is already listening on the requested port, `has-text` reuses it only when it is clearly the HaS model and its `-np`/`-c` combination still preserves the full 8K context per slot; otherwise it starts a new local port instead and only stops the PID it created

**Manual fallback — Start**:

1. Probe the default port (8080): `curl -fsS "http://127.0.0.1:8080/health"`
2. If health is OK, identify the listening PID and inspect its command line:

```bash
pid="$(lsof -tiTCP:8080 -sTCP:LISTEN | head -n 1)"
cmd="$(ps -p "$pid" -o command=)"
```

3. Reuse the existing service **only** if the command line clearly shows both `llama-server` and `has_text_model.gguf`. Health alone is not enough; another model may already be using that port.
4. If the running service is missing, unhealthy, or not the HaS model, leave that process alone and choose another free port (for example `8090`).
5. Decide the slot budget before starting llama-server. Use `1` for serial `hide`-only work; for chunk-parallel `scan`, model-backed `seek`, or batch `hide --dir`, set it to the number of model work items you expect, capped at `--max-parallel-requests` and 4 local slots. Keep `-c = 8192 * parallel` so each slot retains the full 8K context budget.
6. Start llama-server in the background and record the PID you started:

```bash
parallel="${HAS_TEXT_MAX_PARALLEL_REQUESTS:-4}"
[ "$parallel" -gt 4 ] && parallel=4
ctx_size=$((8192 * parallel))
server_pid=""
llama-server \
  --host 127.0.0.1 \
  -m ~/.openclaw/tools/has-anonymizer/models/has_text_model.gguf \
  -ngl 999 \
  -c "$ctx_size" \
  -np "$parallel" \
  -fa on \
  -ctk q8_0 \
  -ctv q8_0 \
  --port 8080 &
server_pid=$!
```

7. Wait for readiness: poll the health endpoint until it returns ok

**After use — Stop**:

If and only if this task set `server_pid`, terminate that PID to free memory:

```bash
if [ -n "${server_pid:-}" ]; then
  kill "$server_pid"
  wait "$server_pid" 2>/dev/null || true
fi
```

Do not kill by port, and do not stop a server that you only reused.

## Usage

```bash
{baseDir}/scripts/has-text.sh [global-options] <command> [options]
```

Global options:

| Option | Description |
|--------|-------------|
| `--pretty` | Pretty-print JSON output |
| `-q, --quiet` | For `hide`/`seek`, output text only without the JSON wrapper. `scan` still returns JSON |

Input methods (common to scan/hide/seek):

| Method | Description |
|--------|-------------|
| `--text '<text>'` | Pass text directly |
| `--file <path>` | Read text from a file |
| stdin | Pipe input, e.g., `cat file \| has-text ...` |

> `--max-chunk-tokens`: Maximum tokens per chunk (default 3000), available for `scan`, `hide`, and model-backed `seek`.
>
> `--max-parallel-requests`: Shared parallel request cap for `scan`, model-backed `seek`, and batch `hide --dir` (default 4, env `HAS_TEXT_MAX_PARALLEL_REQUESTS`). Legacy aliases: `--max-parallel-chunks`, `--max-parallel-files`.

## Command Reference

Directory mode rules for `scan`, `hide`, and `seek`: process only the immediate UTF-8 plaintext files in the target directory, never recurse into subdirectories, skip binary or non-UTF-8 files, and report symlinked files whose realpath escapes the input directory as `symlink_escape`.

### scan (Privacy Scan)

Identifies sensitive entities only, without replacement. Suitable for quick privacy risk assessment of text. Long scans fan out chunk requests in parallel by default and merge them back in original chunk order so the output remains stable. `has-text` only starts llama-server when at least one chunk needs the model.

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--types` | ✅ | Entity types to identify, JSON array format |
| `--dir` | | Batch-scan the immediate plaintext files in a directory (non-recursive) |
| `--max-parallel-requests` | | Maximum scan chunks to run in parallel (default 4, env `HAS_TEXT_MAX_PARALLEL_REQUESTS`). Set to `1` to force serial execution |

```bash
# Scan text for person names and phone numbers
{baseDir}/scripts/has-text.sh scan --types '["person name","phone number"]' --text "John's phone number is 13912345678"

# Scan a file for multiple entity types
{baseDir}/scripts/has-text.sh scan --types '["person name","address","phone number","email","ID number"]' --file /path/to/document.txt

# Batch-scan a directory of plaintext files
{baseDir}/scripts/has-text.sh scan --types '["person name","phone number"]' --dir ./reports/
```

**Output** (JSON): Single-file scan returns `{"entities": ...}`. Directory scan returns `{"results":[...],"count":N,"summary":{...}}` and may include `skipped` / `skipped_count`.

### hide (Privacy Anonymization)

Identifies and replaces sensitive entities with semantic tags, outputting anonymized text + mapping table. `--dir` writes anonymized files plus one mapping JSON per source file. Batch mode treats each file independently; it does not accumulate new mappings across files, and `hide --dir` does not accept `--mapping`. If mapping extraction cannot validate the anonymized output, `hide` fails closed instead of returning an untrusted mapping. Empty files do not start llama-server.

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--types` | ✅ | Entity types to anonymize, JSON array format |
| `--mapping` | Single-file only | Existing mapping dictionary (file path or inline JSON), for incremental anonymization to maintain cross-session consistency |
| `--dir` | | Batch-anonymize the immediate plaintext files in a directory (non-recursive) |
| `--output-dir` | | Batch output directory for anonymized files (default: `anonymized/` under the input directory) |
| `--mapping-dir` | | Batch output directory for per-file mapping JSON files (default: `mappings/` under the output directory) |
| `--max-parallel-requests` | | Maximum files to anonymize in parallel when using `--dir` (default 4, env `HAS_TEXT_MAX_PARALLEL_REQUESTS`) |

```bash
# First-time anonymization
{baseDir}/scripts/has-text.sh --pretty hide --types '["person name","address","phone number"]' --text "John lives in Brooklyn, New York, phone 13912345678"

# Incremental anonymization (carry previous mapping to maintain consistency)
{baseDir}/scripts/has-text.sh hide --types '["person name","address"]' --text "John is going to Boston on a business trip next week" --mapping mapping.json

# Batch-anonymize a directory of plaintext files
{baseDir}/scripts/has-text.sh hide --types '["person name"]' --dir ./docs/ --output-dir ./anonymized/ --mapping-dir ./anonymized/mappings/
```

**Output** (JSON): Single-file hide returns `{"text": "...", "mapping": {...}}`. Directory hide writes anonymized files and per-file mapping JSON files, then returns `{"results":[{"file":"...","output":"...","mapping":"..."}], ...}` plus optional `chunks`, `skipped`, and `skipped_count`.

> 💡 **mapping is the key**: Save the mapping and you can restore. Lose the mapping, and anonymization becomes irreversible.
>
> ⚠️ **Security**: Prefer passing mapping via file path (`--mapping mapping.json`) rather than inline JSON. Inline JSON appears in `ps aux` process listings and shell history, exposing the original sensitive data.

### seek (Privacy Restoration)

Restores anonymized tags to original values using the mapping table. Uses pure string replacement for same-language text (very fast), and automatically switches to model inference for cross-language scenarios. Long model-backed `seek` requests are chunked automatically; each chunk only carries the mapping keys that actually appear in that chunk, and model-backed chunks can run in parallel up to `--max-parallel-requests`. If a model-backed seek chunk still contains anonymized tags after one pass, `seek` retries that chunk once with the same mapping and then fails closed if unresolved tags remain. Same-language files and files without surviving tags do not start llama-server. `--dir` writes the results to `restored/` or `--output-dir`. When restoring a directory produced by `hide --dir`, `seek --dir` uses each file's own mapping JSON under `<input-dir>/mappings/` by default, or the per-file directory specified by `--mapping-dir`. `seek --dir` does not accept a shared `--mapping`.

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--mapping` | Single-file: ✅ | Mapping dictionary (file path or inline JSON) |
| `--dir` | | Batch-restore the immediate plaintext files in a directory (non-recursive) |
| `--mapping-dir` | | Batch mapping directory for per-file mapping JSON files (default: `mappings/` under the input directory) |
| `--output-dir` | | Batch output directory for restored files (default: `restored/` under the input directory) |
| `--max-parallel-requests` | | Maximum model-backed seek chunks to run in parallel (default 4, env `HAS_TEXT_MAX_PARALLEL_REQUESTS`) |

```bash
# Restore anonymized text
{baseDir}/scripts/has-text.sh -q seek --mapping mapping.json --text "<person name[1].personal.name> lives in <address[1].city.name>"

# Restore from file
{baseDir}/scripts/has-text.sh --pretty seek --mapping mapping.json --file anonymized.txt

# Batch-restore a directory produced by hide --dir (uses ./anonymized/mappings/*.mapping.json by default)
{baseDir}/scripts/has-text.sh seek --dir ./anonymized/ --output-dir ./restored/

# Batch-restore with an explicit per-file mapping directory
{baseDir}/scripts/has-text.sh seek --dir ./anonymized/ --mapping-dir ./exported-mappings/ --output-dir ./restored/

```

**Output** (JSON): Single-file seek returns `{"text": ...}`. Directory seek writes restored files and returns `{"results":[{"file":"...","output":"..."}], ...}` plus optional `chunks`, `skipped`, and `skipped_count`.

## Typical Workflow

### Anonymize → Send to Cloud LLM → Restore

1. `hide` to anonymize → obtain anonymized text + mapping
2. Send anonymized text to cloud LLM (no privacy data included)
3. `seek` with mapping to restore the LLM response

> ⚠️ For multi-line text, it is recommended to use file intermediation (hide output → write to file → read), to avoid JSON parsing failures caused by shell variable handling.

---

# Part 2: Image Anonymization (has-image)

Performs pixel-level detection and masking of privacy regions in images. Based on a YOLO11 instance segmentation model, supports 21 privacy categories.

`has-image` loads its YOLO model directly and does **not** require `llama-server`.

## Usage

```bash
{baseDir}/scripts/has-image.sh [global-options] <command> [options]
```

| Option | Description |
|--------|-------------|
| `--model PATH` | Model file path (auto-detected by default, can be set via env var `HAS_IMAGE_MODEL`) |
| `--pretty` | Pretty-print JSON output |

## Privacy Categories (21 Classes)

| ID | Category | Display Name | Group |
|----|----------|--------------|-------|
| 0 | `biometric_face` | Face | Biometric |
| 1 | `biometric_fingerprint` | Fingerprint | Biometric |
| 2 | `biometric_palmprint` | Palmprint | Biometric |
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

`--types` accepts English names, Chinese names, or IDs, comma-separated. Short names are also supported via partial matching (e.g. `face` → `biometric_face`, `fingerprint` → `biometric_fingerprint`). If a short name matches multiple categories, the CLI stops with an ambiguity error and asks for a more specific type.


## Command Reference

Directory mode rules for `scan` and `hide`: process only the immediate files in the target directory, never recurse into subdirectories, and ignore symlinked files whose realpath escapes the input directory.

### scan (Privacy Scan)

Identifies privacy regions only, **does not modify the image**.

```bash
# Scan a single image
{baseDir}/scripts/has-image.sh --pretty scan --image photo.jpg --types face,id_card

# Batch scan a directory
{baseDir}/scripts/has-image.sh --pretty scan --dir ./photos/ --types face,id_card
```

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--image` | Either | Input image path |
| `--dir` | Either | Batch scanning directory |
| `--types` | | Category filter (comma-separated), defaults to all 21 categories |
| `--conf` | | Confidence threshold (default 0.25) |

**Output** (JSON): `{"detections": [{"category": "...", "confidence": 0.95, "bbox": [...], "has_mask": true}], "summary": {"biometric_face": 2}}`

### hide (Privacy Anonymization)

Detects and masks privacy regions, outputs the anonymized image.

```bash
# Mosaic all privacy regions
{baseDir}/scripts/has-image.sh hide --image photo.jpg

# Specify categories, method, and strength
{baseDir}/scripts/has-image.sh hide --image photo.jpg --types face,license_plate --method blur --strength 25

# Batch process a directory
{baseDir}/scripts/has-image.sh hide --dir ./photos/ --output-dir ./masked/
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

### categories

Lists all 21 supported privacy categories with their IDs and Chinese display names.

```bash
{baseDir}/scripts/has-image.sh --pretty categories
```
