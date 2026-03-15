
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
#     "google-genai",
# ]
# ///

"""
智能新闻处理器 - 抓取中外媒体、翻译、去重、分析利好利空
"""

import json
import hashlib
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import requests

# 缓存目录
CACHE_DIR = Path(os.path.expanduser("~/.openclaw/workspace-group/market-monitor/news_cache"))
CACHE_DURATION_HOURS = 24

# 确保缓存目录存在
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 外国媒体RSS源
FOREIGN_RSS_SOURCES = [
    {
        "name": "BBC Business",
        "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "language": "en"
    },
    {
        "name": "Yahoo Finance",
        "url": "https://finance.yahoo.com/rss/",
        "language": "en"
    }
]


def get_news_hash(title: str) -> str:
    """生成新闻唯一标识（用于完全一样的新闻去重）"""
    return hashlib.md5(title.strip().encode()).hexdigest()[:12]


def get_topic_key(title: str) -> str:
    """生成话题关键词（用于同样话题的新闻合并）"""
    patterns_to_remove = [
        r'\d{1,2}日', r'\d{1,2}月', r'\d{4}年',
        r'\d+\.?\d*%', r'\d+亿', r'\d+万', r'\d+元',
        r'涨\d+%', r'跌\d+%', r'超\d+%', r'近\d+%',
        r'目标价\d+', r'评级.*', r'维持.*评级',
    ]
    
    topic = title
    for pattern in patterns_to_remove:
        topic = re.sub(pattern, '', topic)
    
    topic = re.sub(r'[，。？！、：""''（）【】]', '', topic)
    return topic.strip()[:20]


def simple_translate(title_en: str) -> str:
    """简单的英文标题翻译（关键词映射）"""
    # 常见金融术语映射
    translations = {
        'stock': '股票',
        'shares': '股份',
        'market': '市场',
        'trading': '交易',
        'price': '价格',
        'rises': '上涨',
        'falls': '下跌',
        'surges': '暴涨',
        'plunges': '暴跌',
        'earnings': '盈利',
        'revenue': '营收',
        'profit': '利润',
        'loss': '亏损',
        'outlook': '展望',
        'forecast': '预测',
        'target': '目标',
        'upgrade': '上调',
        'downgrade': '下调',
        'buy': '买入',
        'sell': '卖出',
        'hold': '持有',
        'rating': '评级',
        'analyst': '分析师',
        'investor': '投资者',
        'billion': '十亿',
        'million': '百万',
        'AI': '人工智能',
        'tech': '科技',
        'chip': '芯片',
        'semiconductor': '半导体',
        'federal reserve': '美联储',
        'interest rate': '利率',
        'inflation': '通胀',
        'GDP': 'GDP',
        'trade': '贸易',
        'tariff': '关税',
        'sanctions': '制裁',
        'war': '战争',
        'conflict': '冲突',
        'oil': '石油',
        'gold': '黄金',
        'crypto': '加密货币',
        'bitcoin': '比特币',
    }
    
    title_lower = title_en.lower()
    translated = title_en
    
    for en, cn in translations.items():
        if en.lower() in title_lower:
            # 简单替换（实际应用可能需要更复杂的翻译API）
            pass
    
    # 返回原文+标注英文来源
    return title_en


def fetch_rss_news(source: Dict) -> List[Dict]:
    """抓取RSS源的新闻"""
    news_list = []
    
    try:
        response = requests.get(source['url'], timeout=15)
        response.raise_for_status()
        
        # 解析XML
        root = ET.fromstring(response.content)
        
        # RSS 2.0格式
        channel = root.find('.//channel')
        if channel is None:
            return news_list
        
        for item in channel.findall('.//item')[:20]:  # 取前20条
            title_elem = item.find('title')
            pub_date_elem = item.find('pubDate')
            
            if title_elem is not None and title_elem.text:
                title = title_elem.text
                # CDATA处理
                if title.startswith('<![CDATA['):
                    title = title[9:-3]
                
                pub_date = pub_date_elem.text if pub_date_elem is not None else ''
                
                # 翻译标题
                title_cn = simple_translate(title)
                
                news_list.append({
                    'title': f"[EN] {title_cn}",
                    'title_original': title,
                    'source': source['name'],
                    'source_type': 'foreign',
                    'language': source['language'],
                    'pub_date': pub_date,
                    'timestamp': int(datetime.now().timestamp()),
                    'fetched_at': datetime.now().isoformat()
                })
    
    except Exception as e:
        print(f"抓取 {source['name']} 失败: {e}")
    
    return news_list


def load_cached_news() -> List[Dict]:
    """加载24小时内的缓存新闻"""
    cached_news = []
    cutoff_time = datetime.now() - timedelta(hours=CACHE_DURATION_HOURS)
    
    for cache_file in CACHE_DIR.glob("*.json"):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                news_item = json.load(f)
                cached_time = datetime.fromisoformat(news_item.get('cached_at', '2000-01-01'))
                if cached_time > cutoff_time:
                    cached_news.append(news_item)
                else:
                    cache_file.unlink()
        except Exception:
            continue
    
    return cached_news


