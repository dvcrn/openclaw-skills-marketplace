#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格监控 + 推送通知集成版
监控商品价格变化，降价自动推送
"""

import json
import sqlite3
from datetime import datetime
import sys
import os

# 导入推送工具
sys.path.append(os.path.dirname(__file__))
from push_notification import PushNotification


class PriceMonitorWithPush:
    """价格监控（带推送）"""

    def __init__(self, db_path="price_history.db", config_path="../assets/config_template.json"):
        self.db_path = db_path
        self.config = self.load_config(config_path)
        self.push = PushNotification(config_path)
        self.init_database()

    def load_config(self, config_path):
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "items": [],
                "threshold": 0.9
            }

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
        """获取京东价格（模拟）"""
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
        """获取淘宝价格（模拟）"""
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
        """获取商品价格"""
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

    def check_price_drop(self, item_id, current_price, threshold=0.9):
        """检查是否降价"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取历史平均价格
        cursor.execute('''
            SELECT AVG(price), COUNT(*)
            FROM price_history
            WHERE item_id = ?
        ''', (item_id,))

        result = cursor.fetchone()
        conn.close()

        if not result or result[1] < 2:
            return None

        avg_price, count = result

        # 判断是否降价
        if current_price < avg_price * threshold:
            return {
                'is_drop': True,
                'current_price': current_price,
                'avg_price': avg_price,
                'discount': (1 - current_price / avg_price) * 100,
                'count': count
            }

        return None

    def send_price_drop_notification(self, item_data, drop_info):
        """发送降价通知"""
        title = f"🔔 商品降价提醒：{item_data['title']}"
        content = f"""
**{item_data['title']}** 降价了！

💰 当前价格：¥{drop_info['current_price']}
📊 平均价格：¥{drop_info['avg_price']:.2f}
📉 降价幅度：{drop_info['discount']:.1f}%

🔗 购买链接：{item_data['url']}

---
💰 薅羊毛系统自动监控
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        self.push.send(title, content.strip())

    def monitor_items(self, items=None):
        """监控商品列表"""
        if items is None:
            items = self.config.get("items", [])

        if not items:
            print("⚠️ 没有配置监控商品")
            return

        print(f"\n🚀 开始监控 {len(items)} 个商品...\n")

        for item in items:
            platform = item.get('platform')
            item_id = item.get('item_id')

            print(f"🔍 监控: {item.get('name', item_id)} ({platform})")

            # 获取价格
            result = self.get_price(platform, item_id)

            if result.get('success'):
                # 保存价格
                self.save_price(result)

                # 检查降价
                threshold = item.get('threshold', self.config.get('threshold', 0.9))
                drop_info = self.check_price_drop(item_id, result['price'], threshold)

                if drop_info:
                    print(f"   🔔 降价了！当前¥{result['price']}，平均¥{drop_info['avg_price']:.2f}，降幅{drop_info['discount']:.1f}%")

                    # 发送推送通知
                    if self.config.get('push_config', {}).get('enabled'):
                        self.send_price_drop_notification(result, drop_info)
                else:
                    print(f"   ✅ 价格正常：¥{result['price']}")

            else:
                print(f"   ❌ 获取失败：{result.get('error')}")

        print(f"\n✅ 监控完成")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="价格监控（带推送）")
    parser.add_argument("--config", default="../assets/config_template.json", help="配置文件")
    parser.add_argument("--db", default="price_history.db", help="数据库路径")

    args = parser.parse_args()

    monitor = PriceMonitorWithPush(args.db, args.config)
    monitor.monitor_items()


if __name__ == "__main__":
    main()
