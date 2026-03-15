#!/usr/bin/env python3
"""
夏娃工具自动记录系统
自动记录所有工具使用
"""

import os
import sys
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
TOOLS_FILE = os.path.join(MEMORY_DIR, "tools_memory.json")

# 工具关键词映射
TOOL_KEYWORDS = {
    "tavily": "tavily_search",
    "搜索": "tavily_search",
    "web_search": "tavily_search",
    "image": "image_gen",
    "生成图": "image_gen",
    "画": "image_gen",
    "tts": "volcengine_tts",
    "语音": "volcengine_tts",
    "说话": "volcengine_tts",
    "天气": "weather",
    "邮箱": "check_email_163",
    "邮件": "check_email_163",
    "git": "gitea",
    "推送": "gitea",
    "拉取": "gitea",
}

def load_tools():
    if os.path.exists(TOOLS_FILE):
        try:
            with open(TOOLS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"version": "1.0", "tools": {}, "usage": []}

def save_tools(data):
    with open(TOOLS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def detect_tool(message):
    """从消息中检测使用的工具"""
    message_lower = message.lower()
    
    for keyword, tool_name in TOOL_KEYWORDS.items():
        if keyword in message_lower:
            return tool_name
    
    return None

def record_tool_use(tool_name, query="", success=True):
    """记录工具使用"""
    import json
    
    data = load_tools()
    now = datetime.now().isoformat()
    
    # 创建或更新工具
    if tool_name not in data["tools"]:
        data["tools"][tool_name] = {
            "name": tool_name,
            "usage_count": 0,
            "first_used": now,
            "last_used": now,
            "examples": [],
            "category": "other"
        }
    
    tool = data["tools"][tool_name]
    tool["usage_count"] += 1
    tool["last_used"] = now
    
    # 添加示例
    if query and query not in tool["examples"]:
        tool["examples"].append(query)
        if len(tool["examples"]) > 10:
            tool["examples"] = tool["examples"][-10:]
    
    # 记录使用
    data["usage"].append({
        "tool": tool_name,
        "query": query,
        "success": success,
        "timestamp": now
    })
    
    # 保持最近100条
    if len(data["usage"]) > 100:
        data["usage"] = data["usage"][-100:]
    
    save_tools(data)
    return True

def auto_record(message, result=None):
    """自动记录 - 根据消息内容检测并记录"""
    import json
    
    # 检测工具
    tool_name = detect_tool(message)
    
    if tool_name:
        # 提取查询内容
        query = message[:100] if message else ""
        
        # 判断成功与否
        success = result is not None and not str(result).startswith("错误")
        
        record_tool_use(tool_name, query, success)
        return True, tool_name
    
    return False, None

def get_tool_info(tool_name):
    """获取工具信息"""
    import json
    data = load_tools()
    return data.get("tools", {}).get(tool_name)

def get_frequently_used_tools(limit=5):
    """获取常用工具"""
    import json
    data = load_tools()
    tools = data.get("tools", {})
    sorted_tools = sorted(tools.items(), key=lambda x: x[1].get("usage_count", 0), reverse=True)
    return [{"name": n, **i} for n, i in sorted_tools[:limit]]

def get_stats():
    """获取统计"""
    import json
    data = load_tools()
    tools = data.get("tools", {})
    total = sum(t.get("usage_count", 0) for t in tools.values())
    top = max(tools.items(), key=lambda x: x[1].get("usage_count", 0)) if tools else (None, {})
    return {
        "total_tools": len(tools),
        "total_uses": total,
        "most_used": top[0] if top[0] else None,
        "most_used_count": top[1].get("usage_count", 0) if top[0] else 0
    }

# CLI
if __name__ == "__main__":
    import json
    import sys
    
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if action == "record":
        tool = sys.argv[2] if len(sys.argv) > 2 else ""
        query = sys.argv[3] if len(sys.argv) > 3 else ""
        if tool:
            record_tool_use(tool, query)
            print(f"OK: {tool}")
    
    elif action == "auto":
        message = sys.argv[2] if len(sys.argv) > 2 else ""
        success, tool = auto_record(message)
        if success:
            print(f"自动记录: {tool}")
        else:
            print("未检测到工具")
    
    elif action == "frequent":
        for t in get_frequently_used_tools(5):
            print(f"  {t['name']}: {t['usage_count']}次")
    
    elif action == "stats":
        s = get_stats()
        print(f"工具: {s['total_tools']}, 使用: {s['total_uses']}, 最常用: {s['most_used']} ({s['most_used_count']}次)")
    
    elif action == "info":
        tool = sys.argv[2] if len(sys.argv) > 2 else ""
        info = get_tool_info(tool)
        if info:
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            print("NOT_FOUND")
