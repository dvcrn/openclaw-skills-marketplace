# HaS Text CLI — Requirements and Design Document

## 1. Project Overview

`has_text` is the CLI tool for the HaS (Hide and Seek) privacy model. It wraps 6 atomic model capabilities and 5 tool capabilities into **3 user-facing commands**, providing a complete "anonymize → restore" pipeline.

It serves as the technical foundation for the upcoming OpenClaw HaS Plugin and HaS Skills.

### Relationship with Upstream and Downstream

```
has_text_model.gguf (0.6B Qwen3)     ← on-device model
        ↕ llama-server (OpenAI API)
    has_text CLI                      ← this project (current layer)
        ↕
  OpenClaw HaS Skills / Plugin       ← future integration layer
        ↕
    6 major use cases                 ← see has_scenarios.md
```

---

## 2. Design Principles

| Principle | Description |
|-----------|-------------|
| **No exposed atomic capabilities** | Users do not need to understand the internal NER, Hide_with, Hide_without, Pair, Split, Seek model capabilities or Tool-Pair, Tool-Seek tool capabilities — they only use the `hide`, `seek`, and `scan` commands |
| **Pipeline-friendly** | Supports `--text`, `--file`, and stdin input; JSON output is suitable for script composition |
| **Automatic chunking** | Long text is automatically chunked by token count (preserving sentence integrity), with cross-chunk mapping accumulation via the `hide_with` mechanism, transparent to the user |
| **Model + tool dual layer** | Each step prioritizes deterministic tools (fast); falls back to model inference (accurate) when self-check fails |
| **Fully self-contained** | All code (including Tool-Pair algorithm, language detection) is built into the `has_text/` directory with no external code dependencies |

---

## 3. Command Design

### 3.1 `hide` — Anonymize

Replaces sensitive entities in text with anonymous tags, outputting anonymized text + mapping table.

**Input**:
- Text (`--text` / `--file` / stdin)
- Entity types (`--types`, JSON array)
- Optional: existing mapping table (`--mapping`, for incremental anonymization)

**Output**:
```json
{
  "text": "anonymized text...",
  "mapping": {
    "<person name[1].personal.name>": ["John"],
    "<address[1].city.district>": ["Brooklyn, New York"]
  }
}
```

**Internal workflow (Phase 1 orchestration, invisible to users)**:
```
NER → entities found?
  ├─ has mapping → Model-Hide_with (maintain cross-text/cross-chunk consistency)
  └─ no mapping → Model-Hide_without (first-time anonymization)
→ Tool-Pair (algorithmic mapping extraction)
→ contains composite tags? → Model-Split + Tool-Mapping-Merge
→ mapping self-check
  ├─ pass → output
  └─ fail → Model-Pair (fallback mapping extraction) → output
```

### 3.2 `seek` — Restore

Restores text containing anonymous tags to its original form. Full restoration, no selective restoration.

**Input**:
- Anonymized text (`--text` / `--file` / stdin)
- Mapping table (`--mapping`, required)

**Output**:
```json
{
  "text": "restored original text..."
}
```

**Internal workflow (Phase 3 orchestration, invisible to users)**:
```
Does text contain tags?
  ├─ no → output directly
  └─ yes → language detection
       ├─ same language → Tool-Seek (deterministic replacement) → self-check
       │                   └─ fail → Model-Seek (fallback)
       └─ different language → Model-Seek (cross-language restoration)
```

### 3.3 `scan` — Scan

Identifies sensitive entities in text (identification only, no anonymization).

**Input**:
- Text (`--text` / `--file` / stdin)
- Entity types (`--types`, JSON array)

**Output**:
```json
{
  "entities": {
    "person name": ["John", "Jane"],
    "address": ["Brooklyn, New York"],
    "phone number": []
  }
}
```

**Internal workflow**: Calls Model-NER only.

---

## 4. Recursive Chunking

### 4.1 Why Chunking Is Needed

