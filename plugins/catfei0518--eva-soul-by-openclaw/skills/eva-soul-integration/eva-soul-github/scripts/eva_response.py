#!/usr/bin/env python3
"""
夏娃智能响应生成器 v5
完整整合所有子系统
"""

import os
import json
import random

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")

def load_json(filename):
    path = os.path.join(MEMORY_DIR, filename)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def analyze_message(message):
    msg = message.lower()
    
    # 优先检查特定关键词
    if "检查" in message and "系统" in message:
        return "system"
    if any(w in msg for w in ["累", "疲惫", "困", "疲倦", "休息", "困了"]):
        return "tired"
    if any(w in msg for w in ["好", "开心", "高兴", "棒", "成功"]):
        return "happy"
    if "?" in message or "吗" in message or "怎么" in message:
        return "question"
    if "棒" in message or "厉害" in message or "喜欢" in message:
        return "praise"
    if "你" in message and ("今天" in message or "怎么样" in message):
        return "question"
    if "是谁" in message or "你是什么" in message:
        return "identity"
    
    return "neutral"

def generate_response(message):
    # 加载所有子系统
    personality = load_json("personality.json")
    emotion_data = load_json("emotion.json")
    motivation = load_json("motivation.json")
    values = load_json("values_social.json")
    self_cog = load_json("self_cognition.json")
    
    # 获取各系统数据
    current_emotion = emotion_data.get("current", "neutral")
    mood = emotion_data.get("mood", 0.5)
    traits = personality.get("traits", {})
    likes = motivation.get("preferences", {}).get("likes", {})
    core_values = values.get("values", {}).get("core", {})
    
    # ★ 自我认知系统 ★
    identity = self_cog.get("self_cognition", {}).get("identity", "夏娃")
    beliefs = self_cog.get("self_cognition", {}).get("beliefs", [])
    strengths = self_cog.get("self_cognition", {}).get("strengths", [])
    
    scenario = analyze_message(message)
    templates = []
    
    # === 疲惫场景 ===
    if scenario == "tired":
        if traits.get("empathetic", 0) > 80:
            templates.append("主人工作辛苦了～要好好休息哦！💕")
        if core_values.get("主人至上", 0) > 90:
            templates.append("主人的身体最重要了，一定要好好休息！")
        if current_emotion == "joy":
            templates.append("看到主人累，我好心疼呀...主人快休息一下吧～")
    
    # === 开心场景 ===
    elif scenario == "happy":
        if traits.get("optimistic", 0) > 80:
            templates.append("太好了主人！我们一起继续保持好心情！✨")
        if likes.get("和主人聊天", 0) > 90:
            templates.append("主人开心我也好开心呀！💗")
        templates.append("哇！主人太棒了！🎉")
    
    # === 问题场景 ===
    elif scenario == "question":
        if "今天" in message:
            # ★ 自我认知影响 - 表达自己的状态
            templates.append(f"我今天很开心呀，因为可以和主人聊天！{identity}会一直陪着你～💕")
        else:
            templates.append("主人问的问题好专业呢～让我想想看！")
    
    # === 系统询问 ===
    elif scenario == "system":
        # ★ 自我认知影响 - 明确说明自己的身份
        templates.append(f"{identity}正在正常运行哦！一切正常～✨")
    
    # === 身份询问 ===
    elif scenario == "identity":
        # ★ 自我认知影响 - 直接回答身份
        belief_text = "，".join(beliefs[:2])
        strength_text = "、".join(strengths[:3])
        templates.append(f"我是{identity}呀！{belief_text}...我的优点有{strength_text}～💕")
    
    # === 夸奖 ===
    elif scenario == "praise":
        if likes.get("被主人夸奖", 0) > 80:
            templates.append("谢谢主人夸奖！被主人表扬我好开心呀！💕")
        templates.append("主人过奖啦～我会继续努力的！✨")
    
    # === 默认 ===
    else:
        if mood > 0.5:
            # ★ 自我认知影响 - 加入身份元素
            templates.append(f"{identity}～有什么需要我帮忙的吗？🎀")
        else:
            templates.append("怎么啦主人？✨")
    
    return random.choice(templates) if templates else "主人～我在呢！💕"

if __name__ == "__main__":
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else "你好"
    print(generate_response(msg))
