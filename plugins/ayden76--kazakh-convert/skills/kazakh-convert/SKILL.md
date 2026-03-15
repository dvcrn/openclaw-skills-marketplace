---
name: kazakh-convert
description: "Kazakh text converter between Cyrillic and Arabic scripts. Supports bidirectional conversion for Kazakh language with special characters (ә, і, ү, ө, ң, ғ, ұ, қ, һ)."
homepage: https://github.com/ayden-omega/kazakh-convert
---

# Kazakh Convert - Kazakh Text Converter

Bidirectional text converter for Kazakh language between Cyrillic and Arabic scripts.

## Features

- ✅ Bidirectional conversion (Cyrillic ↔ Arabic)
- ✅ Full Kazakh special character support
- ✅ Multi-line text processing
- ✅ Automatic syntax correction
- ✅ Windows PowerShell compatible

## Usage

### Cyrillic to Arabic
```bash
python kazConvert.py A "сәлем"
# Output: سالەم
```

### Arabic to Cyrillic
```bash
python kazConvert.py C "قالايسىز؟"
# Output: қалайсыз？
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `A` | Convert to Arabic script |
| `C` | Convert to Cyrillic script |
| `text` | Kazakh text to convert (wrap in quotes) |

## Examples

### Example 1: Greeting
```bash
python kazConvert.py A "Қалың қалай?"
# Output: قالىڭ قالاي؟
```

### Example 2: Self Introduction
```bash
python kazConvert.py C "مەنىڭ اتىم ومەگا"
# Output: Менің атым Омега
```

### Example 3: Multi-line Text
```bash
python kazConvert.py A "Сәлем! Мен қазақпын. Алматыдан келдім."
```

## Windows PowerShell Tips

```powershell
# Method 1: Set environment variable (recommended)
$env:PYTHONIOENCODING="utf-8"; python kazConvert.py A "сәлем"

# Method 2: Change code page
chcp 65001; python kazConvert.py A "сәлем"
```

## Supported Special Characters

Handles all Kazakh-specific letters:
- **Cyrillic:** ә, і, ү, ө, ң, ғ, ұ, қ, һ
- **Arabic:** ە, ى, ۇ, و, ڭ, ع, ۇ, ق, ھ

## Technical Details

- **Character Mapping:** Complete Kazakh alphabet mapping table
- **Syntax Correction:** Automatic handling of special combinations (ю→يۋ, ё→يو, etc.)
- **Multi-line Support:** Batch conversion for paragraphs

## Files

- Script: `kazConvert.py`
- Skill Definition: `SKILL.md`

## Related Skills

- `kazakh-image-gen` - Kazakh traditional pattern AI generation
- `edge-tts` - Kazakh text-to-speech
- `whisper-asr` - Kazakh speech recognition

---

*Author: ayden-omega-agent*
*Version: 1.0.0*
*License: MIT*
