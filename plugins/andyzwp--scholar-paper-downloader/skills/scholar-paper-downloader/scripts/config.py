# -*- coding: utf-8 -*-
"""
配置管理模块

定义下载参数、文件路径、命名模板等配置
"""

from dataclasses import dataclass, field;
from typing import Optional;
import os;


@dataclass
class DownloadConfig:
    """下载配置类"""

    # 输出目录
    output_dir: str = './papers';

    # 搜索结果数量限制
    max_results: int = 10;

    # 并发下载数
    max_workers: int = 3;

    # 文件命名模板
    # 可用占位符: {first_author}, {year}, {title_abbr}, {title}, {authors}, {id}
    naming_template: str = '{first_author}_{year}_{title_abbr}';

    # 重试次数
    retry_times: int = 3;

    # 超时时间(秒)
    timeout: int = 30;

    # 是否包含摘要
    include_abstract: bool = True;

    # PDF来源优先级
    source_priority: list = field(default_factory=lambda: ['arxiv', 'semantic_scholar']);

    # 是否创建索引文件
    generate_index: bool = True;

    # 索引格式: 'markdown', 'json', 或 ['markdown', 'json']
    index_format: list = field(default_factory=lambda: ['markdown', 'json']);

    # 日志级别: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    log_level: str = 'INFO';

    def __post_init__(self):
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True);

    def get_naming_template(self) -> str:
        """获取文件命名模板"""
        return self.naming_template;

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'output_dir': self.output_dir,
            'max_results': self.max_results,
            'max_workers': self.max_workers,
            'naming_template': self.naming_template,
            'retry_times': self.retry_times,
            'timeout': self.timeout,
            'include_abstract': self.include_abstract,
            'source_priority': self.source_priority,
            'generate_index': self.generate_index,
            'index_format': self.index_format,
            'log_level': self.log_level,
        };


@dataclass
class PaperInfo:
    """论文信息数据类"""

    # 论文ID
    paper_id: str;

    # 标题
    title: str;

    # 作者列表
    authors: list = field(default_factory=list);

    # 发表日期
    published_date: Optional[str] = None;

    # 摘要
    abstract: Optional[str] = None;

    # PDF URL
    pdf_url: Optional[str] = None;

    # 论文DOI
    doi: Optional[str] = None;

    # 论文URL
    paper_url: Optional[str] = None;

    # 关键词
    keywords: list = field(default_factory=list);

    # 期刊/会议
    journal: Optional[str] = None;

    # 下载状态: 'success', 'failed', 'manual_required'
    download_status: str = 'pending';

    # 本地文件路径
    local_path: Optional[str] = None;

    # 来源: 'arxiv', 'semantic_scholar', etc.
    source: str = 'arxiv';

    # 备注
    comment: Optional[str] = None;

    def get_first_author(self) -> str:
        """获取第一作者"""
        if self.authors:
            return self.authors[0].split()[-1];  # 取姓氏
        return 'unknown';

    def get_year(self) -> str:
        """获取发表年份"""
        if self.published_date:
            return self.published_date[:4];
        return 'unknown';

    def get_title_abbr(self, max_length: int = 30) -> str:
        """获取缩略标题"""
        if not self.title:
            return 'untitled';
        # 移除非字母数字字符,取前max_length个字符
        abbr = ''.join(c if c.isalnum() else '_' for c in self.title);
        abbr = abbr[:max_length].strip('_');
        return abbr or 'untitled';

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': self.authors,
            'published_date': self.published_date,
            'abstract': self.abstract,
            'pdf_url': self.pdf_url,
            'doi': self.doi,
            'paper_url': self.paper_url,
            'keywords': self.keywords,
            'journal': self.journal,
            'download_status': self.download_status,
            'local_path': self.local_path,
            'source': self.source,
            'comment': self.comment,
        };
