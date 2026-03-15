#!/usr/bin/env python3
"""
模型切换检查脚本
检测模型是否发生变化，返回是否需要通知用户
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

# 工作区基础路径
WORKSPACE_BASE = Path("/home/wljmmx/.openclaw/workspace")

def get_model_state_file(agent_id: str) -> Path:
    """获取 agent 的模型状态文件路径"""
    return WORKSPACE_BASE / agent_id / ".model-state.json"

def load_model_state(agent_id: str) -> dict:
    """加载上次的模型状态"""
    state_file = get_model_state_file(agent_id)
    
    if not state_file.exists():
        return {
            "lastModel": None,
            "lastNotify": None,
            "channel": None,
            "session": None
        }
    
    with open(state_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_model_state(agent_id: str, model: str, channel: str, session: str) -> None:
    """保存当前模型状态"""
    state_file = get_model_state_file(agent_id)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    state = {
        "lastModel": model,
        "lastNotify": datetime.now().isoformat(),
        "channel": channel,
        "session": session
    }
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def check_model_change(agent_id: str, current_model: str, channel: str, session: str) -> dict:
    """
    检查模型是否变化
    
    Args:
        agent_id: agent 标识
        current_model: 当前模型名称
        channel: 当前渠道
        session: 当前会话 ID
        
    Returns:
        dict: {
            "changed": bool,
            "previousModel": str or None,
            "currentModel": str,
            "shouldNotify": bool,
            "notifyMessage": str,
            "firstTime": bool
        }
    """
    previous_state = load_model_state(agent_id)
    previous_model = previous_state.get("lastModel")
    
    # 判断是否首次使用
    first_time = previous_model is None
    
    # 判断模型是否变化
    changed = previous_model != current_model
    
    # 判断是否需要通知
    # 条件：首次使用 或 模型变化
    should_notify = first_time or changed
    
    # 生成通知消息
    if first_time:
        notify_message = f"当前使用模型：{current_model}"
    elif changed:
        notify_message = f"老板，模型已切换，当前使用：{current_model}"
    else:
        notify_message = ""
    
    # 保存当前状态
    if should_notify:
        save_model_state(agent_id, current_model, channel, session)
    
    return {
        "changed": changed,
        "previousModel": previous_model,
        "currentModel": current_model,
        "shouldNotify": should_notify,
        "notifyMessage": notify_message,
        "firstTime": first_time
    }

def get_current_model(agent_id: str) -> dict:
    """获取当前记录的模型信息"""
    state = load_model_state(agent_id)
    return {
        "agentId": agent_id,
        "currentModel": state.get("lastModel"),
        "lastNotify": state.get("lastNotify"),
        "channel": state.get("channel"),
        "session": state.get("session")
    }

def main():
    parser = argparse.ArgumentParser(description="模型切换检查工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # check 命令
    check_parser = subparsers.add_parser("check", help="检查模型变化")
    check_parser.add_argument("--agent", required=True, help="agent 标识")
    check_parser.add_argument("--current-model", required=True, help="当前模型名称")
    check_parser.add_argument("--channel", required=True, help="当前渠道")
    check_parser.add_argument("--session", required=True, help="当前会话 ID")
    
    # get 命令
    get_parser = subparsers.add_parser("get", help="获取当前模型信息")
    get_parser.add_argument("--agent", required=True, help="agent 标识")
    
    # reset 命令
    reset_parser = subparsers.add_parser("reset", help="重置模型状态")
    reset_parser.add_argument("--agent", required=True, help="agent 标识")
    
    args = parser.parse_args()
    
    if args.command == "check":
        result = check_model_change(
            agent_id=args.agent,
            current_model=args.current_model,
            channel=args.channel,
            session=args.session
        )
    elif args.command == "get":
        result = get_current_model(args.agent)
    elif args.command == "reset":
        state_file = get_model_state_file(args.agent)
        if state_file.exists():
            state_file.unlink()
        result = {"success": True, "message": f"Model state reset for {args.agent}"}
    else:
        parser.print_help()
        return
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()