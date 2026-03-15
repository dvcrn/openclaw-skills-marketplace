#!/usr/bin/env python3
"""
复杂度分析器（O(n²) 及以上预警）
"""

import re
from pathlib import Path


class ComplexityAnalyzer:
    """检测算法复杂度问题"""
    
    def __init__(self):
        self.issues = []
        
    def scan_file(self, file_path: Path) -> list:
        """扫描单个文件"""
        issues = []
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except:
            return issues
        
        # 复杂度计数
        for_loop_count = 0
        nested_loop_depth = 0
        max_depth = 0
        
        for line_num, line in enumerate(lines, 1):
            # 计算缩进层级
            indent = len(line) - len(line.lstrip())
            if indent > max_depth:
                max_depth = indent
            
            # 统计 for 循环
            if re.search(r"\bfor\b", line):
                for_loop_count += 1
            
            # 检测嵌套循环模式
            nested_patterns = [
                r"\bfor\b.*\bfor\b",
                r"\bwhile\b.*\bwhile\b",
                r"\bfor\b.*\bwhile\b",
                r"\bwhile\b.*\bfor\b",
            ]
            for pattern in nested_patterns:
                if re.search(pattern, line):
                    issues.append({
                        "type": "NESTED_LOOP",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"检测到嵌套循环，可能是 O(n²) 复杂度",
                        "severity": "medium"
                    })
        
        # 深度检查
        if max_depth >= 4:
            issues.append({
                "type": "EXCESSIVE_NESTING",
                "file": str(file_path),
                "line": 1,
                "message": f"代码嵌套深度达到 {max_depth//4} 层，建议重构",
                "severity": "low"
            })
        
        return issues
    
    def scan_directory(self, dir_path: Path) -> list:
        """扫描目录"""
        all_issues = []
        for file in dir_path.rglob("*"):
            if file.is_file():
                suffix = file.suffix.lower()
                if suffix in [".py", ".js", ".ts", ".java", ".c", ".cpp", ".go"]:
                    issues = self.scan_file(file)
                    all_issues.extend(issues)
        
        # 去重
        seen = set()
        unique_issues = []
        for issue in all_issues:
            key = (issue["file"], issue["line"], issue["type"])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues
