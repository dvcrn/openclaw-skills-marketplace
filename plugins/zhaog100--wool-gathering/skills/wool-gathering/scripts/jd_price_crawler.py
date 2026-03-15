#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东价格爬虫
支持通过API和网页解析获取价格
"""

import re
import json
import time
import requests
from datetime import datetime


class JDPriceCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def get_item_id(self, url):
        """从URL提取商品ID"""
        patterns = [
            r'/(\d+)\.html',
            r'item\.jd\.com/(\d+)',
            r'sku=(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_price_by_api(self, item_id):
        """通过API获取价格"""
        url = f"https://p.3.cn/prices/mgets?skuIds=J_{item_id}"

        try:
            response = self.session.get(url, timeout=10)
            data = response.json()

            if data and len(data) > 0:
                price = float(data[0].get('p', 0))
                return {
                    'success': True,
                    'price': price,
                    'item_id': item_id,
                    'source': 'api',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"⚠️ API获取价格失败: {e}")

        return {'success': False, 'error': str(e)}

    def get_item_info(self, item_id):
        """获取商品详细信息"""
        url = f"https://item.jd.com/{item_id}.html"

        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'

            # 提取商品标题
            title_match = re.search(r'<title>(.*?)</title>', response.text)
            title = title_match.group(1).replace(' -京东', '') if title_match else '未知商品'

            # 提取价格（从页面JS变量）
            price_match = re.search(r'"price":"([\d.]+)"', response.text)
            price = float(price_match.group(1)) if price_match else None

            # 如果页面没有价格，用API获取
            if not price:
                api_result = self.get_price_by_api(item_id)
                price = api_result.get('price') if api_result['success'] else None

            return {
                'success': True if price else False,
                'item_id': item_id,
                'title': title,
                'price': price,
                'url': url,
                'platform': 'jd',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ 获取商品信息失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'item_id': item_id
            }

    def monitor(self, item_id_or_url):
        """监控商品"""
        # 提取商品ID
        if 'http' in item_id_or_url:
            item_id = self.get_item_id(item_id_or_url)
            url = item_id_or_url
        else:
            item_id = item_id_or_url
            url = f"https://item.jd.com/{item_id}.html"

        if not item_id:
            print(f"❌ 无效的商品ID或URL: {item_id_or_url}")
            return {'success': False}

        print(f"🔍 监控京东商品: {item_id}")

        # 获取商品信息
        item_info = self.get_item_info(item_id)

        if item_info['success']:
            print(f"✅ 商品: {item_info['title']}")
            print(f"💰 价格: ¥{item_info['price']}")
            print(f"🔗 链接: {item_info['url']}")
        else:
            print(f"❌ 获取失败: {item_info.get('error')}")

        return item_info


def main():
    import argparse

    parser = argparse.ArgumentParser(description="京东价格监控")
    parser.add_argument("item", help="商品ID或链接")
    parser.add_argument("--loop", action="store_true", help="持续监控")
    parser.add_argument("--interval", type=int, default=3600, help="监控间隔（秒）")

    args = parser.parse_args()

    crawler = JDPriceCrawler()

    if args.loop:
        print(f"🔄 开始持续监控，间隔 {args.interval} 秒")
        while True:
            crawler.monitor(args.item)
            time.sleep(args.interval)
    else:
        crawler.monitor(args.item)


if __name__ == "__main__":
    main()
