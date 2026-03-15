#!/usr/bin/env python3
"""
DeepWiki Ask - 提问查询仓库。通过 DeepWiki MCP 查询仓库信息。

Usage:
    python deepwiki_ask.py -r owner/repo -q "question"
    python deepwiki_ask.py -r owner/repo -q -          # 从 stdin 读问题 (UTF-8)
    python deepwiki_ask.py -r owner/repo -q @file.txt  # 从文件读问题 (UTF-8)
"""

import sys
import json
import argparse
import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any

if sys.platform == 'win32':
    try:
        os.system('chcp 65001 >nul 2>&1')
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"

DEFAULT_CONFIG = {
    "request_timeout_seconds": 120,
    "request_max_retries": 3,
}

CONFIG_VALIDATION = {
    "request_timeout_seconds": {"min": 10, "max": 600},
    "request_max_retries": {"min": 0, "max": 10},
}


def _print_json(data):
    """UTF-8 安全 JSON 输出。"""
    text = json.dumps(data, ensure_ascii=False, indent=2)
    try:
        sys.stdout.buffer.write(text.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.flush()
    except (AttributeError, OSError):
        print(text)


def load_config() -> dict:
    config = DEFAULT_CONFIG.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            for k in DEFAULT_CONFIG:
                if k in loaded and isinstance(loaded[k], (int, float)):
                    lim = CONFIG_VALIDATION.get(k, {})
                    if lim and (loaded[k] < lim["min"] or loaded[k] > lim["max"]):
                        continue
                    config[k] = loaded[k]
        except (json.JSONDecodeError, OSError):
            pass
    return config


def save_default_config():
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)


def call_mcp(method: str, params: Optional[Dict] = None, timeout: int = 120, max_retries: int = 3) -> Dict:
    url = "https://mcp.deepwiki.com/mcp"
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    payload = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": 1}
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.encoding = 'utf-8'
            response.raise_for_status()
            ct = response.headers.get('Content-Type', '')
            if 'application/json' in ct:
                return response.json()
            if 'text/event-stream' in ct:
                for line in response.text.strip().split('\n'):
                    if line.startswith('data:'):
                        try:
                            return json.loads(line[5:].strip())
                        except (json.JSONDecodeError, ValueError):
                            continue
                raise ValueError("Failed to parse SSE response")
            return response.json()
        except requests.exceptions.Timeout:
            last_error = f"Request timeout ({timeout}s)"
            if attempt < max_retries:
                time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            if attempt < max_retries:
                time.sleep(2 ** attempt)
        except Exception as e:
            last_error = str(e)
            break
    raise Exception(f"Request failed after {max_retries + 1} attempts: {last_error}")


def initialize_mcp(timeout: int = 120, max_retries: int = 3):
    call_mcp("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "deepwiki-ask", "version": "1.0.0"}
    }, timeout, max_retries)


def extract_text(result: Any) -> str:
    if isinstance(result, dict):
        content = result.get("content", [])
        if content and isinstance(content, list):
            texts = [item.get("text", "") for item in content
                     if isinstance(item, dict) and item.get("type") == "text"]
            return "\n".join(texts)
        if "result" in result.get("structuredContent", {}):
            return result["structuredContent"]["result"]
    return str(result)


def ask(repo: str, question: str, config: dict) -> str:
    if "/" not in repo:
        raise ValueError(f"Invalid repo format: {repo}. Expected: owner/repo")
    timeout = config.get("request_timeout_seconds", 120)
    max_retries = config.get("request_max_retries", 3)
    initialize_mcp(timeout, max_retries)
    params = {"name": "ask_question", "arguments": {"repoName": repo, "question": question}}
    data = call_mcp("tools/call", params, timeout, max_retries)
    if "error" in data:
        raise Exception(data["error"].get("message", "Unknown error"))
    raw_result = data.get("result", {})
    if config.get("_debug"):
        print("DEBUG raw MCP result:", json.dumps(raw_result, ensure_ascii=False, indent=2), file=sys.stderr)
    answer = extract_text(raw_result)
    if not answer or answer.strip() == "{}":
        answer = (
            "【请求已成功到达 DeepWiki】MCP 返回空结果。可能：该问题在知识库无匹配，或仓库未在 MCP 侧索引。"
            "可尝试更泛化的问题，或访问 https://deepwiki.com/{} 浏览文档。"
        ).format(repo)
    return answer


def main():
    parser = argparse.ArgumentParser(description="DeepWiki 提问查询仓库")
    parser.add_argument("-r", "--repo", help="仓库 owner/repo")
    parser.add_argument("-q", "--question", help="问题；'-' 从 stdin，'@path' 从文件 (UTF-8)")
    parser.add_argument("--json", action="store_true", help="输出 JSON 供 Agent 解析")
    parser.add_argument("--debug", action="store_true", help="将 MCP 原始 result 输出到 stderr")
    args = parser.parse_args()
    save_default_config()
    config = load_config()
    if getattr(args, "debug", False):
        config["_debug"] = True

    if not args.repo:
        out = {"status": "error", "message": "请提供 -r owner/repo"}
        _print_json(out) if args.json else print("Error:", out["message"])
        sys.exit(1)
    if not args.question:
        out = {"status": "error", "message": "请提供 -q 问题"}
        _print_json(out) if args.json else print("Error:", out["message"])
        sys.exit(1)

    question = args.question
    if question == "-":
        question = sys.stdin.read().strip()
        if not question:
            out = {"status": "error", "message": "标准输入为空"}
            _print_json(out) if args.json else print("Error:", out["message"])
            sys.exit(1)
    elif question.startswith("@"):
        path = Path(question[1:].strip())
        if not path.exists():
            out = {"status": "error", "message": f"文件不存在: {path}"}
            _print_json(out) if args.json else print("Error:", out["message"])
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            question = f.read().strip()
        if not question:
            out = {"status": "error", "message": "问题文件为空"}
            _print_json(out) if args.json else print("Error:", out["message"])
            sys.exit(1)

    if not args.json:
        print("=" * 60)
        print("DeepWiki 仓库问答")
        print("=" * 60)
        print(f"Repo: {args.repo}")
        print(f"Question: {question}")
        print("=" * 60)
        print("Answer:")
        print("-" * 60)

    try:
        answer = ask(args.repo, question, config)
        if args.json:
            _print_json({"status": "success", "repo": args.repo, "question": question, "answer": answer})
        else:
            print(answer)
            print("-" * 60)
    except (ValueError, Exception) as e:
        if args.json:
            _print_json({"status": "error", "repo": args.repo, "message": str(e)})
        else:
            print("Error:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
