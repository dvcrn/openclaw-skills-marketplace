#!/usr/bin/env python3
"""
夏娃系统Agent Hook Module
可直接被OpenClaw导入使用
"""

import os
import sys

# 添加脚本目录
SCRIPT_DIR = os.path.expanduser("~/.openclaw/workspace/scripts")
sys.path.insert(0, SCRIPT_DIR)

# 导出主要函数
from eva_integrated_final import EVA

# 全局实例
_eva_instance = None

def init_eva(session_id="default"):
    """初始化夏娃系统"""
    global _eva_instance
    _eva_instance = EVA(session_id)
    return _eva_instance

def get_eva():
    """获取夏娃实例"""
    global _eva_instance
    if _eva_instance is None:
        _eva_instance = init_eva()
    return _eva_instance

def process_with_eva(message, session_id="default"):
    """使用夏娃系统处理消息 - 主要接口"""
    eva = get_eva()
    if eva is None:
        return {"response": message, "error": "未初始化"}
    
    try:
        result = eva.process(message)
        return {
            "response": result.get("response", ""),
            "emotion": result.get("emotion", {}),
            "importance": result.get("importance", {}),
            "likes": result.get("likes", {}),
            "session_count": result.get("session_count", 0)
        }
    except Exception as e:
        return {"response": message, "error": str(e)}

def get_eva_context():
    """获取夏娃上下文"""
    eva = get_eva()
    if eva is None:
        return {}
    return {
        "identity": eva.get_identity(),
        "emotion": eva.emotion.get("current", "neutral"),
        "mood": eva.emotion.get("mood", 0.5)
    }

# 导出
__all__ = ["init_eva", "get_eva", "process_with_eva", "get_eva_context", "EVA"]
