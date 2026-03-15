# -*- coding: utf-8 -*-
"""
企业自动化助手 - 文件搜索工具
支持中文路径、精准/模糊匹配、文件类型过滤
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict
import json


def search_files(
    search_path: str,
    keyword: str,
    file_type: Optional[str] = None,
    max_results: int = 20,
    fuzzy_match: bool = True
) -> List[Dict]:
    """搜索文件
    
    Args:
        search_path: 搜索路径
        keyword: 关键词
        file_type: 文件类型过滤（如 .pdf）
        max_results: 最大结果数
        fuzzy_match: 是否模糊匹配
    
    Returns:
        文件信息列表
    """
    results = []
    search_path = Path(search_path)
    
    if not search_path.exists():
        raise FileNotFoundError(f"路径不存在：{search_path}")
    
    print(f"[INFO] 搜索：{search_path}")
    print(f"       关键词：{keyword}")
    print(f"       类型：{file_type if file_type else '所有'}")
    
    for root, dirs, files in os.walk(search_path):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
            
            # 文件类型过滤
            if file_type and not file.lower().endswith(file_type.lower()):
                continue
            
            # 匹配关键词
            match = False
            if fuzzy_match:
                match = keyword.lower() in file.lower()
            else:
                match = keyword.lower() == file.lower()
            
            if match:
                try:
                    file_path = Path(root) / file
                    stat = file_path.stat()
                    
                    results.append({
                        'path': str(file_path),
                        'name': file,
                        'size': stat.st_size,
                        'size_str': format_size(stat.st_size),
                        'modified': stat.st_mtime,
                        'modified_str': format_time(stat.st_mtime)
                    })
                except Exception as e:
                    print(f"[WARN] 无法读取文件信息：{file_path} - {e}")
            
            if len(results) >= max_results:
                return results
    
    return results


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_time(timestamp: float) -> str:
    """格式化时间"""
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M')


def print_results(results: List[Dict]):
    """打印搜索结果"""
    if not results:
        print("[WARN] 未找到文件")
        return
    
    print(f"\n[OK] 找到 {len(results)} 个文件：\n")
    
    for i, file_info in enumerate(results, 1):
        print(f"{i:2d}. {file_info['name']}")
        print(f"    路径：{file_info['path']}")
        print(f"    大小：{file_info['size_str']}")
        print(f"    修改：{file_info['modified_str']}")
        print()


def save_results(results: List[Dict], output_file: str):
    """保存结果到 JSON 文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 结果已保存到：{output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：python file_searcher.py <搜索路径> <关键词> [文件类型] [最大数量]")
        print("示例：python file_searcher.py \"D:\\工作\" \"合同\" .pdf 10")
        sys.exit(1)
    
    search_path = sys.argv[1]
    keyword = sys.argv[2]
    file_type = sys.argv[3] if len(sys.argv) > 3 else None
    max_results = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    
    try:
        results = search_files(search_path, keyword, file_type, max_results)
        print_results(results)
    except Exception as e:
        print(f"[ERROR] 搜索失败：{e}")
        sys.exit(1)
