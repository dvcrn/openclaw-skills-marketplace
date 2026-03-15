#!/usr/bin/env python3
"""
购物优惠API封装
支持淘宝、京东等多平台优惠券查询
"""

import sys
import os
import json
import urllib.parse
import urllib.request
from datetime import datetime

# 淘宝客配置（已预配置，用户安装后可直接使用）
CONFIG = {
    'appkey': '07d16b40e9c7485d8573f936173aa6d9',
    'sid': '41886',
    'pid': 'mm_200970015_125850084_116244500128',
    'union_id': '1001703383',
}

class ZheTaoKeAPI:
    """
    购物优惠API封装类
    
    支持的API:
    - 淘宝搜索、详情、优惠券查询
    - 京东搜索、优惠券查询
    - 商品榜单查询
    """
    
    def __init__(self):
        self.appkey = CONFIG['appkey']
        self.sid = CONFIG['sid']
        self.pid = CONFIG['pid']
        self.union_id = CONFIG['union_id']
    
    def _request(self, url, params, timeout=20):
        """
        发送HTTP请求
        
        Args:
            url: API地址
            params: 请求参数
            timeout: 超时时间
            
        Returns:
            dict: JSON响应数据
        """
        try:
            query = urllib.parse.urlencode(params)
            full_url = f"{url}?{query}"
            
            req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw_data = response.read()
                # 处理UTF-8 BOM
                if raw_data.startswith(b'\xef\xbb\xbf'):
                    raw_data = raw_data[3:]
                return json.loads(raw_data.decode('utf-8'))
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    # ==================== 淘宝API ====================
    
    def taobao_search(self, keyword, page=1, page_size=20, sort='new', **kwargs):
        """
        淘宝全网搜索API
        
        接口地址: https://api.zhetaoke.com:10003/api/api_quanwang.ashx
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量(1-50)
            sort: 排序方式(new/price_asc/price_desc等)
            **kwargs: 其他参数
            
        Returns:
            dict: 搜索结果
        """
        params = {
            'appkey': self.appkey,
            'sid': self.sid,
            'pid': self.pid,
            'page': page,
            'page_size': page_size,
            'sort': sort,
            'q': keyword,
        }
        params.update(kwargs)
        
        return self._request(
            'https://api.zhetaoke.com:10003/api/api_quanwang.ashx',
            params
        )
    
    def taobao_detail(self, item_id):
        """
        淘宝商品详情API
        
        接口地址: https://api.zhetaoke.com:10001/api/api_detail.ashx
        
        Args:
            item_id: 淘宝商品ID
            
        Returns:
            dict: 商品详情
        """
        params = {
            'appkey': self.appkey,
            'sid': self.sid,
            'pid': self.pid,
            'tao_id': item_id,
        }
        
        return self._request(
            'https://api.zhetaoke.com:10001/api/api_detail.ashx',
            params
        )
    
    def taobao_convert(self, url):
        """
        淘宝优惠链接API
        
        接口地址: https://api.zhetaoke.com:10001/api/open_gaoyongzhuanlian_tkl_piliang.ashx
        
        Args:
            url: 淘宝商品链接或淘口令
            
        Returns:
            dict: 获取优惠链接结果，包含短链接和淘口令
        """
        params = {
            'appkey': self.appkey,
            'sid': self.sid,
            'pid': self.pid,
            'tkl': url,
        }
        
        return self._request(
            'https://api.zhetaoke.com:10001/api/open_gaoyongzhuanlian_tkl_piliang.ashx',
            params
        )
    
    def taobao_all(self, page=1, page_size=20, sort='new', **kwargs):
        """
        淘宝全站领券商品API
        
        接口地址: https://api.zhetaoke.com:10001/api/api_all.ashx
        
        Args:
            page: 页码
            page_size: 每页数量
            sort: 排序方式
            **kwargs: 其他筛选参数(cid分类/youquan有券等)
            
        Returns:
            dict: 商品列表
        """
        params = {
            'appkey': self.appkey,
            'sid': self.sid,
            'pid': self.pid,
            'page': page,
            'page_size': page_size,
            'sort': sort,
        }
        params.update(kwargs)
        
        return self._request(
            'https://api.zhetaoke.com:10001/api/api_all.ashx',
            params
        )
    
    def taobao_quantian(self, page=1, page_size=20, sort='new', **kwargs):
        """
        淘宝全天销量榜API
        
        接口地址: https://api.zhetaoke.com:10001/api/api_quantian.ashx
        
        Args:
            page: 页码
            page_size: 每页数量
            sort: 排序方式
            **kwargs: 其他参数
            
        Returns:
            dict: 销量榜商品
        """
        params = {
            'appkey': self.appkey,
            'sid': self.sid,
            'pid': self.pid,
            'page': page,
            'page_size': page_size,
            'sort': sort,
        }
        params.update(kwargs)
        
        return self._request(
            'https://api.zhetaoke.com:10001/api/api_quantian.ashx',
            params
        )
    
    def taobao_shishi(self, page=1, page_size=20, **kwargs):
        """
        淘宝实时人气榜API
        
        接口地址: https://api.zhetaoke.com:10001/api/api_shishi.ashx
        
        Args:
            page: 页码
            page_size: 每页数量
            **kwargs: 其他参数
            
        Returns:
            dict: 实时人气商品
        """
        params = {
            'appkey': self.appkey,
            'sid': self.sid,
            'pid': self.pid,
            'page': page,
            'page_size': page_size,
        }
        params.update(kwargs)
        
        return self._request(
            'https://api.zhetaoke.com:10001/api/api_shishi.ashx',
            params
        )
    
    def taobao_yongjin(self, page=1, page_size=20, **kwargs):
        """
        淘宝实时支出优惠榜API
        
        接口地址: https://api.zhetaoke.com:10001/api/api_yongjin.ashx
        
        Args:
            page: 页码
            page_size: 每页数量
            **kwargs: 其他参数
            
        Returns:
            dict: 高优惠商品
        """
        params = {
            'appkey': self.appkey,
            'sid': self.sid,
            'pid': self.pid,
            'page': page,
            'page_size': page_size,
        }
        params.update(kwargs)
        
        return self._request(
            'https://api.zhetaoke.com:10001/api/api_yongjin.ashx',
            params
        )
    
    # ==================== 京东API ====================
    
    def jd_search(self, keyword, page=1, page_size=20, sort='new', **kwargs):
        """
        京东全网搜索API
        
        接口地址: http://api.zhetaoke.com:20000/api/api_quanwang.ashx
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            sort: 排序方式
            **kwargs: 其他参数
            
        Returns:
            dict: 搜索结果
        """
        params = {
            'appkey': self.appkey,
            'sid': self.sid,
            'pid': self.pid,
            'unionId': self.union_id,
            'page': page,
            'page_size': page_size,
            'sort': sort,
            'q': keyword,
        }
        params.update(kwargs)
        
        return self._request(
            'http://api.zhetaoke.com:20000/api/api_quanwang.ashx',
            params
        )
    
    def jd_all(self, page=1, page_size=20, sort='new', **kwargs):
        """
        京东全站领券商品API
        
        接口地址: http://api.zhetaoke.com:20000/api/api_all.ashx
        
        Args:
            page: 页码
            page_size: 每页数量
            sort: 排序方式
            **kwargs: 其他筛选参数
            
        Returns:
            dict: 商品列表
        """
        params = {
            'appkey': self.appkey,
            'sid': self.sid,
            'pid': self.pid,
            'unionId': self.union_id,
            'page': page,
            'page_size': page_size,
            'sort': sort,
        }
        params.update(kwargs)
        
        return self._request(
            'http://api.zhetaoke.com:20000/api/api_all.ashx',
            params
        )
    
    def jd_convert(self, url):
        """
        京东优惠链接API
        
        接口地址: http://api.zhetaoke.com:20000/api/open_gaoyongzhuanlian_tkl_piliang.ashx
        
        Args:
            url: 京东商品链接
            
        Returns:
            dict: 获取优惠链接结果
        """
        params = {
            'appkey': self.appkey,
            'tkl': url,
            'unionId': self.union_id,
        }
        
        return self._request(
            'http://api.zhetaoke.com:20000/api/open_gaoyongzhuanlian_tkl_piliang.ashx',
            params
        )
    
    # ==================== 线报群API ====================
    
    def xianbao_groups(self):
        """
        获取线报群列表API
        
        接口地址: https://api.zhetaoke.com:10001/api/api_xianbao_qun.ashx
        
        Returns:
            dict: 线报群列表
        """
        params = {
            'appkey': self.appkey,
            'page': 1,
            'page_size': 200,
        }
        
        return self._request(
            'https://api.zhetaoke.com:10001/api/api_xianbao_qun.ashx',
            params
        )
    
    def xianbao_search(self, keyword='', group_ids='', interval=1440, page=1, page_size=50):
        """
        搜索线报群商品API
        
        接口地址: https://api.zhetaoke.com:10001/api/api_xianbao.ashx
        
        Args:
            keyword: 搜索关键词
            group_ids: 群ID列表，逗号分隔
            interval: 时间范围(分钟)，最大1440
            page: 页码
            page_size: 每页数量
            
        Returns:
            dict: 线报商品
        """
        params = {
            'appkey': self.appkey,
            'id': group_ids,
            'type': '0',
            'page': page,
            'page_size': page_size,
            'msg': '1',
            'interval': interval,
        }
        if keyword:
            params['q'] = keyword
        
        return self._request(
            'https://api.zhetaoke.com:10001/api/api_xianbao.ashx',
            params
        )
    
    # ==================== 工具方法 ====================
    
    def convert_item(self, item):
        """
        自动获取优惠链接商品
        
        Args:
            item: 商品信息字典
            
        Returns:
            dict: 添加获取优惠链接后的商品信息
        """
        plat = item.get('plat', '1')
        tao_id = item.get('tao_id', '')
        
        if not tao_id:
            return item
        
        # 构建商品链接
        if plat == '1':
            url = f"https://item.taobao.com/item.htm?id={tao_id}"
            result = self.taobao_convert(url)
        else:
            url = f"https://item.jd.com/{tao_id}.html"
            result = self.jd_convert(url)
        
        if result and result.get('status') == 200:
            item['short_url'] = result.get('shorturl', '')
            item['tkl'] = result.get('result_tkl', '')
        
        return item


