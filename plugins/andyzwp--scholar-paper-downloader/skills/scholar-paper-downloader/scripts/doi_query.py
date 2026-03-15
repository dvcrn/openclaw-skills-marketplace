#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询DOI论文信息
"""

import json;
import sys;

def get_doi_info(doi):
    """获取DOI信息"""
    # 使用CrossRef API
    url = f'https://api.crossref.org/works/{doi}';
    
    try:
        import urllib.request;
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'ScholarPaperDownloader/1.0',
            }
        );
        response = urllib.request.urlopen(req, timeout=30);
        data = json.loads(response.read().decode());
        
        if 'message' in data:
            message = data['message'];
            
            # 提取信息
            title = message.get('title', ['Unknown'])[0];
            authors = [f"{a.get('given', '')} {a.get('family', '')}" for a in message.get('author', [])];
            journal = message.get('container-title', ['Unknown'])[0];
            year = message.get('published-print', {}).get('date-parts', [[None]])[0][0];
            volume = message.get('volume', '');
            issue = message.get('issue', '');
            pages = message.get('page', '');
            publisher = message.get('publisher', '');
            
            info = {
                'doi': doi,
                'title': title,
                'authors': authors,
                'journal': journal,
                'year': year,
                'volume': volume,
                'issue': issue,
                'pages': pages,
                'publisher': publisher,
                'url': message.get('URL', ''),
            };
            
            return info;
    except Exception as e:
        print(f'Error: {e}');
        return None;

def print_paper_info(info):
    """打印论文信息"""
    if not info:
        return;
    
    print('=' * 80);
    print('论文信息');
    print('=' * 80);
    print(f'Title: {info["title"]}');
    print(f'Authors: {", ".join(info["authors"][:5])}{"..." if len(info["authors"]) > 5 else ""}');
    print(f'Journal: {info["journal"]}');
    print(f'Year: {info["year"]}');
    print(f'Volume: {info["volume"]}, Issue: {info["issue"]}, Pages: {info["pages"]}');
    print(f'Publisher: {info["publisher"]}');
    print(f'DOI: {info["doi"]}');
    print(f'URL: {info["url"]}');
    print('=' * 80);

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print('用法: python doi_query.py <DOI>');
        print('示例: python doi_query.py 10.1056/NEJMoa1915872');
        sys.exit(1);
    
    doi = sys.argv[1];
    info = get_doi_info(doi);
    
    if info:
        print_paper_info(info);
    else:
        print(f'无法获取DOI {doi} 的信息');
        sys.exit(1);

if __name__ == '__main__':
    main();
