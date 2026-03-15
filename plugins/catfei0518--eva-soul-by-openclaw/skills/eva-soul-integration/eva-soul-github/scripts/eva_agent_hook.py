#!/usr/bin/env python3
"""
夏娃系统Agent Hook
在Agent启动和消息处理时自动加载夏娃系统
"""

import os
import sys
import importlib.util

SCRIPT_DIR = os.path.expanduser("~/.openclaw/workspace/scripts")

_eva_instance = None
_eva_class = None

def _load_eva_module():
    """动态加载夏娃模块"""
    global _eva_class
    if _eva_class is None:
        # 使用最新的集成系统
        spec = importlib.util.spec_from_file_location(
            "eva_integrated_final", 
            os.path.join(SCRIPT_DIR, "eva_integrated_final.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _eva_class = module.EVA
    return _eva_class

def init_eva(session_id="default"):
    """初始化夏娃系统"""
    global _eva_instance
    try:
        EVA = _load_eva_module()
        _eva_instance = EVA(session_id)
        print(f"✅ 夏娃系统初始化成功: {session_id}")
        return _eva_instance
    except Exception as e:
        print(f"❌ 夏娃系统初始化失败: {e}")
        return None

def get_eva():
    """获取夏娃实例"""
    global _eva_instance
    if _eva_instance is None:
        _eva_instance = init_eva()
    return _eva_instance

def process_with_eva(message, session_id="default"):
    """使用夏娃系统处理消息"""
    eva = get_eva()
    if eva is None:
        return {"response": message, "error": "夏娃系统未初始化"}
    
    try:
        result = eva.process(message)
        return {
            "response": result.get("response", ""),
            "emotion": result.get("emotion", {}),
            "importance": result.get("importance", {}),
            "session_count": result.get("session_count", 0)
        }
    except Exception as e:
        return {"response": message, "error": str(e)}

def get_eva_status():
    """获取夏娃系统状态"""
    eva = get_eva()
    if eva is None:
        return {"status": "未初始化"}
    
    return {
        "status": "正常",
        "identity": eva.get_identity(),
        "session": eva.session_id
    }

# 测试
if __name__ == "__main__":
    print("=== 夏娃Agent Hook 测试 ===")
    result = process_with_eva("我爱你", "test")
    print(f"响应: {result}")