def save_news_to_cache(news_list: List[Dict]):
    """保存新闻到缓存"""
    for news in news_list:
        news_hash = get_news_hash(news.get('title_original', news['title']))
        cache_file = CACHE_DIR / f"{news_hash}.json"
        
        news['cached_at'] = datetime.now().isoformat()
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(news, f, ensure_ascii=False, indent=2)


def deduplicate_and_merge_news(news_list: List[Dict]) -> List[Dict]:
    """去重并合并同样话题的新闻（保留最新的）"""
    
    unique_by_hash = {}
    for news in news_list:
        # 使用原文标题生成hash
        title_for_hash = news.get('title_original', news['title'])
        news_hash = get_news_hash(title_for_hash)
        
        if news_hash not in unique_by_hash:
            unique_by_hash[news_hash] = news
        else:
            existing_time = unique_by_hash[news_hash].get('timestamp', 0)
            new_time = news.get('timestamp', 0)
            if new_time > existing_time:
                unique_by_hash[news_hash] = news
    
    topic_groups = {}
    for news in unique_by_hash.values():
        title_for_topic = news.get('title_original', news['title'])
        topic_key = get_topic_key(title_for_topic)
        
        if topic_key not in topic_groups:
            topic_groups[topic_key] = news
        else:
            existing_time = topic_groups[topic_key].get('timestamp', 0)
            new_time = news.get('timestamp', 0)
            if new_time > existing_time:
                topic_groups[topic_key] = news
    
    result = sorted(topic_groups.values(), 
                   key=lambda x: x.get('timestamp', 0), 
                   reverse=True)
    
    return result


def analyze_sentiment(title: str, source: str = '') -> str:
    """分析新闻是利好还是利空"""
    
    title_lower = title.lower()
    
    bullish_keywords = [
        '上涨', '涨', '反弹', '创新高', '突破', '利好', '强劲', '增长', '盈利', '超预期',
        '买入', '增持', '上调目标价', '看好', '乐观', '复苏', '回暖', '企稳', '支持',
        '降息', '宽松', '刺激', '政策利好', '获批准', '签约', '合作', '收购', '扩张',
        '涨超', '涨逾', '大涨', '飙升', '暴涨', '涨停', '牛市', '资金流入', '净流入',
        '目标价', '买入评级', '增持评级', '跑赢大市', '推荐', '荣誉', '获奖', '第一',
        # 英文关键词
        'rises', 'surges', 'jumps', 'gains', 'rally', 'bullish', 'upgrade',
        'beats', 'outperform', 'buy rating', 'price target raised',
        'strong', 'growth', 'profit', 'revenue up', 'earnings beat'
    ]
    
    bearish_keywords = [
        '下跌', '跌', '跳水', '崩盘', '创新低', '跌破', '利空', '疲软', '亏损', '不及预期',
        '卖出', '减持', '下调目标价', '看空', '悲观', '衰退', '恶化', '风险', '警告',
        '加息', '收紧', '监管', '调查', '处罚', '停产', '罢工', '违约', '破产', '裁员',
        '跌超', '跌逾', '大跌', '暴跌', '跌停', '熊市', '资金流出', '净流出',
        '卖出评级', '减持评级', '跑输大市', '下调', '剔除', '禁止', '封锁', '冲突',
        # 英文关键词
        'falls', 'plunges', 'drops', 'declines', 'crash', 'bearish', 'downgrade',
        'misses', 'underperform', 'sell rating', 'price target cut',
        'weak', 'loss', 'revenue down', 'earnings miss', 'sanctions', 'war'
    ]
    
    bullish_count = sum(1 for kw in bullish_keywords if kw in title_lower)
    bearish_count = sum(1 for kw in bearish_keywords if kw in title_lower)
    
    if '战争' in title or 'conflict' in title_lower or 'war' in title_lower:
        return '利空'
    if '达成' in title and '协议' in title:
        return '利好'
    if '涨停' in title or 'surges' in title_lower:
        return '利好'
    if '跌停' in title or 'plunges' in title_lower:
        return '利空'
    
    if bullish_count > bearish_count:
        return '利好'
    elif bearish_count > bullish_count:
        return '利空'
    else:
        return '中性'


