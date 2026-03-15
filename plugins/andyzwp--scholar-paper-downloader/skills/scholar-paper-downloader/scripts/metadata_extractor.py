# -*- coding: utf-8 -*-
"""
元数据提取器模块

从PDF和API提取结构化数据,验证PDF完整性
"""

import logging;
from typing import List, Optional;
import os;

try:
    import fitz;  # PyMuPDF
except ImportError:
    fitz = None;

try:
    from .config import DownloadConfig, PaperInfo;
except ImportError:
    from config import DownloadConfig, PaperInfo;


logger = logging.getLogger(__name__);


class MetadataExtractor:
    """元数据提取器"""

    def __init__(self, config: DownloadConfig):
        """初始化提取器"""
        self.config = config;

    def extract_from_pdfs(self, papers: List[PaperInfo]) -> List[PaperInfo]:
        """
        从PDF文件提取元数据

        Args:
            papers: 论文信息列表

        Returns:
            更新后的论文信息列表
        """
        for paper in papers:
            if paper.local_path and os.path.exists(paper.local_path):
                try:
                    extracted = self._extract_from_pdf(paper.local_path);
                    # 补充缺失的元数据
                    if not paper.title and extracted.get('title'):
                        paper.title = extracted['title'];
                    if not paper.authors and extracted.get('authors'):
                        paper.authors = extracted['authors'];
                    if not paper.keywords and extracted.get('keywords'):
                        paper.keywords = extracted['keywords'];
                except Exception as e:
                    logger.warning(f'Failed to extract metadata from {paper.local_path}: {e}');

        return papers;

    def _extract_from_pdf(self, pdf_path: str) -> dict:
        """
        从单个PDF文件提取元数据

        Args:
            pdf_path: PDF文件路径

        Returns:
            提取的元数据字典
        """
        if not fitz:
            logger.warning('PyMuPDF not installed, skipping PDF metadata extraction');
            return {};

        metadata = {};

        try:
            doc = fitz.open(pdf_path);

            # 获取PDF元数据
            pdf_meta = doc.metadata;
            if pdf_meta:
                metadata['title'] = pdf_meta.get('title', '');
                metadata['author'] = pdf_meta.get('author', '');
                metadata['subject'] = pdf_meta.get('subject', '');
                metadata['creator'] = pdf_meta.get('creator', '');
                metadata['producer'] = pdf_meta.get('producer', '');

            # 处理作者
            if metadata.get('author'):
                authors = [a.strip() for a in metadata['author'].split(',')];
                metadata['authors'] = authors;

            # 尝试从第一页提取标题(作为后备)
            if not metadata.get('title') or metadata['title'] == os.path.basename(pdf_path):
                for page in doc:
                    text = page.get_text();
                    if text:
                        lines = [l.strip() for l in text.split('\n') if l.strip()];
                        if lines:
                            # 假设第一行是标题
                            metadata['title'] = lines[0];
                            break;
                    break;

            doc.close();

            # 验证PDF完整性
            metadata['valid'] = os.path.getsize(pdf_path) > 0;

        except Exception as e:
            logger.error(f'Error extracting metadata from {pdf_path}: {e}');
            metadata['error'] = str(e);

        return metadata;

    def validate_pdfs(self, papers: List[PaperInfo]) -> List[PaperInfo]:
        """
        验证PDF文件完整性

        Args:
            papers: 论文信息列表

        Returns:
            更新后的论文信息列表
        """
        for paper in papers:
            if paper.local_path and os.path.exists(paper.local_path):
                try:
                    if not fitz:
                        # 如果没有PyMuPDF,简单检查文件大小
                        size = os.path.getsize(paper.local_path);
                        if size > 1000:  # 至少1KB
                            paper.comment = (paper.comment or '') + ' | PDF validated';
                        else:
                            paper.download_status = 'failed';
                            paper.comment = 'PDF file too small, may be corrupted';
                        continue;

                    # 使用PyMuPDF验证
                    doc = fitz.open(paper.local_path);
                    if doc.page_count > 0:
                        paper.comment = (paper.comment or '') + f' | {doc.page_count} pages';
                    else:
                        paper.download_status = 'failed';
                        paper.comment = 'PDF has no pages, may be corrupted';
                    doc.close();

                except Exception as e:
                    logger.error(f'Error validating {paper.local_path}: {e}');
                    paper.download_status = 'failed';
                    paper.comment = f'PDF validation error: {str(e)}';

        return papers;

    def enrich_metadata(self, papers: List[PaperInfo]) -> List[PaperInfo]:
        """
        丰富元数据(从多个来源获取补充信息)

        Args:
            papers: 论文信息列表

        Returns:
            更新后的论文信息列表
        """
        for paper in papers:
            # 添加本地文件信息
            if paper.local_path and os.path.exists(paper.local_path):
                stat = os.stat(paper.local_path);
                paper.comment = (paper.comment or '') + f' | Size: {stat.st_size / 1024 / 1024:.2f}MB';

        return papers;
