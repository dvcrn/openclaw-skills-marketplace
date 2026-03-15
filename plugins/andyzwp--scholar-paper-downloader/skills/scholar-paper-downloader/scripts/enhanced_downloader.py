#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强批量下载器 - 优先官方渠道

支持从arXiv、PubMed Central等官方免费渠道下载,
付费文献生成详细的手动下载指引。
"""

import argparse
import logging
import sys
import os
from datetime import datetime
from typing import List, Optional
from urllib.parse import quote

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("请先安装依赖: pip install requests beautifulsoup4")
    sys.exit(1)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PaperInfo:
    """论文信息类"""
    
    def __init__(self, title="", authors="", year="", doi="", source="", url="", pdf_url=""):
        self.title = title
        self.authors = authors
        self.year = year
        self.doi = doi
        self.source = source  # 来源: arxiv, pmc, manual
        self.url = url
        self.pdf_url = pdf_url
        self.status = "pending"  # pending, downloaded, manual


class OfficialDownloader:
    """官方渠道下载器"""
    
    def __init__(self, output_dir="./downloads", max_workers=3):
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        os.makedirs(output_dir, exist_ok=True)
    
    def search_arxiv(self, query: str, max_results: int = 5) -> List[PaperInfo]:
        """从arXiv搜索论文"""
        print(f"\n🔍 搜索arXiv: {query}")
        print("=" * 70)
        
        papers = []
        try:
            url = f"http://export.arxiv.org/api/query?search_query=all:{quote(query)}&start=0&max_results={max_results}"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                
                for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                    title = entry.findtext('.//{http://www.w3.org/2005/Atom}title', '').strip()
                    arxiv_id = entry.findtext('.//{http://www.w3.org/2005/Atom}id', '').split('/')[-1]
                    authors = ', '.join([a.text for a in entry.findall('.//{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')])
                    published = entry.findtext('.//{http://www.w3.org/2005/Atom}published', '')[:4]
                    
                    paper = PaperInfo(
                        title=title,
                        authors=authors,
                        year=published,
                        source="arxiv",
                        url=f"https://arxiv.org/abs/{arxiv_id}",
                        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    )
                    papers.append(paper)
                    
                    print(f"   {len(papers)}. {title[:60]}...")
                    print(f"      arXiv ID: {arxiv_id}, 年份: {published}")
            
            print(f"\n✅ 找到 {len(papers)} 篇arXiv论文")
            
        except Exception as e:
            print(f"❌ arXiv搜索失败: {str(e)[:50]}")
        
        return papers
    
    def search_pmc(self, query: str, max_results: int = 5) -> List[PaperInfo]:
        """从PMC搜索开放获取论文"""
        print(f"\n🔍 搜索PMC: {query}")
        print("=" * 70)
        
        papers = []
        try:
            url = f"https://www.ncbi.nlm.nih.gov/pmc/?term={quote(query)}"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找PMC文章链接
                articles = soup.find_all('div', class_='rprt')[:max_results]
                
                for i, article in enumerate(articles, 1):
                    title_elem = article.find('a', class_='title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    pmc_link = title_elem.get('href', '')
                    
                    # 提取PMCID
                    pmcid = pmc_link.split('/')[-1] if pmc_link else ''
                    
                    # 提取作者
                    author_elem = article.find('div', class_='authors')
                    authors = author_elem.get_text(strip=True) if author_elem else ""
                    
                    paper = PaperInfo(
                        title=title,
                        authors=authors,
                        year="",
                        source="pmc",
                        url=f"https://www.ncbi.nlm.nih.gov{pmc_link}" if pmc_link else "",
                        pdf_url=f"https://www.ncbi.nlm.nih.gov{pmc_link}/pdf" if pmc_link else ""
                    )
                    papers.append(paper)
                    
                    print(f"   {i}. {title[:60]}...")
                    print(f"      PMC ID: {pmcid}")
            
            print(f"\n✅ 找到 {len(papers)} 篇PMC开放获取论文")
            
        except Exception as e:
            print(f"❌ PMC搜索失败: {str(e)[:50]}")
        
        return papers
    
    def download_pdf(self, paper: PaperInfo, filename: str) -> bool:
        """下载PDF"""
        try:
            if not paper.pdf_url:
                print(f"   ❌ 无PDF链接")
                return False
            
            print(f"   📥 下载: {paper.pdf_url[:70]}...")
            
            response = self.session.get(paper.pdf_url, timeout=30, stream=True)
            
            if response.status_code == 200:
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # 验证文件大小
                size_kb = os.path.getsize(filepath) / 1024
                if size_kb > 10:
                    print(f"   ✅ 保存成功: {filename} ({size_kb:.1f} KB)")
                    paper.status = "downloaded"
                    return True
                else:
                    os.remove(filepath)
                    print(f"   ❌ 文件太小,可能无效")
                    return False
            else:
                print(f"   ❌ 下载失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ 下载错误: {str(e)[:50]}")
            return False
    
    def create_manual_guide(self, paper: PaperInfo, filename: str) -> str:
        """创建手动下载指引"""
        guide_filename = filename.replace('.pdf', '_DOWNLOAD.md')
        guide_path = os.path.join(self.output_dir, guide_filename)
        
        guide_content = f"""# 论文下载指南

