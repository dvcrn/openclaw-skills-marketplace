#!/usr/bin/env python3
"""
监控命令行工具
用法:
  python3 monitor_cli.py add <商品链接>    - 添加商品到监控
  python3 monitor_cli.py query             - 查询所有监控商品价格
  python3 monitor_cli.py list              - 列出监控商品
  python3 monitor_cli.py clear             - 清空监控列表
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor_manager import (
    add_to_monitor, query_all_prices, format_query_results,
    list_monitors, clear_monitors
)

def main():
    if len(sys.argv) < 2:
        print("监控管理工具")
        print("=" * 50)
        print("\n用法:")
        print("  python3 monitor_cli.py add <商品链接>  - 添加商品到监控")
        print("  python3 monitor_cli.py query           - 查询所有监控商品价格")
        print("  python3 monitor_cli.py list            - 列出监控商品")
        print("  python3 monitor_cli.py clear           - 清空监控列表")
        print("\n示例:")
        print('  python3 monitor_cli.py add "￥xxx￥"')
        print('  python3 monitor_cli.py add "https://u.jd.com/xxx"')
        print("  python3 monitor_cli.py query")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'add':
        if len(sys.argv) < 3:
            print("❌ 请提供商品链接")
            sys.exit(1)
        
        url = sys.argv[2]
        monitor, msg = add_to_monitor(url)
        
        if monitor:
            platform_name = '淘宝' if monitor['platform'] == 'taobao' else '京东'
            print(f"✅ {msg}")
            print(f"\n📦 {monitor['title']}")
            print(f"🏪 平台：{platform_name}")
            print(f"💰 当前价格：¥{monitor['current_price']}")
        else:
            print(f"❌ {msg}")
    
    elif cmd == 'query':
        results, timestamp = query_all_prices()
        
        if results:
            print(format_query_results(results, timestamp))
        else:
            print(f"📭 {timestamp}")
    
    elif cmd == 'list':
        print(list_monitors())
    
    elif cmd == 'clear':
        print(clear_monitors())
    
    else:
        print(f"❌ 未知命令: {cmd}")

if __name__ == '__main__':
    main()
