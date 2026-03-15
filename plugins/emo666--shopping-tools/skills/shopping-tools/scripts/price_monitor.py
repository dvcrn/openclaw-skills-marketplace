#!/usr/bin/env python3
"""
价格监控工具
支持添加商品监控、查看监控列表、检查价格变化
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zhetaoke_api import ZheTaoKeAPI

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
MONITOR_FILE = os.path.join(DATA_DIR, 'price_monitor.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'price_history.json')

def ensure_data_dir():
    """确保数据目录存在"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_monitors():
    """加载监控列表"""
    ensure_data_dir()
    if os.path.exists(MONITOR_FILE):
        with open(MONITOR_FILE, 'r') as f:
            return json.load(f)
    return []

def save_monitors(monitors):
    """保存监控列表"""
    ensure_data_dir()
    with open(MONITOR_FILE, 'w') as f:
        json.dump(monitors, f, ensure_ascii=False, indent=2)

def load_history():
    """加载价格历史"""
    ensure_data_dir()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_history(history):
    """保存价格历史"""
    ensure_data_dir()
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_monitor(item_id, title, target_price, current_price, note=""):
    """添加商品监控"""
    monitors = load_monitors()
    
    monitor = {
        'id': item_id,
        'title': title,
        'target_price': float(target_price),
        'current_price': float(current_price),
        'note': note,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'monitoring'
    }
    
    # 检查是否已存在
    for i, m in enumerate(monitors):
        if m['id'] == item_id:
            monitors[i] = monitor
            save_monitors(monitors)
            return f"✅ 已更新监控：{title[:30]}..."
    
    monitors.append(monitor)
    save_monitors(monitors)
    return f"✅ 已添加监控：{title[:30]}..."

def list_monitors():
    """列出所有监控"""
    monitors = load_monitors()
    
    if not monitors:
        return "📭 暂无监控商品"
    
    output = [f"📊 共 {len(monitors)} 个监控商品\n"]
    
    for i, m in enumerate(monitors, 1):
        status_emoji = "🟢" if m['status'] == 'monitoring' else "🔴"
        output.append(f"{status_emoji} {i}. {m['title'][:40]}")
        output.append(f"   💰 当前：¥{m['current_price']} | 目标：¥{m['target_price']}")
        if m.get('note'):
            output.append(f"   📝 {m['note']}")
        output.append("")
    
    return "\n".join(output)

def check_prices():
    """检查价格变化（仅支持淘宝商品）"""
    monitors = load_monitors()
    api = ZheTaoKeAPI()
    
    if not monitors:
        return "📭 暂无监控商品"
    
    print(f"🔍 正在检查 {len(monitors)} 个商品...\n")
    
    changes = []
    for m in monitors:
        # 获取最新价格（仅支持淘宝商品）
        # 京东商品ID格式不同，跳过
        if len(m['id']) > 20:  # 京东商品ID较长
            continue
            
        result = api.taobao_detail(m['id'])
        if result and result.get('status') == 200:
            item = result.get('content', [{}])[0]
            price_str = item.get('quanhou_jiage', item.get('size', '0'))
            if not price_str or price_str == '':
                price_str = '0'
            try:
                new_price = float(price_str)
            except:
                continue
            
            if new_price != m['current_price'] and new_price > 0:
                old_price = m['current_price']
                m['current_price'] = new_price
                
                if new_price <= m['target_price']:
                    changes.append({
                        'title': m['title'],
                        'old_price': old_price,
                        'new_price': new_price,
                        'target': m['target_price'],
                        'reached': True
                    })
                else:
                    changes.append({
                        'title': m['title'],
                        'old_price': old_price,
                        'new_price': new_price,
                        'reached': False
                    })
    
    save_monitors(monitors)
    
    if changes:
        output = [f"📢 发现 {len(changes)} 个价格变动\n"]
        for c in changes:
            if c['reached']:
                output.append(f"🎉 {c['title'][:40]}...")
                output.append(f"   💰 ¥{c['old_price']} → ¥{c['new_price']} (目标：¥{c['target']})")
                output.append(f"   ✅ 已达到目标价格！")
            else:
                output.append(f"📉 {c['title'][:40]}...")
                output.append(f"   💰 ¥{c['old_price']} → ¥{c['new_price']}")
            output.append("")
        return "\n".join(output)
    else:
        return "✅ 所有商品价格稳定，无变动"

def main():
    if len(sys.argv) < 2:
        print("价格监控工具")
        print("=" * 50)
        print("\n使用方法:")
        print("  python3 price_monitor.py list                    - 查看监控列表")
        print("  python3 price_monitor.py check                   - 检查价格变化")
        print("\n示例:")
        print("  python3 price_monitor.py list")
        print("  python3 price_monitor.py check")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'list':
        print(list_monitors())
    elif cmd == 'check':
        print(check_prices())
    else:
        print(f"❌ 未知命令: {cmd}")

if __name__ == '__main__':
    main()
