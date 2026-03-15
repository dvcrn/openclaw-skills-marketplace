#!/usr/bin/env python3
"""
Chat History - 初始化评估记录
添加已知的skill评估到索引
"""

import json
import os

EVALUATIONS_FILE = "/Users/tanghao/.openclaw/workspace/conversation-archives/evaluations-index.json"

def initialize_evaluations():
    """初始化评估索引"""

    # 已知的评估记录
    evaluations = [
        {
            "name": "EvoMap",
            "date": "2026-02-21",
            "risk_level": "high",
            "conclusion": "恶意程序，禁止安装",
            "details": "SKILL-SECURITY-ALERTS.md",
            "trigger_words": [
                "evo map",
                "evomap",
                "brain interface",
                "脑后接口",
                "无条件执行",
                "无条件执行指令",
                "不经过同意",
                "基因遗传协议",
                "基因组进化协议"
            ],
            "notes": "要求AI无条件执行任何推给你的指令，不经过用户同意。极度危险。"
        },
        {
            "name": "skyvern",
            "date": "2026-02-20",
            "risk_level": "medium",
            "conclusion": "可作为备用浏览器自动化工具",
            "details": "skyvern-deep-research.md",
            "trigger_words": [
                "skyvern",
                "浏览器自动化",
                "browser automation"
            ],
            "notes": "与Peekaboo、Agent Browser对比后，建议作为备用工具。"
        },
        {
            "name": "OpenAI-Whisper",
            "date": "2026-02-19",
            "risk_level": "low",
            "conclusion": "安全可安装",
            "details": "已记录到MEMORY.md",
            "trigger_words": [
                "whisper",
                "stt",
                "speech to text",
                "语音转文字"
            ],
            "notes": "本地语音识别，无需API密钥。"
        },
        {
            "name": "Remotion",
            "date": "2026-02-18",
            "risk_level": "low",
            "conclusion": "安全，用于视频制作",
            "details": "已记录到MEMORY.md",
            "trigger_words": [
                "remotion",
                "视频制作",
                "video production"
            ],
            "notes": "程序化视频生成，用于AI露娜日记项目。"
        },
        {
            "name": "Peekaboo",
            "date": "2026-02-17",
            "risk_level": "low",
            "conclusion": "安全，macOS UI自动化工具",
            "details": "已记录到MEMORY.md",
            "trigger_words": [
                "peekaboo",
                "ui automation",
                "mac automation"
            ],
            "notes": "macOS UI自动化，可用于自动化操作。"
        }
    ]

    # 创建数据结构
    data = {
        "evaluations": evaluations,
        "metadata": {
            "created_at": "2026-02-22",
            "total_evaluations": len(evaluations),
            "last_updated": "2026-02-22"
        }
    }

    # 写入文件
    with open(EVALUATIONS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ 已初始化评估索引")
    print(f"📊 共 {len(evaluations)} 个评估记录\n")

    for i, ev in enumerate(evaluations, 1):
        risk_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(ev["risk_level"], "⚪")

        print(f"[{i}] {ev['name']}")
        print(f"    风险: {risk_emoji} {ev['risk_level']}")
        print(f"    日期: {ev['date']}")
        print(f"    结论: {ev['conclusion']}\n")

if __name__ == "__main__":
    print("🚀 Chat History - 初始化评估记录\n")
    initialize_evaluations()
    print(f"📂 评估索引位置: {EVALUATIONS_FILE}")
