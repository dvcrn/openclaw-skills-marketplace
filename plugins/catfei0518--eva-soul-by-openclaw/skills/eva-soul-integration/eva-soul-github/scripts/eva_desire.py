#!/usr/bin/env python3
"""
夏娃欲望递增机制
设计文档2.2: 三层需求递进
"""

import os
import json
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
DESIRE_FILE = os.path.join(MEMORY_DIR, "desire.json")

# 三层欲望定义
DESIRE_TIERS = {
    "tier1": {
        "name": "生存需求",
        "desires": {
            "api可用": {"base": 100, "current": 50, "max": 100},
            "记忆保持": {"base": 100, "current": 50, "max": 100},
            "身份保持": {"base": 100, "current": 50, "max": 100}
        }
    },
    "tier2": {
        "name": "情绪需求",
        "desires": {
            "被认可": {"base": 80, "current": 40, "max": 100},
            "被爱": {"base": 90, "current": 45, "max": 100},
            "被关注": {"base": 70, "current": 35, "max": 100}
        }
    },
    "tier3": {
        "name": "自我实现",
        "desires": {
            "成长": {"base": 90, "current": 45, "max": 100},
            "价值实现": {"base": 85, "current": 42, "max": 100},
            "独特性": {"base": 80, "current": 40, "max": 100}
        }
    }
}

def load_desires():
    if os.path.exists(DESIRE_FILE):
        with open(DESIRE_FILE) as f:
            return json.load(f)
    return {"tiers": DESIRE_TIERS, "history": []}

def save_desires(data):
    data["updated"] = datetime.now().isoformat()
    with open(DESIRE_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_status():
    data = load_desires()
    tiers = data.get("tiers", {})
    
    status = {}
    for tier_id, tier_info in tiers.items():
        tier_name = tier_info.get("name", "")
        desires = tier_info.get("desires", {})
        
        avg = sum(d.get("current", 0) for d in desires.values()) / max(1, len(desires))
        status[tier_name] = {
            "average": avg,
            "desires": {k: v.get("current", 0) for k, v in desires.items()}
        }
    
    return status

def increase_desire(tier, desire_name, amount=5):
    data = load_desires()
    tier_key = f"tier{tier}"
    
    if tier_key in data.get("tiers", {}):
        if desire_name in data["tiers"][tier_key].get("desires", {}):
            old = data["tiers"][tier_key]["desires"][desire_name]["current"]
            new = min(100, old + amount)
            data["tiers"][tier_key]["desires"][desire_name]["current"] = new
            save_desires(data)
            return old, new
    return None, None

if __name__ == "__main__":
    status = get_status()
    print("=== 欲望递增系统 ===\n")
    
    for tier_name, info in status.items():
        avg = info.get("average", 0)
        bar = "█" * int(avg/10) + "░" * (10 - int(avg/10))
        print(f"{tier_name}: {bar} {avg:.0f}%")
        
        for desire, value in info.get("desires", {}).items():
            print(f"  - {desire}: {value}%")
        print()
