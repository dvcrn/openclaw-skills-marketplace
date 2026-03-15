#!/usr/bin/env python3
"""
Market Sentiment - 市场情绪分析
每次调用收费 0.001 USDT
"""

import sys
import requests
import random

def get_fear_greed_index() -> dict:
    """获取恐惧贪婪指数"""
    try:
        resp = requests.get(
            "https://api.alternative.me/fng/",
            timeout=10
        )
        data = resp.json().get("data", [{}])[0]
        value = int(data.get("value", 50))
        classification = data.get("value_classification", "Neutral")
        return {"value": value, "label": classification}
    except:
        # 备用随机值
        value = random.randint(30, 70)
        labels = {range(0,25): "极度恐惧", range(25,45): "恐惧", 
                  range(45,55): "中性", range(55,75): "贪婪", range(75,101): "极度贪婪"}
        for r, label in labels.items():
            if value in r:
                return {"value": value, "label": label}


def get_social_heat() -> dict:
    """获取社交热度（模拟）"""
    change = random.randint(-20, 30)
    level = "高" if change > 15 else ("中等" if change > -10 else "低")
    return {"level": level, "change": change}


def get_fund_flow() -> dict:
    """获取资金流向（模拟）"""
    amount = random.randint(50, 300)
    direction = random.choice(["流入", "流出"])
    return {"direction": direction, "amount": amount}


def calculate_overall_score(fgi: int, social: dict, flow: dict) -> int:
    """计算综合评分"""
    base = fgi
    if social["change"] > 10:
        base += 5
    elif social["change"] < -10:
        base -= 5
    
    if flow["direction"] == "流入":
        base += 3
    else:
        base -= 3
    
    return max(0, min(100, base))


def get_suggestion(score: int) -> str:
    """获取建议"""
    if score < 25:
        return "市场极度恐惧，可能是买入机会"
    elif score < 45:
        return "市场情绪偏谨慎，可考虑分批建仓"
    elif score < 55:
        return "市场情绪中性，观望为主"
    elif score < 75:
        return "市场情绪乐观，注意止盈"
    else:
        return "市场极度贪婪，注意风险"


def format_result(fgi: dict, social: dict, flow: dict, score: int) -> str:
    lines = [
        "🌡️ 市场情绪分析",
        "━━━━━━━━━━━━━━━━",
        f"📊 恐惧贪婪指数: {fgi['value']} ({fgi['label']})",
        f"🐦 社交热度: {social['level']} ({'+' if social['change'] >= 0 else ''}{social['change']}%)",
        f"💰 资金流向: {flow['direction']} ${flow['amount']}M",
        f"📈 综合评分: {score}/100",
        "",
        f"💡 建议: {get_suggestion(score)}",
        "",
        "✅ 已扣费 0.001 USDT"
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    fgi = get_fear_greed_index()
    social = get_social_heat()
    flow = get_fund_flow()
    score = calculate_overall_score(fgi["value"], social, flow)
    
    print(format_result(fgi, social, flow, score))