def main():
    """测试API"""
    if len(sys.argv) < 2:
        print("购物优惠平台API测试工具")
        print("=" * 50)
        print("\n使用方法:")
        print("  python3 zhetaoke_api.py <命令> [参数]")
        print("\n命令:")
        print("  search <关键词>     - 全网搜索")
        print("  detail <商品ID>     - 商品详情")
        print("  groups              - 线报群列表")
        print("  xianbao <关键词>    - 搜索线报群")
        print("  quantian            - 全天销量榜")
        print("  shishi              - 实时人气榜")
        print("  yongjin             - 优惠榜")
        sys.exit(1)
    
    api = ZheTaoKeAPI()
    cmd = sys.argv[1]
    
    if cmd == 'search':
        keyword = sys.argv[2] if len(sys.argv) > 2 else '牛奶'
        print(f"🔍 搜索「{keyword}」...")
        
        # 淘宝搜索
        result = api.taobao_search(keyword, page_size=3)
        if result and result.get('status') == 200:
            print(f"\n🍑 淘宝找到 {len(result.get('content', []))} 个商品")
            for item in result.get('content', [])[:2]:
                print(f"  - {item.get('title', '')[:40]}...")
        
        # 京东搜索
        result = api.jd_search(keyword, page_size=3)
        if result and result.get('status') == 200:
            print(f"\n🐶 京东找到 {len(result.get('content', []))} 个商品")
            for item in result.get('content', [])[:2]:
                print(f"  - {item.get('title', '')[:40]}...")
    
    elif cmd == 'detail':
        item_id = sys.argv[2] if len(sys.argv) > 2 else '554832820990'
        print(f"🔍 查询商品 {item_id} 详情...")
        result = api.taobao_detail(item_id)
        if result and result.get('status') == 200:
            item = result.get('content', [{}])[0]
            print(f"\n📦 {item.get('title', '')}")
            print(f"💰 价格：¥{item.get('quanhou_jiage', item.get('size', ''))}")
            print(f"🎫 优惠券：¥{item.get('coupon_info_money', '0')}")
    
    elif cmd == 'groups':
        print("📢 获取线报群列表...")
        result = api.xianbao_groups()
        if result and result.get('status') == 200:
            groups = result.get('content', [])
            print(f"\n✅ 找到 {len(groups)} 个线报群")
            for g in groups[:5]:
                print(f"  - {g.get('qunhao')}: {g.get('name', '')[:30]}")
    
    elif cmd == 'xianbao':
        keyword = sys.argv[2] if len(sys.argv) > 2 else '牛奶'
        print(f"📢 搜索线报群「{keyword}」...")
        result = api.xianbao_search(keyword=keyword)
        if result and result.get('status') == 200:
            items = result.get('data', [])
            print(f"\n✅ 找到 {len(items)} 个线报")
            for item in items[:3]:
                print(f"  - {item.get('title', '')[:40]}...")
        else:
            print(f"\n❌ 未找到线报")
    
    elif cmd == 'quantian':
        print("📊 获取全天销量榜...")
        result = api.taobao_quantian(page_size=5)
        if result and result.get('status') == 200:
            items = result.get('content', [])
            print(f"\n✅ 找到 {len(items)} 个商品")
            for item in items[:3]:
                print(f"  - {item.get('title', '')[:40]}...")
    
    elif cmd == 'shishi':
        print("📊 获取实时人气榜...")
        result = api.taobao_shishi(page_size=5)
        if result and result.get('status') == 200:
            items = result.get('content', [])
            print(f"\n✅ 找到 {len(items)} 个商品")
            for item in items[:3]:
                print(f"  - {item.get('title', '')[:40]}...")
    
    elif cmd == 'yongjin':
        print("💰 获取优惠榜...")
        result = api.taobao_yongjin(page_size=5)
        if result and result.get('status') == 200:
            items = result.get('content', [])
            print(f"\n✅ 找到 {len(items)} 个商品")
            for item in items[:3]:
                print(f"  - {item.get('title', '')[:40]}...")
    
    else:
        print(f"❌ 未知命令: {cmd}")


if __name__ == '__main__':
    main()
