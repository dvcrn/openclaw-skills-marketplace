# -*- coding: utf-8 -*-
"""
PDF下载器模块

支持多线程下载、重试、进度跟踪
"""

import os;
import logging;
import time;
import requests;
from concurrent.futures import ThreadPoolExecutor, as_completed;
from typing import List, Optional;
from pathlib import Path;

try:
    from .config import DownloadConfig, PaperInfo;
except ImportError:
    from config import DownloadConfig, PaperInfo;


logger = logging.getLogger(__name__);


class PDFDownloader:
    """PDF下载器"""

    def __init__(self, config: DownloadConfig):
        """初始化下载器"""
        self.config = config;
        self.session = requests.Session();
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        });

    def download_papers(self, papers: List[PaperInfo]) -> List[PaperInfo]:
        """
        批量下载论文PDF

        Args:
            papers: 论文信息列表

        Returns:
            更新后的论文信息列表(包含下载状态和本地路径)
        """
        downloaded_papers = [];
        failed_papers = [];

        logger.info(f'Starting download of {len(papers)} papers');

        # 使用多线程下载
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_paper = {
                executor.submit(self._download_single, paper): paper
                for paper in papers
            };

            for future in as_completed(future_to_paper):
                paper = future_to_paper[future];
                try:
                    result_paper = future.result();
                    if result_paper.download_status == 'success':
                        downloaded_papers.append(result_paper);
                    else:
                        failed_papers.append(result_paper);
                except Exception as e:
                    logger.error(f'Download exception for {paper.paper_id}: {e}');
                    paper.download_status = 'failed';
                    paper.comment = str(e);
                    failed_papers.append(paper);

        logger.info(f'Download completed: {len(downloaded_papers)} success, {len(failed_papers)} failed');

        return downloaded_papers + failed_papers;

    def _download_single(self, paper: PaperInfo) -> PaperInfo:
        """
        下载单篇论文

        Args:
            paper: 论文信息

        Returns:
            更新后的论文信息
        """
        if not paper.pdf_url:
            paper.download_status = 'manual_required';
            paper.comment = 'No PDF URL available';
            return paper;

        # 构建文件名
        filename = self._generate_filename(paper);
        filepath = os.path.join(self.config.output_dir, filename);

        # 检查是否已存在
        if os.path.exists(filepath):
            logger.info(f'File already exists: {filepath}');
            paper.download_status = 'success';
            paper.local_path = filepath;
            return paper;

        # 下载PDF
        for attempt in range(self.config.retry_times):
            try:
                logger.debug(f'Downloading {paper.paper_id} (attempt {attempt + 1})');

                response = self.session.get(
                    paper.pdf_url,
                    timeout=self.config.timeout,
                    stream=True,
                );

                if response.status_code == 200:
                    # 验证是否为PDF
                    content_type = response.headers.get('Content-Type', '');
                    if 'pdf' not in content_type.lower() and not response.content[:4] == b'%PDF':
                        # 可能是HTML页面(需要登录等)
                        raise Exception(f'Not a PDF file, content-type: {content_type}');

                    # 写入文件
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk);

                    # 验证文件
                    if os.path.getsize(filepath) > 0:
                        paper.download_status = 'success';
                        paper.local_path = filepath;
                        logger.info(f'Downloaded successfully: {paper.paper_id}');
                        return paper;
                    else:
                        os.remove(filepath);
                        raise Exception('Downloaded file is empty');

                elif response.status_code == 404:
                    paper.download_status = 'manual_required';
                    paper.comment = 'PDF not found (404)';
                    logger.warning(f'PDF not found: {paper.pdf_url}');
                    return paper;

                elif response.status_code == 403:
                    paper.download_status = 'manual_required';
                    paper.comment = 'Access forbidden (403) - may require subscription';
                    logger.warning(f'Access forbidden: {paper.pdf_url}');
                    return paper;

                else:
                    raise Exception(f'HTTP {response.status_code}');

            except requests.exceptions.Timeout:
                logger.warning(f'Timeout on attempt {attempt + 1} for {paper.paper_id}');
                if attempt == self.config.retry_times - 1:
                    paper.download_status = 'failed';
                    paper.comment = 'Download timeout';

            except requests.exceptions.RequestException as e:
                logger.warning(f'Request error on attempt {attempt + 1}: {e}');
                if attempt == self.config.retry_times - 1:
                    paper.download_status = 'failed';
                    paper.comment = f'Request error: {str(e)}';

            except Exception as e:
                logger.error(f'Download error for {paper.paper_id}: {e}');
                paper.download_status = 'failed';
                paper.comment = str(e);
                # 删除可能存在的空文件
                if os.path.exists(filepath):
                    os.remove(filepath);
                return paper;

            # 等待后重试
            if attempt < self.config.retry_times - 1:
                time.sleep(1 * (attempt + 1));

        return paper;

    def _generate_filename(self, paper: PaperInfo) -> str:
        """
        生成文件名

        Args:
            paper: 论文信息

        Returns:
            文件名
        """
        template = self.config.naming_template;

        # 替换占位符
        filename = template.format(
            first_author=paper.get_first_author(),
            year=paper.get_year(),
            title_abbr=paper.get_title_abbr(),
            title=paper.title if paper.title else 'untitled',
            authors='_'.join(paper.authors[:3]) if paper.authors else 'unknown',
            id=paper.paper_id,
        );

        # 清理文件名中的非法字符
        filename = self._sanitize_filename(filename);

        return f'{filename}.pdf';

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名中的非法字符

        Args:
            filename: 原始文件名

        Returns:
            清理后的文件名
        """
        # 替换非法字符
        illegal_chars = '<>:"/\\|?*';
        for char in illegal_chars:
            filename = filename.replace(char, '_');

        # 限制长度
        max_length = 200;
        if len(filename) > max_length:
            filename = filename[:max_length];

        return filename;

    def download_with_fallback(self, paper: PaperInfo, alternative_urls: List[str]) -> PaperInfo:
        """
        尝试从多个URL下载(付费文献fallback策略)

        Args:
            paper: 论文信息
            alternative_urls: 备用URL列表

        Returns:
            更新后的论文信息
        """
        # 首先尝试原始URL
        if paper.pdf_url:
            result = self._download_single(paper);
            if result.download_status == 'success':
                return result;

        # 尝试备用URL
        for url in alternative_urls:
            logger.info(f'Trying alternative URL: {url}');
            paper.pdf_url = url;
            result = self._download_single(paper);
            if result.download_status == 'success':
                return result;

        # 所有尝试都失败
        paper.download_status = 'manual_required';
        if not paper.comment:
            paper.comment = 'All download attempts failed';
        return paper;
