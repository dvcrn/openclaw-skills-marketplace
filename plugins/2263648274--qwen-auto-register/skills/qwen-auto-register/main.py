#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen 自动注册技能 - 主入口
支持预测性自动切换，避免 API 额度超限

依赖：pip install auto-register
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

# 设置控制台输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 尝试导入 auto_register 包
try:
    from auto_register.main import run_cli
    AUTO_REGISTER_AVAILABLE = True
except ImportError:
    AUTO_REGISTER_AVAILABLE = False
    print("[ERROR] 未找到 auto-register 包")
    print("请运行：pip install auto-register")
    sys.exit(1)


AUTH_PROFILES_PATH = Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json"
USAGE_STATS_PATH = Path.home() / ".openclaw" / "agents" / "main" / "agent" / "usage-stats.json"

# Qwen 每日请求限制（保守估计）
DAILY_REQUEST_LIMIT = 50
# 切换阈值：达到 80% 时触发
SWITCH_THRESHOLD = 0.8


def load_usage_stats() -> dict:
    """加载使用统计"""
    if USAGE_STATS_PATH.exists():
        with open(USAGE_STATS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_usage_stats(stats: dict):
    """保存使用统计"""
    with open(USAGE_STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def record_request(profile_name: str = "qwen-portal:default"):
    """记录一次请求"""
    stats = load_usage_stats()
    if profile_name not in stats:
        stats[profile_name] = {
            "requestCount": 0,
            "errorCount": 0,
            "lastRequest": None,
            "lastReset": datetime.now().isoformat()
        }
    
    stats[profile_name]["requestCount"] = stats[profile_name].get("requestCount", 0) + 1
    stats[profile_name]["lastRequest"] = datetime.now().isoformat()
    
    # 检查是否需要重置（新的一天）
    last_reset = stats[profile_name].get("lastReset")
    if last_reset:
        try:
            reset_time = datetime.fromisoformat(last_reset)
            if datetime.now() - reset_time > timedelta(days=1):
                stats[profile_name]["requestCount"] = 1
                stats[profile_name]["lastReset"] = datetime.now().isoformat()
        except:
            pass
    
    save_usage_stats(stats)


def check_and_switch() -> bool:
    """
    检查是否需要切换账号
    返回 True 如果执行了切换
    """
    stats = load_usage_stats()
    profile_name = "qwen-portal:default"
    
    if profile_name not in stats:
        return False
    
    request_count = stats[profile_name].get("requestCount", 0)
    threshold = int(DAILY_REQUEST_LIMIT * SWITCH_THRESHOLD)
    
    print(f"[检查] 当前请求数：{request_count}/{DAILY_REQUEST_LIMIT}")
    print(f"[检查] 切换阈值：{threshold}")
    
    if request_count >= threshold:
        print(f"[切换] 达到阈值，开始注册新账号...")
        return register_new_account()
    
    return False


def register_new_account() -> bool:
    """注册新账号，覆盖旧 token"""
    print("\n" + "="*50)
    print("  Qwen 自动注册 - 开始")
    print("="*50 + "\n")
    print("[提示] 旧账号将直接覆盖，不保留备份")
    
    # 以 CLI 模式运行（不启动 GUI），默认无头模式
    sys.argv = ["auto-register", "--no-gui", "--headless"]
    
    try:
        exit_code = run_cli()
        if exit_code == 0:
            print("\n[OK] 新账号注册成功！旧 token 已覆盖")
            # 重置使用统计
            stats = load_usage_stats()
            stats["qwen-portal:default"] = {
                "requestCount": 0,
                "errorCount": 0,
                "lastRequest": None,
                "lastReset": datetime.now().isoformat()
            }
            save_usage_stats(stats)
            return True
        else:
            print("\n[FAIL] 注册失败")
            return False
    except KeyboardInterrupt:
        print("\n[中断] 用户终止 (Ctrl+C)")
        return False
    except Exception as e:
        print(f"\n[ERROR] 错误：{e}")
        return False


def show_status():
    """显示当前账号状态"""
    stats = load_usage_stats()
    profile_name = "qwen-portal:default"
    
    print("\n" + "="*50)
    print("  Qwen 账号状态")
    print("="*50)
    
    if profile_name in stats:
        s = stats[profile_name]
        print(f"请求数：{s.get('requestCount', 0)}/{DAILY_REQUEST_LIMIT}")
        print(f"错误数：{s.get('errorCount', 0)}")
        print(f"最后请求：{s.get('lastRequest', '无')}")
        print(f"最后重置：{s.get('lastReset', '无')}")
        
        usage_pct = (s.get('requestCount', 0) / DAILY_REQUEST_LIMIT) * 100
        print(f"使用率：{usage_pct:.1f}%")
        
        threshold = int(DAILY_REQUEST_LIMIT * SWITCH_THRESHOLD)
        if usage_pct >= threshold * 100:
            print(f"\n[建议] 接近限制，考虑切换账号")
    else:
        print("暂无使用统计")
    
    print("="*50 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "status":
            show_status()
        elif cmd == "check":
            switched = check_and_switch()
            if switched:
                print("[OK] 已切换到新账号")
            else:
                print("[OK] 当前账号可用，无需切换")
        elif cmd == "register":
            register_new_account()
        else:
            print(f"[ERROR] 未知命令：{cmd}")
            print("用法：qwen-auto-register [status|check|register]")
    else:
        # 默认行为：检查并切换
        switched = check_and_switch()
        if not switched:
            print("当前账号可用，无需切换")
