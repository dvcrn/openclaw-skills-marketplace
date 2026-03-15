# -*- coding: utf-8 -*-
"""
文件管理器模块

处理文件重命名、组织、去重逻辑
"""

import os;
import shutil;
import logging;
from typing import List, Dict, Optional;
from pathlib import Path;

try:
    from .config import DownloadConfig, PaperInfo;
except ImportError:
    from config import DownloadConfig, PaperInfo;


logger = logging.getLogger(__name__);


class FileManager:
    """文件管理器"""

    def __init__(self, config: DownloadConfig):
        """初始化文件管理器"""
        self.config = config;

    def organize_papers(self, papers: List[PaperInfo]) -> List[PaperInfo]:
        """
        组织论文文件(重命名、去重)

        Args:
            papers: 论文信息列表

        Returns:
            更新后的论文信息列表
        """
        # 按来源分组
        papers_by_source = {};
        for paper in papers:
            source = paper.source;
            if source not in papers_by_source:
                papers_by_source[source] = [];
            papers_by_source[source].append(paper);

        # 处理每组
        for source, source_papers in papers_by_source.items():
            # 创建来源子目录
            source_dir = os.path.join(self.config.output_dir, source);
            os.makedirs(source_dir, exist_ok=True);

            # 重命名文件
            for paper in source_papers:
                if paper.local_path and os.path.exists(paper.local_path):
                    new_path = self._rename_file(paper, source_dir);
                    if new_path != paper.local_path:
                        paper.local_path = new_path;

        return papers;

    def _rename_file(self, paper: PaperInfo, target_dir: str) -> str:
        """
        重命名文件

        Args:
            paper: 论文信息
            target_dir: 目标目录

        Returns:
            新的文件路径
        """
        # 生成新文件名
        new_filename = self._generate_filename(paper);
        new_path = os.path.join(target_dir, new_filename);

        # 检查是否已存在
        if os.path.exists(new_path):
            # 避免冲突,添加数字后缀
            base, ext = os.path.splitext(new_filename);
            counter = 1;
            while os.path.exists(new_path):
                new_filename = f'{base}_{counter}{ext}';
                new_path = os.path.join(target_dir, new_filename);
                counter += 1;

        # 重命名文件
        try:
            if os.path.exists(paper.local_path):
                shutil.move(paper.local_path, new_path);
                logger.info(f'Renamed: {paper.local_path} -> {new_path}');
        except Exception as e:
            logger.error(f'Failed to rename file: {e}');
            return paper.local_path;

        return new_path;

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
            first_author=self._sanitize(paper.get_first_author()),
            year=paper.get_year(),
            title_abbr=self._sanitize(paper.get_title_abbr()),
            title=self._sanitize(paper.title) if paper.title else 'untitled',
            authors=self._sanitize('_'.join(paper.authors[:3])) if paper.authors else 'unknown',
            id=paper.paper_id,
        );

        return f'{filename}.pdf';

    def _sanitize(self, text: str) -> str:
        """
        清理文本,移除非法文件名字符

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        illegal_chars = '<>:"/\\|?*';
        for char in illegal_chars:
            text = text.replace(char, '_');

        # 移除多余空格
        text = '_'.join(text.split());

        # 限制长度
        max_length = 150;
        if len(text) > max_length:
            text = text[:max_length];

        return text.strip('_');

    def deduplicate(self, papers: List[PaperInfo]) -> List[PaperInfo]:
        """
        去重处理

        Args:
            papers: 论文信息列表

        Returns:
            去重后的论文信息列表
        """
        seen_ids = set();
        unique_papers = [];

        for paper in papers:
            # 使用paper_id作为唯一标识
            if paper.paper_id not in seen_ids:
                seen_ids.add(paper.paper_id);
                unique_papers.append(paper);
            else:
                # 标记为重复
                logger.info(f'Duplicate paper skipped: {paper.paper_id}');

        return unique_papers;

    def cleanup_failed(self, papers: List[PaperInfo]) -> None:
        """
        清理下载失败的文件

        Args:
            papers: 论文信息列表
        """
        for paper in papers:
            if paper.download_status == 'failed' and paper.local_path:
                try:
                    if os.path.exists(paper.local_path):
                        os.remove(paper.local_path);
                        logger.info(f'Cleaned up failed download: {paper.local_path}');
                except Exception as e:
                    logger.error(f'Failed to cleanup {paper.local_path}: {e}');

    def get_storage_stats(self, papers: List[PaperInfo]) -> Dict:
        """
        获取存储统计信息

        Args:
            papers: 论文信息列表

        Returns:
            统计信息字典
        """
        stats = {
            'total': len(papers),
            'success': 0,
            'failed': 0,
            'manual_required': 0,
            'pending': 0,
            'total_size_mb': 0,
            'sources': {},
        };

        for paper in papers:
            # 统计状态
            status = paper.download_status;
            if status in stats:
                stats[status] += 1;

            # 统计来源
            source = paper.source;
            if source not in stats['sources']:
                stats['sources'][source] = 0;
            stats['sources'][source] += 1;

            # 统计文件大小
            if paper.local_path and os.path.exists(paper.local_path):
                try:
                    size = os.path.getsize(paper.local_path);
                    stats['total_size_mb'] += size / (1024 * 1024);
                except Exception:
                    pass;

        return stats;
