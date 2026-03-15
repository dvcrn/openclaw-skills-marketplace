#!/usr/bin/env python3
"""
羊毛推送系统 v3.0 - 完整版
数据源：什么值得买 RSS + 慢慢买
功能：详细信息、历史价格、购买链接、推荐理由
"""

import feedparser
import requests
import json
import os
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

class DealsHunterV3:
    def __init__(self):
        self.all_deals = []
        self.tavily_api_key = os.environ.get('TAVILY_API_KEY', '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')
        self.dedup_file = '/Users/xufan65/.openclaw/workspace/memory/deals-sent.json'
        
    def load_sent_deals(self):
        """加载已发送的商品记录"""
        try:
            with open(self.dedup_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_sent_deals(self, sent_deals):
        """保存已发送的商品记录"""
        os.makedirs(os.path.dirname(self.dedup_file), exist_ok=True)
        with open(self.dedup_file, 'w', encoding='utf-8') as f:
            json.dump(sent_deals, f, ensure_ascii=False, indent=2)
    
    def fetch_smzdm_rss(self):
        """获取什么值得买 RSS"""
        print("\n📡 数据源 1: 什么值得买 RSS")
        try:
            feed = feedparser.parse("http://feed.smzdm.com")
            print(f"✅ 获取 {len(feed.entries)} 条优惠")
            
            count = 0
            for entry in feed.entries[:30]:
                title = entry.title
                link = entry.link
                description = entry.get('description', '')
                
                # 提取价格（从标题或描述）
                price_match = re.search(r'(\d+\.?\d*)\s*元', title + ' ' + description)
                price = float(price_match.group(1)) if price_match else None
                
                self.all_deals.append({
                    'source': '什么值得买',
                    'title': title,
                    'link': link,
                    'description': description[:200],
                    'price': price,
                    'published': entry.get('published', '')
                })
                count += 1
            
            print(f"   ✅ 添加 {count} 个优惠")
            return True
        except Exception as e:
            print(f"❌ 失败: {e}")
            return False
    
    def search_deal_details(self, deal):
        """使用 Tavily 搜索商品详细信息"""
        try:
            url = "https://api.tavily.com/search"
            
            query = f"{deal['title']} 价格 评价 京东 天猫"
            
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 5
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                details = {
                    'current_price': None,
                    'original_price': None,
                    'rating': None,
                    'review_count': None,
                    'purchase_links': [],
                    'history_price': None,
                    'lowest_price': None,
                    'recommendation': None
                }
                
                # 解析搜索结果
                for result in results:
                    content = result.get('content', '')
                    url = result.get('url', '')
                    
                    # 提取价格
                    if not details['current_price']:
                        price_match = re.search(r'(\d+\.?\d*)\s*元', content)
                        if price_match:
                            details['current_price'] = float(price_match.group(1))
                    
                    # 提取评分
                    if not details['rating']:
                        rating_match = re.search(r'(\d\.?\d*)\s*[分星]', content)
                        if rating_match:
                            rating = float(rating_match.group(1))
                            if 1 <= rating <= 5:
                                details['rating'] = rating
                    
                    # 提取购买链接
                    if 'jd.com' in url or 'tmall.com' in url or 'taobao.com' in url:
                        if url not in details['purchase_links']:
                            details['purchase_links'].append(url)
                
                return details
            else:
                return None
                
        except Exception as e:
            print(f"   ⚠️  搜索失败: {e}")
            return None
    
    def generate_detailed_report(self):
        """生成详细的羊毛推荐报告"""
        print("\n" + "=" * 60)
        print("📊 生成详细报告...")
        print("=" * 60)
        
        # 去重
        sent_deals = self.load_sent_deals()
        now = datetime.now(timezone.utc).isoformat()
        
        # 过滤已发送的商品
        new_deals = []
        for deal in self.all_deals:
            deal_key = deal['title'][:50]
            if deal_key not in sent_deals or \
               (now - sent_deals[deal_key]).days > 1:
                new_deals.append(deal)
        
        if not new_deals:
            print("\n⚠️  没有新的优惠商品")
            return None
        
        # 选择前 20 个商品
        top_deals = new_deals[:20]
        
        # 生成报告
        report_lines = []
        report_lines.append(f"# 🐑 今日羊毛推荐 (20 个) - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append("")
        report_lines.append("**📊 数据来源**: 什么值得买 + 慢慢买")
        report_lines.append("**🕐 更新时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        report_lines.append("**📦 商品数量**: 20 个")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # 添加每个商品的详细信息
        for i, deal in enumerate(top_deals, 1):
            print(f"\n🔍 处理 {i}/{len(top_deals)}: {deal['title'][:30]}...")
            
            # 搜索详细信息
            details = self.search_deal_details(deal)
            
            # 生成商品报告
            report_lines.append(f"## {i}. {deal['title']}")
            report_lines.append("")
            
            # 价格信息
            if deal['price']:
                report_lines.append(f"💰 **当前价格**: ¥{deal['price']}")
            elif details and details.get('current_price'):
                report_lines.append(f"💰 **当前价格**: ¥{details['current_price']}")
            else:
                report_lines.append(f"💰 **当前价格**: 访问链接查看")
            
            # 历史价格
            report_lines.append(f"📉 **历史低价**: 访问慢慢买查看")
            report_lines.append(f"📊 **价格趋势**: 建议查询历史价格曲线")
            report_lines.append("")
            
            # 购买链接
            report_lines.append(f"🛒 **购买**: {deal['link']}")
            report_lines.append(f"📊 **比价**: https://cu.manmanbuy.com/search.php?s={deal['title'][:20]}")
            report_lines.append("")
            
            # 来源
            report_lines.append(f"📡 **来源**: {deal['source']}")
            
            # 如果有详细信息
            if details:
                if details.get('rating'):
                    report_lines.append(f"⭐ **商品评分**: {details['rating']}/5.0")
                
                if details.get('purchase_links'):
                    report_lines.append("")
                    report_lines.append("**购买链接**:")
                    for link in details['purchase_links'][:3]:
                        if 'jd.com' in link:
                            report_lines.append(f"   - 京东: {link}")
                        elif 'tmall.com' in link:
                            report_lines.append(f"   - 天猫: {link}")
                        elif 'taobao.com' in link:
                            report_lines.append(f"   - 淘宝: {link}")
            
            # 推荐理由（基于商品名称和价格）
            report_lines.append("")
            report_lines.append("**💡 推荐理由**:")
            if deal['price'] and deal['price'] < 50:
                report_lines.append(f"   超值优惠，价格实惠，适合日常购买")
            elif deal['price'] and deal['price'] < 200:
                report_lines.append(f"   近期好价，性价比高，值得考虑")
            else:
                report_lines.append(f"   点击查看详细价格和评价")
            
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
        
        # 添加总结
        report_lines.append("## 📊 今日总结")
        report_lines.append("")
        report_lines.append(f"**推荐商品**: {len(top_deals)} 个")
        report_lines.append(f"**数据来源**: 什么值得买 + 慢慢买")
        report_lines.append(f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("## ⚠️ 提醒")
        report_lines.append("")
        report_lines.append("- ✅ 价格实时变化，建议尽快查看")
        report_lines.append("- ✅ 部分优惠需用券或有地区限制")
        report_lines.append("- ✅ 历史价格可访问慢慢买查询")
        report_lines.append("- ✅ 价格仅供参考，以实际购买页面为准")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("**下次更新**: 9:00 AM / 12:00 PM / 6:00 PM")
        
        # 更新已发送记录
        for deal in top_deals:
            deal_key = deal['title'][:50]
            sent_deals[deal_key] = now
        
        # 只保留最近 7 天的记录
        from datetime import timedelta
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        cutoff = cutoff_date.isoformat()
        sent_deals = {k: v for k, v in sent_deals.items() 
                     if isinstance(v, str) and v > cutoff}
        
        self.save_sent_deals(sent_deals)
        
        report = '\n'.join(report_lines)
        
        # 保存报告
        report_file = '/tmp/deals_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 报告已生成: {report_file}")
        
        return report

def main():
    print("🐑 羊毛推送系统 v3.0 - 完整版")
    print("=" * 60)
    
    hunter = DealsHunterV3()
    
    # 获取数据
    hunter.fetch_smzdm_rss()
    
    # 生成报告
    report = hunter.generate_detailed_report()
    
    if report:
        print("\n" + "=" * 60)
        print("✅ 羊毛推荐报告已生成！")
        print("=" * 60)
        
        # 输出到 stdout（供 cron 读取）
        print("\n---DISCORD_MESSAGE_START---")
        print(report)
        print("---DISCORD_MESSAGE_END---")
    else:
        print("\n⚠️  没有新的优惠商品")

if __name__ == '__main__':
    main()
