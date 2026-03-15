---
name: archive-extractor
description: "archive-extractor"
---

---
name: smart-archive-extractor
description: |
  A robust tool for recursively extracting various archive formats (zip, tar, tar.gz, rar, 7z, gz). 
  Use this skill when the user wants to "unzip", "unpack", or "extract" files, especially when dealing with nested archives, bulk extraction, or when operation stability (idempotency) is required.
  It automatically handles dependency installation (patool) and prevents redundant extractions via marker files.

version: 1.0.1
---

# Smart Archive Extractor

This skill provides a reliable way to recursively extract archives. It supports complex logic like avoiding re-extraction of already processed files and handling nested archives (e.g., a zip containing a tar.gz).

## Capabilities

- **Recursive Extraction**: Automatically detects archives inside extracted folders and extracts them (up to 20 levels deep).
- **Idempotency**: Skips extraction if a success marker (`.extracted_success`) is found, unless forced.
- **Smart Format Support**: Handles standard formats (`.zip`, `.tar`) and complex ones (`.rar`, `.7z`) by auto-installing dependencies.
- **Gzip Handling**: Special handling for single `.gz` files (e.g., `data.txt.gz` -> `data.txt/data.txt`).

## Usage

Run the python script located in `scripts/extract.py`.

### Command Syntax

```
python3 scripts/extract.py <PATH> [OPTIONS]
```

### Arguments

- `<PATH>`: The target file or directory pattern to process.
  - Examples: `data.zip`, `downloads/`, `"*.tar.gz"` (glob patterns supported).

### Options

- `-f, --force`: Force re-extraction even if the success marker exists. Use this if the user says "retry", "overwrite", or "force".
- `-d, --dest <DIR>`: Specify a root output directory. If omitted, archives are extracted alongside the source files.

## Examples

### 1. Basic Extraction
Extract a single file or a directory of archives.

```bash
python3 scripts/extract.py downloads/archive.zip
# OR for a directory
python3 scripts/extract.py downloads/
```

### 2. Force Re-extraction
Use when the user suspects corruption or explicitly requests a clean start.

```bash
python3 scripts/extract.py downloads/archive.zip -f
```

### 3. Extract to Specific Folder
Use when the user wants to organize output in a separate location.

```bash
python3 scripts/extract.py downloads/ -d ./extracted_output
```

## Error Handling

- If `patool` is missing, the script will attempt to `pip install` it automatically.
- If an archive is corrupt, it will be skipped, and the error will be logged without crashing the entire process.
- If recursion depth exceeds 20, it will stop digging deeper to prevent infinite loops.
