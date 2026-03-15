#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东价格爬虫 - 简化版
直接使用requests，无需额外依赖
"""

import re
import json
import time
import requests
from datetime import datetime


class JDPriceSpiderSimple:
    """京东价格爬虫（简化版）"""

    def __init__(self):
        self.session = requests.Session()

    def get_price_api(self, sku_id):
        """使用京东价格API"""
        url = f"https://p.3.cn/prices/mgets?skuIds=J_{sku_id}&type=1"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': f'https://item.jd.com/{sku_id}.html'
        }

        try:
            response = self.session.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if data and len(data) > 0:
                    price = float(data[0].get('p', 0))
                    original_price = float(data[0].get('m', price)) if data[0].get('m') else price

                    return {
                        'success': True,
                        'platform': 'jd',
                        'item_id': sku_id,
                        'title': f'京东商品-{sku_id}',
                        'price': price,
                        'original_price': original_price,
                        'url': f'https://item.jd.com/{sku_id}.html',
                        'source': 'api',
                        'timestamp': datetime.now().isoformat()
                    }

            return {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_item_page(self, sku_id):
        """从商品页面提取信息"""
        url = f"https://item.jd.com/{sku_id}.html"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'

            # 提取标题
            title_match = re.search(r'<title>(.*?)</title>', response.text)
            title = title_match.group(1).replace(' -京东', '').strip() if title_match else f'京东商品-{sku_id}'

            # 提取价格
            price_match = re.search(r'"price":"([\d.]+)"', response.text)

            if price_match:
                price = float(price_match.group(1))

                return {
                    'success': True,
                    'platform': 'jd',
                    'item_id': sku_id,
                    'title': title,
                    'price': price,
                    'url': url,
                    'source': 'page',
                    'timestamp': datetime.now().isoformat()
                }

            return {'success': False, 'error': '页面未找到价格'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_price(self, sku_id):
        """获取价格（自动尝试多种方法）"""
        print(f"🔍 获取京东商品价格: {sku_id}")

        # 方法1: API（推荐）
        result = self.get_price_api(sku_id)
        if result.get('success'):
            print(f"✅ API成功: ¥{result['price']}")
            return result

        print(f"⚠️ API失败，尝试页面解析...")

        # 方法2: 页面解析
        result = self.get_item_page(sku_id)
        if result.get('success'):
            print(f"✅ 页面解析成功: ¥{result['price']}")
            return result

        print(f"❌ 所有方法都失败")
        return {'success': False, 'item_id': sku_id, 'error': '无法获取价格'}


def test():
    """测试"""
    spider = JDPriceSpiderSimple()

    # 测试商品
    test_items = [
        '100012043978',  # iPhone 15 Pro Max
        '100048127491',  # 华为 Mate 60 Pro
    ]

    print("\n" + "="*60)
    print("京东价格爬虫测试")
    print("="*60)

    for sku_id in test_items:
        print(f"\n--- 测试: {sku_id} ---")
        result = spider.get_price(sku_id)

        if result.get('success'):
            print(f"   商品: {result.get('title')}")
            print(f"   价格: ¥{result.get('price')}")
            print(f"   原价: ¥{result.get('original_price')}")
            print(f"   来源: {result.get('source')}")
        else:
            print(f"   失败: {result.get('error')}")

        time.sleep(1)

    print("\n" + "="*60)


if __name__ == "__main__":
    test()
