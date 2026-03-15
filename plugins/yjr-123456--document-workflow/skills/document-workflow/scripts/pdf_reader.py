#!/usr/bin/env python3
"""Extract text from PDF files using PyMuPDF."""

import argparse
import io
import json
import os
import sys
import fitz  # PyMuPDF


def extract_pdf(pdf_path: str, start: int = 1, end: int = None, output: str = None) -> dict:
    """Extract text from PDF with page range support."""
    if not os.path.exists(pdf_path):
        return {"error": f"File not found: {pdf_path}"}
    
    doc = fitz.open(pdf_path)
    total = len(doc)
    end = min(end or total, total)
    start = max(1, start)
    
    result = {
        "filename": os.path.basename(pdf_path),
        "total_pages": total,
        "extracted_pages": f"{start}-{end}",
        "page_count": end - start + 1,
        "metadata": {k: doc.metadata.get(k, "") for k in ["title", "author", "subject", "creator"]},
        "pages": [{"page": i+1, "text": doc[i].get_text().strip()} for i in range(start-1, end)]
    }
    doc.close()
    
    if output:
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Wrote {end-start+1} pages ({start}-{end}) to: {output}")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("pdf", help="PDF file path")
    parser.add_argument("--start", type=int, default=1, help="Start page (1-indexed)")
    parser.add_argument("--end", type=int, help="End page")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()
    
    result = extract_pdf(args.pdf, args.start, args.end, args.output)
    if not args.output:
        # Use UTF-8 for Windows console compatibility
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
