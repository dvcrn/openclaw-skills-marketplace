#!/usr/bin/env python3
"""
夏娃工具记忆系统
"""

import os
import json
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
TOOLS_FILE = os.path.join(MEMORY_DIR, "tools_memory.json")

def load_tools():
    if os.path.exists(TOOLS_FILE):
        with open(TOOLS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": "1.0", "tools": {}, "usage": []}

def save_tools(data):
    with open(TOOLS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def record_tool_use(tool_name, query):
    data = load_tools()
    now = datetime.now().isoformat()
    
    if tool_name not in data["tools"]:
        data["tools"][tool_name] = {
            "name": tool_name, "usage_count": 0, "first_used": now,
            "last_used": now, "examples": [], "category": "other"
        }
    
    tool = data["tools"][tool_name]
    tool["usage_count"] += 1
    tool["last_used"] = now
    
    if query and query not in tool["examples"]:
        tool["examples"].append(query)
        if len(tool["examples"]) > 10:
            tool["examples"] = tool["examples"][-10:]
    
    data["usage"].append({"tool": tool_name, "query": query, "timestamp": now})
    if len(data["usage"]) > 100:
        data["usage"] = data["usage"][-100:]
    
    save_tools(data)
    return f"OK: {tool_name} ({tool['usage_count']})"

def get_tool_info(tool_name):
    data = load_tools()
    return data.get("tools", {}).get(tool_name)

def get_frequently_used_tools(limit=5):
    data = load_tools()
    tools = data.get("tools", {})
    sorted_tools = sorted(tools.items(), key=lambda x: x[1].get("usage_count", 0), reverse=True)
    return [{"name": n, **i} for n, i in sorted_tools[:limit]]

def get_stats():
    data = load_tools()
    tools = data.get("tools", {})
    total = sum(t.get("usage_count", 0) for t in tools.values())
    top = max(tools.items(), key=lambda x: x[1].get("usage_count", 0)) if tools else (None, {})
    return {"total": len(tools), "uses": total, "top": top[0] if top[0] else "None", "count": top[1].get("usage_count", 0) if top[0] else 0}

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if action == "record":
        print(record_tool_use(sys.argv[2] if len(sys.argv) > 2 else "", sys.argv[3] if len(sys.argv) > 3 else ""))
    elif action == "frequent":
        for t in get_frequently_used_tools(int(sys.argv[2]) if len(sys.argv) > 2 else 5):
            print(f"  {t['name']}: {t['usage_count']}次")
    elif action == "stats":
        s = get_stats()
        print(f"工具: {s['total']}, 使用: {s['uses']}, 最常用: {s['top']} ({s['count']}次)")
    elif action == "info":
        info = get_tool_info(sys.argv[2] if len(sys.argv) > 2 else "")
        if info:
            print(f"名称: {info['name']}, 使用: {info['usage_count']}次, 示例: {info.get('examples', [])[:3]}")
