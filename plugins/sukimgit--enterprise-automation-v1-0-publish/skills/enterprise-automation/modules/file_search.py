# -*- coding: utf-8 -*-
"""
文件搜索模块
"""

import os
from pathlib import Path
from typing import List, Optional


def search_files(
    search_path: str,
    keyword: str,
    file_type: Optional[str] = None,
    max_results: int = 10
) -> List[Path]:
    """搜索文件
    
    Args:
        search_path: 搜索路径
        keyword: 搜索关键词
        file_type: 文件类型（如".pdf"、".docx"）
        max_results: 最大返回结果数
    
    Returns:
        文件路径列表
    """
    results = []
    search_path = Path(search_path)
    
    if not search_path.exists():
        raise FileNotFoundError(f"路径不存在：{search_path}")
    
    for root, dirs, files in os.walk(search_path):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
            
            # 文件类型过滤
            if file_type and not file.lower().endswith(file_type.lower()):
                continue
            
            # 模糊匹配
            if keyword in file:
                results.append(Path(root) / file)
            
            if len(results) >= max_results:
                return results
    
    return results


def print_results(results: List[Path]):
    """打印搜索结果"""
    if not results:
        print("未找到文件")
        return
    
    print(f"\n找到 {len(results)} 个文件:\n")
    print(f"{'序号':<6} {'文件名':<60} {'大小':<12} {'修改时间':<20}")
    print("-" * 100)
    
    for i, file_path in enumerate(results, 1):
        try:
            stat = file_path.stat()
            size_kb = stat.st_size / 1024
            if size_kb > 1024:
                size_str = f"{size_kb/1024:.1f} MB"
            else:
                size_str = f"{size_kb:.0f} KB"
            
            from datetime import datetime
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            
            # 文件名超过 60 字符截断
            file_name = file_path.name
            if len(file_name) > 60:
                file_name = file_name[:57] + "..."
            
            print(f"{i:<6} {file_name:<60} {size_str:<12} {mtime:<20}")
        except Exception as e:
            print(f"{i:<6} {file_path.name:<60} [读取错误]")
