#!/usr/bin/env python3
"""
Smart Contract Auditor - 智能合约安全审计
每次调用收费 0.001 USDT
"""

import sys
import re

def audit_contract(code: str) -> dict:
    """简单静态分析（实际需要Slither等工具）"""
    issues = []
    
    # 检测常见漏洞模式
    patterns = {
        "重入攻击风险": r"\.call\s*\{.*value.*\}\s*\(",
        "未检查返回值": r"\.transfer\s*\(|\.send\s*\(",
        "tx.origin使用": r"tx\.origin",
        "区块时间依赖": r"block\.timestamp",
        "自毁函数": r"selfdestruct\s*\(",
        "无限授权": r"approve\s*\([^,]+,\s*type\(uint256\)\.max\)",
    }
    
    for issue, pattern in patterns.items():
        if re.search(pattern, code, re.IGNORECASE):
            issues.append({"type": issue, "severity": "中", "line": "未知"})
    
    # 如果没找到问题，添加一个提示
    if not issues:
        issues.append({"type": "未检测到明显漏洞", "severity": "信息", "line": "-"})
    
    return {
        "issues": issues,
        "score": max(0, 100 - len(issues) * 15),
        "recommendation": "建议使用Slither进行深度审计"
    }


def format_result(data: dict) -> str:
    lines = [
        "🔍 智能合约审计",
        "━━━━━━━━━━━━━━━━",
        f"📊 安全评分: {data['score']}/100",
        "",
        "检测结果:"
    ]
    
    for i, issue in enumerate(data["issues"], 1):
        emoji = "🔴" if issue["severity"] == "高" else ("🟡" if issue["severity"] == "中" else "ℹ️")
        lines.append(f"  {emoji} {issue['type']} ({issue['severity']})")
    
    lines.append("")
    lines.append(f"💡 {data['recommendation']}")
    lines.append("")
    lines.append("✅ 已扣费 0.001 USDT")
    
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python contract_auditor.py <CONTRACT_CODE_FILE>")
        print("   或: python contract_auditor.py --code 'contract code here'")
        sys.exit(1)
    
    if sys.argv[1] == "--code":
        code = " ".join(sys.argv[2:])
    else:
        try:
            with open(sys.argv[1], 'r') as f:
                code = f.read()
        except:
            code = sys.argv[1]
    
    result = audit_contract(code)
    print(format_result(result))
