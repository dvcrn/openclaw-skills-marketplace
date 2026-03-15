#!/usr/bin/env python3
"""
Generate content for publishing based on curated corpus and strategy
"""

import argparse
import random
from pathlib import Path
from datetime import datetime

def load_strategy(strategy_file: Path) -> dict:
    """Load strategy from markdown file"""
    with open(strategy_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    strategy = {}
    # Extract frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    strategy[key.strip()] = value.strip()
    
    return strategy

def load_corpus(corpus_dir: Path) -> list:
    """Load all curated corpus files"""
    corpus_files = list((corpus_dir / "curated").glob("*.md"))
    return corpus_files

def generate_content_template(topic: str, platform: str, account: str) -> str:
    """Generate content template"""
    
    date_str = datetime.now().strftime("%Y%m%d")
    
    template = f"""---
platform: {platform}
account: {account}
status: draft
topics:
  - {topic}
created_at: {datetime.now().strftime('%Y-%m-%dT%H:%M')}
---

# 发布内容 - {topic}

## 标题选项（请选择一个）
1. [待填写 - 吸引人、有痛点/好奇心的标题]
2. [待填写 - 备选标题]
3. [待填写 - 备选标题]

## 正文

### 开头（吸引注意）
[待填写 - 钩子开头]

### 正文内容
[待填写 - 基于语料改编的内容]

### 结尾（引导互动）
[待填写 - CTA：点赞/收藏/评论/关注]

## 标签
#标签1 #标签2 #标签3 #标签4 #标签5

## 配图
- [ ] 图片1: [描述]
- [ ] 图片2: [描述]
- [ ] 图片3: [描述]

## 参考语料
- [语料文件](../corpus/curated/{topic}.md)

## 审核清单
- [ ] 标题吸引人
- [ ] 正文通顺、有价值
- [ ] 符合平台规范
- [ ] 配图合适
- [ ] 标签准确

## 发布计划
- 发布时间: [待填写]
- 是否定时: [是/否]

---

**发布后更新**:
- published_at: 
- post_url: 
- status: published
"""
    return template

def main():
    parser = argparse.ArgumentParser(description='Generate content for publishing')
    parser.add_argument('platform', help='Target platform')
    parser.add_argument('account', help='Account name')
    parser.add_argument('--topic', help='Specific topic to write about')
    parser.add_argument('--corpus', help='Specific corpus file to use')
    parser.add_argument('--workspace', default='content-ops-workspace',
                       help='Workspace directory')
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    
    # Load strategy
    strategy_file = workspace / "strategies" / f"{args.platform}-{args.account}-strategy.md"
    if strategy_file.exists():
        strategy = load_strategy(strategy_file)
        print(f"✅ 已加载运营策略: {strategy_file}")
    else:
        print(f"⚠️ 未找到运营策略: {strategy_file}")
        strategy = {}
    
    # Load or select corpus
    corpus_dir = workspace / "corpus"
    if args.corpus:
        corpus_file = Path(args.corpus)
        topic = corpus_file.stem
    else:
        corpus_files = load_corpus(corpus_dir)
        if not corpus_files:
            print("❌ 没有找到已整理的语料，请先抓取并确认语料")
            return
        # Randomly select or use specified topic
        if args.topic:
            matching = [f for f in corpus_files if args.topic.lower() in f.stem.lower()]
            corpus_file = matching[0] if matching else corpus_files[0]
        else:
            corpus_file = random.choice(corpus_files)
        topic = corpus_file.stem
    
    print(f"📚 参考语料: {corpus_file}")
    
    # Generate content
    content = generate_content_template(topic, args.platform, args.account)
    
    # Save to published directory (as draft)
    published_dir = workspace / "corpus" / "published"
    published_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{args.platform}-{args.account}-{date_str}-{topic[:20]}.md"
    filepath = published_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 内容草稿已生成: {filepath}")
    print(f"\n📝 下一步:")
    print(f"   1. 查看文件并填写标题和正文")
    print(f"   2. 准备配图")
    print(f"   3. 审核通过后发布到 {args.platform}")

if __name__ == '__main__':
    main()
