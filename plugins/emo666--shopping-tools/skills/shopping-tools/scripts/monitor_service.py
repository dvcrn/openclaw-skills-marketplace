#!/usr/bin/env python3
"""
交互式价格监控服务
支持用户设置监控价格和定时通知
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopping_helper import detect_platform, convert_link_backend
from zhetaoke_api import ZheTaoKeAPI

class MonitorService:
    """价格监控服务"""
    
    def __init__(self):
        self.api = ZheTaoKeAPI()
        self.running = False
        
    def add_monitor(self, url, target_price, interval=10):
        """添加监控任务
        
        Args:
            url: 商品链接或淘口令
            target_price: 目标价格
            interval: 检查间隔（秒）
        """
        # 识别平台
        platform = detect_platform(url)
        if platform == 'unknown':
            return None, "无法识别链接格式"
        
        # 获取商品信息
        result = convert_link_backend(url, platform)
        if not result or result.get('status') != 200:
            return None, "获取商品信息失败"
        
        item_id = result.get('tao_id', '')
        title = result.get('title', '') or result.get('tao_title', '')
        current_price = result.get('quanhou_jiage', result.get('size', '0'))
        
        if not current_price or current_price == '0':
            current_price = result.get('size', '0')
        
        try:
            current_price_float = float(current_price)
        except:
            current_price_float = 0
        
        # 获取购买链接
        short_url = result.get('shorturl', '') or result.get('shortUrl', '') or result.get('result_url', '')
        
        monitor_info = {
            'id': item_id,
            'title': title,
            'url': url,
            'platform': platform,
            'current_price': current_price_float,
            'target_price': float(target_price),
            'interval': interval,
            'short_url': short_url,
            'added_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return monitor_info, None
    
    def check_price(self, monitor_info):
        """检查单个商品价格"""
        try:
            if monitor_info['platform'] == 'taobao':
                result = self.api.taobao_detail(monitor_info['id'])
            else:
                result = self.api.jd_convert(monitor_info['url'])
            
            if result and result.get('status') == 200:
                if monitor_info['platform'] == 'taobao':
                    item = result.get('content', [{}])[0]
                    new_price_str = item.get('quanhou_jiage', item.get('size', '0'))
                else:
                    new_price_str = result.get('quanhou_jiage', result.get('size', '0'))
                
                if not new_price_str or new_price_str == '':
                    new_price_str = '0'
                
                try:
                    new_price = float(new_price_str)
                except:
                    new_price = 0
                
                old_price = monitor_info['current_price']
                monitor_info['current_price'] = new_price
                
                # 检查是否达到目标价格
                if new_price > 0 and new_price <= monitor_info['target_price']:
                    return {
                        'status': 'target_reached',
                        'title': monitor_info['title'],
                        'old_price': old_price,
                        'new_price': new_price,
                        'target': monitor_info['target_price']
                    }
                elif new_price != old_price and new_price > 0:
                    return {
                        'status': 'price_changed',
                        'title': monitor_info['title'],
                        'old_price': old_price,
                        'new_price': new_price
                    }
                else:
                    return {'status': 'no_change'}
            
            return {'status': 'error', 'message': 'API请求失败'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


def format_monitor_result(monitor_info):
    """格式化监控信息"""
    platform_name = '淘宝' if monitor_info['platform'] == 'taobao' else '京东'
    
    output = []
    output.append(f"📦 {monitor_info['title']}")
    output.append(f"• 💰 当前价格：¥{monitor_info['current_price']}")
    output.append(f"• 🎯 目标价格：¥{monitor_info['target_price']}")
    output.append(f"• 🏪 平台：{platform_name}")
    output.append(f"• ⏰ 检查间隔：{monitor_info['interval']}秒")
    
    return "\n".join(output)


def format_notification(result):
    """格式化通知消息"""
    if result['status'] == 'target_reached':
        return f"""🎉 价格监控提醒！

📦 {result['title'][:40]}...
💰 价格变动：¥{result['old_price']} → ¥{result['new_price']}
✅ 已达到目标价格 ¥{result['target']}！

👇 可以下单了！"""
    elif result['status'] == 'price_changed':
        return f"""📉 价格变动提醒

📦 {result['title'][:40]}...
💰 ¥{result['old_price']} → ¥{result['new_price']}"""
    else:
        return None


if __name__ == '__main__':
    # 测试
    service = MonitorService()
    print("价格监控服务已加载")
