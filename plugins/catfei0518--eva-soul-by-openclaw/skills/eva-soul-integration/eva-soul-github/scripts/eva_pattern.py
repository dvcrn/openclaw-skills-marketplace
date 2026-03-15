#!/usr/bin/env python3
"""
夏娃模式识别系统
发现重复规律/周期

功能:
- 时间模式: 按时/天/周/月分组
- 行为模式: 重复动作识别  
- 情绪模式: 情绪触发点发现
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
PATTERNS_FILE = os.path.join(MEMORY_DIR, "patterns.json")

def load_patterns():
    """加载模式库"""
    if os.path.exists(PATTERNS_FILE):
        with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "1.0",
        "updated_at": None,
        "patterns": [],
        "stats": {
            "time_patterns": 0,
            "behavior_patterns": 0,
            "emotion_patterns": 0,
            "last_scan": None
        }
    }

def save_patterns(data):
    """保存模式库"""
    data["updated_at"] = datetime.now().isoformat()
    with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_memories():
    """加载所有记忆"""
    memories = []
    
    for level in ["short", "medium", "long"]:
        level_file = os.path.join(MEMORY_DIR, level, f"{level}.json")
        if os.path.exists(level_file):
            with open(level_file, 'r', encoding='utf-8') as f:
                memories.extend(json.load(f))
    
    return memories

def extract_time_features(memories):
    """提取时间特征"""
    time_features = {
        "hour": defaultdict(list),      # 小时
        "weekday": defaultdict(list),   # 星期
        "day": defaultdict(list),       # 日期
        "month": defaultdict(list)      # 月份
    }
    
    for mem in memories:
        try:
            created = mem.get("created_at", "")
            if not created:
                continue
            
            dt = datetime.fromisoformat(created)
            
            # 按小时分组
            time_features["hour"][dt.hour].append(mem)
            
            # 按星期分组 (0=周一)
            time_features["weekday"][dt.weekday()].append(mem)
            
            # 按日期分组
            time_features["day"][dt.day].append(mem)
            
            # 按月份分组
            time_features["month"][dt.month].append(mem)
            
        except:
            continue
    
    return time_features

def detect_time_patterns(time_features):
    """检测时间模式"""
    patterns = []
    
    # 1. 每周模式 (某星期几经常做什么)
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    for weekday, mems in time_features["weekday"].items():
        if len(mems) >= 5:  # 至少5条
            # 提取共同话题
            topics = []
            for m in mems[:10]:
                tags = m.get("tags", {})
                topics.extend(tags.get("topic", []))
            
            if topics:
                common = Counter(topics).most_common(2)
                pattern = {
                    "id": f"模式_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
                    "type": "time",
                    "subtype": "weekly",
                    "trigger": weekday_names[weekday],
                    "action": f"经常讨论: {', '.join([t for t, _ in common])}",
                    "frequency": f"每周{weekday_names[weekday]}",
                    "count": len(mems),
                    "confidence": min(len(mems) * 0.1, 0.95),
                    "evidence": [m.get("content", "")[:30] for m in mems[:3]],
                    "created_at": datetime.now().isoformat()
                }
                patterns.append(pattern)
    
    # 2. 每日模式 (某小时经常做什么)
    for hour, mems in time_features["hour"].items():
        if len(mems) >= 5 and 6 <= hour <= 23:  # 至少5条，工作时间
            topics = []
            for m in mems[:10]:
                tags = m.get("tags", {})
                topics.extend(tags.get("topic", []))
            
            if topics:
                common = Counter(topics).most_common(2)
                time_str = f"{hour}:00" if hour >= 10 else f"0{hour}:00"
                pattern = {
                    "id": f"模式_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
                    "type": "time",
                    "subtype": "daily",
                    "trigger": time_str,
                    "action": f"经常讨论: {', '.join([t for t, _ in common])}",
                    "frequency": f"每天{time_str}",
                    "count": len(mems),
                    "confidence": min(len(mems) * 0.1, 0.95),
                    "evidence": [m.get("content", "")[:30] for m in mems[:3]],
                    "created_at": datetime.now().isoformat()
                }
                patterns.append(pattern)
    
    return patterns

def detect_behavior_patterns(memories):
    """检测行为模式 - 重复动作"""
    patterns = []
    
    # 1. 检测重复关键词序列
    keyword_sequences = defaultdict(list)
    
    action_keywords = ["查", "看", "问", "说", "告诉", "要", "做", "处理"]
    
    for mem in memories:
        content = mem.get("content", "")
        
        for keyword in action_keywords:
            if keyword in content:
                # 找关键词前后的词
                idx = content.find(keyword)
                context = content[max(0, idx-5):idx+5]
                keyword_sequences[keyword].append({
                    "context": context,
                    "memory": mem
                })
    
    # 生成行为模式
    for keyword, items in keyword_sequences.items():
        if len(items) >= 5:  # 至少5次
            # 分析常见上下文
            contexts = [i["context"] for i in items]
            
            pattern = {
                "id": f"模式_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
                "type": "behavior",
                "subtype": "action",
                "trigger": f"经常'{keyword}'",
                "action": f"出现{len(items)}次",
                "frequency": f"高频 ({len(items)}次)",
                "count": len(items),
                "confidence": min(len(items) * 0.1, 0.9),
                "evidence": [i["context"] for i in items[:3]],
                "created_at": datetime.now().isoformat()
            }
            patterns.append(pattern)
    
    # 2. 检测连续行为 (A后经常B)
    for i in range(len(memories) - 1):
        current = memories[i].get("content", "")
        next_mem = memories[i + 1].get("content", "")
        
        # 简单检测: 包含相同关键词
        current_tags = memories[i].get("tags", {}).get("topic", [])
        next_tags = memories[i + 1].get("tags", {}).get("topic", [])
        
        if current_tags and next_tags:
            common = set(current_tags) & set(next_tags)
            if common:
                pattern = {
                    "id": f"模式_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
                    "type": "behavior",
                    "subtype": "sequence",
                    "trigger": f"讨论{current_tags[0]}",
                    "action": f"接着讨论{next_tags[0]}",
                    "frequency": "顺序",
                    "count": 1,
                    "confidence": 0.5,
                    "evidence": [current[:30], next_mem[:30]],
                    "created_at": datetime.now().isoformat()
                }
                patterns.append(pattern)
    
    return patterns

def detect_emotion_patterns(memories):
    """检测情绪模式 - 什么触发什么情绪"""
    patterns = []
    
    # 按情感标签分组
    emotion_triggers = defaultdict(list)
    
    for mem in memories:
        tags = mem.get("tags", {})
        emotions = tags.get("emotion", [])
        topics = tags.get("topic", [])
        
        for emotion in emotions:
            for topic in topics:
                emotion_triggers[(emotion, topic)].append(mem)
    
    # 生成情绪模式
    for (emotion, topic), mems in emotion_triggers.items():
        if len(mems) >= 3:  # 至少3次
            pattern = {
                "id": f"模式_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
                "type": "emotion",
                "subtype": "trigger",
                "trigger": f"提到'{topic}'",
                "action": f"会感到'{emotion}'",
                "frequency": f"出现{len(mems)}次",
                "count": len(mems),
                "confidence": min(len(mems) * 0.2, 0.95),
                "evidence": [m.get("content", "")[:30] for m in mems[:3]],
                "created_at": datetime.now().isoformat()
            }
            patterns.append(pattern)
    
    # 2. 情绪序列模式 (情绪转换)
    current_emotion = None
    emotion_sequence = []
    
    for mem in memories:
        tags = mem.get("tags", {})
        emotions = tags.get("emotion", [])
        
        if emotions:
            emotion_sequence.append(emotions[0])
    
    # 统计情绪转换
    if len(emotion_sequence) >= 5:
        for i in range(len(emotion_sequence) - 1):
            from_emotion = emotion_sequence[i]
            to_emotion = emotion_sequence[i + 1]
            
            if from_emotion != to_emotion:
                key = f"{from_emotion}→{to_emotion}"
                # 简化: 只记录主要转换
                pattern = {
                    "id": f"模式_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
                    "type": "emotion",
                    "subtype": "transition",
                    "trigger": f"感到'{from_emotion}'",
                    "action": f"通常转为'{to_emotion}'",
                    "frequency": "情绪转换",
                    "count": 1,
                    "confidence": 0.3,
                    "evidence": [],
                    "created_at": datetime.now().isoformat()
                }
                patterns.append(pattern)
    
    return patterns

def run_pattern_detection():
    """运行完整模式检测"""
    print("🔍 开始模式识别...")
    
    patterns_data = load_patterns()
    memories = load_memories()
    
    if not memories:
        print("⚠️ 无记忆可分析")
        return {"error": "no memories"}
    
    print(f"   加载 {len(memories)} 条记忆")
    
    # 1. 时间模式
    print("   检测时间模式...")
    time_features = extract_time_features(memories)
    time_patterns = detect_time_patterns(time_features)
    print(f"   发现 {len(time_patterns)} 个时间模式")
    
    # 2. 行为模式
    print("   检测行为模式...")
    behavior_patterns = detect_behavior_patterns(memories)
    print(f"   发现 {len(behavior_patterns)} 个行为模式")
    
    # 3. 情绪模式
    print("   检测情绪模式...")
    emotion_patterns = detect_emotion_patterns(memories)
    print(f"   发现 {len(emotion_patterns)} 个情绪模式")
    
    # 合并去重
    all_patterns = time_patterns + behavior_patterns + emotion_patterns
    merged = merge_patterns(patterns_data.get("patterns", []), all_patterns)
    
    # 更新统计
    patterns_data["patterns"] = merged
    patterns_data["stats"] = {
        "time_patterns": len([p for p in merged if p["type"] == "time"]),
        "behavior_patterns": len([p for p in merged if p["type"] == "behavior"]),
        "emotion_patterns": len([p for p in merged if p["type"] == "emotion"]),
        "last_scan": datetime.now().isoformat()
    }
    
    save_patterns(patterns_data)
    
    print(f"✅ 模式识别完成: 共 {len(merged)} 个模式")
    
    return {
        "total": len(merged),
        "time": len(time_patterns),
        "behavior": len(behavior_patterns),
        "emotion": len(emotion_patterns)
    }

def merge_patterns(old, new):
    """合并新旧模式"""
    merged = old.copy()
    
    for np in new:
        exists = False
        for op in merged:
            # 相同类型+触发器=已存在
            if op.get("type") == np.get("type") and op.get("trigger") == np.get("trigger"):
                # 更新
                if np.get("count", 0) > op.get("count", 0):
                    op.update(np)
                exists = True
                break
        
        if not exists:
            merged.append(np)
    
    return merged

def get_pattern_stats():
    """获取模式统计"""
    patterns = load_patterns()
    
    return {
        "total": len(patterns["patterns"]),
        "stats": patterns["stats"],
        "recent": patterns["patterns"][-5:] if patterns["patterns"] else []
    }

def get_patterns_by_type(pattern_type):
    """按类型获取模式"""
    patterns = load_patterns()
    
    return [p for p in patterns["patterns"] if p.get("type") == pattern_type]

# CLI入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 eva_pattern.py run    - 运行模式检测")
        print("  python3 eva_pattern.py stats   - 查看统计")
        print("  python3 eva_pattern.py time    - 时间模式")
        print("  python3 eva_pattern.py behavior - 行为模式")
        print("  python3 eva_pattern.py emotion - 情绪模式")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "run":
        result = run_pattern_detection()
        print(f"结果: {result}")
    
    elif action == "stats":
        stats = get_pattern_stats()
        print("=== 模式统计 ===")
        print(f"总数: {stats['total']}")
        print(f"统计: {stats['stats']}")
    
    elif action == "time":
        patterns = get_patterns_by_type("time")
        print(f"=== 时间模式 ({len(patterns)}个) ===")
        for p in patterns[:10]:
            print(f"  {p['trigger']}: {p['action']}")
    
    elif action == "behavior":
        patterns = get_patterns_by_type("behavior")
        print(f"=== 行为模式 ({len(patterns)}个) ===")
        for p in patterns[:10]:
            print(f"  {p['trigger']}: {p['action']}")
    
    elif action == "emotion":
        patterns = get_patterns_by_type("emotion")
        print(f"=== 情绪模式 ({len(patterns)}个) ===")
        for p in patterns[:10]:
            print(f"  {p['trigger']}: {p['action']}")
    
    else:
        print(f"❌ 未知动作: {action}")
