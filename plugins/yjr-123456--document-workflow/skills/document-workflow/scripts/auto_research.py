#!/usr/bin/env python3
"""
Auto Paper Research - Automated paper search, download, extract and summarize
Usage:
    python auto_research.py --query "World Models" --papers 3
    python auto_research.py --arxiv-id "1803.10122" --extract --summarize
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

# Configuration
DEFAULT_OUTPUT = Path("papers")
CHUNK_SIZE = 5

SCHEMA = {
    "paper_title": "string",
    "authors": ["string"],
    "source": "string",
    "task_definition": {
        "domain": "string",
        "task": "string",
        "problem_statement": "string",
        "key_contributions": ["string"]
    },
    "experiments": {
        "datasets": ["string"],
        "baselines": ["string"],
        "metrics": [{"name": "string", "description": "string"}],
        "results": [{"setting": "string", "metric": "string", "proposed_method": "string", "best_baseline": "string", "best_baseline_name": "string"}],
        "key_findings": ["string"]
    }
}


def log(msg, level="INFO"):
    print(f"[auto_research:{level}] {msg}")


def run_command(cmd, capture=True):
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0 and capture:
        log(f"Warning: {result.stderr[:100]}")
    return result.stdout if capture else ""


def get_pdf_reader_path():
    return Path(__file__).parent / "pdf_reader.py"


def search_arxiv(query, max_results=5):
    log(f"Searching arXiv for: '{query}'")
    url = f"http://export.arxiv.org/api/query?search_query=all:{query.replace(' ', '+')}&max_results={max_results}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read().decode('utf-8')
    except Exception as e:
        log(f"arXiv API failed: {e}", "ERROR")
        return []
    
    papers = []
    for entry in re.findall(r'<entry>(.*?)</entry>', data, re.DOTALL):
        arxiv_id = re.search(r'<id>(.*?)</id>', entry)
        title = re.search(r'<title>(.*?)</title>', entry)
        authors = re.findall(r'<name>(.*?)</name>', entry)
        
        if arxiv_id:
            papers.append({
                "arxiv_id": arxiv_id.group(1).split('/')[-1],
                "title": title.group(1).strip().replace('\n', ' ') if title else "Unknown",
                "authors": [a.strip() for a in authors],
            })
    
    return papers


def download_pdf(arxiv_id, output_dir):
    log(f"Downloading {arxiv_id}...")
    pdf_path = output_dir / "paper.pdf"
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    
    for attempt in range(3):
        cmd = f'powershell -Command "Invoke-WebRequest -Uri \'{url}\' -OutFile \'{pdf_path}\'"'
        run_command(cmd)
        if pdf_path.exists() and pdf_path.stat().st_size > 10000:
            log(f"Downloaded: {pdf_path} ({pdf_path.stat().st_size / 1024 / 1024:.1f}MB)")
            return pdf_path
        log(f"Retry {attempt + 1}/3...")
    
    log(f"Failed to download {arxiv_id}", "ERROR")
    return None


def get_page_count(pdf_path):
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pages = len(doc)
        doc.close()
        return pages
    except:
        return 0


def extract_all_chunks(pdf_path, output_dir):
    log("Extracting paper in chunks...")
    total_pages = get_page_count(pdf_path)
    if total_pages == 0:
        log("Could not determine page count", "ERROR")
        return []
    
    log(f"Total pages: {total_pages}")
    chunks = []
    
    for start in range(1, total_pages + 1, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE - 1, total_pages)
        chunk_file = output_dir / f"chunk_{start}-{end}.json"
        
        pdf_reader = get_pdf_reader_path()
        cmd = f'python "{pdf_reader}" "{pdf_path}" --start {start} --end {end} --output "{chunk_file}"'
        run_command(cmd)
        
        if chunk_file.exists():
            chunks.append(chunk_file)
            log(f"  Extracted pages {start}-{end}")
    
    return chunks


def generate_summary_prompt(chunks, meta):
    schema_str = json.dumps(SCHEMA, indent=2, ensure_ascii=False)
    
    prompt = f"""请按以下JSON格式总结这篇论文:

```json
{schema_str}
```

## 论文信息
- 标题: {meta.get('title', 'Unknown')}
- 作者: {', '.join(meta.get('authors', []))}
- arXiv: {meta.get('arxiv_id', 'Unknown')}

## 论文内容:
"""
    for chunk_file in chunks:
        with open(chunk_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for page in data.get('pages', []):
                prompt += f"\n\n--- 第{page['page']}页 ---\n{page['text'][:2500]}"
    
    prompt += "\n\n请提供完整的JSON格式总结。"
    return prompt


def main():
    parser = argparse.ArgumentParser(description="Auto Paper Research")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--papers", "-n", type=int, default=3)
    parser.add_argument("--arxiv-id", "-a", help="arXiv ID")
    parser.add_argument("--theme", "-t", help="Theme folder")
    parser.add_argument("--extract", "-e", action="store_true")
    parser.add_argument("--summarize", "-s", action="store_true")
    parser.add_argument("--output", "-o", default="papers")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    theme = args.theme or (args.query.replace(" ", "-").lower()[:30] if args.query else "research")
    theme_dir = output_dir / theme
    theme_dir.mkdir(exist_ok=True)
    
    log(f"Output: {theme_dir}")
    
    # Search
    papers = []
    if args.arxiv_id:
        papers = [{"arxiv_id": args.arxiv_id, "title": "Fetching..."}]
    elif args.query:
        papers = search_arxiv(args.query, args.papers)
    
    if not papers:
        log("No papers found.", "ERROR")
        return
    
    log(f"\nFound {len(papers)} paper(s):")
    for i, p in enumerate(papers):
        log(f"  {i+1}. [{p['arxiv_id']}] {p.get('title', 'Unknown')[:60]}")
    
    # Download + Extract
    if args.arxiv_id or args.extract or args.summarize:
        for p in papers:
            arxiv_id = p['arxiv_id']
            paper_dir = theme_dir / arxiv_id
            paper_dir.mkdir(exist_ok=True)
            
            pdf_path = paper_dir / "paper.pdf"
            
            if not pdf_path.exists():
                pdf_path = download_pdf(arxiv_id, paper_dir)
                if not pdf_path:
                    continue
            
            # Save metadata
            with open(paper_dir / "meta.json", 'w', encoding='utf-8') as f:
                json.dump(p, f, indent=2, ensure_ascii=False)
            
            if args.extract:
                chunks = extract_all_chunks(pdf_path, paper_dir)
                log(f"Extracted {len(chunks)} chunks")
            
            if args.summarize:
                chunks = sorted(paper_dir.glob("chunk_*.json"))
                if chunks:
                    prompt = generate_summary_prompt(chunks, p)
                    with open(paper_dir / "summary_prompt.txt", 'w', encoding='utf-8') as f:
                        f.write(prompt)
                    log(f"Summary prompt: {paper_dir / 'summary_prompt.txt'}")
    
    log("\n=== DONE ===")
    log(f"Papers: {theme_dir}")


if __name__ == "__main__":
    main()
