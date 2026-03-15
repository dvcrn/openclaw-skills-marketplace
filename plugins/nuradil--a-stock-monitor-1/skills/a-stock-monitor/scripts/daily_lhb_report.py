#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日龙虎榜分析报告
功能：获取当日龙虎榜、分析机构动向、推荐关注股票
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lhb_fetcher import LHBFetcher
from stock_cache_db import StockCache
from news_policy_monitor import NewsPolicyMonitor


def generate_daily_lhb_report():
    """生成每日龙虎榜报告（含新闻政策）"""
    print("=" * 80)
    print(f"📈 每日龙虎榜分析报告 - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 80)
    
    fetcher = LHBFetcher()
    cache = StockCache()
    monitor = NewsPolicyMonitor()
    
    # 获取新闻政策简报
    print("\n📰 新闻政策面:")
    print("-" * 80)
    briefing = monitor.get_daily_briefing()
    monitor.print_briefing(briefing)
    
    # 1. 获取并保存今日龙虎榜
    today = datetime.now().strftime('%Y%m%d')
    print(f"\n📊 获取 {today} 龙虎榜数据...")
    fetcher.save_lhb_to_cache(today)
    
    # 2. 龙虎榜情绪分析
    print("\n📈 龙虎榜整体情绪")
    print("-" * 80)
    sentiment = fetcher.analyze_lhb_sentiment()
    print(f"   情绪评级：{sentiment['emoji']} {sentiment['sentiment']} ({sentiment['score']}分)")
    print(f"   {sentiment['description']}")
    
    # 3. 净买入 TOP10
    print("\n🏆 龙虎榜净买入 TOP10")
    print("-" * 80)
    top_stocks = fetcher.get_top_lhb_stocks(limit=10)
    
    if top_stocks:
        print(f"{'排名':<4} {'代码':<8} {'名称':<12} {'净买入金额':>14} {'买入额':>12} {'卖出额':>12}")
        print("-" * 80)
        
        for i, stock in enumerate(top_stocks, 1):
            # 获取股票名称
            stock_info = cache.get_stock(stock['code'])
            name = stock_info['name'] if stock_info else stock['code']
            
            net = stock['net_amount'] / 10000  # 转换为万元
            buy = stock['buy_amount'] / 10000
            sell = stock['sell_amount'] / 10000
            print(f"{i:<4} {stock['code']:<8} {name:<12} ¥{net:>12.1f}万 ¥{buy:>11.1f}万 ¥{sell:>11.1f}万")
    else:
        print("   暂无净买入为正的龙虎榜数据")
    
    # 4. 净卖出 TOP10 (风险警示)
    print("\n⚠️  龙虎榜净卖出 TOP10 (风险警示)")
    print("-" * 80)
    
    cursor = cache.conn.cursor()
    cutoff = datetime.now() - timedelta(hours=48)
    
    cursor.execute('''
        SELECT code, buy_amount, sell_amount, net_amount, update_time
        FROM lhb
        WHERE update_time > ? AND net_amount < 0
        ORDER BY net_amount ASC
        LIMIT 10
    ''', (cutoff,))
    
    sell_stocks = cursor.fetchall()
    if sell_stocks:
        print(f"{'排名':<4} {'代码':<8} {'名称':<12} {'净卖出金额':>14} {'买入额':>12} {'卖出额':>12}")
        print("-" * 80)
        
        for i, row in enumerate(sell_stocks, 1):
            code = row[0]
            # 获取股票名称
            stock_info = cache.get_stock(code)
            name = stock_info['name'] if stock_info else code
            
            net = row[3] / 10000
            buy = row[1] / 10000
            sell = row[2] / 10000
            print(f"{i:<4} {code:<8} {name:<12} ¥{abs(net):>12.1f}万 ¥{buy:>11.1f}万 ¥{sell:>11.1f}万")
    else:
        print("   暂无净卖出数据")
    
    # 5. 重点股票详细分析
    print("\n💡 重点股票分析")
    print("-" * 80)
    
    if top_stocks:
        for i, stock in enumerate(top_stocks[:3], 1):
            code = stock['code']
            net = stock['net_amount'] / 10000
            buy = stock['buy_amount'] / 10000
            sell = stock['sell_amount'] / 10000
            
            print(f"\n{i}. {code} (净买入：¥{net:.1f}万)")
            print(f"   龙虎榜买入：¥{buy:.1f}万 | 卖出：¥{sell:.1f}万")
            
            # 买卖比分析
            if sell > 0:
                ratio = buy / sell
                print(f"   买卖比：{ratio:.2f} (买盘{'强劲' if ratio > 2 else '一般' if ratio > 1 else '较弱'})")
            
            # 操作建议
            if net > 50000:  # 净买入>5 亿
                print(f"   建议：🔥 机构大额买入，重点关注，可逢低布局")
            elif net > 10000:  # 净买入>1 亿
                print(f"   建议：🟢 机构买入，积极关注")
            elif net > 5000:  # 净买入>5 千万
                print(f"   建议：🟡 适度关注，观察后续走势")
            else:
                print(f"   建议：⚪ 少量买入，保持观望")
    
    # 6. 总结
    print("\n" + "=" * 80)
    print("📋 今日总结")
    print("-" * 80)
    
    if sentiment['score'] >= 60:
        print("   ✅ 龙虎榜情绪乐观，机构买入积极，可适度参与")
    elif sentiment['score'] >= 50:
        print("   ⚠️  龙虎榜情绪中性，精选个股，控制仓位")
    else:
        print("   🔴 龙虎榜情绪偏悲观，谨慎操作，注意风险")
    
    print(f"\n   数据更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == '__main__':
    generate_daily_lhb_report()
