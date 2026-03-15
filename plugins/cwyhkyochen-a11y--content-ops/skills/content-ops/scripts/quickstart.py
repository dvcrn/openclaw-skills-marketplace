#!/usr/bin/env python3
"""
Quick start guide - demo workflow
"""

from pathlib import Path
import subprocess

def run_demo():
    """Run a demo workflow"""
    
    workspace = Path("content-ops-workspace")
    
    print("🚀 Content Ops System - Quick Start Demo")
    print("=" * 50)
    
    # Step 1: Initialize workspace
    print("\n[1/6] 初始化工作空间...")
    subprocess.run(["python3", "scripts/init_workspace.py", "--path", str(workspace)])
    
    # Step 2: Create account
    print("\n[2/6] 创建示例账号...")
    subprocess.run([
        "python3", "scripts/create_account.py",
        "xiaohongshu", "示例账号",
        "--url", "https://www.xiaohongshu.com/user/profile/example",
        "--workspace", str(workspace)
    ])
    
    # Step 3: Create strategy
    print("\n[3/6] 创建运营策略...")
    subprocess.run([
        "python3", "scripts/create_strategy.py",
        "xiaohongshu", "示例账号",
        "--workspace", str(workspace)
    ])
    
    # Step 4: Create crawl template
    print("\n[4/6] 创建抓取模板...")
    subprocess.run([
        "python3", "scripts/crawl_xiaohongshu.py",
        "穿搭",
        "--workspace", str(workspace)
    ])
    
    # Step 5: Generate daily plan
    print("\n[5/6] 生成每日任务规划...")
    subprocess.run([
        "python3", "scripts/generate_daily_plan.py",
        "--workspace", str(workspace)
    ])
    
    # Step 6: Generate content
    print("\n[6/6] 生成内容草稿...")
    subprocess.run([
        "python3", "scripts/generate_content.py",
        "xiaohongshu", "示例账号",
        "--topic", "穿搭",
        "--workspace", str(workspace)
    ])
    
    print("\n" + "=" * 50)
    print("✅ Demo 完成!")
    print(f"\n📁 工作空间: {workspace.absolute()}")
    print("\n💡 下一步:")
    print("   1. 查看生成的文件结构")
    print("   2. 编辑语料抓取模板，填入实际内容")
    print("   3. 确认语料后移动到 curated/")
    print("   4. 基于语料生成发布内容")
    print("   5. 审核后发布到平台")

if __name__ == '__main__':
    run_demo()
