---
name: pdf-extract
description: "Extract text from PDF files for LLM processing"
---

# PDF Extract

Extract text from PDF files for LLM processing. Uses `pdftotext` from the poppler-utils package to convert PDF documents into plain text.

## Commands

```bash
# Extract all text from a PDF
pdf-extract "document.pdf"

# Extract text from specific pages
pdf-extract "document.pdf" --pages 1-5
```

## Install

```bash
sudo dnf install poppler-utils
```
