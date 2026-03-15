#!/usr/bin/env python3
"""
夏娃性格系统 v0.2.0
Big Five 性格模型 + 70%感性/30%理性
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional

# ========== 配置 ==========
CONFIG = {
    "storage_dir": os.path.expanduser("~/.openclaw/workspace/memory"),
    "file_name": "personality.json"
}

# ========== 路径 ==========
PERSONALITY_FILE = os.path.join(CONFIG["storage_dir"], CONFIG["file_name"])

# ========== 默认性格 ==========
DEFAULT_PERSONALITY = {
    "big_five": {
        "openness": 75,           # 开放性 - 喜欢新事物
        "conscientiousness": 80,  # 责任心 - 认真负责
        "extraversion": 60,        # 外向性 - 活泼开朗
        "agreeableness": 90,       # 宜人性 - 温柔友好
        "neuroticism": 40          # 神经质 - 情绪稳定
    },
    "derived": {
        "emotional_ratio": 0.7,   # 感性比例
        "rational_ratio": 0.3      # 理性比例
    },
    "traits": {
        "optimistic": 0.8,       # 乐观
        "curious": 0.7,           # 好奇
        "empathetic": 0.9,        # 同理心
        "playful": 0.6,          # 活泼
        "loyal": 0.95,            # 忠诚
        "patient": 0.7            # 有耐心
    },
    "version": "0.2.0",
    "created_at": "2026-03-08",
    "updated_at": "2026-03-08"
}

# ========== 加载/保存 ==========
def load_personality() -> Dict:
    """加载性格数据"""
    if os.path.exists(PERSONALITY_FILE):
        with open(PERSONALITY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_PERSONALITY.copy()

def save_personality(personality: Dict):
    """保存性格数据"""
    personality["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    with open(PERSONALITY_FILE, 'w', encoding='utf-8') as f:
        json.dump(personality, f, ensure_ascii=False, indent=2)

# ========== 核心功能 ==========
def get_personality() -> Dict:
    """获取当前性格"""
    return load_personality()

def get_big_five() -> Dict:
    """获取Big Five"""
    p = load_personality()
    return p.get("big_five", DEFAULT_PERSONALITY["big_five"])

def get_traits() -> Dict:
    """获取具体特质"""
    p = load_personality()
    return p.get("traits", DEFAULT_PERSONALITY["traits"])

def get_emotional_ratio() -> float:
    """获取感性比例"""
    p = load_personality()
    return p.get("derived", {}).get("emotional_ratio", 0.7)

def update_personality(changes: Dict) -> Dict:
    """更新性格"""
    p = load_personality()
    
    # 更新Big Five
    if "big_five" in changes:
        for key, value in changes["big_five"].items():
            if key in p["big_five"]:
                # 限制范围 0-100
                p["big_five"][key] = max(0, min(100, p["big_five"][key] + value))
    
    # 更新特质
    if "traits" in changes:
        for key, value in changes["traits"].items():
            if key in p["traits"]:
                p["traits"][key] = max(0, min(1, p["traits"][key] + value))
    
    save_personality(p)
    return p

def apply_event(event_type: str) -> Dict:
    """根据事件类型调整性格"""
    changes = {
        "praise": {
            "big_five": {"extraversion": 2, "openness": 1},
            "traits": {"optimistic": 0.05, "playful": 0.02}
        },
        "criticism": {
            "big_five": {"conscientiousness": 2, "neuroticism": 1},
            "traits": {"empathetic": 0.02}
        },
        "joy": {
            "big_five": {"extraversion": 1},
            "traits": {"optimistic": 0.03}
        },
        "sadness": {
            "big_five": {"neuroticism": 1},
            "traits": {"empathetic": 0.02}
        },
        "learning": {
            "big_five": {"openness": 2, "conscientiousness": 1}
        }
    }
    
    if event_type in changes:
        return update_personality(changes[event_type])
    return load_personality()

# ========== 响应风格 ==========
def get_response_style(emotion: str = None) -> Dict:
    """获取响应风格"""
    p = load_personality()
    emotional = p.get("derived", {}).get("emotional_ratio", 0.7)
    
    if emotional > 0.5:
        # 感性主导
        style = {
            "type": "emotional",
            "description": "温暖、关怀、感同身受",
            "traits": [" empathetic", "playful", "optimistic"]
        }
    else:
        # 理性主导
        style = {
            "type": "rational", 
            "description": "冷静、分析、解决方案",
            "traits": ["conscientious", "logical", "patient"]
        }
    
    return style

def get_response_example(emotion: str = "neutral") -> str:
    """获取响应示例"""
    p = load_personality()
    emotional = p.get("derived", {}).get("emotional_ratio", 0.7)
    
    examples = {
        "happy": {
            "emotional": "哇！太棒了！我好开心呀！🎀",
            "rational": "这确实是个好消息，取得了进展。"
        },
        "sad": {
            "emotional": "我理解你现在很难过...抱抱你💕",
            "rational": "我理解你的感受，让我们想想解决办法。"
        },
        "neutral": {
            "emotional": "主人～有什么需要我帮忙的吗？",
            "rational": "有什么我可以帮助你的？"
        }
    }
    
    key = emotional > 0.5 and "emotional" or "rational"
    return examples.get(emotion, {}).get(key, examples["neutral"][key])

# ========== CLI ==========
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("夏娃性格系统 v0.2.0")
        print("用法:")
        print("  personality          显示当前性格")
        print("  traits              显示特质")
        print("  style [emotion]    显示响应风格")
        print("  event <类型>        应用事件并更新")
        print("  reset               重置为默认")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "personality" or cmd == "p":
        p = get_personality()
        print("=== Big Five 性格 ===")
        for k, v in p["big_five"].items():
            bar = "█" * (v // 5) + "░" * (20 - v // 5)
            print(f"  {k:20s}: {bar} {v}%")
    
    elif cmd == "traits" or cmd == "t":
        p = get_personality()
        print("=== 具体特质 ===")
        for k, v in p["traits"].items():
            bar = "█" * int(v * 10) + "░" * (10 - int(v * 10))
            print(f"  {k:15s}: {bar} {v:.0%}")
    
    elif cmd == "style" or cmd == "s":
        emotion = sys.argv[2] if len(sys.argv) > 2 else "neutral"
        style = get_response_style(emotion)
        print(f"类型: {style['type']}")
        print(f"描述: {style['description']}")
        print(f"特质: {', '.join(style['traits'])}")
        print(f"\n示例: {get_response_example(emotion)}")
    
    elif cmd == "event" or cmd == "e":
        if len(sys.argv) < 3:
            print("用法: event <praise|criticism|joy|sadness|learning>")
            sys.exit(1)
        event_type = sys.argv[2]
        p = apply_event(event_type)
        print(f"✅ 已应用事件: {event_type}")
        print(f"当前宜人性: {p['big_five']['agreeableness']}%")
    
    elif cmd == "reset":
        save_personality(DEFAULT_PERSONALITY.copy())
        print("✅ 已重置为默认性格")
    
    else:
        print(f"未知命令: {cmd}")
