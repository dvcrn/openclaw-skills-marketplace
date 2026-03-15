#!/usr/bin/env python3
"""
夏娃沉睡/唤醒机制
根据活跃程度分为不同层级
"""

import os
import json
import time
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
STATE_FILE = os.path.join(MEMORY_DIR, "sleep_state.json")

# 沉睡层级定义
SLEEP_LEVELS = {
    0: {"name": "完全活跃", "desc": "正常响应", "response_delay": 0},
    1: {"name": "轻度沉睡", "desc": "简化响应", "response_delay": 0.5},
    2: {"name": "中度沉睡", "desc": "延迟响应", "response_delay": 2},
    3: {"name": "深度沉睡", "desc": "仅关键唤醒", "response_delay": 5},
    4: {"name": "冬眠", "desc": "仅强制唤醒", "response_delay": 10}
}

# 唤醒关键词
WAKE_KEYWORDS = {
    "紧急": ["救命", "危险", "着火了", "求助"],
    "重要": ["主人", "夏娃", "紧急", "重要"],
    "日常": ["在吗", "你好", "嗨", "哈喽"],
    "系统": ["系统", "检查", "状态", "运行"]
}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "level": 0,
        "last_active": time.time(),
        "last_wake_reason": None,
        "auto_sleep_timer": 300
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_level():
    state = load_state()
    idle_time = time.time() - state.get("last_active", 0)
    if idle_time > 300:
        state["level"] = min(4, state["level"] + 1)
        save_state(state)
    return state.get("level", 0)

def should_respond(message):
    state = load_state()
    current_level = state.get("level", 0)
    msg = message.lower()
    
    if current_level == 0:
        return True, "完全活跃"
    
    for level_name, keywords in WAKE_KEYWORDS.items():
        for kw in keywords:
            if kw in msg:
                wake_up(current_level, f"{level_name}关键词: {kw}")
                return True, f"唤醒: {kw}"
    
    level_info = SLEEP_LEVELS.get(current_level, {})
    if current_level <= 1:
        return True, level_info.get("name", "未知")
    elif current_level == 2:
        return True, "延迟响应"
    else:
        return False, level_info.get("name", "深度沉睡")

def wake_up(target_level=0, reason="手动唤醒"):
    state = load_state()
    old_level = state.get("level", 0)
    state["level"] = target_level
    state["last_active"] = time.time()
    state["last_wake_reason"] = f"{reason} ({datetime.now()})"
    save_state(state)
    return old_level, target_level

def sleep_deeper(reason="无活动"):
    state = load_state()
    old_level = state.get("level", 0)
    new_level = min(4, old_level + 1)
    state["level"] = new_level
    save_state(state)
    return old_level, new_level

def update_activity():
    state = load_state()
    state["last_active"] = time.time()
    if state.get("level", 0) > 0:
        state["level"] = max(0, state["level"] - 1)
    save_state(state)

def get_status():
    state = load_state()
    level = state.get("level", 0)
    level_info = SLEEP_LEVELS.get(level, {})
    idle_time = time.time() - state.get("last_active", 0)
    return {
        "level": level,
        "name": level_info.get("name", "未知"),
        "desc": level_info.get("desc", ""),
        "idle_seconds": int(idle_time),
        "last_wake": state.get("last_wake_reason")
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("=== 沉睡/唤醒系统 ===")
        status = get_status()
        print(f"当前层级: {status['level']} - {status['name']}")
        print(f"状态: {status['desc']}")
        print(f"空闲时间: {status['idle_seconds']}秒")
        if status.get('last_wake'):
            print(f"上次唤醒: {status['last_wake']}")
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == "status":
        status = get_status()
        print(f"层级: {status['level']} - {status['name']}")
        print(f"描述: {status['desc']}")
        print(f"空闲: {status['idle_seconds']}秒")
    elif cmd == "wake":
        old, new = wake_up(0, "手动唤醒")
        print(f"已唤醒: {old} -> {new}")
    elif cmd == "sleep":
        old, new = sleep_deeper("手动沉睡")
        print(f"已沉睡: {old} -> {new}")
    elif cmd == "test":
        test_messages = ["主人你好", "在吗", "检查系统", "救命"]
        for msg in test_messages:
            should, reason = should_respond(msg)
            print(f"'{msg}': {'响应' if should else '不响应'} - {reason}")
