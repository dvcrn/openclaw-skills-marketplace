#!/usr/bin/env python3
"""
路径遍历检测器
"""

import os
import re
from pathlib import Path


class PathTraversalDetector:
    """检测路径遍历（Directory Traversal）风险"""
    
    # 危险模式
    TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"\.\.\.",
        r"%2e%2e%2f",  # URL encoded
        r"%2e%2e/",
        r"\.\.%2f",
        r"%252e%252e",
        r"%c0%ae",  # UTF-8 encoded
    ]
    
    # 敏感文件路径
    SENSITIVE_PATHS = [
        "/etc/passwd",
        "/etc/shadow",
        "config.json",
        ".env",
        "id_rsa",
        "id_rsa.pub",
        "credentials.json",
        "service-account.json",
    ]
    
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
            # 检查路径遍历模式
            for pattern in self.TRAVERSAL_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "type": "PATH_TRAVERSAL",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"存在路径遍历风险: {line.strip()[:60]}...",
                        "severity": "high"
                    })
            
            # 检查敏感文件访问
            for path in self.SENSITIVE_PATHS:
                if path in line:
                    issues.append({
                        "type": "SENSITIVE_FILE_ACCESS",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"可能访问敏感文件: {path}",
                        "severity": "high"
                    })
        
        return issues
    
    def scan_directory(self, dir_path: Path) -> list:
        """扫描目录"""
        all_issues = []
        for file in dir_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".js", ".ts", ".go", ".java", ".php"]:
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
