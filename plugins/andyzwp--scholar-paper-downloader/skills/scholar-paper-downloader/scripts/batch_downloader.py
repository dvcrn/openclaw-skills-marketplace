# -*- coding: utf-8 -*-
"""
批量下载器主程序

协调各模块完成完整的批量下载流程
"""

import argparse;
import logging;
import sys;
from typing import List, Optional;

try:
    from .config import DownloadConfig, PaperInfo;
    from .paper_search import PaperSearcher;
    from .pdf_downloader import PDFDownloader;
    from .metadata_extractor import MetadataExtractor;
    from .file_manager import FileManager;
    from .index_generator import IndexGenerator;
except ImportError:
    from config import DownloadConfig, PaperInfo;
    from paper_search import PaperSearcher;
    from pdf_downloader import PDFDownloader;
    from metadata_extractor import MetadataExtractor;
    from file_manager import FileManager;
    from index_generator import IndexGenerator;


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
);
logger = logging.getLogger(__name__);


class BatchDownloader:
    """批量下载器"""

    def __init__(self, config: Optional[DownloadConfig] = None):
        """初始化批量下载器"""
        self.config = config or DownloadConfig();

        # 初始化各模块
        self.searcher = PaperSearcher(self.config);
        self.downloader = PDFDownloader(self.config);
        self.extractor = MetadataExtractor(self.config);
        self.file_manager = FileManager(self.config);
        self.index_generator = IndexGenerator(self.config);

    def search_and_download(self, query: str, source: Optional[str] = None) -> List[PaperInfo]:
        """
        搜索并下载论文

        Args:
            query: 搜索关键词
            source: 来源

        Returns:
            论文信息列表
        """
        logger.info(f'Starting search for: {query}');

        # 1. 搜索论文
        papers = self.searcher.search_papers(query, source);
        if not papers:
            logger.warning('No papers found');
            return [];

        logger.info(f'Found {len(papers)} papers');

        # 2. 下载PDF
        papers = self.downloader.download_papers(papers);

        # 3. 提取元数据
        papers = self.extractor.extract_from_pdfs(papers);
        papers = self.extractor.validate_pdfs(papers);
        papers = self.extractor.enrich_metadata(papers);

        # 4. 组织文件
        papers = self.file_manager.organize_papers(papers);

        # 5. 去重
        papers = self.file_manager.deduplicate(papers);

        # 6. 生成索引
        if self.config.generate_index:
            self.index_generator.generate(papers);

        # 7. 输出摘要
        summary = self.index_generator.generate_summary(papers);
        print(summary);

        return papers;

    def download_by_ids(self, paper_ids: List[str], source: str = 'arxiv') -> List[PaperInfo]:
        """
        通过论文ID列表下载

        Args:
            paper_ids: 论文ID列表
            source: 来源

        Returns:
            论文信息列表
        """
        logger.info(f'Starting download for {len(paper_ids)} papers by IDs');

        # 1. 搜索论文
        papers = self.searcher.search_by_ids(paper_ids, source);
        if not papers:
            logger.warning('No papers found');
            return [];

        # 2. 下载PDF
        papers = self.downloader.download_papers(papers);

        # 3. 提取元数据
        papers = self.extractor.extract_from_pdfs(papers);
        papers = self.extractor.validate_pdfs(papers);

        # 4. 组织文件
        papers = self.file_manager.organize_papers(papers);

        # 5. 生成索引
        if self.config.generate_index:
            self.index_generator.generate(papers);

        # 6. 输出摘要
        summary = self.index_generator.generate_summary(papers);
        print(summary);

        return papers;

    def download_by_urls(self, pdf_urls: List[str]) -> List[PaperInfo]:
        """
        通过PDF URL列表下载

        Args:
            pdf_urls: PDF URL列表

        Returns:
            论文信息列表
        """
        logger.info(f'Starting download for {len(pdf_urls)} URLs');

        # 1. 创建论文信息
        papers = self.searcher.search_by_urls(pdf_urls);

        # 2. 下载PDF
        papers = self.downloader.download_papers(papers);

        # 3. 验证PDF
        papers = self.extractor.validate_pdfs(papers);

        # 4. 组织文件
        papers = self.file_manager.organize_papers(papers);

        # 5. 生成索引
        if self.config.generate_index:
            self.index_generator.generate(papers);

        # 6. 输出摘要
        summary = self.index_generator.generate_summary(papers);
        print(summary);

        return papers;


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='学术文献批量下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 按关键词搜索下载
  python batch_downloader.py -q "machine learning"

  # 按arXiv ID下载
  python batch_downloader.py --ids 2103.00001 2103.00002

  # 按PDF URL下载
  python batch_downloader.py --urls "https://arxiv.org/pdf/2103.00001.pdf"

  # 自定义输出目录
  python batch_downloader.py -q "deep learning" -o /path/to/papers
        ''',
    );

    parser.add_argument('-q', '--query', type=str, help='搜索关键词');
    parser.add_argument('--ids', nargs='+', help='论文ID列表');
    parser.add_argument('--urls', nargs='+', help='PDF URL列表');
    parser.add_argument('-o', '--output', type=str, default='./papers', help='输出目录');
    parser.add_argument('-m', '--max-results', type=int, default=10, help='最大结果数');
    parser.add_argument('-w', '--workers', type=int, default=3, help='并发下载数');
    parser.add_argument('--source', type=str, default=None, help='来源 (arxiv, semantic_scholar)');
    parser.add_argument('--no-index', action='store_true', help='不生成索引文件');

    args = parser.parse_args();

    # 创建配置
    config = DownloadConfig(
        output_dir=args.output,
        max_results=args.max_results,
        max_workers=args.workers,
        generate_index=not args.no_index,
    );

    # 创建下载器
    downloader = BatchDownloader(config);

    # 执行下载
    try:
        if args.query:
            papers = downloader.search_and_download(args.query, args.source);
        elif args.ids:
            papers = downloader.download_by_ids(args.ids, args.source or 'arxiv');
        elif args.urls:
            papers = downloader.download_by_urls(args.urls);
        else:
            parser.print_help();
            sys.exit(1);

        # 输出统计
        stats = FileManager(config).get_storage_stats(papers);
        logger.info(f'Download complete: {stats["success"]}/{stats["total"]} successful');

    except KeyboardInterrupt:
        logger.info('Download interrupted by user');
        sys.exit(1);
    except Exception as e:
        logger.error(f'Download failed: {e}');
        sys.exit(1);


if __name__ == '__main__':
    main();
