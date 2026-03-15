#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格监控系统 - 测试版
演示价格监控功能
"""

import json
import sqlite3
from datetime import datetime, timedelta
import random


class PriceMonitorDemo:
    def __init__(self):
        self.db_path = "price_history.db"
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
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ 数据库初始化完成")

    def add_test_data(self):
        """添加测试数据"""
        test_items = [
            {
                "item_id": "100012043978",
                "platform": "jd",
                "title": "Apple iPhone 15 Pro Max 256GB 原色钛金属",
                "base_price": 9999,
                "variance": 500
            },
            {
                "item_id": "100048127491",
                "platform": "jd",
                "title": "华为 Mate 60 Pro 12GB+512GB 雅丹黑",
                "base_price": 7999,
                "variance": 300
            }
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in test_items:
            # 生成过去30天的价格数据
            base_date = datetime.now() - timedelta(days=30)

            for i in range(30):
                date = base_date + timedelta(days=i)
                # 模拟价格波动
                price = item["base_price"] + random.randint(-item["variance"], item["variance"])

                cursor.execute('''
                    INSERT INTO price_history
                    (item_id, platform, title, price, url, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    item["item_id"],
                    item["platform"],
                    item["title"],
                    price,
                    f"https://item.jd.com/{item['item_id']}.html",
                    date.isoformat()
                ))

        conn.commit()
        conn.close()

        print(f"✅ 添加测试数据完成: {len(test_items)} 个商品, 每个30天历史")

    def monitor_test(self):
        """测试监控"""
        print("\n" + "="*60)
        print("🔍 价格监控测试")
        print("="*60)

        # 模拟当前价格
        current_items = [
            {
                "item_id": "100012043978",
                "title": "Apple iPhone 15 Pro Max 256GB",
                "current_price": 9499,  # 降价了
                "url": "https://item.jd.com/100012043978.html"
            },
            {
                "item_id": "100048127491",
                "title": "华为 Mate 60 Pro",
                "current_price": 7899,  # 小幅降价
                "url": "https://item.jd.com/100048127491.html"
            }
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in current_items:
            print(f"\n📱 {item['title']}")
            print(f"   当前价格: ¥{item['current_price']}")

            # 获取历史平均价格
            cursor.execute('''
                SELECT AVG(price), MIN(price), MAX(price)
                FROM price_history
                WHERE item_id = ?
            ''', (item['item_id'],))

            avg, min_p, max_p = cursor.fetchone()

            print(f"   平均价格: ¥{avg:.2f}")
            print(f"   最低价格: ¥{min_p:.2f}")
            print(f"   最高价格: ¥{max_p:.2f}")

            # 判断是否降价
            threshold = avg * 0.9  # 90%阈值

            if item['current_price'] < threshold:
                discount = (1 - item['current_price'] / avg) * 100
                print(f"   🔔 降价提醒！降价 {discount:.1f}%")
                print(f"   💰 节省: ¥{avg - item['current_price']:.2f}")
            elif item['current_price'] < avg:
                discount = (1 - item['current_price'] / avg) * 100
                print(f"   📉 价格低于平均 {discount:.1f}%")
            else:
                print(f"   ✅ 价格正常")

            # 保存当前价格
            cursor.execute('''
                INSERT INTO price_history
                (item_id, platform, title, price, url)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                item['item_id'],
                'jd',
                item['title'],
                item['current_price'],
                item['url']
            ))

        conn.commit()
        conn.close()

        print("\n" + "="*60)
        print("✅ 监控测试完成")
        print("="*60)

    def show_statistics(self):
        """显示统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(DISTINCT item_id) FROM price_history')
        item_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM price_history')
        total_records = cursor.fetchone()[0]

        cursor.execute('''
            SELECT item_id, title, COUNT(*)
            FROM price_history
            GROUP BY item_id
        ''')
        items = cursor.fetchall()

        print("\n📊 监控统计")
        print("="*60)
        print(f"监控商品数: {item_count}")
        print(f"历史记录数: {total_records}")
        print("\n商品列表:")
        for item_id, title, count in items:
            print(f"  - {title} ({count} 条记录)")

        conn.close()


def main():
    demo = PriceMonitorDemo()

    print("\n🌾 价格监控系统 - 演示版")
    print("="*60)

    # 添加测试数据
    demo.add_test_data()

    # 显示统计
    demo.show_statistics()

    # 测试监控
    demo.monitor_test()


if __name__ == "__main__":
    main()
