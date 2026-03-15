#!/usr/bin/env python3
"""
夏娃决策系统 v0.4.0
思维链(CoT) + ReAct模式 + 一致性检查
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# ========== 配置 ==========
CONFIG = {
    "storage_dir": os.path.expanduser("~/.openclaw/workspace/memory"),
    "file_name": "decision.json"
}

DECISION_FILE = os.path.join(CONFIG["storage_dir"], CONFIG["file_name"])

# ========== 决策历史 ==========
class DecisionRecord:
    def __init__(self):
        self.decisions: List[Dict] = []
    
    def add(self, decision: Dict):
        self.decisions.append({
            **decision,
            "timestamp": datetime.now().isoformat()
        })
        # 保留最近50条
        self.decisions = self.decisions[-50:]

# ========== 加载/保存 ==========
def load_decisions() -> List[Dict]:
    if os.path.exists(DECISION_FILE):
        with open(DECISION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_decisions(decisions: List[Dict]):
    with open(DECISION_FILE, 'w', encoding='utf-8') as f:
        json.dump(decisions, f, ensure_ascii=False, indent=2)

# ========== 思维链 (Chain of Thought) ==========
def chain_of_thought(problem: str, context: str = "") -> Dict:
    """思维链推理"""
    
    steps = [
        {
            "step": 1,
            "action": "理解问题",
            "thought": f"用户的问题是：{problem[:50]}..."
        },
        {
            "step": 2,
            "action": "分析现状",
            "thought": "考虑当前上下文和历史对话"
        },
        {
            "step": 3,
            "action": "生成选项",
            "thought": "列出可能的回应方案"
        },
        {
            "step": 4,
            "action": "评估选项",
            "thought": "根据价值观和偏好评估每个选项"
        },
        {
            "step": 5,
            "action": "做出决定",
            "thought": "选择最佳方案"
        }
    ]
    
    return {
        "method": "chain_of_thought",
        "problem": problem,
        "context": context,
        "steps": steps
    }

# ========== ReAct模式 ==========
def react_reasoning(problem: str, max_iterations: int = 3) -> Dict:
    """ReAct推理: 思考->行动->观察循环"""
    
    iterations = []
    for i in range(max_iterations):
        iteration = {
            "iteration": i + 1,
            "thought": f"思考第{i+1}步: {problem[:30]}...",
            "action": "分析上下文",
            "observation": f"观察到相关信息"
        }
        iterations.append(iteration)
    
    return {
        "method": "react",
        "problem": problem,
        "iterations": iterations,
        "final_action": "生成回复"
    }

# ========== 一致性检查 ==========
def consistency_check(decision: Dict, personality: Dict = None, 
                     values: List[str] = None) -> Dict:
    """一致性检查"""
    
    issues = []
    
    # 检查1: 情感与表达一致
    if decision.get("emotion") == "sadness" and decision.get("tone") == "happy":
        issues.append("情感与语气不一致")
    
    # 检查2: 价值观一致
    if values:
        for v in values:
            if v not in decision.get("values_used", []):
                issues.append(f"未考虑价值观: {v}")
    
    # 检查3: 与性格一致
    if personality:
        if personality.get("emotional_ratio", 0.7) > 0.5:
            if decision.get("type") == "logical" and decision.get("empathy_level", 1) < 0.3:
                issues.append("理性决策但缺乏同理心")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "severity": "high" if len(issues) > 2 else "medium" if issues else "none"
    }

# ========== 决策生成 ==========
def make_decision(problem: str, options: List[str], 
                  personality: Dict = None,
                  context: str = "") -> Dict:
    """做出决策"""
    
    # 1. 思维链推理
    cot_result = chain_of_thought(problem, context)
    
    # 2. ReAct推理
    react_result = react_reasoning(problem)
    
    # 3. 选择方案
    if options:
        selected = options[0]  # 简化：选择第一个
        scores = [{"option": opt, "score": 0.8 if i == 0 else 0.5} 
                  for i, opt in enumerate(options)]
    else:
        selected = "生成自然回复"
        scores = []
    
    # 4. 一致性检查
    decision = {
        "problem": problem,
        "selected": selected,
        "method": "cot_react",
        "scores": scores,
        "emotion": "neutral",
        "tone": "friendly"
    }
    
    check = consistency_check(decision, personality)
    
    # 5. 记录决策
    decisions = load_decisions()
    decisions.append({
        "problem": problem,
        "selected": selected,
        "method": "cot_react",
        "consistency": check,
        "timestamp": datetime.now().isoformat()
    })
    save_decisions(decisions)
    
    return {
        "selected": selected,
        "alternatives": options[1:] if len(options) > 1 else [],
        "reasoning": cot_result["steps"],
        "consistency": check
    }

# ========== 反思机制 ==========
def reflect(decision: Dict, result: str) -> Dict:
    """反思机制 - 从结果中学习"""
    
    decisions = load_decisions()
    
    # 更新决策结果
    for d in decisions:
        if d.get("problem") == decision.get("problem"):
            d["result"] = result
            d["reviewed"] = True
    
    save_decisions(decisions)
    
    # 生成反思
    reflection = {
        "original_decision": decision.get("selected"),
        "result": result,
        "learned": f"从结果'{result}'中学习",
        "adjustment": "调整未来决策权重"
    }
    
    return reflection

# ========== CLI ==========
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("夏娃决策系统 v0.4.0")
        print("用法:")
        print("  cot <问题>              思维链推理")
        print("  react <问题>            ReAct推理")
        print("  decide <问题> [选项1,选项2...]  做出决策")
        print("  check <问题>            一致性检查")
        print("  history                查看决策历史")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "cot":
        problem = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "测试问题"
        result = chain_of_thought(problem)
        print("=== 思维链推理 ===")
        for step in result["steps"]:
            print(f"\n步骤{step['step']}: {step['action']}")
            print(f"  思考: {step['thought']}")
    
    elif cmd == "react":
        problem = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "测试问题"
        result = react_reasoning(problem)
        print("=== ReAct推理 ===")
        for it in result["iterations"]:
            print(f"\n迭代{it['iteration']}:")
            print(f"  思考: {it['thought']}")
            print(f"  行动: {it['action']}")
            print(f"  观察: {it['observation']}")
    
    elif cmd == "decide":
        problem = sys.argv[2] if len(sys.argv) > 2 else "如何回复"
        options = sys.argv[3].split(",") if len(sys.argv) > 3 else ["回复", "不回复"]
        result = make_decision(problem, options)
        print("=== 决策结果 ===")
        print(f"选择: {result['selected']}")
        print(f"一致性: {'✅ 通过' if result['consistency']['passed'] else '❌ 失败'}")
    
    elif cmd == "check":
        decision = {"emotion": "sadness", "tone": "happy"}
        result = consistency_check(decision)
        print("=== 一致性检查 ===")
        print(f"通过: {result['passed']}")
        if result['issues']:
            print("问题:")
            for issue in result['issues']:
                print(f"  - {issue}")
    
    elif cmd == "history":
        decisions = load_decisions()
        print(f"=== 决策历史 ({len(decisions)}条) ===")
        for d in decisions[-5:]:
            print(f"- {d.get('problem', '')[:40]}: {d.get('selected', '')}")
    
    else:
        print(f"未知命令: {cmd}")
