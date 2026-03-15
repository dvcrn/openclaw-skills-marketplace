#!/usr/bin/env python3
"""
One-Click Paper Research Workflow
Usage:
    python -m skills.document-workflow.scripts.research --query "world model autonomous driving" --output "./papers"
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


SCRIPT_DIR = Path(__file__).parent


def run_script(script: str, args: list, capture: bool = True) -> str:
    """Run a script and return output."""
    cmd = [sys.executable, "-m", f"skills.document-workflow.scripts.{script}"] + args
    result = subprocess.run(cmd, capture_output=capture, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0 and capture:
        print(f"[ERROR] {script}: {result.stderr[:200]}", file=sys.stderr)
    return result.stdout if capture else ""


def log(msg: str, level: str = "INFO"):
    print(f"[research:{level}] {msg}")


def main():
    parser = argparse.ArgumentParser(description="One-click paper research workflow")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--output", default="./papers", help="Output directory")
    parser.add_argument("--max_papers", type=int, default=3, help="Max papers to process")
    parser.add_argument("--year_from", type=int, default=2024, help="Filter from year")
    parser.add_argument("--download", action="store_true", help="Download PDFs")
    parser.add_argument("--extract", action="store_true", help="Extract text")
    parser.add_argument("--chunk_size", type=int, default=10, help="Pages per chunk")
    parser.add_argument("--require_pdf", action="store_true", default=True, help="Only papers with PDF URLs")
    args = parser.parse_args()

    # Optimize query for better results
    optimized_query = args.query
    if "survey" in args.query.lower() or "review" in args.query.lower():
        # Add "paper" to avoid confusion with questionnaires
        optimized_query = args.query + " paper"

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Search (Tavily first for better PDF coverage)
    log(f"Searching for: '{optimized_query}' (Tavily priority)")
    search_output = run_script("search_papers", [
        "--query", optimized_query,
        "--max_results", str(args.max_papers * 2 if args.require_pdf else args.max_papers),  # Get more if filtering
        "--year_from", str(args.year_from),
        "--use_tavily"  # Explicitly use Tavily first
    ])
    
    papers = json.loads(search_output) if search_output else []
    papers_with_pdf = [p for p in papers if p.get("pdf_url")]
    
    log(f"Found {len(papers)} papers, {len(papers_with_pdf)} with PDF URLs")
    
    if not papers_with_pdf:
        log("No papers with PDF URLs found", "WARNING")
        # Save search results anyway
        with open(output_dir / "search_results.json", 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        return
    
    # Step 2: Download (if requested)
    if args.download:
        log("Downloading papers...")
        for i, paper in enumerate(papers_with_pdf):
            paper_dir = output_dir / f"paper_{i+1}"
            paper_dir.mkdir(exist_ok=True)
            
            # Save metadata
            with open(paper_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(paper, f, ensure_ascii=False, indent=2)
            
            # Download
            json_input = json.dumps(paper)
            download_output = run_script("download_paper", [
                "--json_input", json_input,
                "--papers_dir", str(paper_dir),
                "--theme", "pdf"
            ], capture=False)
    
    # Step 3: Extract (if requested)
    if args.extract:
        log("Extracting text...")
        import fitz
        
        for i, paper in enumerate(papers_with_pdf):
            paper_dir = output_dir / f"paper_{i+1}"
            pdf_dir = paper_dir / "pdf"
            
            # Find PDF file
            pdf_file = None
            if pdf_dir.exists():
                for f in pdf_dir.glob("*.pdf"):
                    pdf_file = f
                    break
            
            if pdf_file and pdf_file.exists():
                # Get total pages
                doc = fitz.open(str(pdf_file))
                total_pages = len(doc)
                doc.close()
                
                log(f"Extracting {paper.get('title', 'paper')[:50]}... ({total_pages} pages)")
                
                # Extract in chunks
                for start in range(1, total_pages + 1, args.chunk_size):
                    end = min(start + args.chunk_size - 1, total_pages)
                    chunk_file = paper_dir / f"chunk_{start}_{end}.json"
                    
                    run_script("pdf_reader", [
                        str(pdf_file),
                        "--start", str(start),
                        "--end", str(end),
                        "--output", str(chunk_file)
                    ])
            else:
                log(f"PDF not found for paper {i+1}", "WARNING")
    
    # Summary
    log(f"Done! Results saved to: {output_dir}")
    log(f"  - Search results: {output_dir / 'search_results.json'}")
    if args.download:
        log(f"  - PDFs: {output_dir / 'paper_X' / 'pdf'}")
    if args.extract:
        log(f"  - Extracted text: {output_dir / 'paper_X' / 'chunk_*.json'}")


if __name__ == "__main__":
    main()
