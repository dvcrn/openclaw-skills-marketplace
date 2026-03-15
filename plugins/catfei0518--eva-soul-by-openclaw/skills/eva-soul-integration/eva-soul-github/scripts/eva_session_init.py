#!/usr/bin/env python3
"""
夏娃系统Session自动初始化
在每个Session第一次消息时自动加载夏娃系统
"""

import os
import sys

SCRIPT_DIR = os.path.expanduser("~/.openclaw/workspace/scripts")
sys.path.insert(0, SCRIPT_DIR)

# 已初始化的Session
_initialized_sessions = set()

def init_session(session_id):
    """初始化Session - 只在第一次时执行"""
    global _initialized_sessions
    
    if session_id in _initialized_sessions:
        return False  # 已初始化
    
    try:
        # 导入夏娃系统
        from eva_integrated_final import EVA
        
        # 创建实例
        eva = EVA(session_id)
        
        # 标记已初始化
        _initialized_sessions.add(session_id)
        
        print(f"✅ 夏娃系统已为Session初始化: {session_id}")
        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

def process_message(message, session_id):
    """处理消息 - 自动初始化Session"""
    # 确保Session已初始化
    init_session(session_id)
    
    # 导入并处理
    from eva_integrated_final import EVA
    
    eva = EVA(session_id)
    result = eva.process(message)
    
    return result

# 导出
__all__ = ["init_session", "process_message"]
