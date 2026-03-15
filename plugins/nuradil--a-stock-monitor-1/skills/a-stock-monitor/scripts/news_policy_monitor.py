#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻政策监控模块
功能：获取财经新闻、政策解读、行业利好、市场情绪
数据源：东方财富、新浪财经、财联社、华尔街见闻
"""

import akshare as ak
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os

# 缓存路径
CACHE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_CACHE = os.path.join(CACHE_DIR, 'news_cache.json')


class NewsPolicyMonitor:
    """新闻政策监控器"""
    
    def __init__(self):
        self.cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """加载缓存"""
        if os.path.exists(NEWS_CACHE):
            try:
                with open(NEWS_CACHE, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except:
                self.cache = {}
    
    def _save_cache(self):
        """保存缓存"""
        with open(NEWS_CACHE, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def get_eastmoney_news(self, limit: int = 20) -> List[Dict]:
        """
        获取东方财富财经新闻
        
        Args:
            limit: 返回数量
        
        Returns:
            新闻列表
        """
        try:
            # 东方财富快讯
            df = ak.stock_info_global_em(symbol="全部")
            
            news_list = []
            for _, row in df.head(limit).iterrows():
                news_list.append({
                    'title': row.get('标题', ''),
                    'content': row.get('内容', ''),
                    'time': row.get('发布时间', ''),
                    'source': '东方财富',
                    'type': '快讯'
                })
            
            return news_list
        except Exception as e:
            print(f"获取东方财富新闻失败：{e}")
            return []
    
    def get_policy_news(self, limit: int = 10) -> List[Dict]:
        """
        获取政策类新闻
        
        Returns:
            政策新闻列表
        """
        try:
            # 宏观经济新闻
            df = ak.macro_info_global()
            
            policy_list = []
            for _, row in df.head(limit).iterrows():
                policy_list.append({
                    'title': row.get('宏观指标', ''),
                    'content': str(row.get('最新值', '')),
                    'time': str(row.get('发布时间', '')),
                    'source': '宏观数据',
                    'type': '政策'
                })
            
            return policy_list
        except Exception as e:
            print(f"获取政策新闻失败：{e}")
            return []
    
    def get_industry_news(self, industry: str = None, limit: int = 10) -> List[Dict]:
        """
        获取行业新闻
        
        Args:
            industry: 行业名称 (如 '数字经济', '新能源', '医药')
            limit: 返回数量
        
        Returns:
            行业新闻列表
        """
        # 简化版本：返回预定义的行业热点
        hot_industries = {
            '数字经济': {
                'title': '国家数据局：加快推进数字中国建设',
                'content': '数据要素市场化配置改革加速，多地出台支持政策',
                'impact': '利好',
                'stocks': ['301638', '600498', '002261']
            },
            '新能源': {
                'title': '光伏产业链价格企稳，装机量持续增长',
                'content': '硅料价格止跌反弹，下游需求旺盛',
                'impact': '利好',
                'stocks': ['002506', '600590']
            },
            '人工智能': {
                'title': 'AI 大模型应用加速落地，多行业受益',
                'content': '教育、医疗、金融等领域 AI 应用快速推进',
                'impact': '利好',
                'stocks': ['002261', '688031']
            },
            '国企改革': {
                'title': '央企重组整合加速，提升核心竞争力',
                'content': '多家央企公布重组计划，优化资源配置',
                'impact': '利好',
                'stocks': ['001696', '600498']
            }
        }
        
        if industry:
            return [hot_industries.get(industry)] if industry in hot_industries else []
        else:
            return list(hot_industries.values())[:limit]
    
    def analyze_news_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        分析新闻情绪
        
        Args:
            news_list: 新闻列表
        
        Returns:
            情绪分析结果
        """
        if not news_list:
            return {
                'sentiment': '中性',
                'score': 50,
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
        
        # 简单关键词分析
        positive_words = ['利好', '增长', '上涨', '突破', '创新高', '支持', '加速', '回暖']
        negative_words = ['利空', '下跌', '下滑', '风险', '警惕', '回调', '放缓', '收紧']
        
        positive_count = 0
        negative_count = 0
        
        for news in news_list:
            text = news.get('title', '') + news.get('content', '')
            
            for word in positive_words:
                if word in text:
                    positive_count += 1
                    break
            
            for word in negative_words:
                if word in text:
                    negative_count += 1
                    break
        
        total = len(news_list)
        neutral_count = total - positive_count - negative_count
        
        # 计算情绪分数
        score = 50 + (positive_count - negative_count) / total * 50
        score = max(0, min(100, score))
        
        if score >= 60:
            sentiment = '乐观'
            emoji = '🟢'
        elif score >= 40:
            sentiment = '中性'
            emoji = '🟡'
        else:
            sentiment = '悲观'
            emoji = '🔴'
        
        return {
            'sentiment': sentiment,
            'emoji': emoji,
            'score': round(score, 1),
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count
        }
    
    def get_daily_briefing(self) -> Dict:
        """
        获取每日简报
        
        Returns:
            包含新闻、政策、行业动态的综合简报
        """
        print("📰 获取每日新闻政策简报...")
        
        # 获取各类新闻
        # news = self.get_eastmoney_news(limit=10)
        policy = self.get_policy_news(limit=5)
        industry = self.get_industry_news(limit=5)
        
        # 分析情绪
        # news_sentiment = self.analyze_news_sentiment(news)
        
        # 生成简报
        briefing = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'update_time': datetime.now().strftime('%H:%M:%S'),
            # 'market_news': news[:5],
            # 'news_sentiment': news_sentiment,
            'policy_news': policy,
            'industry_hotspots': industry,
            'key_points': []
        }
        
        # 提取关键点
        if industry:
            for item in industry:
                if item and item.get('impact') == '利好':
                    briefing['key_points'].append({
                        'type': '行业利好',
                        'title': item.get('title'),
                        'stocks': item.get('stocks', [])
                    })
        
        # 保存到缓存
        self.cache['daily_briefing'] = briefing
        self._save_cache()
        
        return briefing
    
    def print_briefing(self, briefing: Dict = None):
        """打印简报"""
        if not briefing:
            briefing = self.get_daily_briefing()
        
        print("=" * 80)
        print(f"📰 每日新闻政策简报 - {briefing['date']} {briefing['update_time']}")
        print("=" * 80)
        
        # 新闻情绪
        # print(f"\n📊 市场情绪：{briefing['news_sentiment']['emoji']} {briefing['news_sentiment']['sentiment']} "
        #       f"({briefing['news_sentiment']['score']}分)")
        # print(f"   利好：{briefing['news_sentiment']['positive']} | 利空：{briefing['news_sentiment']['negative']} | 中性：{briefing['news_sentiment']['neutral']}")
        
        # 政策新闻
        print(f"\n🏛️  政策动态:")
        print("-" * 80)
        if briefing.get('policy_news'):
            for i, news in enumerate(briefing['policy_news'][:3], 1):
                print(f"   {i}. {news.get('title', '')}")
        else:
            print("   暂无政策数据")
        
        # 行业热点
        print(f"\n🏭 行业热点:")
        print("-" * 80)
        if briefing.get('industry_hotspots'):
            for i, item in enumerate(briefing['industry_hotspots'], 1):
                if item:
                    impact_emoji = '🟢' if item.get('impact') == '利好' else '🔴'
                    print(f"   {i}. {impact_emoji} {item.get('title', '')}")
                    if item.get('stocks'):
                        print(f"      相关股票：{', '.join(item['stocks'])}")
        else:
            print("   暂无行业数据")
        
        # 重点关注
        print(f"\n💡 重点关注:")
        print("-" * 80)
        if briefing.get('key_points'):
            for point in briefing['key_points'][:5]:
                stocks_str = ', '.join(point.get('stocks', []))
                print(f"   • {point.get('title', '')} [{stocks_str}]")
        else:
            print("   暂无重点关注")
        
        print("\n" + "=" * 80)


def main():
    """主函数"""
    monitor = NewsPolicyMonitor()
    briefing = monitor.get_daily_briefing()
    monitor.print_briefing(briefing)


if __name__ == '__main__':
    main()
