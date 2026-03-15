#!/usr/bin/env python3
"""
多语言检测器聚合器
支持: Python, JavaScript/TypeScript, Java, Go, Rust, C/C++
"""

from pathlib import Path
from typing import List, Dict


class LanguageDetector:
    """语言检测器抽象基类"""
    
    def __init__(self):
        self.issues = []
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """扫描文件"""
        raise NotImplementedError
    
    def scan_directory(self, dir_path: Path) -> List[Dict]:
        """扫描目录"""
        all_issues = []
        for file in dir_path.rglob("*"):
            if file.is_file() and self._is_language_file(file):
                issues = self.scan_file(file)
                all_issues.extend(issues)
        return all_issues
    
    def _is_language_file(self, file_path: Path) -> bool:
        """是否为本语言文件"""
        raise NotImplementedError


class JavaDetector(LanguageDetector):
    """Java 检测器"""
    
    def _is_language_file(self, file_path: Path) -> bool:
        return file_path.suffix == ".java"
    
    def scan_file(self, file_path: Path):
        # TODO: 实现 Java 专属检测
        return []


class GoDetector(LanguageDetector):
    """Go 检测器"""
    
    def _is_language_file(self, file_path: Path) -> bool:
        return file_path.suffix == ".go"
    
    def scan_file(self, file_path: Path):
        # TODO: 实现 Go 专属检测
        return []


class RustDetector(LanguageDetector):
    """Rust 检测器"""
    
    def _is_language_file(self, file_path: Path) -> bool:
        return file_path.suffix == ".rs"
    
    def scan_file(self, file_path: Path):
        # TODO: 实现 Rust 专属检测
        return []


def get_language_detector(file_path: Path):
    """获取对应语言的检测器"""
    suffix = file_path.suffix.lower()
    
    detectors = {
        ".py": "py",
        ".js": "js",
        ".ts": "js",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "cpp",
    }
    
    return detectors.get(suffix, None)
