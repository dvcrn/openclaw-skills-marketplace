#!/usr/bin/env python3
"""
Xiaohongshu Content Crawler
抓取小红书搜索结果的笔记内容
"""

import argparse
import json
import sys
import re
from datetime import datetime
from pathlib import Path

# Note: This is a template. Actual implementation requires:
# - playwright/selenium for browser automation
# - xhs-api or reverse-engineered API calls

def generate_crawl_template(topic: str, queries: list) -> str:
    """Generate a markdown template for crawled content"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""---
topic: {topic}
source_platform: xiaohongshu
query_list:
{chr(10).join(f'  - {q}' for q in queries)}
crawled_at: {date_str}
curated: false
---

# 抓取结果: {topic}

> 抓取时间: {date_str}
> 搜索Query: {', '.join(queries)}

## 待抓取内容列表

<!-- 使用浏览器自动化工具抓取以下内容 -->

### 笔记1
- **标题**: [待填写]
- **作者**: [待填写]
- **链接**: [待填写]
- **点赞数**: [待填写]
- **收藏数**: [待填写]
- **内容摘要**: [待填写]
- **标签**: [待填写]
- **图片**: [待填写]

### 笔记2
...

---

## 人工确认区

- [ ] 内容1已审核 - 质量: [高/中/低] - 是否可用: [是/否]
- [ ] 内容2已审核 - 质量: [高/中/低] - 是否可用: [是/否]

确认后执行: `python3 scripts/curate_content.py corpus/raw/{date_str}-{topic}.md`
"""
    return content

def expand_queries(topic: str) -> list:
    """根据主题扩展搜索词"""
    # 基础扩展规则
    expansions = {
        "穿搭": ["穿搭", "OOTD", "每日穿搭", "搭配"],
        "美妆": ["美妆", "化妆", "护肤", "彩妆"],
        "美食": ["美食", "探店", "食谱", "料理"],
        "旅行": ["旅行", "旅游", "游记", "攻略"],
        "家居": ["家居", "装修", "收纳", "软装"],
    }
    
    queries = [topic]
    for key, values in expansions.items():
        if key in topic:
            queries.extend(values)
    
    # 去重并保持顺序
    seen = set()
    unique_queries = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)
    
    return unique_queries[:5]  # 最多5个query

def main():
    parser = argparse.ArgumentParser(description='Crawl Xiaohongshu content')
    parser.add_argument('topic', help='Topic to search for')
    parser.add_argument('--workspace', default='content-ops-workspace', 
                       help='Workspace directory')
    parser.add_argument('--queries', nargs='+', help='Custom search queries')
    
    args = parser.parse_args()
    
    # Expand or use custom queries
    queries = args.queries if args.queries else expand_queries(args.topic)
    
    # Generate filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_topic = re.sub(r'[^\w\s-]', '', args.topic).strip().replace(' ', '-')
    filename = f"{date_str}-{safe_topic}.md"
    
    # Ensure directory exists
    workspace = Path(args.workspace)
    raw_dir = workspace / "corpus" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate content
    content = generate_crawl_template(args.topic, queries)
    
    # Write file
    filepath = raw_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 抓取模板已创建: {filepath}")
    print(f"📋 主题: {args.topic}")
    print(f"🔍 搜索Query: {', '.join(queries)}")
    print(f"\n💡 下一步:")
    print(f"   1. 使用浏览器工具抓取内容并填入模板")
    print(f"   2. 人工审核内容质量")
    print(f"   3. 确认后执行: python3 scripts/curate_content.py {filepath}")

if __name__ == '__main__':
    main()
