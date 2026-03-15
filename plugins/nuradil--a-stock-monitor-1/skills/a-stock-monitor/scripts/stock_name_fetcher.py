#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取 A 股股票名称映射
用于龙虎榜等数据补充股票名称
"""

import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stock_cache_db import StockCache


def fetch_all_stock_names():
    """获取全市场股票名称映射"""
    print("📊 获取全市场股票列表...")
    
    try:
        # 使用 akshare 获取 A 股列表
        df = ak.stock_info_a_code_name()
        
        if df is not None and not df.empty:
            print(f"✅ 获取到 {len(df)} 只股票")
            
            # 保存到缓存
            cache = StockCache()
            
            # 转换为缓存格式
            stocks = []
            for _, row in df.iterrows():
                code = str(row['code']) if 'code' in row else str(row['股票代码'])
                name = str(row['name']) if 'name' in row else str(row['股票名称'])
                
                stocks.append({
                    'code': code,
                    'name': name,
                    'price': 0,
                    'change_pct': 0,
                    'volume': 0,
                    'amount': 0,
                    'update_time': datetime.now()
                })
            
            cache.save_stocks(stocks)
            print(f"✅ 已保存 {len(stocks)} 只股票到缓存")
            
            return len(stocks)
        else:
            print("⚠️  未获取到股票数据")
            return 0
            
    except Exception as e:
        print(f"❌ 获取失败：{e}")
        return 0


def get_stock_name(code: str) -> Optional[str]:
    """获取单只股票名称"""
    cache = StockCache()
    stock = cache.get_stock(code)
    
    if stock and stock.get('name'):
        return stock['name']
    
    # 缓存中没有，尝试实时获取
    try:
        df = ak.stock_info_a_code_name()
        code_str = str(code).zfill(6)
        row = df[df['code'] == code_str]
        
        if not row.empty:
            name = row.iloc[0]['name']
            # 保存到缓存
            cache.save_stocks([{
                'code': code_str,
                'name': name,
                'price': 0,
                'change_pct': 0,
                'volume': 0,
                'amount': 0,
                'update_time': datetime.now()
            }])
            return name
    except:
        pass
    
    return code


if __name__ == '__main__':
    fetch_all_stock_names()
    
    # 测试
    print("\n测试获取股票名称:")
    test_codes = ['002261', '002506', '600519', '000858']
    
    cache = StockCache()
    for code in test_codes:
        stock = cache.get_stock(code)
        if stock:
            print(f"  {code}: {stock['name']}")
        else:
            print(f"  {code}: 未找到")
