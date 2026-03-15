#!/usr/bin/env python3
"""
夏娃情感预测系统
基于向量相似度、时间规律、上下文趋势预测情绪

不依赖关键词，基于多维度推理
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from collections import Counter

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
PREDICT_FILE = os.path.join(MEMORY_DIR, "emotion_predict.json")

def load_predict_config():
    """加载预测配置"""
    if os.path.exists(PREDICT_FILE):
        with open(PREDICT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {
        "version": "1.0",
        "updated_at": None,
        "predictions": [],  # 历史预测记录
        "models": {
            "vector": {"weight": 0.5, "enabled": True},   # 提高向量权重
            "time": {"weight": 0.15, "enabled": True},   # 降低时间权重
            "context": {"weight": 0.15, "enabled": True},
            "event": {"weight": 0.2, "enabled": True}
        }
    }

def save_predict_config(data):
    """保存预测配置"""
    data["updated_at"] = datetime.now().isoformat()
    with open(PREDICT_FILE, 'w', encoding='utf-8') as f:
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

def get_time_features():
    """获取时间特征"""
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0=周一
    
    # 时段映射
    time_periods = {
        "early_morning": (5, 8),
        "morning": (8, 11),
        "noon": (11, 13),
        "afternoon": (13, 17),
        "evening": (17, 20),
        "night": (20, 23),
        "late_night": (23, 5)
    }
    
    period = "unknown"
    for name, (start, end) in time_periods.items():
        if start <= hour < end:
            period = name
            break
    
    # 星期特征
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday_name = weekday_names[weekday]
    is_weekend = weekday >= 5
    
    return {
        "hour": hour,
        "period": period,
        "weekday": weekday,
        "weekday_name": weekday_name,
        "is_weekend": is_weekend
    }

def predict_by_time(time_features):
    """基于时间规律预测情绪"""
    hour = time_features["hour"]
    weekday = time_features["weekday"]
    period = time_features["period"]
    is_weekend = time_features["is_weekend"]
    
    emotions = []
    confidence = 0.3
    
    # 1. 时段预测
    if period == "early_morning":
        emotions.append({"emotion": "清醒", "confidence": 0.6})
    elif period == "morning":
        emotions.append({"emotion": "忙碌", "confidence": 0.7})
    elif period == "noon":
        emotions.append({"emotion": "放松", "confidence": 0.5})
    elif period == "afternoon":
        emotions.append({"emotion": "专注", "confidence": 0.6})
    elif period == "evening":
        emotions.append({"emotion": "放松", "confidence": 0.6})
    elif period == "night":
        emotions.append({"emotion": "疲惫", "confidence": 0.7})
    elif period == "late_night":
        emotions.append({"emotion": "困倦", "confidence": 0.8})
    
    # 2. 星期预测
    if weekday == 0:  # 周一
        emotions.append({"emotion": "压力", "confidence": 0.6})
    elif weekday == 4:  # 周五
        emotions.append({"emotion": "期待", "confidence": 0.5})
    elif is_weekend:
        emotions.append({"emotion": "放松", "confidence": 0.7})
    
    # 3. 深夜工作
    if hour >= 22 or hour <= 5:
        emotions.append({"emotion": "疲惫", "confidence": 0.8})
    
    return emotions

def predict_by_vector(current_message, memories):
    """基于向量相似度预测 - 不依赖关键词"""
    # 使用简单文本相似度代替向量
    
    # 预处理当前消息
    msg = current_message.lower()
    bigrams = set([msg[i:i+2] for i in range(len(msg)-1)])
    
    best_matches = []
    
    # 取所有有情感标签的记忆
    emotion_memories = [m for m in memories if m.get("tags", {}).get("emotion")]
    
    for mem in emotion_memories:
        mem_content = mem.get("content", "").lower()
        
        # 字符级bigram相似度
        mem_bigrams = set([mem_content[i:i+2] for i in range(len(mem_content)-1)])
        
        if len(bigrams) > 0 and len(mem_bigrams) > 0:
            overlap = len(bigrams & mem_bigrams)
            similarity = overlap / max(len(bigrams), len(mem_bigrams), 1)
            
            if similarity > 0.12:
                emotion = mem.get("tags", {}).get("emotion", ["平静"])[0]
                best_matches.append({
                    "emotion": emotion,
                    "similarity": similarity,
                    "content": mem.get("content", "")[:50]
                })
    
    # 排序取top
    best_matches.sort(key=lambda x: -x["similarity"])
    
    # 提取主要情绪
    if best_matches[:3]:
        top3 = best_matches[:3]
        emotions = [m["emotion"] for m in top3]
        counter = Counter(emotions)
        most_common = counter.most_common(1)[0]
        
        avg_similarity = sum(m["similarity"] for m in top3) / len(top3)
        
        return [{
            "emotion": most_common[0],
            "confidence": min(0.3 + avg_similarity * 2, 0.9),
            "matches": len(best_matches)
        }]
    
    return []

def predict_by_context(memories):
    """基于上下文趋势预测 - 看最近几条的整体情绪"""
    # 取最近10条记忆的情感
    recent = []
    for mem in reversed(memories[-20:]):
        emotion = mem.get("tags", {}).get("emotion", [])
        if emotion:
            recent.append(emotion[0])
    
    if len(recent) < 3:
        return []
    
    # 分析趋势
    recent_emotions = recent[:5]  # 最近5条
    
    # 统计
    counter = Counter(recent_emotions)
    
    # 判断趋势
    if len(set(recent_emotions)) == 1:
        # 情绪稳定
        dominant = counter.most_common(1)[0]
        return [{
            "emotion": dominant[0],
            "confidence": 0.6,
            "trend": "stable"
        }]
    
    # 检查是否有负面趋势
    negative = ["难过", "疲惫", "焦虑", "生气", "恐惧"]
    positive = ["开心", "爱", "期待", "温暖"]
    
    negative_count = sum(1 for e in recent_emotions if e in negative)
    positive_count = sum(1 for e in recent_emotions if e in positive)
    
    if negative_count >= 3:
        return [{
            "emotion": "需要关怀",
            "confidence": 0.7,
            "trend": "declining"
        }]
    elif positive_count >= 3:
        return [{
            "emotion": "愉快",
            "confidence": 0.6,
            "trend": "rising"
        }]
    
    return []

def detect_event(current_message):
    """事件推断 - 检测特定场景"""
    events = []
    
    # 检测特定场景词（不用情绪词，用场景词）
    scene_patterns = {
        "刚完成": {"emotion": "放松", "confidence": 0.7},
        "要开会": {"emotion": "紧张", "confidence": 0.6},
        "开完会": {"emotion": "疲惫", "confidence": 0.7},
        "下班": {"emotion": "放松", "confidence": 0.7},
        "上班": {"emotion": "忙碌", "confidence": 0.6},
        "出差": {"emotion": "忙碌", "confidence": 0.6},
        "放假": {"emotion": "期待", "confidence": 0.8},
        "生病": {"emotion": "不适", "confidence": 0.8},
        "吵架": {"emotion": "生气", "confidence": 0.8},
        "完成": {"emotion": "满足", "confidence": 0.7},
        "解决": {"emotion": "轻松", "confidence": 0.7}
    }
    
    for pattern, result in scene_patterns.items():
        if pattern in current_message:
            events.append(result)
    
    return events

def predict_emotion(current_message, memories=None):
    """
    综合预测情绪
    
    不依赖关键词，使用多维度推理:
    1. 向量相似度 - 和历史情绪记忆比较
    2. 时间规律 - 根据时段/星期
    3. 上下文趋势 - 最近几条消息的整体情绪
    4. 事件推断 - 特定场景自动推理
    """
    config = load_predict_config()
    
    if memories is None:
        memories = load_memories()
    
    results = {}
    
    # 1. 向量相似度预测
    if config["models"]["vector"]["enabled"]:
        vector_result = predict_by_vector(current_message, memories)
        if vector_result:
            results["vector"] = vector_result[0]
    
    # 2. 时间规律预测
    if config["models"]["time"]["enabled"]:
        time_features = get_time_features()
        time_result = predict_by_time(time_features)
        if time_result:
            results["time"] = time_result[0]
    
    # 3. 上下文趋势
    if config["models"]["context"]["enabled"]:
        context_result = predict_by_context(memories)
        if context_result:
            results["context"] = context_result[0]
    
    # 4. 事件推断
    if config["models"]["event"]["enabled"]:
        event_result = detect_event(current_message)
        if event_result:
            results["event"] = event_result[0]
    
    # 综合决策
    if not results:
        return {"emotion": "平静", "confidence": 0.5, "method": "default"}
    
    # 加权投票
    weights = {
        "vector": config["models"]["vector"]["weight"],
        "time": config["models"]["time"]["weight"],
        "context": config["models"]["context"]["weight"],
        "event": config["models"]["event"]["weight"]
    }
    
    # 收集所有预测
    all_predictions = []
    for method, pred in results.items():
        all_predictions.append({
            "emotion": pred["emotion"],
            "confidence": pred["confidence"] * weights.get(method, 0.25),
            "method": method
        })
    
    # 按置信度排序
    all_predictions.sort(key=lambda x: -x["confidence"])
    
    # 取最高
    best = all_predictions[0]
    
    # 构建建议
    suggestion = get_suggestion(best["emotion"])
    
    return {
        "emotion": best["emotion"],
        "confidence": best["confidence"],
        "method": best["method"],
        "all_predictions": results,
        "suggestion": suggestion,
        "timestamp": datetime.now().isoformat()
    }

def get_suggestion(emotion):
    """根据预测情绪给出建议"""
    suggestions = {
        "疲惫": "关心一下主人，提醒休息",
        "困倦": "提醒主人该睡觉了",
        "忙碌": "尽量简洁，少打扰",
        "压力": "给主人加油鼓励",
        "需要关怀": "主动关心，表达温暖",
        "焦虑": "安慰主人，一切会好的",
        "难过": "陪伴主人，倾听",
        "生气": "小心应对，不惹麻烦",
        "紧张": "帮助放松",
        "放松": "可以正常聊天",
        "愉快": "积极回应",
        "期待": "支持主人的计划",
        "开心": "一起开心",
        "满足": "认可主人的成就",
        "平静": "正常交流"
    }
    
    return suggestions.get(emotion, "正常交流")

def get_recent_predictions(limit=10):
    """获取最近的预测记录"""
    config = load_predict_config()
    return config["predictions"][-limit:]

# CLI入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 eva_emotion_predict.py predict <消息>  - 预测情绪")
        print("  python3 eva_emotion_predict.py time              - 时间特征")
        print("  python3 eva_emotion_predict.py recent            - 最近预测")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "predict":
        message = sys.argv[2] if len(sys.argv) > 2 else "今天工作怎么样"
        result = predict_emotion(message)
        print("=== 情感预测结果 ===")
        print(f"预测情绪: {result['emotion']}")
        print(f"置信度: {result['confidence']:.0%}")
        print(f"预测方法: {result['method']}")
        print(f"建议: {result['suggestion']}")
    
    elif action == "time":
        features = get_time_features()
        print("=== 当前时间特征 ===")
        print(f"小时: {features['hour']}")
        print(f"时段: {features['period']}")
        print(f"星期: {features['weekday_name']}")
        print(f"是否周末: {features['is_weekend']}")
        
        # 测试时间预测
        result = predict_by_time(features)
        print(f"\n时间预测: {result}")
    
    elif action == "recent":
        recent = get_recent_predictions()
        print("=== 最近预测 ===")
        for r in recent:
            print(f"  {r.get('emotion')} ({r.get('method')}) - {r.get('timestamp', '')[:16]}")
    
    else:
        print(f"❌ 未知动作: {action}")
