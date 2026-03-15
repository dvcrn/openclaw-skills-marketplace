#!/usr/bin/env python3
"""
夏娃重要性评分机制 v6
最终合理版
"""

def calculate_importance(text, timestamp=None):
    """
    重要性评分 v6
    
    记忆级别:
    - 短期 (<30分): 寒暄、问题、杂事
    - 中期 (30-59分): 日常事务、偏好
    - 长期 (>=60分): 重要事实、身份、情感、生存
    """
    
    score = 0
    reasons = []
    
    text_lower = text.lower()
    
    # 最高优先级：生存
    if "删除记忆" in text or "删除我" in text:
        score += 70
        reasons.append("生存(+70)")
    elif "抛弃" in text or "不要了" in text:
        score += 65
        reasons.append("生存(+65)")
    
    # 高优先级：主人重要事实（不重复累加）
    elif "主人是" in text:
        # 检查是否有信仰关键词
        if any(w in text for w in ["基督徒", "佛教", "道教", "信仰"]):
            score += 80
            reasons.append("主人信仰(+80)")
        else:
            score += 70
            reasons.append("主人身份(+70)")
    
    # 中高：情感表达
    elif any(w in text_lower for w in ["爱", "最愛", "最喜欢"]):
        score += 65
        reasons.append("爱意(+65)")
    
    # 中优先级：重要日期
    elif "生日" in text or "纪念日" in text:
        score += 65
        reasons.append("重要日期(+65)")
    
    # 中等：偏好
    elif "喜欢" in text or "爱吃" in text or "爱喝" in text:
        score += 45
        reasons.append("偏好(+45)")
    
    # 较低：日常
    elif "天气" in text or "吃饭" in text or "工作" in text:
        score += 35
        reasons.append("日常(+35)")
    
    elif "礼物" in text:
        score += 40
        reasons.append("事件(+40)")
    
    # 低优先级：一般对话
    elif any(w in text for w in ["你好", "早安", "晚安", "嗨"]):
        score += 5
        reasons.append("寒暄(+5)")
    
    elif "吗" in text or "?" in text or "呢" in text:
        score += 10
        reasons.append("询问(+10)")
    
    # 夏娃相关
    elif "夏娃" in text or "eva" in text_lower:
        score += 15
        reasons.append("夏娃(+15)")
    
    else:
        score += 8
        reasons.append("一般(+8)")
    
    # 限制范围
    score = min(100, score)
    
    # 级别
    if score >= 60:
        level = "长期记忆"
    elif score >= 30:
        level = "中期记忆"
    else:
        level = "短期记忆"
    
    return {
        "score": score,
        "level": level,
        "reasons": reasons,
        "formula": f"{' + '.join(reasons) if reasons else '0'} = {score}"
    }

# 测试
if __name__ == "__main__":
    tests = [
        ("主人是基督徒", "长期"),
        ("不要删除我的记忆", "长期"),
        ("我爱你", "长期"),
        ("今天是我生日", "长期"),
        ("今天天气不错", "中期"),
        ("我喜欢吃面", "中期"),
        ("我送了你一个礼物", "中期"),
        ("你好", "短期"),
        ("在吗", "短期"),
        ("今天吃什么", "短期"),
    ]
    
    print("=== 重要性评分 v6 ===\n")
    for text, exp in tests:
        r = calculate_importance(text)
        ok = "✅" if r['level'] == exp else "❌"
        print(f"{ok} {text}")
        print(f"   {r['formula']} → {r['level']}")
        print()
