#!/usr/bin/env python3
"""
Create or update account archive
"""

import argparse
from pathlib import Path
from datetime import datetime

def create_account_template(platform: str, account_name: str, account_id: str = "", 
                           homepage_url: str = "", positioning: str = "",
                           target_audience: str = "", content_direction: str = "") -> str:
    """Generate account archive template"""
    
    template = f"""---
platform: {platform}
account_name: {account_name}
account_id: {account_id}
homepage_url: {homepage_url}
created_at: {datetime.now().strftime('%Y-%m-%d')}
status: active
---

# {account_name} ({platform})

## 账号定位
- **人设**: {positioning or '待填写'}
- **目标受众**: {target_audience or '待填写'}
- **内容方向**: {content_direction or '待填写'}

## 运营数据追踪

### {datetime.now().strftime('%Y-%m')}
- 粉丝数: [填写] → [填写] (+/-)
- 笔记数: [填写]
- 总赞藏: [填写]

## 关联策略文件
- [运营策略](../strategies/{platform}-{account_name}-strategy.md)

## 已发布内容索引
<!-- 发布后自动更新 -->

## 发布计划
<!-- 从 schedules/ 目录链接 -->

## 备注
<!-- 运营过程中的重要笔记 -->
"""
    return template

def main():
    parser = argparse.ArgumentParser(description='Create account archive')
    parser.add_argument('platform', help='Platform name (xiaohongshu, reddit, etc.)')
    parser.add_argument('account_name', help='Account name')
    parser.add_argument('--id', help='Account ID')
    parser.add_argument('--url', help='Homepage URL')
    parser.add_argument('--positioning', help='Account positioning')
    parser.add_argument('--audience', help='Target audience')
    parser.add_argument('--direction', help='Content direction')
    parser.add_argument('--workspace', default='content-ops-workspace',
                       help='Workspace directory')
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    accounts_dir = workspace / "accounts"
    accounts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename
    filename = f"{args.platform}-{args.account_name}.md"
    filepath = accounts_dir / filename
    
    # Generate content
    content = create_account_template(
        args.platform, 
        args.account_name,
        args.id or "",
        args.url or "",
        args.positioning or "",
        args.audience or "",
        args.direction or ""
    )
    
    # Check if file exists
    if filepath.exists():
        print(f"⚠️ 账号档案已存在: {filepath}")
        response = input("是否覆盖? (y/N): ")
        if response.lower() != 'y':
            print("已取消")
            return
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 账号档案已创建: {filepath}")
    print(f"\n📋 账号信息:")
    print(f"   平台: {args.platform}")
    print(f"   名称: {args.account_name}")
    print(f"   ID: {args.id or '待填写'}")
    print(f"   主页: {args.url or '待填写'}")

if __name__ == '__main__':
    main()
