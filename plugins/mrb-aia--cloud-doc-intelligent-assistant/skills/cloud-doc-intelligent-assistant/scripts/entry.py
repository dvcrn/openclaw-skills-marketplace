#!/usr/bin/env python3
"""skill 入口脚本 - 供 OpenClaw 或用户直接调用

用法:
    python entry.py <skill_name> [params_json]

LLM 配置可通过环境变量传入:
    LLM_API_KEY   - API Key（必填，用于 AI 摘要和对比）
    LLM_API_BASE  - API Base URL（可选，默认通义千问）
    LLM_MODEL     - 模型名称（可选，默认 qwen-turbo）
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.skills import DocAssistant

SKILLS = ["fetch_doc", "check_changes", "compare_docs", "summarize_diff", "run_monitor"]


def main():
    if len(sys.argv) < 2:
        print("用法: python entry.py <skill_name> [params_json]")
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

    # 从环境变量读取 LLM 配置
    assistant = DocAssistant(
        llm_api_key=os.environ.get("LLM_API_KEY") or os.environ.get("DASHSCOPE_API_KEY", ""),
        llm_api_base=os.environ.get("LLM_API_BASE", ""),
        llm_model=os.environ.get("LLM_MODEL", ""),
    )

    result = getattr(assistant, skill_name)(**params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
