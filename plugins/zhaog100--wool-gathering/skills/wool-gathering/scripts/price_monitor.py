#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格监控脚本
支持淘宝、京东商品价格监控
"""

import json
import time
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

class PriceMonitor:
    def __init__(self, config_path="../assets/config.json"):
        self.config = self.load_config(config_path)
        self.db_path = self.config.get("db_path", "price_history.db")
        self.init_database()

    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 配置文件不存在: {config_path}")
            return {
                "db_path": "price_history.db",
                "items": [],
                "threshold": 0.8,  # 降价阈值（80%）
                "push_config": {}
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
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ 数据库初始化完成")

    def get_jd_price(self, item_id):
        """获取京东商品价格"""
        url = f"https://item.jd.com/{item_id}.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            # 这里需要解析HTML或使用API获取价格
            # 简化示例，实际需要更复杂的解析逻辑
            return {
                "platform": "jd",
                "item_id": item_id,
                "price": None,  # 实际从页面解析
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ 获取京东价格失败: {e}")
            return None

    def get_taobao_price(self, item_id):
        """获取淘宝商品价格"""
        # 淘宝需要登录Cookie，建议使用联盟API
        print("⚠️ 淘宝价格监控需要联盟API或Cookie")
        return None

    def save_price(self, price_data):
        """保存价格记录"""
        if not price_data:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_history
            (item_id, platform, title, price, original_price, url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            price_data.get("item_id"),
            price_data.get("platform"),
            price_data.get("title"),
            price_data.get("price"),
            price_data.get("original_price"),
            price_data.get("url")
        ))
        conn.commit()
        conn.close()

    def check_price_drop(self, item_id, current_price):
        """检查是否降价"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price FROM price_history
            WHERE item_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (item_id,))
        prices = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not prices or len(prices) < 2:
            return False

        avg_price = sum(prices) / len(prices)
        threshold = self.config.get("threshold", 0.8)

        return current_price < avg_price * threshold

    def monitor_items(self):
        """监控商品列表"""
        items = self.config.get("items", [])

        for item in items:
            platform = item.get("platform")
            item_id = item.get("item_id")

            print(f"📊 监控商品: {platform} - {item_id}")

            if platform == "jd":
                price_data = self.get_jd_price(item_id)
            elif platform == "taobao":
                price_data = self.get_taobao_price(item_id)
            else:
                print(f"❌ 不支持的平台: {platform}")
                continue

            if price_data and price_data.get("price"):
                self.save_price(price_data)

                # 检查降价
                if self.check_price_drop(item_id, price_data["price"]):
                    self.send_notification(item, price_data)

            time.sleep(2)  # 避免频繁请求

    def send_notification(self, item, price_data):
        """发送降价通知"""
        print(f"🔔 降价通知: {item.get('name')}")
        print(f"   当前价格: ¥{price_data['price']}")
        print(f"   商品链接: {price_data['url']}")

        # TODO: 集成推送服务（微信、QQ等）
        push_config = self.config.get("push_config", {})
        if push_config.get("enabled"):
            self.push_to_wechat(item, price_data, push_config)

    def push_to_wechat(self, item, price_data, push_config):
        """推送消息到微信"""
        serverchan_key = push_config.get("serverchan_key")
        if not serverchan_key:
            return

        url = f"https://sctapi.ftqq.com/{serverchan_key}.send"
        data = {
            "title": f"降价通知: {item.get('name')}",
            "desp": f"""
**商品**: {item.get('name')}

**当前价格**: ¥{price_data['price']}

**商品链接**: [点击查看]({price_data['url']})

**监控时间**: {price_data['timestamp']}
            """
        }

        try:
            requests.post(url, data=data)
            print("✅ 微信推送成功")
        except Exception as e:
            print(f"❌ 微信推送失败: {e}")

    def add_item(self, url):
        """添加监控商品"""
        # 解析URL获取item_id和platform
        if "jd.com" in url:
            platform = "jd"
            item_id = url.split("/")[-1].replace(".html", "")
        elif "taobao.com" in url or "tmall.com" in url:
            platform = "taobao"
            # 解析淘宝商品ID需要更复杂的逻辑
            item_id = None
        else:
            print("❌ 不支持的平台")
            return

        if item_id:
            print(f"✅ 添加监控商品: {platform} - {item_id}")
            # TODO: 保存到配置文件

def main():
    import argparse

    parser = argparse.ArgumentParser(description="价格监控工具")
    parser.add_argument("--config", default="../assets/config.json", help="配置文件路径")
    parser.add_argument("--add", action="store_true", help="添加监控商品")
    parser.add_argument("--url", help="商品链接")
    parser.add_argument("--history", action="store_true", help="查看价格历史")
    parser.add_argument("--item", help="商品ID")

    args = parser.parse_args()

    monitor = PriceMonitor(args.config)

    if args.add and args.url:
        monitor.add_item(args.url)
    elif args.history and args.item:
        # TODO: 实现价格历史查询
        print(f"📊 查询商品价格历史: {args.item}")
    else:
        monitor.monitor_items()

if __name__ == "__main__":
    main()
