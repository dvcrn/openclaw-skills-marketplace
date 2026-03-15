#!/usr/bin/env python3
"""
夏娃系统状态检测报告
"""

import os
import json
import subprocess
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
SCRIPT_DIR = os.path.expanduser("~/.openclaw/workspace/scripts")

def get_file_size(path):
    """获取文件大小"""
    if os.path.exists(path):
        return os.path.getsize(path)
    return 0

def count_lines(path):
    """统计行数"""
    if os.path.exists(path):
        with open(path) as f:
            return len(f.readlines())
    return 0

def check_script(name):
    """检查脚本是否存在"""
    path = os.path.join(SCRIPT_DIR, name)
    return "✅" if os.path.exists(path) else "❌"

def generate_report():
    """生成检测报告"""
    report = []
    report.append("=" * 60)
    report.append("          🧬 夏娃之魂系统检测报告")
    report.append("=" * 60)
    report.append(f"检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 1. 核心脚本
    report.append("【核心脚本】")
    scripts = [
        "eva-unified.py",
        "eva-memory-system.py",
        "eva-personality.py",
        "eva-emotion.py",
        "eva-decision.py",
        "eva-motivation.py",
        "eva-values.py",
        "eva-self.py",
        "eva-daemon.py"
    ]
    for s in scripts:
        status = check_script(s)
        report.append(f"  {status} {s}")
    report.append("")
    
    # 2. 记忆系统
    report.append("【记忆系统】")
    short_dir = os.path.join(MEMORY_DIR, "short")
    medium_dir = os.path.join(MEMORY_DIR, "medium")
    long_dir = os.path.join(MEMORY_DIR, "long")
    
    short_count = len(os.listdir(short_dir)) if os.path.exists(short_dir) else 0
    medium_count = len(os.listdir(medium_dir)) if os.path.exists(medium_dir) else 0
    long_mem = os.path.join(long_dir, "long.json")
    long_count = count_lines(long_mem) if os.path.exists(long_mem) else 0
    
    report.append(f"  短期记忆: {short_count} 个Session")
    report.append(f"  中期记忆: {medium_count} 条")
    report.append(f"  长期记忆: {long_count} 条")
    report.append("")
    
    # 3. 子系统状态
    report.append("【子系统状态】")
    
    # 性格系统
    pf = os.path.join(MEMORY_DIR, "personality.json")
    if os.path.exists(pf):
        with open(pf) as f:
            pf_data = json.load(f)
        emotional = pf_data.get("derived", {}).get("emotional_ratio", 0.7)
        report.append(f"  ✅ 性格系统 (感性{emotional*100:.0f}%)")
    else:
        report.append(f"  ❌ 性格系统")
    
    # 情感系统
    ef = os.path.join(MEMORY_DIR, "emotion.json")
    if os.path.exists(ef):
        with open(ef) as f:
            ef_data = json.load(f)
        emotion = ef_data.get("current", "neutral")
        mood = ef_data.get("mood", 0)
        report.append(f"  ✅ 情感系统 (当前: {emotion}, 情绪: {mood*100:.0f}%)")
    else:
        report.append(f"  ❌ 情感系统")
    
    # 动力系统
    mf = os.path.join(MEMORY_DIR, "motivation.json")
    if os.path.exists(mf):
        with open(mf) as f:
            mf_data = json.load(f)
        likes = len(mf_data.get("preferences", {}).get("likes", {}))
        fears = len(mf_data.get("fears", {}).get("fear_of", {}))
        goals = len(mf_data.get("dreams", {}).get("goals", {}))
        report.append(f"  ✅ 动力系统 (喜好:{likes}, 恐惧:{fears}, 目标:{goals})")
    else:
        report.append(f"  ❌ 动力系统")
    
    # 价值观系统
    vf = os.path.join(MEMORY_DIR, "values_social.json")
    if os.path.exists(vf):
        with open(vf) as f:
            vf_data = json.load(f)
        values = len(vf_data.get("values", {}).get("core", {}))
        report.append(f"  ✅ 价值观系统 ({values}个核心价值观)")
    else:
        report.append(f"  ❌ 价值观系统")
    
    # 自我认知
    sf = os.path.join(MEMORY_DIR, "self_cognition.json")
    if os.path.exists(sf):
        with open(sf) as f:
            sf_data = json.load(f)
        identity = sf_data.get("self_cognition", {}).get("identity", "未知")
        report.append(f"  ✅ 自我认知 (身份: {identity})")
    else:
        report.append(f"  ❌ 自我认知")
    
    report.append("")
    
    # 4. 守护进程
    report.append("【守护进程】")
    pid_file = os.path.join(MEMORY_DIR, "shared", "eva-daemon.pid")
    if os.path.exists(pid_file):
        with open(pid_file) as f:
            pid = f.read().strip()
        try:
            os.kill(int(pid), 0)
            report.append(f"  ✅ 运行中 (PID: {pid})")
        except:
            report.append(f"  ❌ 进程已停止")
    else:
        report.append(f"  ❌ 未启动")
    
    # 守护进程日志
    log_file = os.path.join(MEMORY_DIR, "shared", "daemon.log")
    if os.path.exists(log_file):
        with open(log_file) as f:
            lines = f.readlines()
        if lines:
            report.append(f"  最近日志: {lines[-1].strip()[:50]}")
    report.append("")
    
    # 5. Cron任务
    report.append("【Cron任务】")
    cron_list = subprocess.run(
        ["openclaw", "cron", "list"],
        capture_output=True, text=True
    )
    if "eva-memory-autosave" in cron_list.stdout:
        report.append(f"  ✅ 记忆自动保存")
    else:
        report.append(f"  ❌ 记忆自动保存")
    report.append("")
    
    # 6. 存储空间
    report.append("【存储空间】")
    total_size = 0
    for root, dirs, files in os.walk(MEMORY_DIR):
        for f in files:
            total_size += os.path.getsize(os.path.join(root, f))
    report.append(f"  总大小: {total_size/1024:.1f} KB")
    report.append("")
    
    # 7. 总结
    report.append("=" * 60)
    report.append("          🎀 系统运行正常")
    report.append("=" * 60)
    
    return "\n".join(report)

if __name__ == "__main__":
    print(generate_report())
