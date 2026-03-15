# -*- coding: utf-8 -*-
"""
论文检索模块

支持从arXiv、Semantic Scholar等多个来源搜索论文
"""

import logging;
from typing import List, Optional;
from datetime import datetime;

try:
    import arxiv;
except ImportError:
    arxiv = None;

try:
    from resp import semantic_scholar;
except ImportError:
    semantic_scholar = None;

try:
    from .config import DownloadConfig, PaperInfo;
except ImportError:
    from config import DownloadConfig, PaperInfo;


logger = logging.getLogger(__name__);


class PaperSearcher:
    """论文检索器"""

    def __init__(self, config: DownloadConfig):
        """初始化检索器"""
        self.config = config;
        self.arxiv_client = None;
        if arxiv:
            try:
                self.arxiv_client = arxiv.Client();
            except Exception as e:
                logger.warning(f'Failed to initialize arXiv client: {e}');

    def search_papers(self, query: str, source: Optional[str] = None) -> List[PaperInfo]:
        """
        通过关键词搜索论文

        Args:
            query: 搜索关键词
            source: 来源, None表示按优先级尝试所有来源

        Returns:
            论文信息列表
        """
        papers = [];

        # 确定搜索来源
        sources = [source] if source else self.config.source_priority;

        for src in sources:
            try:
                if src == 'arxiv':
                    papers.extend(self._search_arxiv(query));
                    break;
                elif src == 'semantic_scholar':
                    papers.extend(self._search_semantic_scholar(query));
                    break;
                else:
                    logger.warning(f'Unknown source: {src}');
            except Exception as e:
                logger.error(f'Search from {src} failed: {e}');
                continue;

        logger.info(f'Found {len(papers)} papers for query: {query}');
        return papers;

    def search_by_ids(self, paper_ids: List[str], source: str = 'arxiv') -> List[PaperInfo]:
        """
        通过论文ID列表搜索

        Args:
            paper_ids: 论文ID列表
            source: 来源 (arxiv, semantic_scholar)

        Returns:
            论文信息列表
        """
        papers = [];

        try:
            if source == 'arxiv':
                papers = self._search_arxiv_by_ids(paper_ids);
            elif source == 'semantic_scholar':
                papers = self._search_semantic_scholar_by_ids(paper_ids);
            else:
                logger.warning(f'Unsupported source for ID search: {source}');
        except Exception as e:
            logger.error(f'Search by IDs failed: {e}');

        return papers;

    def search_by_urls(self, pdf_urls: List[str]) -> List[PaperInfo]:
        """
        通过PDF URL列表搜索

        Args:
            pdf_urls: PDF URL列表

        Returns:
            论文信息列表(仅包含URL,元数据需要后续获取)
        """
        papers = [];

        for url in pdf_urls:
            paper_id = self._extract_paper_id_from_url(url);
            paper = PaperInfo(
                paper_id=paper_id,
                title=f'Paper from {url}',
                pdf_url=url,
                source='url',
            );
            papers.append(paper);

        return papers;

    def _search_arxiv(self, query: str) -> List[PaperInfo]:
        """从arXiv搜索论文"""
        if not self.arxiv_client:
            logger.error('arXiv client not initialized');
            return [];

        papers = [];
        try:
            search = arxiv.Search(
                query=query,
                max_results=self.config.max_results,
                sort_by=arxiv.SortCriterion.Relevance,
            );

            for result in self.arxiv_client.results(search):
                # 提取PDF URL
                pdf_url = None;
                for link in result.links:
                    if link.title == 'pdf':
                        pdf_url = link.href;
                        break;

                paper = PaperInfo(
                    paper_id=result.entry_id.split('/')[-1],
                    title=result.title,
                    authors=[a.name for a in result.authors],
                    published_date=result.published.strftime('%Y-%m-%d') if result.published else None,
                    abstract=result.summary,
                    pdf_url=pdf_url,
                    paper_url=result.entry_id,
                    source='arxiv',
                );
                papers.append(paper);

        except Exception as e:
            logger.error(f'arXiv search failed: {e}');

        return papers;

    def _search_arxiv_by_ids(self, paper_ids: List[str]) -> List[PaperInfo]:
        """通过arXiv ID搜索论文"""
        if not self.arxiv_client:
            logger.error('arXiv client not initialized');
            return [];

        papers = [];
        for paper_id in paper_ids:
            try:
                search = arxiv.Search(id_list=[paper_id]);
                results = list(self.arxiv_client.results(search));

                if results:
                    result = results[0];
                    pdf_url = None;
                    for link in result.links:
                        if link.title == 'pdf':
                            pdf_url = link.href;
                            break;

                    paper = PaperInfo(
                        paper_id=result.entry_id.split('/')[-1],
                        title=result.title,
                        authors=[a.name for a in result.authors],
                        published_date=result.published.strftime('%Y-%m-%d') if result.published else None,
                        abstract=result.summary,
                        pdf_url=pdf_url,
                        paper_url=result.entry_id,
                        source='arxiv',
                    );
                    papers.append(paper);
            except Exception as e:
                logger.error(f'arXiv ID search failed for {paper_id}: {e}');

        return papers;

    def _search_semantic_scholar(self, query: str) -> List[PaperInfo]:
        """从Semantic Scholar搜索论文"""
        if not semantic_scholar:
            logger.warning('respsearch not installed');
            return [];

        papers = [];
        try:
            results = semantic_scholar.search_papers(query, max_results=self.config.max_results);

            for result in results:
                # 尝试获取PDF URL
                pdf_url = result.get('pdf') or result.get('openAccessPdf', {}).get('url');

                paper = PaperInfo(
                    paper_id=result.get('paperId', ''),
                    title=result.get('title', ''),
                    authors=[a.get('name', '') for a in result.get('authors', [])],
                    published_date=result.get('year'),
                    abstract=result.get('abstract'),
                    pdf_url=pdf_url,
                    doi=result.get('doi'),
                    paper_url=result.get('url'),
                    source='semantic_scholar',
                );
                papers.append(paper);

        except Exception as e:
            logger.error(f'Semantic Scholar search failed: {e}');

        return papers;

    def _search_semantic_scholar_by_ids(self, paper_ids: List[str]) -> List[PaperInfo]:
        """通过Semantic Scholar ID搜索论文"""
        if not semantic_scholar:
            logger.warning('respsearch not installed');
            return [];

        papers = [];
        for paper_id in paper_ids:
            try:
                result = semantic_scholar.get_paper(paper_id);
                if result:
                    pdf_url = result.get('pdf') or result.get('openAccessPdf', {}).get('url');

                    paper = PaperInfo(
                        paper_id=result.get('paperId', ''),
                        title=result.get('title', ''),
                        authors=[a.get('name', '') for a in result.get('authors', [])],
                        published_date=result.get('year'),
                        abstract=result.get('abstract'),
                        pdf_url=pdf_url,
                        doi=result.get('doi'),
                        paper_url=result.get('url'),
                        source='semantic_scholar',
                    );
                    papers.append(paper);
            except Exception as e:
                logger.error(f'Semantic Scholar ID search failed for {paper_id}: {e}');

        return papers;

    def _extract_paper_id_from_url(self, url: str) -> str:
        """从URL中提取论文ID"""
        # 尝试从URL中提取arXiv ID
        import re;
        arxiv_match = re.search(r'arxiv\.org/(?:pdf|abs)/([^.]+)', url);
        if arxiv_match:
            return arxiv_match.group(1);

        # 尝试从Semantic Scholar URL提取
        ss_match = re.search(r'semanticscholar\.org/paper/([^/]+)', url);
        if ss_match:
            return ss_match.group(1);

        # 返回URL的哈希作为ID
        return str(hash(url))[:12];
