#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一价格监控 - 集成京东和淘宝爬虫
"""

import json
import sqlite3
from datetime import datetime


class UnifiedPriceMonitor:
    """统一价格监控（支持京东和淘宝）"""

    def __init__(self, db_path="price_history.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                title TEXT,
                price REAL NOT NULL,
                original_price REAL,
                url TEXT,
                source TEXT DEFAULT 'monitor',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def get_jd_price(self, item_id):
        """获取京东价格（模拟数据）"""
        mock_prices = {
            '100012043978': {'price': 9499, 'title': 'Apple iPhone 15 Pro Max 256GB'},
            '100048127491': {'price': 7899, 'title': '华为 Mate 60 Pro'},
        }

        if item_id in mock_prices:
            return {
                'success': True,
                'platform': 'jd',
                'item_id': item_id,
                'title': mock_prices[item_id]['title'],
                'price': mock_prices[item_id]['price'],
                'url': f'https://item.jd.com/{item_id}.html',
                'source': 'mock'
            }

        return {'success': False, 'error': '商品不存在'}

    def get_taobao_price(self, item_id):
        """获取淘宝价格（模拟数据）"""
        mock_prices = {
            '560852934047': {'price': 1299, 'title': 'Apple AirPods Pro 2'},
            '607234567890': {'price': 599, 'title': '小米手环8 Pro'},
        }

        if item_id in mock_prices:
            return {
                'success': True,
                'platform': 'taobao',
                'item_id': item_id,
                'title': mock_prices[item_id]['title'],
                'price': mock_prices[item_id]['price'],
                'url': f'https://item.taobao.com/item.htm?id={item_id}',
                'source': 'mock'
            }

        return {'success': False, 'error': '商品不存在'}

    def get_price(self, platform, item_id):
        """
        获取商品价格（支持多平台）

        Args:
            platform: jd / taobao
            item_id: 商品ID
        """
        if platform == 'jd':
            return self.get_jd_price(item_id)
        elif platform == 'taobao':
            return self.get_taobao_price(item_id)
        else:
            return {'success': False, 'error': f'不支持的平台: {platform}'}

    def save_price(self, data):
        """保存价格记录"""
        if not data.get('success'):
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_history
            (item_id, platform, title, price, url, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['item_id'],
            data['platform'],
            data['title'],
            data['price'],
            data['url'],
            data.get('source', 'monitor')
        ))
        conn.commit()
        conn.close()

    def monitor_item(self, platform, item_id):
        """监控单个商品"""
        print(f"🔍 监控商品: {platform} - {item_id}")

        result = self.get_price(platform, item_id)

        if result['success']:
            self.save_price(result)
            print(f"✅ {result['title']}")
            print(f"   价格: ¥{result['price']}")
            print(f"   链接: {result['url']}")
        else:
            print(f"❌ 获取失败: {result['error']}")

        return result

    def batch_monitor(self, items):
        """
        批量监控

        Args:
            items: [{"platform": "jd", "item_id": "xxx"}, ...]
        """
        print(f"\n🚀 批量监控 {len(items)} 个商品\n")

        results = []
        for item in items:
            platform = item.get('platform')
            item_id = item.get('item_id')

            result = self.monitor_item(platform, item_id)
            results.append(result)

        return results

    def show_history(self, item_id=None, days=7):
        """显示价格历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if item_id:
            cursor.execute('''
                SELECT item_id, platform, title, price, timestamp
                FROM price_history
                WHERE item_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (item_id, days))
        else:
            cursor.execute('''
                SELECT item_id, platform, title, price, timestamp
                FROM price_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (days,))

        records = cursor.fetchall()
        conn.close()

        print(f"\n📊 价格历史记录")
        print("="*70)

        if not records:
            print("暂无记录")
        else:
            for item_id, platform, title, price, timestamp in records:
                date = timestamp.split()[0]
                print(f"{date} [{platform:8}] {title[:30]:30} ¥{price:.2f}")

        print("="*70)


def quick_test():
    """快速测试"""
    monitor = UnifiedPriceMonitor()

    # 测试商品列表
    test_items = [
        {'platform': 'jd', 'item_id': '100012043978'},      # iPhone
        {'platform': 'jd', 'item_id': '100048127491'},      # 华为
        {'platform': 'taobao', 'item_id': '560852934047'}, # AirPods
        {'platform': 'taobao', 'item_id': '607234567890'}, # 小米手环
    ]

    # 批量监控
    results = monitor.batch_monitor(test_items)

    # 显示历史记录
    monitor.show_history(days=10)

    # 统计结果
    success_count = sum(1 for r in results if r['success'])

    print(f"\n✅ 监控完成: {success_count}/{len(results)} 成功")


if __name__ == "__main__":
    quick_test()
