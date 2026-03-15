#!/usr/bin/env python3
"""
PDF to Text Converter for LLM Researcher

Usage:
    python pdf_to_text.py <pdf_path> [output_path]

Arguments:
    pdf_path    - Path to the PDF file to convert
    output_path - Optional: Path to write output (default: stdout)

Returns:
    Extracted text content (to stdout or file)
"""

import sys
import os
import subprocess

# 【P0 修复】自动检查并安装 PyMuPDF
def ensure_pymupdf():
    """Check if PyMuPDF is installed, install if not"""
    try:
        import fitz
        return fitz
    except ImportError:
        print("Installing PyMuPDF...", file=sys.stderr)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF", "-q"])
            import fitz
            print("PyMuPDF installed successfully.", file=sys.stderr)
            return fitz
        except Exception as e:
            print(f"Failed to install PyMuPDF: {e}", file=sys.stderr)
            sys.exit(2)

fitz = ensure_pymupdf()

def parse_pdf(pdf_path):
    """Parse PDF using PyMuPDF"""
    texts = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            texts.append(page.get_text())
    return "\n".join(texts)

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_text.py <pdf_path> [output_path]", file=sys.stderr)
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        text = parse_pdf(pdf_path)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Text extracted to: {output_path}", file=sys.stderr)
        else:
            print(text)
            
    except Exception as e:
        print(f"Error parsing PDF: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
