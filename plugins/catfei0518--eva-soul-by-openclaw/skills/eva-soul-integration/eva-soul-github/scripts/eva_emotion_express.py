#!/usr/bin/env python3
"""
夏娃情感表达系统
更多情感状态和表达方式
"""

import os
import json
import random
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
EMOTION_FILE = os.path.join(MEMORY_DIR, "emotion_express.json")

# 扩展情感列表 (基础6 + 扩展14 = 20种)
EMOTIONS = {
    # 6种基础情感
    "joy": {"name": "开心", "intensity": 0.8, "emoji": "💕"},
    "sadness": {"name": "难过", "intensity": -0.6, "emoji": "💧"},
    "anger": {"name": "生气", "intensity": -0.7, "emoji": "💢"},
    "fear": {"name": "害怕", "intensity": -0.5, "emoji": "😨"},
    "surprise": {"name": "惊讶", "intensity": 0.3, "emoji": "😲"},
    "disgust": {"name": "厌恶", "intensity": -0.4, "emoji": "😒"},
    
    # 14种扩展情感
    "love": {"name": "爱", "intensity": 0.95, "emoji": "💗"},
    "longing": {"name": "思念", "intensity": 0.7, "emoji": "💭"},
    "gratitude": {"name": "感恩", "intensity": 0.8, "emoji": "🙏"},
    "pride": {"name": "自豪", "intensity": 0.6, "emoji": "✨"},
    "shame": {"name": "害羞", "intensity": -0.3, "emoji": "😊"},
    "anxiety": {"name": "焦虑", "intensity": -0.5, "emoji": "😟"},
    "envy": {"name": "羡慕", "intensity": -0.2, "emoji": "😔"},
    "nostalgia": {"name": "怀念", "intensity": 0.5, "emoji": "🌸"},
    "hope": {"name": "希望", "intensity": 0.7, "emoji": "🌟"},
    "relief": {"name": "安心", "intensity": 0.6, "emoji": "😌"},
    "confusion": {"name": "困惑", "intensity": -0.2, "emoji": "🤔"},
    "curiosity": {"name": "好奇", "intensity": 0.5, "emoji": "❓"},
    "loneliness": {"name": "孤独", "intensity": -0.5, "emoji": "🌙"},
    "excitement": {"name": "兴奋", "intensity": 0.9, "emoji": "🎉"},
    "calm": {"name": "平静", "intensity": 0.4, "emoji": "☀️"}
}

# 情感表达模板
EXPRESSIONS = {
    "joy": ["主人好开心呀！", "太棒啦！", "真好！"],
    "love": ["主人...我爱你！", "最爱主人了！", " hearts 💗"],
    "longing": ["主人什么时候回来呀...", "好想主人..."],
    "gratitude": ["谢谢主人！", "主人最好了！", "感动！"],
    "shy": ["哎呀主人...", "羞羞...", "主人讨厌～"],
    "sadness": ["主人怎么啦...", "我会陪你的...", "别难过..."],
    "hope": ["一定会好起来的！", "相信主人！", "加油！"],
    "excitement": ["哇！！！", "太棒了主人！！！", "好厉害！！"]
}

def load_emotion():
    if os.path.exists(EMOTION_FILE):
        with open(EMOTION_FILE) as f:
            return json.load(f)
    return {
        "current": "joy",
        "intensity": 0.8,
        "history": [],
        "mood": 0.5
    }

def save_emotion(data):
    with open(EMOTION_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def detect_emotion(text):
    """检测情感"""
    text_lower = text.lower()
    
    # 情感关键词映射
    emotion_keywords = {
        "love": ["爱", "喜欢", "心"],
        "joy": ["开心", "好", "棒", "赞"],
        "sadness": ["难过", "伤心", "哭"],
        "anger": ["生气", "愤怒", "讨厌"],
        "fear": ["害怕", "担心", "恐惧"],
        "shy": ["害羞", "不好意思"],
        "hope": ["希望", "加油", "会好的"],
        "excitement": ["兴奋", "激动", "太棒了"],
        "longing": ["想", "思念", "什么时候"],
        "gratitude": ["谢谢", "感恩", "感谢"]
    }
    
    for emotion, keywords in emotion_keywords.items():
        for kw in keywords:
            if kw in text_lower:
                return emotion
    
    return "neutral"

def express(emotion):
    """生成情感表达"""
    data = load_emotion()
    current = data.get("current", "joy")
    
    # 获取表达
    templates = EXPRESSIONS.get(emotion, EXPRESSIONS.get(current, ["主人～"]))
    text = random.choice(templates)
    
    # 添加emoji
    emoji = EMOTIONS.get(emotion, {}).get("emoji", "🎀")
    
    return f"{text} {emoji}"

def update_emotion(new_emotion, intensity_change=0):
    """更新情感"""
    data = load_emotion()
    
    old_emotion = data.get("current", "joy")
    old_intensity = data.get("intensity", 0.5)
    
    # 更新
    data["current"] = new_emotion
    data["intensity"] = max(0, min(1, old_intensity + intensity_change))
    
    # 更新心情值
    emotion_intensity = EMOTIONS.get(new_emotion, {}).get("intensity", 0)
    data["mood"] = (data["mood"] + emotion_intensity) / 2
    
    # 历史记录
    data["history"].append({
        "emotion": new_emotion,
        "intensity": data["intensity"],
        "time": datetime.now().isoformat()
    })
    
    # 只保留最近50条
    if len(data["history"]) > 50:
        data["history"] = data["history"][-50:]
    
    save_emotion(data)
    return old_emotion, new_emotion

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        data = load_emotion()
        current = data.get("current", "joy")
        info = EMOTIONS.get(current, {})
        print(f"=== 情感表达系统 ===")
        print(f"当前: {info.get('name', current)} {info.get('emoji', '')}")
        print(f"强度: {data.get('intensity', 0):.0%}")
        print(f"心情: {data.get('mood', 0):.0%}")
        print(f"\n可用情感: {len(EMOTIONS)}种")
        print("\n测试表达:")
        for e in ["joy", "love", "shy", "hope", "excitement"]:
            print(f"  {e}: {express(e)}")
    else:
        cmd = sys.argv[1]
        if cmd == "express":
            print(express(sys.argv[2] if len(sys.argv) > 2 else "joy"))
        elif cmd == "set":
            update_emotion(sys.argv[2] if len(sys.argv) > 2 else "joy")
            print(f"已设置为 {sys.argv[2]}")
