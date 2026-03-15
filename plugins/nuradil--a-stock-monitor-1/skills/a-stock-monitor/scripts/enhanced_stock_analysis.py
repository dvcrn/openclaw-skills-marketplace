#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版股票分析系统
整合：龙虎榜 + 主力资金 + 技术指标 + 市场情绪
功能：综合评分、智能选股、买卖点建议
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_cache_db import StockCache
from eastmoney_api import EastMoneyAPI
from lhb_fetcher import LHBFetcher


class EnhancedStockAnalyzer:
    """增强版股票分析器"""
    
    def __init__(self):
        self.cache = StockCache()
        self.api = EastMoneyAPI()
        self.lhb = LHBFetcher()
    
    def analyze_stock(self, code: str) -> Dict:
        """
        综合分析单只股票
        
        Args:
            code: 股票代码
        
        Returns:
            综合分析报告
        """
        # 1. 获取实时行情
        realtime = self.api.get_realtime(code)
        if not realtime:
            return {'error': f'无法获取 {code} 实时数据'}
        
        # 2. 获取龙虎榜数据
        lhb_data = self.cache.get_lhb(code)
        
        # 3. 获取主力资金数据
        fund_data = self.cache.get_fund_flow(code)
        
        # 4. 计算综合评分 (0-100)
        score = 50  # 基础分
        
        # 涨跌幅评分 (+/- 20 分)
        change_pct = realtime.get('change_pct', 0)
        if change_pct > 5:
            score += 15
        elif change_pct > 3:
            score += 10
        elif change_pct > 0:
            score += 5
        elif change_pct < -5:
            score -= 15
        elif change_pct < -3:
            score -= 10
        elif change_pct < 0:
            score -= 5
        
        # 龙虎榜评分 (+/- 20 分)
        if lhb_data:
            net_amount = lhb_data.get('net_amount', 0)
            if net_amount > 100000000:  # 净买入>1 亿
                score += 20
            elif net_amount > 50000000:  # 净买入>5 千万
                score += 15
            elif net_amount > 10000000:  # 净买入>1 千万
                score += 10
            elif net_amount < -50000000:  # 净卖出>5 千万
                score -= 15
            elif net_amount < -10000000:  # 净卖出>1 千万
                score -= 10
        
        # 量比评分 (+/- 10 分)
        volume_ratio = realtime.get('volume_ratio', 1)
        if volume_ratio > 3:
            score += 10
        elif volume_ratio > 2:
            score += 5
        elif volume_ratio < 0.5:
            score -= 5
        
        # 换手率评分 (+/- 10 分)
        turnover_rate = realtime.get('turnover_rate', 0)
        if 5 <= turnover_rate <= 15:
            score += 10
        elif 3 <= turnover_rate <= 20:
            score += 5
        elif turnover_rate > 20:
            score -= 5
        
        score = max(0, min(100, score))
        
        # 5. 生成评级
        if score >= 80:
            rating = '强烈推荐'
            emoji = '🔥'
        elif score >= 70:
            rating = '推荐'
            emoji = '🟢'
        elif score >= 60:
            rating = '谨慎推荐'
            emoji = '🟡'
        elif score >= 50:
            rating = '中性'
            emoji = '⚪'
        elif score >= 40:
            rating = '谨慎'
            emoji = '🟠'
        else:
            rating = '回避'
            emoji = '🔴'
        
        # 6. 生成买卖点建议
        current_price = realtime.get('latest_price', 0)
        if score >= 70:
            suggestion = f'可考虑买入，目标价 {current_price * 1.1:.2f}，止损 {current_price * 0.95:.2f}'
        elif score >= 60:
            suggestion = f'观望为主，若突破 {current_price * 1.05:.2f} 可跟进'
        elif score >= 40:
            suggestion = f'持有观望，跌破 {current_price * 0.95:.2f} 考虑减仓'
        else:
            suggestion = f'建议回避或减仓，反弹至 {current_price * 0.98:.2f} 附近离场'
        
        return {
            'code': code,
            'name': realtime.get('name', ''),
            'price': current_price,
            'change_pct': change_pct,
            'volume_ratio': volume_ratio,
            'turnover_rate': turnover_rate,
            'lhb_net': lhb_data.get('net_amount', 0) if lhb_data else None,
            'score': score,
            'rating': rating,
            'emoji': emoji,
            'suggestion': suggestion,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def analyze_lhb_top_stocks(self, limit: int = 10) -> List[Dict]:
        """
        分析龙虎榜净买入最多的股票
        
        Args:
            limit: 分析数量
        
        Returns:
            分析报告列表
        """
        top_stocks = self.lhb.get_top_lhb_stocks(limit=limit)
        results = []
        
        for stock in top_stocks:
            code = stock['code']
            report = self.analyze_stock(code)
            report['lhb_rank'] = len(results) + 1
            report['lhb_net_amount'] = stock['net_amount']
            results.append(report)
        
        return results
    
    def generate_market_report(self) -> Dict:
        """
        生成市场综合报告
        
        Returns:
            市场报告
        """
        # 1. 龙虎榜情绪
        lhb_sentiment = self.lhb.analyze_lhb_sentiment()
        
        # 2. 获取涨跌家数
        market_data = self.api.get_market_all('all')
        if market_data:
            gainers = len([s for s in market_data if s.get('change_pct', 0) > 0])
            losers = len([s for s in market_data if s.get('change_pct', 0) < 0])
            total = len(market_data)
        else:
            gainers = losers = total = 0
        
        # 3. 综合市场情绪
        market_score = 50
        if total > 0:
            gainer_ratio = gainers / total
            market_score = 50 + (gainer_ratio - 0.5) * 40
        
        # 结合龙虎榜情绪
        if lhb_sentiment.get('score'):
            market_score = (market_score + lhb_sentiment['score']) / 2
        
        if market_score >= 70:
            market_sentiment = '极度乐观'
            market_emoji = '🔴'
        elif market_score >= 60:
            market_sentiment = '乐观'
            market_emoji = '🟠'
        elif market_score >= 50:
            market_sentiment = '偏乐观'
            market_emoji = '🟢'
        elif market_score >= 40:
            market_sentiment = '偏悲观'
            market_emoji = '🟡'
        elif market_score >= 30:
            market_sentiment = '悲观'
            market_emoji = '🔵'
        else:
            market_sentiment = '极度悲观'
            market_emoji = '⚫'
        
        return {
            'market_score': round(market_score, 1),
            'market_sentiment': market_sentiment,
            'market_emoji': market_emoji,
            'total_stocks': total,
            'gainers': gainers,
            'losers': losers,
            'gainer_ratio': round(gainers/total*100, 1) if total > 0 else 0,
            'lhb_sentiment': lhb_sentiment.get('sentiment', '无数据'),
            'lhb_score': lhb_sentiment.get('score', 50),
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def main():
    """主函数：生成综合股票分析报告"""
    print("=" * 80)
    print("增强版股票分析系统 - 龙虎榜 + 资金流向 + 技术指标")
    print("=" * 80)
    
    analyzer = EnhancedStockAnalyzer()
    
    # 1. 市场综合报告
    print("\n📊 市场综合报告")
    print("-" * 80)
    report = analyzer.generate_market_report()
    print(f"   市场情绪：{report['market_emoji']} {report['market_sentiment']} ({report['market_score']}分)")
    print(f"   涨跌家数：{report['gainers']}涨 {report['losers']}跌 (共{report['total_stocks']}只)")
    print(f"   上涨占比：{report['gainer_ratio']}%")
    print(f"   龙虎榜情绪：{report['lhb_sentiment']} ({report['lhb_score']}分)")
    print(f"   更新时间：{report['update_time']}")
    
    # 2. 龙虎榜 TOP10 股票分析
    print("\n🏆 龙虎榜净买入 TOP10 股票分析")
    print("-" * 80)
    top_stocks = analyzer.analyze_lhb_top_stocks(limit=10)
    
    if top_stocks:
        print(f"{'排名':<4} {'代码':<8} {'名称':<12} {'价格':>8} {'涨跌':>8} {'净买入':>12} {'评分':>6} {'评级':>10}")
        print("-" * 80)
        
        for stock in top_stocks:
            if 'error' not in stock:
                lhb_net = stock.get('lhb_net_amount', 0)
                lhb_net_str = f"{lhb_net/10000:.1f}万" if lhb_net else "N/A"
                print(f"{stock.get('lhb_rank', 0):<4} {stock['code']:<8} {stock['name']:<12} "
                      f"¥{stock['price']:>6.2f} {stock['change_pct']:>+7.2f}% "
                      f"{lhb_net_str:>12} {stock['score']:>5.0f}分 {stock['emoji']} {stock['rating']}")
        
        # 3. 详细建议
        print("\n💡 重点股票操作建议")
        print("-" * 80)
        for i, stock in enumerate(top_stocks[:3], 1):
            if 'error' not in stock:
                print(f"\n{i}. {stock['code']} {stock['name']} (评分：{stock['score']}分)")
                print(f"   当前价：¥{stock['price']} ({stock['change_pct']:+.2f}%)")
                print(f"   龙虎榜净买入：{stock.get('lhb_net_amount', 0)/10000:.1f}万")
                print(f"   建议：{stock['suggestion']}")
    else:
        print("   暂无龙虎榜数据或数据异常")
    
    print("\n" + "=" * 80)
    print(f"分析完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == '__main__':
    main()
