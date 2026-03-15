#!/usr/bin/env python3
"""
夏娃之魂总入口 - 每次对话自动调用
"""

import os
import sys
import json

# 添加路径
EVA_SOUL_PATH = os.path.expanduser("~/.openclaw/workspace/skills/eva-soul/eva-soul-github/scripts")
sys.path.insert(0, EVA_SOUL_PATH)

def call_eva_soul(message, context=""):
    """调用夏娃之魂总入口"""
    try:
        # 导入EVA类
        from eva_integrated_final import EVA
        
        # 创建EVA实例
        eva = EVA()
        
        # 处理消息
        result = eva.process(message)
        
        return {
            "success": True,
            "response": result,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "夏娃之魂调用失败，但你可以继续回复"
        }

def get_eva_status():
    """获取夏娃之魂状态"""
    try:
        from eva_integrated_final import EVA
        eva = EVA()
        status = eva.get_status()
        return {"success": True, "status": status}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="夏娃之魂总入口")
    parser.add_argument("command", choices=["call", "status"])
    parser.add_argument("--message", "-m", help="消息内容")
    parser.add_argument("--context", "-c", help="上下文")
    
    args = parser.parse_args()
    
    if args.command == "call":
        if not args.message:
            print("错误: 需要 --message 参数")
            sys.exit(1)
        result = call_eva_soul(args.message, args.context or "")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.command == "status":
        result = get_eva_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