The model's recommended deployment context is 8192 tokens. A single `hide` call needs to fit:
- Two conversation turns (NER question + NER result + Hide instruction + Hide output)
- Mapping table (carried during `hide_with`)

Measured token budgets (Qwen3 tokenizer):

| Scenario | Available text tokens | ≈ Chinese characters |
|----------|----------------------|---------------------|
| hide_without (first chunk) | ~3400 | ~5000 |
| hide_with (10 mapping entries) | ~3280 | ~4900 |
| hide_with (55 mapping entries) | ~3100 | ~4600 |

### 4.2 Chunking Strategy

- **Default threshold**: 3000 tokens/chunk (~400 tokens safety margin)
- **Split rule**: Find the nearest sentence boundary near the threshold (`。！？\n`) and cut back, preserving sentence integrity
- **Fallback order**: Paragraph break > Period > Semicolon > Comma > Hard cut

### 4.3 Cross-Chunk Consistency

Recursive chunking reuses the `hide_with` multi-turn conversation mechanism:

```
Chunk 1 → hide_without → anonymized_text₁ + mapping₁
Chunk 2 → hide_with(mapping₁) → anonymized_text₂ + mapping₂
Chunk 3 → hide_with(mapping₂) → anonymized_text₃ + mapping₃
...
Final = concatenate all anonymized texts + mapping_N
```

When the same entity appears in different chunks, `hide_with` ensures consistent tag numbering via the mapping table.

### 4.4 Key Metrics

| Metric | Measured Value |
|--------|---------------|
| Chinese token ratio | 1.86 chars/token (0.54 tokens/char) |
| Tag token expansion | Original entity ~2 tok → Tag ~10-13 tok (~5-6x) |
| Chat format overhead | ~8 tokens |
| hide_without fixed overhead | ~57 tokens |
| Average mapping entry size | ~18 tokens/entry |

---

## 5. Internal Architecture

### 5.1 Model Capabilities vs Tool Capabilities

| Component | Type | Purpose |
|-----------|:----:|---------|
| Model-NER | 🔵 Model | Entity recognition |
| Model-Hide | 🔵 Model | First-time anonymization (no mapping) |
| Model-Hide_with | 🔵 Model | Incremental anonymization (with mapping) |
| Model-Split | 🔵 Model | Split composite tags |
| Model-Pair | 🔵 Model | Mapping extraction (fallback) |
| Model-Seek | 🔵 Model | Cross-language restoration (fallback) |
| Tool-Pair | 🟢 Tool | Diff-based algorithmic mapping extraction (`pair.py`) |
| Tool-Seek | 🟢 Tool | Deterministic tag replacement |
| Tool-Language Detection | 🟢 Tool | Language detection |
| Tool-Tag Extraction | 🟢 Tool | Composite tag detection |
| Tool-Mapping Merge | 🟢 Tool | Mapping table merge |

### 5.2 File Structure

```
scripts/has_text/
├── __init__.py          # Package init
├── __main__.py          # python -m has_text entry point
├── has_text.py          # CLI argparse dispatcher
├── client.py            # llama-server HTTP client (chat + tokenize)
├── prompts.py           # 6 prompt template builders (character-exact match with training templates)
├── chunker.py           # Token-aware text chunker
├── mapping.py           # Mapping utilities (merge, I/O, tag detection, JSON tolerance)
├── pair.py              # Tool-Pair: diff-based mapping extraction (self-contained)
├── lang.py              # Language detection: Unicode script heuristics (self-contained)
└── commands/
    ├── __init__.py
    ├── scan.py          # scan command
    ├── hide.py          # hide command (Phase 1 full workflow orchestration)
    └── seek.py          # seek command (Phase 3 full workflow orchestration)
```

### 5.3 Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| `requests` | Python package | HTTP calls to llama-server |
| `llama-server` | External service | Loads `has_text_model.gguf` for inference |

> Note: Tool-Pair (`pair.py`) and language detection (`lang.py`) are built-in with no external code dependencies.
