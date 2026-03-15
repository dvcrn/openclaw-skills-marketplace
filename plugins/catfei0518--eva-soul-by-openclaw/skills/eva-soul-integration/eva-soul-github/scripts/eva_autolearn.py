#!/usr/bin/env python3
"""
夏娃自动学习系统
从交互中自动学习
"""

import os
import json
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
LEARN_FILE = os.path.join(MEMORY_DIR, "autolearn.json")

def load_learn():
    if os.path.exists(LEARN_FILE):
        with open(LEARN_FILE) as f:
            return json.load(f)
    return {
        "patterns": {},      # 学习到的模式
        "preferences": {},   # 用户偏好
        "topics": {},        # 话题偏好
        "responses": {},     # 常见问答
        "history": []        # 学习历史
    }

def save_learn(data):
    with open(LEARN_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def learn(user_input, response):
    """学习用户输入和响应"""
    data = load_learn()
    
    # 学习问答对
    if user_input not in data["responses"]:
        data["responses"][user_input] = {
            "response": response,
            "count": 1,
            "first_seen": datetime.now().isoformat()
        }
    else:
        data["responses"][user_input]["count"] += 1
    
    # 记录历史
    data["history"].append({
        "input": user_input,
        "response": response,
        "time": datetime.now().isoformat()
    })
    
    # 只保留最近100条
    if len(data["history"]) > 100:
        data["history"] = data["history"][-100:]
    
    save_learn(data)
    return True

def find_response(user_input):
    """查找学习到的响应"""
    data = load_learn()
    
    # 精确匹配
    if user_input in data.get("responses", {}):
        return data["responses"][user_input]
    
    # 模糊匹配
    for pattern, info in data.get("responses", {}).items():
        if pattern in user_input or user_input in pattern:
            return info
    
    return None

def learn_preference(key, value):
    """学习用户偏好"""
    data = load_learn()
    data["preferences"][key] = {
        "value": value,
        "learned_at": datetime.now().isoformat()
    }
    save_learn(data)
    return True

def get_preference(key):
    """获取用户偏好"""
    data = load_learn()
    return data.get("preferences", {}).get(key, {})

# 测试
if __name__ == "__main__":
    import sys
    
    data = load_learn()
    print("=== 自动学习系统 ===")
    print(f"学习的问题: {len(data.get('responses', {}))}")
    print(f"用户偏好: {len(data.get('preferences', {}))}")
    print(f"学习历史: {len(data.get('history', {}))}")
    
    # 测试学习
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        learn("你好", "主人好！")
        print("\n测试学习: 你好")
        result = find_response("你好")
        print(f"查找结果: {result}")
