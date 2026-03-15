# -*- coding: utf-8 -*-
"""
索引生成器模块

生成Markdown和JSON格式的文献列表
"""

import json;
import logging;
import os;
from datetime import datetime;
from typing import List, Dict;
from pathlib import Path;

try:
    from .config import DownloadConfig, PaperInfo;
except ImportError:
    from config import DownloadConfig, PaperInfo;


logger = logging.getLogger(__name__);


class IndexGenerator:
    """索引生成器"""

    def __init__(self, config: DownloadConfig):
        """初始化索引生成器"""
        self.config = config;

    def generate(self, papers: List[PaperInfo]) -> Dict[str, str]:
        """
        生成索引文件

        Args:
            papers: 论文信息列表

        Returns:
            生成的索引文件路径字典
        """
        generated_files = {};

        # 生成Markdown索引
        if 'markdown' in self.config.index_format:
            md_path = self.generate_markdown_index(papers);
            if md_path:
                generated_files['markdown'] = md_path;

        # 生成JSON索引
        if 'json' in self.config.index_format:
            json_path = self.generate_json_index(papers);
            if json_path:
                generated_files['json'] = json_path;

        return generated_files;

    def generate_markdown_index(self, papers: List[PaperInfo], output_path: str = None) -> str:
        """
        生成Markdown格式索引

        Args:
            papers: 论文信息列表
            output_path: 自定义输出路径, None则使用默认路径

        Returns:
            生成的索引文件路径
        """
        if not output_path:
            output_path = os.path.join(self.config.output_dir, 'papers_index.md');

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # 写入标题
                f.write('# 文献索引\n\n');
                f.write(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n');
                f.write(f'文献总数: {len(papers)}\n\n');

                # 写入统计信息
                success = sum(1 for p in papers if p.download_status == 'success');
                failed = sum(1 for p in papers if p.download_status == 'failed');
                manual = sum(1 for p in papers if p.download_status == 'manual_required');

                f.write('## 下载统计\n\n');
                f.write(f'- 成功下载: {success}\n');
                f.write(f'- 下载失败: {failed}\n');
                f.write(f'- 需要手动获取: {manual}\n\n');

                # 写入文献列表
                f.write('## 文献列表\n\n');

                for i, paper in enumerate(papers, 1):
                    f.write(f'### {i}. {paper.title}\n\n');
                    f.write(f'- **作者**: {", ".join(paper.authors) if paper.authors else "未知"}\n');
                    f.write(f'- **年份**: {paper.get_year()}\n');
                    f.write(f'- **来源**: {paper.source}\n');
                    f.write(f'- **状态**: {self._get_status_label(paper.download_status)}\n');

                    if paper.doi:
                        f.write(f'- **DOI**: {paper.doi}\n');

                    if paper.pdf_url:
                        f.write(f'- **PDF URL**: {paper.pdf_url}\n');

                    if paper.local_path and os.path.exists(paper.local_path):
                        rel_path = os.path.relpath(paper.local_path, self.config.output_dir);
                        f.write(f'- **本地文件**: `{rel_path}`\n');

                    if paper.abstract and self.config.include_abstract:
                        abstract = paper.abstract[:500];
                        if len(paper.abstract) > 500:
                            abstract += '...';
                        f.write(f'\n**摘要**: {abstract}\n');

                    if paper.comment:
                        f.write(f'\n**备注**: {paper.comment}\n');

                    f.write('\n---\n\n');

            logger.info(f'Generated markdown index: {output_path}');
            return output_path;

        except Exception as e:
            logger.error(f'Failed to generate markdown index: {e}');
            return '';

    def generate_json_index(self, papers: List[PaperInfo], output_path: str = None) -> str:
        """
        生成JSON格式索引

        Args:
            papers: 论文信息列表
            output_path: 自定义输出路径, None则使用默认路径

        Returns:
            生成的索引文件路径
        """
        if not output_path:
            output_path = os.path.join(self.config.output_dir, 'papers_index.json');

        try:
            # 转换论文信息为字典
            papers_data = [];
            for paper in papers:
                paper_dict = paper.to_dict();
                # 添加相对路径
                if paper.local_path and os.path.exists(paper.local_path):
                    paper_dict['local_path_relative'] = os.path.relpath(
                        paper.local_path, self.config.output_dir
                    );
                papers_data.append(paper_dict);

            # 构建索引数据
            index_data = {
                'generated_at': datetime.now().isoformat(),
                'total_papers': len(papers),
                'statistics': {
                    'success': sum(1 for p in papers if p.download_status == 'success'),
                    'failed': sum(1 for p in papers if p.download_status == 'failed'),
                    'manual_required': sum(1 for p in papers if p.download_status == 'manual_required'),
                },
                'papers': papers_data,
            };

            # 写入JSON文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2);

            logger.info(f'Generated JSON index: {output_path}');
            return output_path;

        except Exception as e:
            logger.error(f'Failed to generate JSON index: {e}');
            return '';

    def _get_status_label(self, status: str) -> str:
        """获取状态标签"""
        labels = {
            'success': '✅ 已下载',
            'failed': '❌ 下载失败',
            'manual_required': '⚠️ 需要手动获取',
            'pending': '⏳ 等待中',
        };
        return labels.get(status, status);

    def generate_summary(self, papers: List[PaperInfo]) -> str:
        """
        生成简洁的摘要报告

        Args:
            papers: 论文信息列表

        Returns:
            摘要报告文本
        """
        success = sum(1 for p in papers if p.download_status == 'success');
        failed = sum(1 for p in papers if p.download_status == 'failed');
        manual = sum(1 for p in papers if p.download_status == 'manual_required');

        total_size = 0;
        for paper in papers:
            if paper.local_path and os.path.exists(paper.local_path):
                try:
                    total_size += os.path.getsize(paper.local_path);
                except Exception:
                    pass;

        size_mb = total_size / (1024 * 1024);

        summary = f'''
📚 文献下载报告
==============
总计: {len(papers)} 篇
✅ 成功: {success} 篇
❌ 失败: {failed} 篇
⚠️ 手动获取: {manual} 篇
📁 总大小: {size_mb:.2f} MB
''';
        return summary.strip();
