# UniDoc Document Parser Skill

A ClawHub skill for parsing documents using the UniDoc API service. Converts various document formats (PDF, DOC, DOCX, images) to Markdown or JSON with support for both synchronous and asynchronous processing modes.

## Features

- **Multiple Format Support**: Parse PDF, DOC, DOCX, PNG, JPG, and more
- **Output Formats**: Convert to Markdown (`.md`) or JSON (`.json`)
- **Dual Processing Modes**:
  - Synchronous mode for immediate results
  - Asynchronous mode for large files with status polling
- **Cloud-Based**: Leverages UniDoc API for robust parsing
- **Organized Output**: Creates per-document output directories

## Installation

### Prerequisites

- Python 3.7+
- `requests` library
- Network connectivity to UniDoc API

### Install Dependencies

```bash
pip install requests
```

## Quick Start

### Basic Usage (Sync Mode)

```bash
python scripts/unidoc_parse.py path/to/document.pdf --format md
```

### Asynchronous Mode

```bash
python scripts/unidoc_parse.py path/to/document.docx --format json --mode async
```

### Custom Output Directory

```bash
python scripts/unidoc_parse.py path/to/file.pdf --output ./my-output
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--format` | `md` | Output format: `md` or `json` |
| `--mode` | `sync` | Processing mode: `sync` or `async` |
| `--func` | `unisound` | Conversion method/algorithm |
| `--output` | `./unidoc-output` | Output directory path |
| `--uid` | Auto-generated | Custom user ID |

## Output Structure

```
unidoc-output/
└── document_name/
    ├── output.md       # or output.json
    └── metadata.json   # (future: processing metadata)
```

## API Endpoints

- **Sync Upload**: `http://unidoc.uat.hivoice.cn/syncUploadFile`
- **Async Upload**: `http://unidoc.uat.hivoice.cn/asyncUploadFile`
- **Export**: `http://unidoc.uat.hivoice.cn/exportFile`
- **Status**: `http://unidoc.uat.hivoice.cn/getFileStatus`

## Examples

### Convert PDF to Markdown

```bash
python scripts/unidoc_parse.py report.pdf --format md
```

### Convert DOCX to JSON (Async)

```bash
python scripts/unidoc_parse.py document.docx --format json --mode async
```

### Parse Image

```bash
python scripts/unidoc_parse.py screenshot.png --format md
```

## Limitations

- Requires active internet connection
- Dependent on UniDoc API availability
- File size limits determined by API service
- Rate limiting may apply based on API configuration

## Troubleshooting

See `references/unidoc-notes.md` for:
- API error codes
- Network connectivity issues
- Status polling behavior
- Common problems and solutions

## License

MIT-0

## Author

云知声智能科技股份有限公司 (Unisound Intelligence Technology Co., Ltd.)

## See Also

- [UniDoc API Documentation](http://unidoc.uat.hivoice.cn)
- Original implementation: `api_test_demo.py`
