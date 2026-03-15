#!/usr/bin/env python3
"""CLI 入口 - pip install 后可直接使用 cloud-doc-skill 命令

用法:
    cloud-doc-skill <skill_name> [params_json]

等价于:
    python scripts/entry.py <skill_name> [params_json]
"""

import json
import os
import sys

from .skills import DocAssistant

SKILLS = ["fetch_doc", "check_changes", "compare_docs", "summarize_diff", "run_monitor"]


def main():
    if len(sys.argv) < 2:
        print("用法: cloud-doc-skill <skill_name> [params_json]")
        print(f"可用 skill: {', '.join(SKILLS)}")
        print()
        print("LLM 配置（环境变量）:")
        print("  LLM_API_KEY   - API Key")
        print("  LLM_API_BASE  - API Base URL（默认: 通义千问 DashScope）")
        print("  LLM_MODEL     - 模型名称（默认: qwen-turbo）")
        sys.exit(0)

    skill_name = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    if skill_name not in SKILLS:
        print(f"错误: 未知 skill '{skill_name}'，可用: {', '.join(SKILLS)}", file=sys.stderr)
        sys.exit(1)

    assistant = DocAssistant(
        llm_api_key=os.environ.get("LLM_API_KEY") or os.environ.get("DASHSCOPE_API_KEY", ""),
        llm_api_base=os.environ.get("LLM_API_BASE", ""),
        llm_model=os.environ.get("LLM_MODEL", ""),
    )

    result = getattr(assistant, skill_name)(**params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
