#!/usr/bin/env python3
"""
夏娃工具自动记录装饰器
在工具函数上使用 @auto_record 装饰器自动记录
"""

import os
import json
from datetime import datetime
from functools import wraps

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
TOOLS_FILE = os.path.join(MEMORY_DIR, "tools_memory.json")

# 工具关键词映射
TOOL_KEYWORDS = {
    "tavily": "tavily_search",
    "搜索": "tavily_search",
    "web_search": "tavily_search",
    "image": "image_gen",
    "生成图": "image_gen",
    "画图": "image_gen",
    "tts": "volcengine_tts",
    "语音": "volcengine_tts",
    "说话": "volcengine_tts",
    "天气": "weather",
    "邮箱": "check_email_163",
    "邮件": "check_email_163",
    "git": "gitea",
    "推送": "gitea",
    "拉取": "gitea",
    "浏览器": "browser",
    "browser": "browser",
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

def detect_tool_name(tool_name_or_message):
    """检测工具名"""
    # 如果直接传入工具名
    if isinstance(tool_name_or_message, str):
        msg = tool_name_or_message.lower()
        for keyword, tool in TOOL_KEYWORDS.items():
            if keyword in msg:
                return tool
        return tool_name_or_message
    return "unknown"

def record(tool_name, query="", success=True, result_preview=""):
    """记录工具使用"""
    data = load_tools()
    now = datetime.now().isoformat()
    
    # 工具不存在则创建
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
        tool["examples"].append(query[:100])
        if len(tool["examples"]) > 10:
            tool["examples"] = tool["examples"][-10:]
    
    # 记录使用历史
    data["usage"].append({
        "tool": tool_name,
        "query": query[:100] if query else "",
        "success": success,
        "result_preview": result_preview[:50] if result_preview else "",
        "timestamp": now
    })
    
    if len(data["usage"]) > 100:
        data["usage"] = data["usage"][-100:]
    
    save_tools(data)
    return True

def auto_record(tool_name=None, query=""):
    """
    装饰器/函数，自动记录工具使用
    
    用法1 - 装饰器:
        @auto_record("tool_name")
        def my_tool():
            ...
    
    用法2 - 函数:
        auto_record("tool_name", "查询内容")
        auto_record(tool_name="image_gen", query="生成女孩")
    """
    # 如果是装饰器用法
    if callable(tool_name):
        # @auto_record() 不带参数
        func = tool_name
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # 自动检测工具名
            tool = func.__name__
            query = str(args[0])[:100] if args else ""
            record(tool, query, True)
            return result
        return wrapper
    
    # 函数用法
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # 使用传入的工具名
            name = tool_name or func.__name__
            q = query or (str(args[0])[:100] if args else "")
            record(name, q, True, str(result)[:50] if result else "")
            return result
        return wrapper
    
    # 如果tool_name是函数，说明是装饰器 @auto_record
    if callable(tool_name):
        return decorator(tool_name)
    
    # 如果是字符串，返回装饰器
    return decorator

def get_stats():
    """获取统计"""
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

# 便捷函数
def record_tool(tool_name, query=""):
    """快速记录工具使用"""
    return record(tool_name, query, True)

def record_search(query):
    """记录搜索使用"""
    return record("tavily_search", query, True)

def record_image(query):
    """记录图像生成使用"""
    return record("image_gen", query, True)

def record_voice(text):
    """记录语音使用"""
    return record("volcengine_tts", text, True)

def record_email(action):
    """记录邮箱使用"""
    return record("check_email_163", action, True)
