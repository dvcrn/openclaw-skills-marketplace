#!/usr/bin/env python3
"""
监控管理器
支持添加商品到监控列表，随时查询实时价格
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor_service import MonitorService

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
MONITOR_LIST_FILE = os.path.join(DATA_DIR, 'monitor_list.json')

def ensure_data_dir():
    """确保数据目录存在"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_monitor_list():
    """加载监控列表"""
    ensure_data_dir()
    if os.path.exists(MONITOR_LIST_FILE):
        with open(MONITOR_LIST_FILE, 'r') as f:
            return json.load(f)
    return []

def save_monitor_list(monitors):
    """保存监控列表"""
    ensure_data_dir()
    with open(MONITOR_LIST_FILE, 'w') as f:
        json.dump(monitors, f, ensure_ascii=False, indent=2)

def add_to_monitor(url):
    """添加商品到监控列表"""
    service = MonitorService()
    monitor, error = service.add_monitor(url, 0, 10)
    
    if error:
        return None, error
    
    monitors = load_monitor_list()
    
    # 检查是否已存在
    for i, m in enumerate(monitors):
        if m['id'] == monitor['id']:
            monitors[i] = monitor
            save_monitor_list(monitors)
            return monitor, "已更新监控商品"
    
    monitors.append(monitor)
    save_monitor_list(monitors)
    return monitor, "已添加监控商品"

def query_all_prices():
    """查询所有监控商品的实时价格"""
    monitors = load_monitor_list()
    service = MonitorService()
    
    if not monitors:
        return None, "暂无监控商品"
    
    results = []
    timestamp = time.strftime('%H:%M:%S')
    
    for m in monitors:
        result = service.check_price(m)
        platform_name = '淘宝' if m['platform'] == 'taobao' else '京东'
        
        # 获取购买链接
        buy_link = ""
        if 'short_url' in m and m['short_url']:
            buy_link = m['short_url']
        elif 'result_url' in m and m['result_url']:
            buy_link = m['result_url']
        elif 'url' in m and m['url']:
            buy_link = m['url']
        
        item_result = {
            'title': m['title'],
            'platform': platform_name,
            'current_price': m['current_price'],
            'price_changed': result['status'] == 'price_changed',
            'old_price': result.get('old_price', m['current_price']) if result['status'] == 'price_changed' else None,
            'buy_link': buy_link
        }
        results.append(item_result)
    
    save_monitor_list(monitors)
    return results, timestamp

def format_query_results(results, timestamp):
    """格式化查询结果"""
    output = []
    output.append(f"📊 监控商品价格查询 [{timestamp}]")
    output.append("=" * 50)
    
    for i, r in enumerate(results, 1):
        change_emoji = ""
        if r['price_changed']:
            if r['current_price'] < r['old_price']:
                change_emoji = "📉 "
            else:
                change_emoji = "📈 "
        
        output.append(f"\n{i}. {change_emoji}{r['title'][:35]}")
        output.append(f"   🏪 {r['platform']} | 💰 ¥{r['current_price']}")
        
        if r['price_changed']:
            output.append(f"   💡 价格变动：¥{r['old_price']} → ¥{r['current_price']}")
        
        # 添加购买链接
        if r.get('buy_link'):
            output.append(f"   🔗 {r['buy_link']}")
    
    output.append("\n" + "=" * 50)
    output.append(f"✅ 共 {len(results)} 个监控商品")
    
    return "\n".join(output)

def list_monitors():
    """列出所有监控商品"""
    monitors = load_monitor_list()
    
    if not monitors:
        return "📭 暂无监控商品"
    
    output = []
    output.append(f"📊 监控商品列表（共 {len(monitors)} 个）\n")
    
    for i, m in enumerate(monitors, 1):
        platform_name = '淘宝' if m['platform'] == 'taobao' else '京东'
        output.append(f"{i}. 📦 {m['title'][:40]}")
        output.append(f"   🏪 {platform_name} | 💰 ¥{m['current_price']}")
        output.append("")
    
    return "\n".join(output)

def clear_monitors():
    """清空监控列表"""
    save_monitor_list([])
    return "✅ 已清空监控列表"

if __name__ == '__main__':
    # 测试
    print("监控管理器已加载")
