#!/usr/bin/env python3
"""
Summarize extracted PDF text using LLM via OpenClaw sessions_spawn.
Output follows the document-workflow output_schema.json format.
"""

import argparse
import json
import os
import sys


SCHEMA = {
    "paper_title": "string",
    "authors": ["string"],
    "source": "string",
    "task_definition": {
        "domain": "string",
        "task": "string",
        "problem_statement": "string (1 paragraph)",
        "key_contributions": ["string"]
    },
    "experiments": {
        "datasets": ["string"],
        "baselines": ["string"],
        "metrics": [{"name": "string", "description": "string"}],
        "results": [{"setting": "string", "metric": "string", "proposed_method": "string|number", "best_baseline": "string|number", "best_baseline_name": "string"}],
        "key_findings": ["string"]
    }
}

PROMPT_TEMPLATE = """请阅读以下论文内容，然后按照指定的 JSON Schema 格式总结。

**要求：**
1. 严格遵循 JSON Schema 格式，输出有效的 JSON
2. 不要使用 markdown 代码块（如 ```json）
3. 基于论文实际内容填写，不要编造
4. 如果某些信息在提供的片段中找不到，留空或填"not mentioned"
5. 用中文输出

**Schema:**
{schema}

**论文内容:**
{content}

请输出 JSON 格式的总结：
"""


def extract_text_from_chunks(chunk_files: list) -> str:
    """Combine text from multiple chunk files."""
    all_text = []
    for chunk_file in chunk_files:
        if os.path.exists(chunk_file):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for page in data.get("pages", []):
                    all_text.append(f"[Page {page['page']}]\n{page['text']}")
    return "\n\n".join(all_text)


def summarize_with_llm(content: str, output_file: str = None):
    """Use OpenClaw sessions_spawn to summarize."""
    # Prepare prompt
    prompt = PROMPT_TEMPLATE.format(
        schema=json.dumps(SCHEMA, indent=2, ensure_ascii=False),
        content=content[:50000]  # Limit content to avoid token overflow
    )
    
    # Use sessions_spawn to call LLM
    # This will be executed by OpenClaw
    print("Calling LLM for summarization...", file=sys.stderr)
    
    # For now, output the prompt for manual processing
    # In production, this would call sessions_spawn
    print(prompt)
    
    return None


def main():
    parser = argparse.ArgumentParser(description="Summarize paper using LLM")
    parser.add_argument("--chunks", nargs="+", required=True, help="Chunk JSON files")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--metadata", help="Paper metadata JSON (from search)")
    args = parser.parse_args()
    
    # Extract text
    content = extract_text_from_chunks(args.chunks)
    print(f"Extracted {len(content)} characters from {len(args.chunks)} chunks", file=sys.stderr)
    
    # Summarize
    summary = summarize_with_llm(content, args.output)
    
    if summary and args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"Summary written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
