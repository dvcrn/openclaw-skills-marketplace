#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日龙虎榜分析报告 (增强版)
功能：龙虎榜 + 新闻政策 + 市场情绪综合分析
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lhb_fetcher import LHBFetcher
from stock_cache_db import StockCache
from news_policy_monitor import NewsPolicyMonitor


def generate_daily_lhb_report():
    """生成每日综合报告"""
    print("=" * 80)
    print(f"📈 每日股票分析报告 - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 80)
    
    fetcher = LHBFetcher()
    cache = StockCache()
    monitor = NewsPolicyMonitor()
    
    # ========== 第一部分：新闻政策面 ==========
    print("\n📰 新闻政策面")
    print("=" * 80)
    briefing = monitor.get_daily_briefing()
    
    print(f"\n🏛️  行业热点:")
    if briefing.get('industry_hotspots'):
        for i, item in enumerate(briefing['industry_hotspots'], 1):
            if item:
                impact_emoji = '🟢' if item.get('impact') == '利好' else '🔴'
                print(f"   {i}. {impact_emoji} {item.get('title', '')}")
                if item.get('stocks'):
                    stocks = item['stocks']
                    stock_names = []
                    for code in stocks:
                        stock_info = cache.get_stock(code)
                        name = stock_info['name'] if stock_info else code
                        stock_names.append(f"{code}({name})")
                    print(f"      相关：{', '.join(stock_names)}")
    
    # ========== 第二部分：龙虎榜数据 ==========
    today = datetime.now().strftime('%Y%m%d')
    print(f"\n📊 获取 {today} 龙虎榜数据...")
    fetcher.save_lhb_to_cache(today)
    
    # ========== 第三部分：情绪分析 ==========
    print("\n📈 市场情绪分析")
    print("-" * 80)
    sentiment = fetcher.analyze_lhb_sentiment()
    print(f"   龙虎榜情绪：{sentiment['emoji']} {sentiment['sentiment']} ({sentiment['score']}分)")
    print(f"   {sentiment['description']}")
    
    # ========== 第四部分：TOP10 排行 ==========
    print("\n🏆 龙虎榜净买入 TOP10")
    print("-" * 80)
    top_stocks = fetcher.get_top_lhb_stocks(limit=10)
    
    if top_stocks:
        print(f"{'排名':<4} {'代码':<8} {'名称':<12} {'净买入':>14} {'买卖比':>8}")
        print("-" * 80)
        
        for i, stock in enumerate(top_stocks, 1):
            net = stock['net_amount'] / 10000
            ratio = stock['buy_amount'] / stock['sell_amount'] if stock['sell_amount'] > 0 else 0
            print(f"{i:<4} {stock['code']:<8} {stock['name']:<12} ¥{net:>12.1f}万 {ratio:>7.2f}")
    
    # ========== 第五部分：重点股票分析 ==========
    print("\n💡 重点股票分析")
    print("-" * 80)
    
    if top_stocks:
        for i, stock in enumerate(top_stocks[:3], 1):
            code = stock['code']
            net = stock['net_amount'] / 10000
            ratio = stock['buy_amount'] / stock['sell_amount'] if stock['sell_amount'] > 0 else 0
            
            print(f"\n{i}. {code} {stock['name']} (净买入：¥{net:.1f}万，买卖比：{ratio:.2f})")
            
            # 操作建议
            if net > 50000 and ratio > 3:
                print(f"   评级：🔥 机构大额买入，重点关注")
                print(f"   建议：逢低布局，设置止损 -5%")
            elif net > 10000:
                print(f"   评级：🟢 机构买入，积极关注")
                print(f"   建议：适度参与，仓位<3 成")
            elif net > 0:
                print(f"   评级：🟡 少量买入，观望为主")
                print(f"   建议：等待更明确信号")
            else:
                print(f"   评级：🔴 资金流出，谨慎")
    
    # ========== 第六部分：综合总结 ==========
    print("\n" + "=" * 80)
    print("📋 今日总结与策略")
    print("-" * 80)
    
    # 综合评分
    total_score = sentiment['score']
    
    if total_score >= 60:
        print("   ✅ 市场情绪乐观，可适度参与")
        print("   建议仓位：5-7 成")
        print("   关注方向：龙虎榜净买入 + 行业利好共振")
    elif total_score >= 50:
        print("   ⚠️  市场情绪中性，精选个股")
        print("   建议仓位：3-5 成")
        print("   策略：低吸龙头，不追高")
    else:
        print("   🔴 市场情绪偏悲观，谨慎操作")
        print("   建议仓位：0-3 成")
        print("   策略：防守为主，等待机会")
    
    print(f"\n   数据更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == '__main__':
    generate_daily_lhb_report()