## 📄 论文信息

**标题**: {paper.title}

**DOI**: {paper.doi if paper.doi else '未提供'}

**来源**: {paper.source}

---

## 🚀 手动下载方法

由于该论文无法通过官方免费渠道自动下载,请使用以下方法:

### 方法1: 访问Sci-Hub (推荐)

**步骤**:

1. 打开浏览器,访问以下任一Sci-Hub镜像:
   - https://sci-hub.tw (推荐)
   - https://sci-hub.se
   - https://sci-hub.ren
   - https://sci-hub.st

2. 在搜索框中输入DOI或标题:
   ```
   {paper.doi if paper.doi else paper.title}
   ```

3. 点击 "Open" 或 "搜索" 按钮

4. 等待页面加载,显示PDF预览

5. 点击下载按钮或右键保存PDF

**预计时间**: 1-2分钟

---

### 方法2: 检查开放获取版本

1. 访问PubMed Central: https://www.ncbi.nlm.nih.gov/pmc/
2. 搜索论文标题或DOI
3. 查看是否有 "Free full text" 链接

---

### 方法3: 联系作者索取

**邮件模板**:

```
Dear Author,

I'm researching related topics and would like to request a PDF of your paper:

"{paper.title}"

I will use it only for academic research and properly cite it.

Could you please share a copy?

Thank you for your time and consideration.

Best regards,
[Your Name]
[Your Institution]
[Your Email]
```

在ResearchGate上搜索作者并点击 "Request full-text"。

---

### 方法4: 机构访问

如果你有以下权限:

1. **大学图书馆IP**
   - 连接校园网或VPN
   - 访问期刊官方页面
   - 机构订阅会自动授权下载

2. **图书馆文献传递**
   - 联系学校图书馆
   - 申请文献传递服务
   - 通常1-3个工作日

---

## 💡 提示

- 优先使用Sci-Hub,成功率最高
- 如果是开放获取期刊,可直接在官网下载
- 保存PDF后,将其重命名为: `{filename}`
- 下载完成后,请更新索引文件中的状态

---

