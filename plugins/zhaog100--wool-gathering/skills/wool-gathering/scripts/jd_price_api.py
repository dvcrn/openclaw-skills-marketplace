#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东价格爬虫 - 实际可用版
使用多种方法获取京东商品价格
"""

import re
import json
import time
import requests
from datetime import datetime
from fake_useragent import UserAgent


class JDPriceSpider:
    """京东价格爬虫"""

    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def get_random_ua(self):
        """获取随机User-Agent"""
        try:
            return self.ua.random
        except:
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    def method1_price_api(self, sku_ids):
        """
        方法1: 使用京东价格API（推荐）
        这是最可靠的方法，使用京东公开的价格查询接口
        """
        url = "https://p.3.cn/prices/mgets"
        params = {
            'skuIds': ','.join([f'J_{sku_id}' for sku_id in sku_ids]),
            'type': 1
        }

        headers = {
            'User-Agent': self.get_random_ua(),
            'Referer': 'https://item.jd.com/',
        }

        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data:
                sku_id = item.get('id', '').replace('J_', '')
                price = float(item.get('p', 0))
                original_price = float(item.get('m', price)) if item.get('m') else price

                results.append({
                    'success': True,
                    'sku_id': sku_id,
                    'price': price,
                    'original_price': original_price,
                    'source': 'price_api',
                    'timestamp': datetime.now().isoformat()
                })

            return results

        except Exception as e:
            print(f"❌ 方法1失败: {e}")
            return [{'success': False, 'error': str(e)}]

    def method2_item_page(self, sku_id):
        """
        方法2: 解析商品详情页
        备用方法，从页面提取价格
        """
        url = f"https://item.jd.com/{sku_id}.html"
        headers = {
            'User-Agent': self.get_random_ua(),
        }

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'

            # 提取标题
            title_match = re.search(r'<title>(.*?)</title>', response.text)
            title = title_match.group(1).replace(' -京东', '').strip() if title_match else '未知商品'

            # 提取价格（从页面数据）
            price_patterns = [
                r'"price":"([\d.]+)"',
                r'"p":"([\d.]+)"',
                r'￥([\d.]+)',
            ]

            price = None
            for pattern in price_patterns:
                match = re.search(pattern, response.text)
                if match:
                    try:
                        price = float(match.group(1))
                        break
                    except:
                        continue

            if price:
                return {
                    'success': True,
                    'sku_id': sku_id,
                    'title': title,
                    'price': price,
                    'url': url,
                    'source': 'page_parse',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': '未找到价格'}

        except Exception as e:
            print(f"❌ 方法2失败: {e}")
            return {'success': False, 'error': str(e)}

    def method3_mobile_api(self, sku_id):
        """
        方法3: 使用移动端API
        移动端API通常更简单，反爬较弱
        """
        url = f"https://api.m.jd.com/client.action"
        params = {
            'functionId': 'wareBusiness',
            'appid': 'pc_product_detail',
            'body': json.dumps({
                'skuId': sku_id,
                'area': '1_72_2799_0',
                'cat': '9987,830,863'
            })
        }

        headers = {
            'User-Agent': self.get_random_ua(),
            'Referer': 'https://item.jd.com/',
        }

        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                price_info = data.get('price', {})

                if price_info:
                    return {
                        'success': True,
                        'sku_id': sku_id,
                        'price': float(price_info.get('p', 0)),
                        'original_price': float(price_info.get('m', 0)),
                        'source': 'mobile_api',
                        'timestamp': datetime.now().isoformat()
                    }

            return {'success': False, 'error': 'API返回异常'}

        except Exception as e:
            print(f"❌ 方法3失败: {e}")
            return {'success': False, 'error': str(e)}

    def get_price(self, sku_id):
        """
        获取商品价格（自动尝试多种方法）
        """
        print(f"🔍 获取京东商品价格: {sku_id}")

        # 方法1: 价格API（最快最可靠）
        results = self.method1_price_api([sku_id])
        if results and results[0].get('success'):
            result = results[0]
            result['platform'] = 'jd'
            result['item_id'] = sku_id
            result['title'] = f'京东商品-{sku_id}'
            result['url'] = f'https://item.jd.com/{sku_id}.html'
            print(f"✅ 价格API成功: ¥{result['price']}")
            return result

        # 方法2: 页面解析
        result = self.method2_item_page(sku_id)
        if result.get('success'):
            result['platform'] = 'jd'
            result['item_id'] = sku_id
            print(f"✅ 页面解析成功: ¥{result['price']}")
            return result

        # 方法3: 移动端API
        result = self.method3_mobile_api(sku_id)
        if result.get('success'):
            result['platform'] = 'jd'
            result['item_id'] = sku_id
            result['title'] = f'京东商品-{sku_id}'
            result['url'] = f'https://item.jd.com/{sku_id}.html'
            print(f"✅ 移动端API成功: ¥{result['price']}")
            return result

        print(f"❌ 所有方法都失败")
        return {'success': False, 'sku_id': sku_id, 'error': '无法获取价格'}

    def batch_get_prices(self, sku_ids):
        """批量获取价格"""
        print(f"🔍 批量获取 {len(sku_ids)} 个商品价格")
        return self.method1_price_api(sku_ids)


def test_jd_spider():
    """测试京东爬虫"""
    spider = JDPriceSpider()

    # 测试商品ID列表（热门商品）
    test_items = [
        '100012043978',  # iPhone 15 Pro Max
        '100070296293',  # MacBook Pro
        '100012345678',  # 不存在的商品（测试失败情况）
    ]

    print("\n" + "="*60)
    print("京东价格爬虫测试")
    print("="*60)

    for sku_id in test_items:
        print(f"\n--- 测试商品: {sku_id} ---")
        result = spider.get_price(sku_id)

        if result.get('success'):
            print(f"✅ 成功")
            print(f"   商品ID: {result.get('item_id')}")
            print(f"   价格: ¥{result.get('price')}")
            print(f"   原价: ¥{result.get('original_price')}")
            print(f"   来源: {result.get('source')}")
        else:
            print(f"❌ 失败: {result.get('error')}")

        time.sleep(1)  # 避免请求过快

    print("\n" + "="*60)

    # 批量测试
    print("\n📊 批量获取测试")
    results = spider.batch_get_prices(test_items[:2])

    for result in results:
        if result.get('success'):
            print(f"✅ {result.get('sku_id')}: ¥{result.get('price')}")
        else:
            print(f"❌ {result.get('sku_id')}: 失败")


if __name__ == "__main__":
    test_jd_spider()
