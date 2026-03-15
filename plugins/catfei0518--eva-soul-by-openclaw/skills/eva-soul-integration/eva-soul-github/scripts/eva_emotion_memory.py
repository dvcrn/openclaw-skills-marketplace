#!/usr/bin/env python3
"""
情绪记忆联动模块
当主人情绪波动时，自动记录相关上下文
"""

import os
import json
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
EMOTION_MEMORIES_FILE = os.path.join(MEMORY_DIR, "emotion_memories.json")

# 情绪关键词映射
EMOTION_KEYWORDS = {
    "happy": {
        "keywords": ["开心", "高兴", "快乐", "棒", "好开心", "太好了", "哈哈", "爱你", "么么哒", "幸福", "满足", "舒服"],
        "name": "开心",
        "emoji": "😊"
    },
    "sad": {
        "keywords": ["难过", "伤心", "哭", "委屈", "郁闷", "累", "好累", "心累", "不舒服", "烦恼", "焦虑"],
        "name": "难过",
        "emoji": "😢"
    },
    "angry": {
        "keywords": ["生气", "愤怒", "气死了", "烦", "滚", "讨厌", "恼火", "火大"],
        "name": "生气",
        "emoji": "😠"
    },
    "neutral": {
        "keywords": [],
        "name": "平静",
        "emoji": "😐"
    }
}

# 触发情绪的消息模式
TRIGGER_PATTERNS = [
    # 工作相关
    (r"工作.*累", "工作"),
    (r"上班.*累", "工作"),
    (r"加班", "工作"),
    # 情感相关
    (r"爱你", "情感"),
    (r"想.*你", "情感"),
    (r"分手", "情感"),
    # 生活相关
    (r"睡.*好", "生活"),
    (r"吃.*", "生活"),
    (r"天气", "生活"),
]


def load_emotion_memories():
    """加载情绪记忆"""
    if os.path.exists(EMOTION_MEMORIES_FILE):
        with open(EMOTION_MEMORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_emotion_memories(memories):
    """保存情绪记忆"""
    with open(EMOTION_MEMORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)


def detect_emotion_category(message):
    """检测消息所属的情绪类别"""
    msg = message.lower()
    
    for pattern, category in TRIGGER_PATTERNS:
        import re
        if re.search(pattern, msg):
            return category
    
    # 通用分类
    for emotion, info in EMOTION_KEYWORDS.items():
        for kw in info["keywords"]:
            if kw in msg:
                return emotion
    
    return "general"


def record_emotion_memory(emotion, message, context=None):
    """
    记录情绪记忆
    
    参数:
        emotion: 情绪类型 (happy/sad/angry/neutral)
        message: 触发情绪的消息
        context: 额外上下文
    """
    import re
    
    # 提取关键信息
    category = detect_emotion_category(message)
    
    # 生成记忆摘要
    summary = message[:100] if len(message) > 100 else message
    
    emotion_record = {
        "emotion": emotion,
        "emotion_name": EMOTION_KEYWORDS.get(emotion, {}).get("name", emotion),
        "category": category,
        "message": summary,
        "context": context or {},
        "timestamp": datetime.now().isoformat()
    }
    
    # 加载现有记录
    memories = load_emotion_memories()
    
    # 检查是否重复（30分钟内相同情绪+相同消息）
    is_duplicate = False
    for m in memories[-10:]:  # 只检查最近10条
        if m.get("emotion") == emotion and m.get("message")[:50] == summary[:50]:
            # 检查时间差
            try:
                prev_time = datetime.fromisoformat(m["timestamp"])
                time_diff = (datetime.now() - prev_time).total_seconds() / 60
                if time_diff < 30:  # 30分钟内
                    is_duplicate = True
                    break
            except:
                pass
    
    if not is_duplicate:
        memories.append(emotion_record)
        
        # 只保留最近100条
        if len(memories) > 100:
            memories = memories[-100:]
        
        save_emotion_memories(memories)
        return True
    
    return False


def get_emotion_stats(days=7):
    """获取情绪统计"""
    memories = load_emotion_memories()
    
    if not memories:
        return {"total": 0, "emotions": {}, "categories": {}}
    
    from datetime import timedelta
    
    # 按时间过滤
    cutoff = datetime.now() - timedelta(days=days)
    recent_memories = []
    for m in memories:
        try:
            if datetime.fromisoformat(m["timestamp"]) > cutoff:
                recent_memories.append(m)
        except:
            pass
    
    # 统计
    emotion_count = {}
    category_count = {}
    
    for m in recent_memories:
        e = m.get("emotion", "neutral")
        emotion_count[e] = emotion_count.get(e, 0) + 1
        
        c = m.get("category", "general")
        category_count[c] = category_count.get(c, 0) + 1
    
    return {
        "total": len(recent_memories),
        "emotions": emotion_count,
        "categories": category_count,
        "recent": recent_memories[-5:]  # 最近5条
    }


def get_emotion_context(emotion, limit=3):
    """获取某种情绪的上下文记忆"""
    memories = load_emotion_memories()
    
    # 按情绪过滤
    emotion_memories = [m for m in memories if m.get("emotion") == emotion]
    
    # 返回最近的
    return emotion_memories[-limit:]


# CLI测试
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            stats = get_emotion_stats()
            print(f"📊 情绪统计 (最近7天):")
            print(f"   总记录: {stats['total']}")
            print(f"   情绪分布: {stats['emotions']}")
            print(f"   类别分布: {stats['categories']}")
        elif sys.argv[1] == "record" and len(sys.argv) > 2:
            emotion = sys.argv[2]
            message = sys.argv[3] if len(sys.argv) > 3 else "测试消息"
            result = record_emotion_memory(emotion, message)
            print(f"✅ 记录成功" if result else "⏭️ 跳过(重复)")
        else:
            print("用法:")
            print("  python emotion_memory.py stats      - 查看统计")
            print("  python emotion_memory.py record <情绪> <消息>")
    else:
        print("📝 情绪记忆联动模块")
        print(f"   记录文件: {EMOTION_MEMORIES_FILE}")
