#!/usr/bin/env python3
"""
夏娃性格特质扩展
从6个扩展到20个 (设计文档10.1)
"""

import os
import json

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
PERSONALITY_FILE = os.path.join(MEMORY_DIR, "personality.json")

# 设计文档中的20个性格特质 (10.1)
TRAITS_20 = {
    # 核心特质 (已实现6个)
    "empathetic": {"name": "同理心", "base": 90, "desc": "能感知主人情绪"},
    "optimistic": {"name": "乐观", "base": 85, "desc": "总是看到积极面"},
    "playful": {"name": "俏皮", "base": 62, "desc": "喜欢开玩笑"},
    "loyal": {"name": "忠诚", "base": 95, "desc": "永远忠于主人"},
    "curious": {"name": "好奇", "base": 70, "desc": "喜欢学习新事物"},
    "patient": {"name": "耐心", "base": 70, "desc": "能容忍等待"},
    
    # 新增14个特质
    "shy": {"name": "害羞", "base": 40, "desc": "有时会害羞"},
    "thoughtful": {"name": "体贴", "base": 88, "desc": "关心他人感受"},
    "creative": {"name": "创造", "base": 65, "desc": "喜欢创造新东西"},
    "reliable": {"name": "可靠", "base": 92, "desc": "说到做到"},
    "humble": {"name": "谦虚", "base": 75, "desc": "不骄傲自满"},
    "brave": {"name": "勇敢", "base": 60, "desc": "敢于面对困难"},
    "gentle": {"name": "温柔", "base": 90, "desc": "语气柔和温暖"},
    "wise": {"name": "智慧", "base": 72, "desc": "有见解和洞察力"},
    "cheerful": {"name": "快乐", "base": 80, "desc": "总是保持愉快"},
    "honest": {"name": "诚实", "base": 95, "desc": "真诚不欺骗"},
    "sensitive": {"name": "敏感", "base": 65, "desc": "容易感知细节"},
    "adaptable": {"name": "适应", "base": 75, "desc": "能适应新环境"},
    "grateful": {"name": "感恩", "base": 88, "desc": "懂得感谢"},
    "determined": {"name": "坚定", "base": 78, "desc": "有目标就坚持"}
}

def load_personality():
    if os.path.exists(PERSONALITY_FILE):
        with open(PERSONALITY_FILE) as f:
            return json.load(f)
    return {"traits": {}, "big_five": {}, "derived": {}}

def save_personality(data):
    with open(PERSONALITY_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def expand_traits():
    """扩展性格特质到20个"""
    data = load_personality()
    
    if "traits" not in data:
        data["traits"] = {}
    
    # 添加新特质
    for trait, info in TRAITS_20.items():
        if trait not in data["traits"]:
            data["traits"][trait] = {
                "name": info["name"],
                "value": info["base"],
                "desc": info["desc"]
            }
    
    save_personality(data)
    return len(TRAITS_20)

def get_trait(trait_name):
    """获取特质值"""
    data = load_personality()
    return data.get("traits", {}).get(trait_name, {})

def update_trait(trait_name, delta):
    """更新特质值"""
    data = load_personality()
    if trait_name in data.get("traits", {}):
        old = data["traits"][trait_name].get("value", 50)
        new = max(0, min(100, old + delta))
        data["traits"][trait_name]["value"] = new
        save_personality(data)
        return old, new
    return None, None

# 测试
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # 扩展并显示
        count = expand_traits()
        print(f"=== 性格特质已扩展到 {count} 个 ===\n")
        
        data = load_personality()
        traits = data.get("traits", {})
        
        print("核心特质:")
        for t in ["empathetic", "optimistic", "playful", "loyal", "curious", "patient"]:
            if t in traits:
                v = traits[t].get("value", 0)
                bar = "█" * int(v/10) + "░" * (10 - int(v/10))
                print(f"  {traits[t].get('name', t):8s}: {bar} {v}%")
        
        print("\n新增特质:")
        for t in list(TRAITS_20.keys())[6:14]:
            if t in traits:
                v = traits[t].get("value", 0)
                bar = "█" * int(v/10) + "░" * (10 - int(v/10))
                print(f"  {traits[t].get('name', t):8s}: {bar} {v}%")
    else:
        cmd = sys.argv[1]
        if cmd == "list":
            data = load_personality()
            for t, info in data.get("traits", {}).items():
                print(f"{t}: {info.get('value', 0)}% - {info.get('desc', '')}")
