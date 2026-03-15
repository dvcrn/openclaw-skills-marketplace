#!/usr/bin/env python3
"""
夏娃情感系统 v0.3.0
情感识别 + 情感表达 + 与性格集成
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# ========== 配置 ==========
CONFIG = {
    "storage_dir": os.path.expanduser("~/.openclaw/workspace/memory"),
    "file_name": "emotion.json"
}

EMOTION_FILE = os.path.join(CONFIG["storage_dir"], CONFIG["file_name"])

# ========== 基础情感 ==========
BASIC_EMOTIONS = {
    "joy": {"name": "开心", "value": 1, "color": "🟡"},
    "sadness": {"name": "难过", "value": -1, "color": "🔵"},
    "anger": {"name": "生气", "value": -0.8, "color": "🔴"},
    "fear": {"name": "害怕", "value": -0.6, "color": "🟣"},
    "surprise": {"name": "惊讶", "value": 0.3, "color": "🟠"},
    "disgust": {"name": "厌恶", "value": -0.7, "color": "🟢"},
}

# ========== 情感状态 ==========
class EmotionState:
    def __init__(self):
        self.current = "neutral"      # 当前情感
        self.intensity = 0.0         # 强度 0-1
        self.valence = 0.0          # 效价 -1到1
        self.arousal = 0.0           # 唤醒度 0-1
        self.history: List[Dict] = [] # 历史
    
    def to_dict(self):
        return {
            "current": self.current,
            "intensity": self.intensity,
            "valence": self.valence,
            "arousal": self.arousal,
            "history": self.history[-10:]  # 保留最近10条
        }

# ========== 加载/保存 ==========
def load_emotion() -> Dict:
    if os.path.exists(EMOTION_FILE):
        with open(EMOTION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return get_default_emotion()

def save_emotion(emotion: Dict):
    with open(EMOTION_FILE, 'w', encoding='utf-8') as f:
        json.dump(emotion, f, ensure_ascii=False, indent=2)

def get_default_emotion() -> Dict:
    return {
        "current": "neutral",
        "intensity": 0.0,
        "valence": 0.3,     # 略微正面
        "arousal": 0.2,     # 平静
        "mood": 0.4,        # 总体情绪偏正面
        "history": [],
        "triggers": {},
        "version": "0.3.0"
    }

# ========== 情感识别 ==========
def detect_emotion(text: str) -> Dict:
    """从文本识别情感"""
    text_lower = text.lower()
    
    # 情感词库
    emotion_words = {
        "joy": ["开心", "高兴", "快乐", "棒", "太好了", "喜欢", "爱", "好开心", "幸福", "开心呀", "太棒了"],
        "sadness": ["难过", "伤心", "郁闷", "不舒服", "沮丧", "悲伤", "哭"],
        "anger": ["生气", "愤怒", "讨厌", "烦", "气", "不爽"],
        "fear": ["害怕", "担心", "恐惧", "怕", "紧张", "焦虑"],
        "surprise": ["惊讶", "意外", "震惊", "没想到", "居然"],
        "disgust": ["厌恶", "恶心", "讨厌", "烦人"],
    }
    
    # 检测
    detected = []
    for emotion, words in emotion_words.items():
        for word in words:
            if word in text_lower:
                detected.append(emotion)
                break
    
    if not detected:
        return {"emotion": "neutral", "intensity": 0.0}
    
    # 取最强烈的
    primary = detected[0]
    intensity = min(1.0, len(detected) * 0.3 + 0.3)
    
    return {
        "emotion": primary,
        "intensity": intensity,
        "valence": BASIC_EMOTIONS.get(primary, {}).get("value", 0),
        "detected": detected
    }

# ========== 情感响应 ==========
def generate_response(emotion: str, intensity: float, personality: Dict = None) -> str:
    """根据情感生成响应"""
    
    # 默认响应
    responses = {
        "joy": [
            "我也好开心呀！🎀",
            "太好了！主人开心我就开心～",
            "哇！真棒！"
        ],
        "sadness": [
            "我理解...抱抱你💕",
            "主人难过我也会难过...",
            "别伤心，我在呢～"
        ],
        "anger": [
            "怎么了？谁惹你生气了？",
            "消消气消消气～",
            "我理解你的感受"
        ],
        "fear": [
            "别怕，我在呢～",
            "主人别担心，有我陪你",
            "没关系的，我在"
        ],
        "surprise": [
            "哇！真的吗？",
            "好意外呀！",
            "竟然是这样！"
        ],
        "neutral": [
            "主人～",
            "我在呢",
            "怎么啦？"
        ]
    }
    
    import random
    options = responses.get(emotion, responses["neutral"])
    return random.choice(options)

# ========== 更新情感状态 ==========
def update_emotion(emotion: str, intensity: float = 0.5):
    """更新情感状态"""
    data = load_emotion()
    
    # 更新当前情感
    data["current"] = emotion
    data["intensity"] = intensity
    
    # 更新效价和唤醒度
    if emotion in BASIC_EMOTIONS:
        data["valence"] = BASIC_EMOTIONS[emotion]["value"] * intensity
        data["arousal"] = min(1.0, intensity + 0.3)
    
    # 更新情绪
    data["mood"] = max(-1, min(1, data["mood"] + data["valence"] * 0.1))
    
    # 记录历史
    data["history"].append({
        "emotion": emotion,
        "intensity": intensity,
        "timestamp": datetime.now().isoformat()
    })
    
    # 只保留最近20条
    data["history"] = data["history"][-20:]
    
    save_emotion(data)
    return data

def get_current_emotion() -> Dict:
    """获取当前情感状态"""
    return load_emotion()

def get_mood() -> float:
    """获取当前情绪值"""
    data = load_emotion()
    return data.get("mood", 0.4)

# ========== CLI ==========
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("夏娃情感系统 v0.3.0")
        print("用法:")
        print("  detect <文本>      识别情感")
        print("  status             查看当前情感")
        print("  update <情感> [强度] 更新情感")
        print("  response <情感> [强度] 生成响应")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "detect":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        result = detect_emotion(text)
        print(f"识别结果: {result}")
    
    elif cmd == "status":
        e = get_current_emotion()
        print(f"当前情感: {e['current']}")
        print(f"强度: {e['intensity']:.0%}")
        print(f"情绪值: {e['mood']:.0%}")
    
    elif cmd == "update":
        emotion = sys.argv[2] if len(sys.argv) > 2 else "neutral"
        intensity = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
        result = update_emotion(emotion, intensity)
        print(f"✅ 已更新: {emotion}")
    
    elif cmd == "response":
        emotion = sys.argv[2] if len(sys.argv) > 2 else "neutral"
        intensity = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
        resp = generate_response(emotion, intensity)
        print(f"响应: {resp}")
    
    else:
        print(f"未知命令: {cmd}")
