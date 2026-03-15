#!/usr/bin/env python3
"""
SQL注入检测器
"""

import re
from pathlib import Path


class SQLInjectionDetector:
    """检测 SQL 注入风险"""
    
    # 关键词模式
    SQL_KEYWORDS = [
        r"SELECT\s+.*\s+FROM",
        r"INSERT\s+INTO",
        r"DELETE\s+FROM",
        r"UPDATE\s+.*\s+SET",
        r"DROP\s+TABLE",
        r"UNION\s+SELECT",
        r"--\s*$",
        r"/\*.*\*/",
    ]
    
    # 危险字符
    DANGEROUS_CHARS = ["'", "\"", ";", "/*", "*/", "--", "#"]
    
    def __init__(self):
        self.issues = []
        
    def scan_file(self, file_path: Path) -> list:
        """扫描单个文件"""
        issues = []
        try:
            content = file_path.read_text(encoding="utf-8")
        except:
            return issues
        
        for line_num, line in enumerate(content.splitlines(), 1):
            # 检查 SQL 关键词
            for pattern in self.SQL_KEYWORDS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "type": "SQL_INJECTION_RISK",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"可能包含 SQL 注入风险: {line.strip()[:60]}...",
                        "severity": "high"
                    })
            
            # 检查危险字符
            for char in self.DANGEROUS_CHARS:
                if char in line and not line.strip().startswith("#"):
                    issues.append({
                        "type": "DANGEROUS_CHAR",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"包含危险字符 '{char}'，可能用于 SQL 注入",
                        "severity": "medium"
                    })
        
        return issues
    
    def scan_directory(self, dir_path: Path) -> list:
        """扫描目录"""
        all_issues = []
        for file in dir_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".js", ".ts", ".sql"]:
                issues = self.scan_file(file)
                all_issues.extend(issues)
        return all_issues
