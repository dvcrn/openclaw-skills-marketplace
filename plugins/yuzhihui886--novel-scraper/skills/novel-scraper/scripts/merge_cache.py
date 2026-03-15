#!/usr/bin/env python3
"""合并缓存文件为完整小说"""
import re
import argparse
import sys
from pathlib import Path

CACHE_DIR = Path('/tmp/novel_scraper_cache')
NOVELS_DIR = Path.home() / '.openclaw' / 'workspace' / 'novels'

def parse_args():
    parser = argparse.ArgumentParser(description='合并缓存文件为完整小说')
    parser.add_argument('--book', '-b', help='书名（可选，自动从缓存提取）')
    parser.add_argument('--cache-dir', default='/tmp/novel_scraper_cache', help='缓存目录')
    parser.add_argument('--output-dir', help='输出目录（可选）')
    return parser.parse_args()

def extract_book_name(chapters):
    """从章节标题提取书名（如果缓存中有 BOOK: 行）"""
    for cache_file in CACHE_DIR.glob('*.txt'):
        with open(cache_file, 'r', encoding='utf-8') as f:
            content = f.read().strip().split('\n')
            if content and content[0].startswith('BOOK:'):
                book_info = content[0].replace('BOOK:', '').split(':')
                if len(book_info) > 0 and book_info[0]:
                    return book_info[0]
    return None

def main():
    args = parse_args()
    cache_dir = Path(args.cache_dir)
    
    # 检查缓存目录
    cache_files = list(cache_dir.glob('*.txt'))
    if not cache_files:
        print('❌ 缓存目录为空')
        sys.exit(1)
    
    chapters = []
    for cache_file in cache_files:
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                content = f.read().strip().split('\n')
                if not content:
                    continue
                    
                if content[0].startswith('BOOK:'):
                    chapter_title = content[1] if len(content) > 1 else '未知章节'
                    chapter_content = content[2:] if len(content) > 2 else []
                else:
                    chapter_title = content[0] if content else '未知章节'
                    chapter_content = content[1:] if len(content) > 1 else []
                
                # 提取章节号 - 支持多种格式
                match = re.search(r'第 (\d+) 章', chapter_title)
                if not match:
                    match = re.search(r'(\d+)\.第\d+章', chapter_title)  # 如 "19.第 19 章"
                chapter_num = int(match.group(1)) if match else 0
                
                chapters.append({
                    'num': chapter_num,
                    'title': chapter_title,
                    'content': chapter_content
                })
                print(f'章节{chapter_num}: {chapter_title[:40]}... ({len(chapter_content)}段)')
        except Exception as e:
            print(f'⚠️ 跳过 {cache_file.name}: {e}')
    
    # 检查是否有章节
    if not chapters:
        print('❌ 没有找到有效章节')
        sys.exit(1)
    
    # 按章节号排序
    chapters.sort(key=lambda x: x['num'])
    
    # 处理章节号为 0 的情况（提取失败）
    zero_chapters = [c for c in chapters if c['num'] == 0]
    if zero_chapters:
        print(f'⚠️ {len(zero_chapters)} 章无法提取章节号，按顺序排列')
    
    print(f'\n共 {len(chapters)} 章')
    print(f'范围：{chapters[0]["title"]} - {chapters[-1]["title"]}')
    
    # 确定书名
    book_name = args.book if args.book else extract_book_name(chapters)
    if not book_name:
        book_name = '小说'
        print('⚠️ 未指定书名，使用默认值')
    
    # 生成文件名
    first_ch = chapters[0]['num']
    last_ch = chapters[-1]['num']
    
    if first_ch == last_ch:
        filename = f'{book_name}_第{first_ch}章.txt'
    else:
        filename = f'{book_name}_第{first_ch}-{last_ch}章.txt'
    
    # 确定输出路径
    if args.output_dir:
        output_path = Path(args.output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = NOVELS_DIR / filename
    
    # 保存文件
    with open(output_path, 'w', encoding='utf-8') as f:
        for c in chapters:
            separator = '=' * 60
            f.write(f'\n{separator}\n{c["title"]}\n{separator}\n\n')
            for para in c['content']:
                f.write(f'{para}\n\n')
    
    print(f'\n✅ 保存：{filename}')
    print(f'总段落：{sum(len(c["content"]) for c in chapters)}')

if __name__ == '__main__':
    main()
