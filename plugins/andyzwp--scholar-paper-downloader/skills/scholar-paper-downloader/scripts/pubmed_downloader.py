#!/usr/bin/env python3
"""
PubMed/PDF下载器 - 仅支持官方免费渠道
优先从PMC(PubMed Central)下载开放获取文献
"""

import sys
import os
import re
import json
from urllib.parse import urljoin, quote

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("请先安装依赖: pip install requests beautifulsoup4")
    sys.exit(1)


class PubMedDownloader:
    """PubMed/PMC官方下载器"""
    
    BASE_URL = "https://pubmed.ncbi.nlm.nih.gov/"
    PMC_BASE_URL = "https://www.ncbi.nlm.nih.gov/pmc/articles/"
    
    def __init__(self, timeout=30, headers=None):
        self.timeout = timeout
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_by_doi(self, doi):
        """通过DOI搜索论文"""
        try:
            search_url = f"{self.BASE_URL}?term={quote(doi)}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                # 提取PMC链接
                pmc_links = re.findall(r'/pmc/articles/(PMC\d+)/', response.text)
                if pmc_links:
                    return {
                        'pmcid': pmc_links[0],
                        'source': 'PMC',
                        'url': f"{self.PMC_BASE_URL}{pmc_links[0]}"
                    }
            
            return None
        except Exception as e:
            print(f"   ❌ 搜索失败: {str(e)[:50]}")
            return None
    
    def search_by_title(self, title):
        """通过标题搜索论文"""
        try:
            search_url = f"{self.BASE_URL}?term={quote(title)}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                # 提取PMC链接
                pmc_links = re.findall(r'/pmc/articles/(PMC\d+)/', response.text)
                if pmc_links:
                    return {
                        'pmcid': pmc_links[0],
                        'source': 'PMC',
                        'url': f"{self.PMC_BASE_URL}{pmc_links[0]}"
                    }
            
            return None
        except Exception as e:
            print(f"   ❌ 搜索失败: {str(e)[:50]}")
            return None
    
    def get_paper_info(self, pmcid):
        """获取PMC论文信息"""
        try:
            url = f"{self.PMC_BASE_URL}{pmcid}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取标题
                title_elem = soup.find('h1', class_='content-title')
                title = title_elem.get_text(strip=True) if title_elem else "Unknown"
                
                # 提取PDF链接
                pdf_link = soup.find('a', {'data-ga-action': 'PDF'})
                pdf_url = None
                if pdf_link:
                    pdf_url = urljoin(url, pdf_link['href'])
                
                return {
                    'title': title,
                    'pmcid': pmcid,
                    'pdf_url': pdf_url,
                    'url': url
                }
            
            return None
        except Exception as e:
            print(f"   ❌ 获取信息失败: {str(e)[:50]}")
            return None
    
    def download_pdf(self, pdf_url, output_path):
        """下载PDF"""
        try:
            print(f"   📥 下载PDF: {pdf_url[:80]}...")
            
            response = self.session.get(pdf_url, timeout=self.timeout, stream=True)
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                # 验证PDF有效性
                if os.path.getsize(output_path) > 1000:
                    print(f"   ✅ 保存成功: {output_path} ({size_mb:.2f} MB)")
                    return True
                else:
                    os.remove(output_path)
                    print(f"   ❌ PDF文件太小,可能无效")
                    return False
            else:
                print(f"   ❌ 下载失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ 下载错误: {str(e)[:50]}")
            return False
    
    def download_by_doi(self, doi, output_path):
        """通过DOI下载"""
        print(f"   🔍 搜索DOI: {doi}")
        
        # 搜索PMC
        result = self.search_by_doi(doi)
        
        if result:
            print(f"   ✅ 找到PMC开放获取版本")
            info = self.get_paper_info(result['pmcid'])
            
            if info and info['pdf_url']:
                return self.download_pdf(info['pdf_url'], output_path)
            else:
                print(f"   ❌ 未找到PDF链接")
                return False
        else:
            print(f"   ℹ️  PMC中未找到该论文")
            return False
    
    def download_by_title(self, title, output_path):
        """通过标题下载"""
        print(f"   🔍 搜索标题: {title[:60]}...")
        
        # 搜索PMC
        result = self.search_by_title(title)
        
        if result:
            print(f"   ✅ 找到PMC开放获取版本")
            info = self.get_paper_info(result['pmcid'])
            
            if info and info['pdf_url']:
                return self.download_pdf(info['pdf_url'], output_path)
            else:
                print(f"   ❌ 未找到PDF链接")
                return False
        else:
            print(f"   ℹ️  PMC中未找到该论文")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='PubMed/PMC官方下载器')
    parser.add_argument('--doi', help='论文DOI')
    parser.add_argument('--title', help='论文标题')
    parser.add_argument('--pmcid', help='PMC ID (例如: PMC1234567)')
    parser.add_argument('output', help='输出PDF路径')
    
    args = parser.parse_args()
    
    if not args.doi and not args.title and not args.pmcid:
        print("错误: 必须提供 --doi, --title 或 --pmcid 参数")
        sys.exit(1)
    
    downloader = PubMedDownloader()
    success = False
    
    if args.doi:
        success = downloader.download_by_doi(args.doi, args.output)
    elif args.title:
        success = downloader.download_by_title(args.title, args.output)
    elif args.pmcid:
        info = downloader.get_paper_info(args.pmcid)
        if info and info['pdf_url']:
            success = downloader.download_pdf(info['pdf_url'], args.output)
    
    if success:
        print(f"\n🎉 下载成功: {args.output}")
    else:
        print(f"\n❌ 下载失败")
        print("\n💡 该论文可能:")
        print("  1. 不在PMC开放获取数据库中")
        print("  2. 是付费期刊论文")
        print("  3. 使用其他下载渠道")
        sys.exit(1)


if __name__ == '__main__':
    main()