**创建时间**: {datetime.now().strftime('%Y-%m-%d')}
**状态**: ⏳ 等待手动下载
"""
        
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"   📄 创建下载指引: {guide_filename}")
        paper.status = "manual"
        
        return guide_filename
    
    def download_batch(self, papers: List[PaperInfo]) -> dict:
        """批量下载"""
        results = {
            'downloaded': [],
            'manual': [],
            'failed': []
        }
        
        print(f"\n📚 开始批量下载 {len(papers)} 篇论文")
        print("=" * 70)
        
        for i, paper in enumerate(papers, 1):
            print(f"\n[{i}/{len(papers)}] {paper.title[:50]}...")
            
            # 生成文件名
            if paper.source == "arxiv":
                arxiv_id = paper.url.split('/')[-1]
                filename = f"{arxiv_id}.pdf"
            elif paper.source == "pmc":
                pmcid = paper.url.split('/')[-1]
                filename = f"{pmcid}.pdf"
            else:
                # 根据作者和年份生成
                author = paper.authors.split(',')[0].replace(' ', '_') if paper.authors else "Unknown"
                year = paper.year if paper.year else "n.d."
                filename = f"{author}_{year}.pdf"
            
            # 尝试下载
            if paper.pdf_url:
                success = self.download_pdf(paper, filename)
                if success:
                    results['downloaded'].append(paper)
                else:
                    # 下载失败,创建手动指引
                    guide_file = self.create_manual_guide(paper, filename)
                    results['manual'].append((paper, guide_file))
            else:
                # 无PDF链接,创建手动指引
                guide_file = self.create_manual_guide(paper, filename)
                results['manual'].append((paper, guide_file))
        
        return results
    
    def generate_index(self, results: dict):
        """生成索引文件"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Markdown索引
        index_md = []
        index_md.append("# 论文索引")
        index_md.append(f"\n生成时间: {timestamp}")
        index_md.append(f"\n## 下载统计")
        index_md.append(f"- ✅ 已下载: {len(results['downloaded'])} 篇")
        index_md.append(f"- 📄 需手动下载: {len(results['manual'])} 篇")
        index_md.append(f"- ❌ 下载失败: {len(results['failed'])} 篇")
        
        if results['downloaded']:
            index_md.append(f"\n## 已下载\n")
            for paper in results['downloaded']:
                index_md.append(f"- {paper.title[:60]}...")
                index_md.append(f"  - 来源: {paper.source}")
                index_md.append(f"  - 年份: {paper.year}")
        
        if results['manual']:
            index_md.append(f"\n## 需手动下载\n")
            for paper, guide in results['manual']:
                index_md.append(f"- {paper.title[:60]}...")
                index_md.append(f"  - DOI: {paper.doi if paper.doi else '未提供'}")
                index_md.append(f"  - 指引: `{guide}`")
        
        index_path = os.path.join(self.output_dir, 'index.md')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(index_md))
        
        print(f"\n📝 生成索引: index.md")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='增强批量下载器 - 优先官方渠道')
    parser.add_argument('-q', '--query', help='搜索关键词')
    parser.add_argument('-o', '--output', default='./downloads', help='输出目录')
    parser.add_argument('-m', '--max', type=int, default=5, help='最大论文数')
    parser.add_argument('-s', '--source', choices=['arxiv', 'pmc', 'both'], default='both', help='搜索来源')
    
    args = parser.parse_args()
    
    if not args.query:
        print("错误: 必须提供搜索关键词 (-q/--query)")
        sys.exit(1)
    
    downloader = OfficialDownloader(output_dir=args.output)
    papers = []
    
    # 搜索论文
    if args.source in ['arxiv', 'both']:
        arxiv_papers = downloader.search_arxiv(args.query, args.max)
        papers.extend(arxiv_papers)
    
    if args.source in ['pmc', 'both'] and len(papers) < args.max:
        pmc_papers = downloader.search_pmc(args.query, args.max - len(papers))
        papers.extend(pmc_papers)
    
    if not papers:
        print("\n❌ 未找到相关论文")
        sys.exit(1)
    
    # 批量下载
    results = downloader.download_batch(papers)
    
    # 生成索引
    downloader.generate_index(results)
    
    # 输出统计
    print(f"\n{'='*70}")
    print(f"✅ 任务完成!")
    print(f"   - 已下载: {len(results['downloaded'])} 篇")
    print(f"   - 需手动下载: {len(results['manual'])} 篇")
    print(f"   - 失败: {len(results['failed'])} 篇")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
