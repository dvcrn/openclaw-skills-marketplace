#!/usr/bin/env python3
"""
Generate daily task plan based on strategies and schedules
"""

import argparse
from pathlib import Path
from datetime import datetime, timedelta
import re

def load_accounts(workspace: Path) -> list:
    """Load all active accounts"""
    accounts_dir = workspace / "accounts"
    if not accounts_dir.exists():
        return []
    
    accounts = []
    for file in accounts_dir.glob("*.md"):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check if active
            if 'status: active' in content:
                # Extract basic info
                platform = ""
                name = ""
                for line in content.split('\n'):
                    if line.startswith('platform:'):
                        platform = line.split(':', 1)[1].strip()
                    elif line.startswith('account_name:'):
                        name = line.split(':', 1)[1].strip()
                accounts.append({
                    'platform': platform,
                    'name': name,
                    'file': file
                })
    return accounts

def generate_daily_plan(workspace: Path, date: datetime) -> str:
    """Generate daily task plan"""
    
    accounts = load_accounts(workspace)
    
    plan = f"""# 每日任务规划 - {date.strftime('%Y-%m-%d %A')}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 今日账号概览

| 平台 | 账号 | 状态 | 今日任务 |
|------|------|------|----------|
"""
    
    for acc in accounts:
        plan += f"| {acc['platform']} | {acc['name']} | 活跃 | 待规划 |\n"
    
    plan += f"""
## 待办任务

### 内容抓取
<!-- 基于运营策略中的选题方向 -->
- [ ] 任务1: [平台] - [主题]

### 内容发布
<!-- 基于发布计划和运营频率 -->
"""
    
    for acc in accounts:
        plan += f"- [ ] [{acc['platform']}] {acc['name']}: 检查今日是否需要发布\n"
    
    plan += """
### 数据复盘
<!-- 每个活跃账号的每日复盘 -->
"""
    
    for acc in accounts:
        plan += f"- [ ] [{acc['platform']}] {acc['name']}: 抓取昨日数据\n"
    
    plan += """
### 已发布内容追踪
<!-- 查看近期发布内容的表现 -->
- [ ] 检查 [账号名] 最近7天发布内容的数据

## 优先级排序
1. 🔴 高优先级: 
2. 🟡 中优先级: 
3. 🟢 低优先级: 

## 时间规划
| 时间段 | 任务 | 预计耗时 |
|--------|------|----------|
| 09:00-10:00 | 数据复盘 | 30min/账号 |
| 10:00-12:00 | 内容策划 | - |
| 14:00-16:00 | 内容制作 | - |
| 16:00-18:00 | 内容发布 | - |

## 备注
"""
    
    return plan

def main():
    parser = argparse.ArgumentParser(description='Generate daily task plan')
    parser.add_argument('--date', help='Date for planning (YYYY-MM-DD), default: today')
    parser.add_argument('--workspace', default='content-ops-workspace',
                       help='Workspace directory')
    
    args = parser.parse_args()
    
    # Parse date
    if args.date:
        plan_date = datetime.strptime(args.date, '%Y-%m-%d')
    else:
        plan_date = datetime.now()
    
    workspace = Path(args.workspace)
    
    # Generate plan
    plan = generate_daily_plan(workspace, plan_date)
    
    # Save to schedules
    schedules_dir = workspace / "schedules"
    schedules_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{plan_date.strftime('%Y-%m-%d')}-plan.md"
    filepath = schedules_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(plan)
    
    print(f"✅ 每日任务规划已生成: {filepath}")
    print(f"\n📋 今日概览:")
    
    accounts = load_accounts(workspace)
    print(f"   活跃账号: {len(accounts)} 个")
    for acc in accounts:
        print(f"   - [{acc['platform']}] {acc['name']}")

if __name__ == '__main__':
    main()
