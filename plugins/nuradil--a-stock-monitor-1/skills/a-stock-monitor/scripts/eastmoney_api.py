#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富实时行情 API
数据源：http://push2.eastmoney.com
特点：免费、实时、无需 API Key
"""

import requests
import time
from typing import Dict, List, Optional
from datetime import datetime

class EastMoneyAPI:
    """东方财富实时行情 API"""
    
    BASE_URL = "http://push2.eastmoney.com/api/qt/stock/get"
    BATCH_URL = "http://push2.eastmoney.com/api/qt/stock/get"
    
    # 常用字段映射
    FIELD_MAP = {
        'f43': 'latest_price',      # 最新价
        'f44': 'open',              # 开盘价
        'f45': 'low',               # 最低价
        'f46': 'high',              # 最高价
        'f47': 'volume',            # 成交量
        'f48': 'turnover',          # 成交额
        'f49': 'turnover_rate',     # 换手率
        'f50': 'pe_ratio',          # 市盈率
        'f51': 'limit_up',          # 涨停价
        'f52': 'limit_down',        # 跌停价
        'f55': 'volume_ratio',      # 量比
        'f57': 'code',              # 股票代码
        'f58': 'name',              # 股票名称
        'f59': 'close',             # 昨收
        'f60': 'total_shares',      # 总股本
        'f61': 'change_rate',       # 涨速
        'f62': 'change_pct',        # 涨跌幅
        'f63': 'change_amount',     # 涨跌额
    }
    
    def __init__(self, timeout: int = 5, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/'
        })
    
    def _get_secid(self, code: str) -> str:
        """获取证券 ID（市场代码。股票代码）"""
        if code.startswith(('000', '001', '002', '300')):
            return f"0.{code}"  # 深交所
        elif code.startswith(('600', '601', '603', '605', '688')):
            return f"1.{code}"  # 上交所
        elif code.startswith(('4', '8')):
            return f"0.{code}"  # 北交所
        else:
            return f"0.{code}"
    
    def get_realtime(self, code: str, fields: str = None) -> Optional[Dict]:
        """
        获取单只股票实时行情
        
        Args:
            code: 股票代码（如 000001）
            fields: 字段列表，默认获取常用字段
        
        Returns:
            行情数据字典，失败返回 None
        """
        if fields is None:
            fields = "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55,f57,f58,f59,f60,f61,f62,f63"
        
        secid = self._get_secid(code)
        params = {
            "secid": secid,
            "fields": fields
        }
        
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json().get('data', {})
                    if data:
                        return self._parse_data(data)
                time.sleep(0.5 * (attempt + 1))  # 重试间隔递增
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                else:
                    print(f"获取 {code} 失败：{e}")
        
        return None
    
    def get_batch(self, codes: List[str], fields: str = None) -> List[Dict]:
        """
        批量获取股票实时行情
        
        Args:
            codes: 股票代码列表
            fields: 字段列表
        
        Returns:
            行情数据列表
        """
        if fields is None:
            fields = "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55,f57,f58,f59,f60,f61,f62,f63"
        
        results = []
        for i, code in enumerate(codes):
            data = self.get_realtime(code, fields)
            if data:
                results.append(data)
            
            # 每 50 只股票暂停一下，避免被封
            if (i + 1) % 50 == 0:
                time.sleep(1)
        
        return results
    
    def _parse_data(self, data: Dict) -> Dict:
        """解析数据，转换为易读格式"""
        result = {}
        for field, name in self.FIELD_MAP.items():
            value = data.get(field)
            if value is not None:
                # 价格类字段除以 100
                if field in ['f43', 'f44', 'f45', 'f46', 'f51', 'f52', 'f59']:
                    result[name] = round(value / 100, 2)
                else:
                    result[name] = value
        
        # 计算涨跌幅（如果没有直接返回）
        if 'change_pct' not in result and 'latest_price' in result and 'close' in result:
            if result['close'] > 0:
                result['change_pct'] = round(
                    (result['latest_price'] - result['close']) / result['close'] * 100, 2
                )
            else:
                result['change_pct'] = 0
        
        return result
    
    def get_market_all(self, market: str = 'all') -> List[Dict]:
        """
        获取全市场股票行情
        
        Args:
            market: 市场 ('all'=全部，'sh'=沪市，'sz'=深市，'bj'=北交所)
        
        Returns:
            全市场股票行情列表
        """
        # 使用东方财富全市场接口
        if market in ['all', 'sz']:
            sz_data = self._fetch_market_page(0, 'm.0')  # 深市
        else:
            sz_data = []
        
        if market in ['all', 'sh']:
            sh_data = self._fetch_market_page(0, 'm.1')  # 沪市
        else:
            sh_data = []
        
        if market == 'bj':
            bj_data = self._fetch_market_page(0, 'm.0', pn=1)  # 北交所
        else:
            bj_data = []
        
        return sz_data + sh_data + bj_data
    
    def _fetch_market_page(self, pn: int = 1, m: str = 'm.0', ps: int = 500) -> List[Dict]:
        """获取市场单页数据"""
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": pn,
            "pz": ps,
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": m,
            "fields": "f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26,f37,f38,f39,f40,f41,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f55,f56,f57,f58,f59,f60,f61,f62,f63"
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                result = resp.json().get('data', {})
                stocks = result.get('diff', [])
                return [self._parse_market_data(s) for s in stocks]
        except Exception as e:
            print(f"获取市场数据失败：{e}")
        
        return []
    
    def _parse_market_data(self, data: Dict) -> Dict:
        """解析市场数据"""
        return {
            'code': data.get('f12', ''),
            'name': data.get('f14', ''),
            'latest_price': data.get('f2', 0),
            'change_pct': data.get('f3', 0),
            'change_amount': data.get('f4', 0),
            'volume': data.get('f5', 0),
            'turnover': data.get('f6', 0),
            'amplitude': data.get('f7', 0),
            'high': data.get('f15', 0),
            'low': data.get('f17', 0),
            'open': data.get('f17', 0),
            'close': data.get('f2', 0),
            'pe_ratio': data.get('f9', 0),
            'pb_ratio': data.get('f23', 0),
            'total_market_cap': data.get('f20', 0),
            'float_market_cap': data.get('f21', 0),
            'turnover_rate': data.get('f8', 0),
            'volume_ratio': data.get('f10', 0),
        }


# 测试函数
def test_api():
    """测试 API 连接"""
    api = EastMoneyAPI()
    
    print("=" * 70)
    print("东方财富实时行情 API 测试")
    print("=" * 70)
    
    # 测试单只股票
    test_codes = ['000001', '600519', '300750', '688981']
    
    for code in test_codes:
        data = api.get_realtime(code)
        if data:
            print(f"\n{data['code']} - {data['name']}:")
            print(f"  最新价：¥{data['latest_price']:.2f}")
            print(f"  涨跌幅：{data['change_pct']:.2f}%")
            print(f"  成交量：{data['volume']:,}")
            print(f"  成交额：¥{data['turnover']/10000:.2f}万")
        else:
            print(f"\n{code}: 获取失败")
    
    print("\n" + "=" * 70)
    print(f"测试完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    test_api()
