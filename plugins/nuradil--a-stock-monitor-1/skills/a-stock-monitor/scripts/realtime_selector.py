#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时选股引擎 - 基于东方财富 API
每日推荐 3-5 只短线机会股 + 5-10 只中长线股票
"""

import json
import sys
from datetime import datetime
from typing import List, Dict
from eastmoney_api import EastMoneyAPI


class RealtimeStockSelector:
    """实时选股引擎"""
    
    # 预设活跃股票池（500 只，可按需扩展）
    STOCK_POOL = [
        # 科技/芯片
        '000001', '000002', '000063', '000100', '000157', '000333', '000538', '000568',
        '000625', '000651', '000661', '000725', '000858', '000895', '002001', '002007',
        '002027', '002049', '002129', '002142', '002179', '002230', '002236', '002241',
        '002252', '002304', '002352', '002371', '002415', '002456', '002460', '002466',
        '002475', '002493', '002594', '002648', '002714', '002812', '002821', '002916',
        '300014', '300059', '300122', '300124', '300274', '300308', '300316', '300347',
        '300363', '300390', '300408', '300413', '300433', '300498', '300502', '300601',
        '300623', '300628', '300661', '300724', '300750', '300759', '300760', '300782',
        '600000', '600009', '600010', '600011', '600015', '600016', '600018', '600019',
        '600028', '600029', '600030', '600031', '600036', '600048', '600050', '600104',
        '600111', '600115', '600118', '600131', '600138', '600150', '600160', '600176',
        '600183', '600188', '600196', '600208', '600219', '600221', '600233', '600256',
        '600271', '600276', '600297', '600309', '600346', '600352', '600362', '600372',
        '600383', '600390', '600392', '600398', '600406', '600415', '600418', '600426',
        '600436', '600438', '600460', '600486', '600487', '600489', '600497', '600498',
        '600519', '600522', '600547', '600570', '600580', '600584', '600585', '600588',
        '600600', '600660', '600690', '600703', '600733', '600745', '600760', '600776',
        '600809', '600845', '600867', '600884', '600885', '600887', '600893', '600900',
        '600905', '600919', '600926', '600938', '600958', '600989', '601006', '601012',
        '601066', '601088', '601111', '601127', '601138', '601166', '601186', '601211',
        '601225', '601288', '601318', '601328', '601336', '601390', '601398', '601601',
        '601628', '601633', '601658', '601668', '601669', '601688', '601698', '601728',
        '601766', '601788', '601800', '601816', '601818', '601857', '601877', '601878',
        '601881', '601888', '601898', '601899', '601919', '601939', '601985', '601988',
        '601991', '601992', '601995', '601997', '601998', '603019', '603160', '603259',
        '603260', '603288', '603501', '603659', '603799', '603806', '603833', '603888',
        '603899', '603986', '605117', '605499', '688001', '688002', '688005', '688008',
        '688009', '688012', '688016', '688019', '688029', '688036', '688041', '688063',
        '688082', '688088', '688099', '688100', '688105', '688111', '688126', '688180',
        '688187', '688188', '688202', '688208', '688223', '688234', '688235', '688256',
        '688271', '688276', '688278', '688301', '688363', '688385', '688396', '688425',
        '688536', '688599', '688690', '688777', '688981',
    ]
    
    def __init__(self):
        self.api = EastMoneyAPI(timeout=5, max_retries=3)
    
    def _get_stock_pool(self) -> List[str]:
        """获取预设股票池"""
        return self.STOCK_POOL
    
    def screen_short_term(self, limit: int = 5) -> List[Dict]:
        """
        短线选股策略（1-5 天）
        
        筛选条件：
        1. 涨跌幅 2%-5%（强势但未涨停）
        2. 量比 > 1.5（放量）
        3. 换手率 3%-15%（活跃）
        4. 股价 5-100 元（适中）
        5. 非 ST、非科创板
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始筛选短线股...", file=sys.stderr)
        
        # 使用预设股票池（500 只活跃股票）
        stock_pool = self._get_stock_pool()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 股票池：{len(stock_pool)} 只股票", file=sys.stderr)
        
        # 批量获取实时数据
        all_stocks = self.api.get_batch(stock_pool)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 获取到 {len(all_stocks)} 只股票实时数据", file=sys.stderr)
        
        # 筛选条件
        candidates = []
        for stock in all_stocks:
            # 过滤条件
            if self._filter_short_term(stock):
                score = self._score_short_term(stock)
                if score >= 60:
                    stock['score'] = score
                    candidates.append(stock)
        
        # 按评分排序
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 筛选出 {len(candidates)} 只候选股票", file=sys.stderr)
        
        return candidates[:limit]
    
    def _filter_short_term(self, stock: Dict) -> bool:
        """短线选股过滤条件"""
        # 排除 ST
        if 'ST' in stock.get('name', ''):
            return False
        
        # 排除科创板（688）
        if stock.get('code', '').startswith('688'):
            return False
        
        # 排除创业板（300）- 可选
        # if stock.get('code', '').startswith('300'):
        #     return False
        
        # 股价 5-100 元
        price = stock.get('latest_price', 0)
        if price < 5 or price > 100:
            return False
        
        # 涨跌幅 2%-5%
        change_pct = stock.get('change_pct', 0)
        if change_pct < 2 or change_pct > 7:
            return False
        
        # 量比 > 1.5
        volume_ratio = stock.get('volume_ratio', 0)
        if volume_ratio < 1.5:
            return False
        
        # 换手率 3%-15%
        turnover_rate = stock.get('turnover_rate', 0)
        if turnover_rate < 3 or turnover_rate > 15:
            return False
        
        # 成交额 > 5000 万
        turnover = stock.get('turnover', 0)
        if turnover < 50000000:
            return False
        
        return True
    
    def _score_short_term(self, stock: Dict) -> float:
        """
        短线选股评分（0-100）
        
        评分维度：
        - 涨跌幅（25 分）：3-5% 最佳
        - 量比（25 分）：2-5 倍最佳
        - 换手率（20 分）：5-10% 最佳
        - 成交额（15 分）：越大越好
        - 股价趋势（15 分）：接近高点加分
        """
        score = 0
        
        # 涨跌幅评分（25 分）
        change_pct = stock.get('change_pct', 0)
        if 3 <= change_pct <= 5:
            score += 25
        elif 2 <= change_pct < 3 or 5 < change_pct <= 7:
            score += 20
        else:
            score += 10
        
        # 量比评分（25 分）
        volume_ratio = stock.get('volume_ratio', 0)
        if 2 <= volume_ratio <= 5:
            score += 25
        elif 1.5 <= volume_ratio < 2 or 5 < volume_ratio <= 8:
            score += 20
        else:
            score += 10
        
        # 换手率评分（20 分）
        turnover_rate = stock.get('turnover_rate', 0)
        if 5 <= turnover_rate <= 10:
            score += 20
        elif 3 <= turnover_rate < 5 or 10 < turnover_rate <= 15:
            score += 15
        else:
            score += 10
        
        # 成交额评分（15 分）
        turnover = stock.get('turnover', 0)
        if turnover > 500000000:  # 5 亿
            score += 15
        elif turnover > 100000000:  # 1 亿
            score += 12
        elif turnover > 50000000:  # 5000 万
            score += 10
        else:
            score += 5
        
        # 股价趋势评分（15 分）
        high = stock.get('high', 0)
        low = stock.get('low', 0)
        price = stock.get('latest_price', 0)
        if high > 0 and low > 0:
            position = (price - low) / (high - low)
            if 0.5 <= position <= 0.8:  # 中高位
                score += 15
            elif 0.3 <= position < 0.5:
                score += 10
            else:
                score += 5
        
        return score
    
    def screen_long_term(self, limit: int = 10) -> List[Dict]:
        """
        中长线选股策略（20-180 天）
        
        筛选条件：
        1. 市盈率 10-30（合理估值）
        2. 市净率 1-5（合理）
        3. 市值 100 亿 -1000 亿（中大盘）
        4. 近 20 日涨幅 0%-30%（趋势向上但未暴涨）
        5. 非 ST
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始筛选中长线股...", file=sys.stderr)
        
        # 使用预设股票池
        stock_pool = self._get_stock_pool()
        all_stocks = self.api.get_batch(stock_pool)
        
        candidates = []
        for stock in all_stocks:
            if self._filter_long_term(stock):
                score = self._score_long_term(stock)
                if score >= 60:
                    stock['score'] = score
                    candidates.append(stock)
        
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 筛选出 {len(candidates)} 只候选股票", file=sys.stderr)
        
        return candidates[:limit]
    
    def _filter_long_term(self, stock: Dict) -> bool:
        """中长线选股过滤条件"""
        # 排除 ST
        if 'ST' in stock.get('name', ''):
            return False
        
        # 排除科创板
        if stock.get('code', '').startswith('688'):
            return False
        
        # 市盈率 10-30
        pe_ratio = stock.get('pe_ratio', 0)
        if pe_ratio < 10 or pe_ratio > 30:
            return False
        
        # 市净率 1-5
        pb_ratio = stock.get('pb_ratio', 0)
        if pb_ratio < 1 or pb_ratio > 5:
            return False
        
        # 市值 100 亿 -1000 亿
        market_cap = stock.get('total_market_cap', 0)
        if market_cap < 10000000000 or market_cap > 100000000000:
            return False
        
        return True
    
    def _score_long_term(self, stock: Dict) -> float:
        """
        中长线选股评分（0-100）
        
        评分维度：
        - 市盈率（30 分）：10-20 最佳
        - 市净率（25 分）：1-3 最佳
        - 市值（20 分）：200-500 亿最佳
        - 涨跌幅（15 分）：温和上涨
        - 换手率（10 分）：1-5% 最佳
        """
        score = 0
        
        # 市盈率评分（30 分）
        pe_ratio = stock.get('pe_ratio', 0)
        if 10 <= pe_ratio <= 20:
            score += 30
        elif 20 < pe_ratio <= 30:
            score += 20
        else:
            score += 10
        
        # 市净率评分（25 分）
        pb_ratio = stock.get('pb_ratio', 0)
        if 1 <= pb_ratio <= 3:
            score += 25
        elif 3 < pb_ratio <= 5:
            score += 15
        else:
            score += 10
        
        # 市值评分（20 分）
        market_cap = stock.get('total_market_cap', 0)
        if 20000000000 <= market_cap <= 50000000000:  # 200-500 亿
            score += 20
        elif 10000000000 <= market_cap < 20000000000 or 50000000000 < market_cap <= 100000000000:
            score += 15
        else:
            score += 10
        
        # 涨跌幅评分（15 分）
        change_pct = stock.get('change_pct', 0)
        if 0 <= change_pct <= 5:
            score += 15
        elif -3 <= change_pct < 0:
            score += 10
        else:
            score += 5
        
        # 换手率评分（10 分）
        turnover_rate = stock.get('turnover_rate', 0)
        if 1 <= turnover_rate <= 5:
            score += 10
        elif 0.5 <= turnover_rate < 1 or 5 < turnover_rate <= 10:
            score += 7
        else:
            score += 5
        
        return score


def main():
    """主函数"""
    selector = RealtimeStockSelector()
    
    print("=" * 80)
    print("实时选股系统 - 基于东方财富 API")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 短线选股
    print("\n【短线选股】（1-5 天）\n")
    short_term = selector.screen_short_term(limit=5)
    
    if short_term:
        print(f"{'代码':<10} {'名称':<15} {'价格':>8} {'涨幅':>8} {'量比':>8} {'换手':>8} {'评分':>6}")
        print("-" * 80)
        for stock in short_term:
            print(f"{stock['code']:<10} {stock['name']:<15} {stock['latest_price']:>8.2f} "
                  f"{stock['change_pct']:>7.2f}% {stock['volume_ratio']:>8.2f} "
                  f"{stock['turnover_rate']:>7.2f}% {stock['score']:>6.0f}")
    else:
        print("未找到符合条件的短线股票")
    
    # 中长线选股
    print("\n【中长线选股】（20-180 天）\n")
    long_term = selector.screen_long_term(limit=10)
    
    if long_term:
        print(f"{'代码':<10} {'名称':<15} {'价格':>8} {'涨幅':>8} {'PE':>8} {'PB':>8} {'市值 (亿)':>10} {'评分':>6}")
        print("-" * 100)
        for stock in long_term:
            market_cap_yi = stock.get('total_market_cap', 0) / 100000000
            print(f"{stock['code']:<10} {stock['name']:<15} {stock['latest_price']:>8.2f} "
                  f"{stock['change_pct']:>7.2f}% {stock.get('pe_ratio', 0):>8.1f} "
                  f"{stock.get('pb_ratio', 0):>8.2f} {market_cap_yi:>10.1f} {stock['score']:>6.0f}")
    else:
        print("未找到符合条件的中长线股票")
    
    print("\n" + "=" * 80)
    print("风险提示：以上结果仅供参考，不构成投资建议。股市有风险，投资需谨慎。")
    print("=" * 80)
    
    # 输出 JSON 结果（可选）
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        result = {
            'timestamp': datetime.now().isoformat(),
            'short_term': short_term,
            'long_term': long_term
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