def fetch_chinese_news() -> List[Dict]:
    """抓取中文新闻（调用原脚本）"""
    import subprocess
    
    news_list = []
    
    try:
        result = subprocess.run(
            ['bash', os.path.expanduser('~/.openclaw/workspace-group/tools/news-fetcher.sh')],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        current_source = ''
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith('【新浪财经') or line.startswith('【财联社') or line.startswith('【华尔街见闻'):
                if '新浪' in line:
                    current_source = '新浪财经'
                elif '财联社' in line:
                    current_source = '财联社'
                elif '华尔街' in line:
                    current_source = '华尔街见闻'
                continue
            
            if line.startswith('• ') and '时间:' not in line:
                title = line[2:].strip()
                if title:
                    news_list.append({
                        'title': title,
                        'source': current_source,
                        'source_type': 'chinese',
                        'language': 'zh',
                        'url': '暂无链接',
                        'timestamp': int(datetime.now().timestamp()),
                        'fetched_at': datetime.now().isoformat()
                    })
    
    except Exception as e:
        print(f"抓取中文新闻失败: {e}")
    
    return news_list


def generate_report(all_news: List[Dict]) -> str:
    """生成市场分析报告"""
    
    bullish_news = [n for n in all_news if n.get('sentiment') == '利好']
    bearish_news = [n for n in all_news if n.get('sentiment') == '利空']
    neutral_news = [n for n in all_news if n.get('sentiment') == '中性']
    
    report = f"""📊 市场新闻分析报告 ({datetime.now().strftime('%Y-%m-%d %H:%M')})

━━━━━━━━━━━━━━━━━━━━
📈 利好因素（共{len(bullish_news)}条）

"""
    
    for i, news in enumerate(bullish_news[:15], 1):
        source_tag = "🇨🇳" if news.get('source_type') == 'chinese' else "🇬🇧"
        report += f"{i}. {news['title']}\n"
        report += f"   来源: {source_tag} {news['source']}\n\n"
    
    if len(bullish_news) > 15:
        report += f"... 还有 {len(bullish_news) - 15} 条利好新闻\n\n"
    
    report += f"""━━━━━━━━━━━━━━━━━━━━
📉 利空因素（共{len(bearish_news)}条）

"""
    
    for i, news in enumerate(bearish_news[:15], 1):
        source_tag = "🇨🇳" if news.get('source_type') == 'chinese' else "🇬🇧"
        report += f"{i}. {news['title']}\n"
        report += f"   来源: {source_tag} {news['source']}\n\n"
    
    if len(bearish_news) > 15:
        report += f"... 还有 {len(bearish_news) - 15} 条利空新闻\n\n"
    
    report += f"""━━━━━━━━━━━━━━━━━━━━
📋 中性/其他（共{len(neutral_news)}条）

"""
    
    for i, news in enumerate(neutral_news[:15], 1):
        source_tag = "🇨🇳" if news.get('source_type') == 'chinese' else "🇬🇧"
        report += f"{i}. {news['title']}\n"
        report += f"   来源: {source_tag} {news['source']}\n\n"
    
    if len(neutral_news) > 15:
        report += f"... 还有 {len(neutral_news) - 15} 条中性新闻\n\n"
    
    report += f"""━━━━━━━━━━━━━━━━━━━━
📊 统计摘要
• 利好: {len(bullish_news)} 条
• 利空: {len(bearish_news)} 条  
• 中性: {len(neutral_news)} 条
• 总计（去重后）: {len(all_news)} 条

数据来源:
🇨🇳 中文: 新浪财经 / 财联社 / 华尔街见闻
🇬🇧 英文: BBC Business / Yahoo Finance
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    return report


def main():
    """主函数"""
    print("🔄 正在抓取中文新闻...")
    chinese_news = fetch_chinese_news()
    print(f"✅ 抓取到 {len(chinese_news)} 条中文新闻")
    
    print("\n🔄 正在抓取外国媒体新闻...")
    foreign_news = []
    for source in FOREIGN_RSS_SOURCES:
        print(f"  - 正在抓取 {source['name']}...")
        news = fetch_rss_news(source)
        print(f"    ✓ 获取 {len(news)} 条")
        foreign_news.extend(news)
    print(f"✅ 共抓取到 {len(foreign_news)} 条外国新闻")
    
    # 合并所有新闻
    all_fetched = chinese_news + foreign_news
    print(f"\n📦 本次共抓取 {len(all_fetched)} 条新闻")
    
    # 保存到缓存
    save_news_to_cache(all_fetched)
    print(f"✅ 已保存到24小时缓存")
    
    # 加载所有缓存
    cached_news = load_cached_news()
    print(f"📦 缓存中共有 {len(cached_news)} 条新闻")
    
    # 合并实时和缓存
    all_news = cached_news + all_fetched
    
    # 去重和合并
    print("🔄 正在去重和合并同样话题的新闻...")
    unique_news = deduplicate_and_merge_news(all_news)
    print(f"✅ 去重后剩余 {len(unique_news)} 条新闻")
    
    # 分析利好利空
    print("📊 正在分析每条新闻的影响...")
    for news in unique_news:
        news['sentiment'] = analyze_sentiment(news['title'], news.get('source', ''))
    
    # 生成报告
    report = generate_report(unique_news)
    
    # 输出报告
    print("\n" + "="*50)
    print(report)
    
    # 保存报告
    report_file = CACHE_DIR.parent / f"news_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n📄 报告已保存: {report_file}")


if __name__ == "__main__":
    main()
