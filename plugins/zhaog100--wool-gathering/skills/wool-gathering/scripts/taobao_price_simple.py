#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝价格爬虫 - 简化版
基于真实API，简化实现
"""

import re
import json
import time
import requests
from datetime import datetime


class TaobaoPriceSpiderSimple:
    """淘宝价格爬虫（简化版）"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })

    def extract_item_id(self, url_or_id):
        """提取商品ID"""
        if url_or_id.isdigit():
            return url_or_id

        patterns = [
            r'[&?]id=(\d+)',
            r'/i(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)

        return None

    def get_item_info(self, item_id):
        """
        获取商品信息（简化版）
        使用淘宝H5接口
        """
        url = f"https://h5api.m.taobao.com/h5/mtop.taobao.detailmtopstability.getitemdetail/1.0/"

        params = {
            'jsv': '2.5.1',
            'appKey': '12574478',
            't': str(int(time.time() * 1000)),
            'api': 'mtop.taobao.detailmtopstability.getitemdetail',
            'v': '1.0',
            'type': 'json',
            'dataType': 'json',
            'data': f'{{"itemNumId":"{item_id}"}}'
        }

        try:
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # 解析返回数据
                ret_list = data.get('data', {}).get('ret', [])

                if ret_list and 'SUCCESS' in ret_list[0]:
                    item_info = data.get('data', {}).get('data', {})

                    title = item_info.get('title', f'淘宝商品-{item_id}')
                    price_str = item_info.get('price', '0')

                    # 解析价格
                    try:
                        price = float(price_str.replace('¥', '').replace(',', ''))
                    except:
                        price = 0.0

                    if price > 0:
                        return {
                            'success': True,
                            'platform': 'taobao',
                            'item_id': item_id,
                            'title': title,
                            'price': price,
                            'original_price': price,
                            'url': f'https://item.taobao.com/item.htm?id={item_id}',
                            'source': 'h5_api',
                            'timestamp': datetime.now().isoformat()
                        }

            return {'success': False, 'error': 'API返回异常'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_price(self, item_id_or_url):
        """获取价格"""
        item_id = self.extract_item_id(item_id_or_url)

        if not item_id:
            print(f"❌ 无效的商品ID或URL")
            return {'success': False, 'error': '无效输入'}

        print(f"🔍 获取淘宝商品价格: {item_id}")

        result = self.get_item_info(item_id)

        if result['success']:
            print(f"✅ 成功: ¥{result['price']}")
        else:
            print(f"❌ 失败: {result['error']}")

        return result


def test():
    """测试"""
    spider = TaobaoPriceSpiderSimple()

    # 测试商品ID（需要真实的淘宝商品ID）
    test_items = [
        '560852934047',  # 示例商品ID
    ]

    print("\n" + "="*60)
    print("淘宝价格爬虫测试")
    print("="*60)

    for item_id in test_items:
        print(f"\n--- 测试: {item_id} ---")
        result = spider.get_price(item_id)

        if result['success']:
            print(f"   商品: {result['title']}")
            print(f"   价格: ¥{result['price']}")
            print(f"   链接: {result['url']}")

        time.sleep(1)

    print("\n" + "="*60)
    print("提示: 淘宝API需要真实的商品ID才能返回数据")
    print("建议: 使用真实的淘宝商品ID进行测试")
    print("="*60)


if __name__ == "__main__":
    test()
