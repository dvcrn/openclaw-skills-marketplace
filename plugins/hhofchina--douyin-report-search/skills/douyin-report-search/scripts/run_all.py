#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音话题数据采集 & 分析 — 一键运行入口

用法：
  python3 run_all.py [关键词] [采集数量] [工作目录]

示例：
  python3 run_all.py 女性成长 100 ./output
  python3 run_all.py 职场提升 50 ./workspace

流程：
  1. 检查 douyin_session.json（不存在则先跑 douyin_login.py）
  2. 采集视频原始数据 → douyin_raw_data.json
  3. 详情页采集 + 验证码自动处理 → douyin_parsed.json
  4. 多因素分析 → analysis_result.json
  5. 生成 HTML 报告 → douyin_analysis_report.html
"""
import subprocess, sys, os
from pathlib import Path

KEYWORD  = sys.argv[1] if len(sys.argv) > 1 else "女性成长"
TOTAL    = sys.argv[2] if len(sys.argv) > 2 else "100"
WORK_DIR = str(Path(sys.argv[3]).resolve()) if len(sys.argv) > 3 else str(Path(".").resolve())

SCRIPT_DIR = Path(__file__).parent.resolve()

def run(script, *args):
    cmd = [sys.executable, str(SCRIPT_DIR / script), *args]
    print(f"\n{'='*60}\n▶ {' '.join(cmd)}\n{'='*60}")
    result = subprocess.run(cmd, check=True)
    return result.returncode == 0

# 1. 检查 session
session_file = Path(WORK_DIR) / "douyin_session.json"
if not session_file.exists():
    print(f"⚠ 未找到 {session_file}")
    print("请先运行登录脚本：")
    print(f"  python3 {SCRIPT_DIR}/douyin_login.py {WORK_DIR}")
    sys.exit(1)

# 2. 采集
run("collect_videos.py", KEYWORD, TOTAL, WORK_DIR)

# 3. 详情+验证码
run("parse_videos.py", WORK_DIR)

# 4. 分析
run("analyze_factors.py", WORK_DIR)

# 5. 报告
run("generate_report.py", WORK_DIR, KEYWORD)

report = Path(WORK_DIR) / "douyin_analysis_report.html"
print(f"\n✅ 全部完成！报告路径：{report}")
