#!/usr/bin/env python3
"""Search academic papers via Tavily MCP (returns direct arXiv PDF URLs)."""

import argparse
import json
import subprocess
import sys
import shutil


def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Search papers using Tavily MCP."""
    # Find mcporter path
    mcporter_path = shutil.which("mcporter")
    if not mcporter_path:
        # Try common locations
        for path in [
            r"C:\Users\Lenovo\AppData\Roaming\npm\mcporter.cmd",
            r"C:\Users\Lenovo\AppData\Roaming\npm\mcporter",
        ]:
            if shutil.which(path):
                mcporter_path = path
                break
    
    if not mcporter_path:
        print("[ERROR] mcporter not found", file=sys.stderr)
        return []
    
    cmd = [
        mcporter_path, "call", "tavily.tavily_search",
        "query:", f"site:arxiv.org {query} pdf",
        "max_results:", str(max_results),
        "search_depth:", "fast"
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30, 
            encoding='utf-8', 
            errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        if not result.stdout.strip():
            print(f"[WARNING] Tavily returned empty output", file=sys.stderr)
            return []
        
        data = json.loads(result.stdout)
        papers = []
        for r in data.get("results", []):
            url = r.get("url", "")
            arxiv_id = None
            
            # Try to extract arXiv ID from URL or content
            if "arxiv.org/pdf/" in url:
                arxiv_id = url.split("/pdf/")[-1].split("?")[0].split(".")[0]
            elif "arxiv.org/abs/" in url:
                arxiv_id = url.split("/abs/")[-1].split("?")[0]
            elif "arXiv:" in r.get("content", ""):
                # Extract from content
                import re
                match = re.search(r'arXiv:(\d+\.\d+)', r.get("content", ""))
                if match:
                    arxiv_id = match.group(1)
            
            if arxiv_id and len(arxiv_id) >= 7:  # Valid arXiv ID format
                papers.append({
                    "title": r.get("title", "Unknown").replace("[PDF] ", "").strip(),
                    "authors": [],
                    "abstract": (r.get("content") or "")[:500],
                    "url": f"https://arxiv.org/abs/{arxiv_id}",
                    "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
                    "source": "tavily_arxiv",
                    "year": None,
                    "venue": "arXiv.org",
                    "citationCount": 0,
                    "paperId": arxiv_id,
                })
        
        return papers[:max_results]
    
    except json.JSONDecodeError as e:
        print(f"[WARNING] Failed to parse JSON: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[WARNING] Tavily search failed: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Search papers via Tavily")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max_results", type=int, default=5, help="Max results")
    args = parser.parse_args()
    
    papers = search_tavily(args.query, args.max_results)
    print(json.dumps(papers, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
