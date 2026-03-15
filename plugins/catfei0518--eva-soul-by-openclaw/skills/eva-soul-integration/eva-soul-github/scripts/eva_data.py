#!/usr/bin/env python3
"""
夏娃统一数据访问模块
统一所有子系统的数据存储路径
"""

import os
import json

# 统一的数据目录
DATA_DIR = os.path.expanduser("~/.openclaw/workspace/memory")

# 统一的数据文件路径
FILES = {
    "personality": os.path.join(DATA_DIR, "personality.json"),
    "emotion": os.path.join(DATA_DIR, "emotion.json"),
    "motivation": os.path.join(DATA_DIR, "motivation.json"),
    "values_social": os.path.join(DATA_DIR, "values_social.json"),
    "self_cognition": os.path.join(DATA_DIR, "self_cognition.json"),
    "decision": os.path.join(DATA_DIR, "decision.json"),
    "short": os.path.join(DATA_DIR, "short"),
    "medium": os.path.join(DATA_DIR, "medium"),
    "long": os.path.join(DATA_DIR, "long"),
}

def ensure_dirs():
    """确保所有目录存在"""
    for key, path in FILES.items():
        if key in ["short", "medium", "long"]:
            os.makedirs(path, exist_ok=True)

def load(key, default=None):
    """加载数据"""
    ensure_dirs()
    filepath = FILES.get(key)
    if not filepath or not filepath.endswith('.json'):
        return default
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save(key, data):
    """保存数据"""
    ensure_dirs()
    filepath = FILES.get(key)
    if not filepath or not filepath.endswith('.json'):
        return False
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

def get_path(key):
    """获取文件路径"""
    return FILES.get(key)

# 便捷函数
def load_personality():
    return load("personality", {})

def save_personality(data):
    return save("personality", data)

def load_emotion():
    return load("emotion", {"current": "neutral", "mood": 0.5})

def save_emotion(data):
    return save("emotion", data)

def load_motivation():
    return load("motivation", {})

def save_motivation(data):
    return save("motivation", data)

def load_values():
    return load("values_social", {})

def save_values(data):
    return save("values_social", data)

def load_self():
    return load("self_cognition", {})

def save_self(data):
    return save("self_cognition", data)
