#!/usr/bin/env python3
"""
内存泄漏检测器
"""

import re
from pathlib import Path


class MemoryLeakDetector:
    """检测内存泄漏风险"""
    
    # JavaScript/TypeScript 问题模式
    JS_LEAK_PATTERNS = [
        r"setInterval\s*\(",  # 未清除的定时器
        r"setTimeout\s*\([^,]+,\s*0",  # 延迟 0 的定时器
        r"addEventListener\s*\([^)]+\)\s*;\s*$",  # 未移除的事件监听器
        r"new\s+WebSocket\s*\(",  # 未关闭的 WebSocket
        r"\.addEventListener\s*\(\s*['\"]scroll['\"]",  # 滚动事件未节流
    ]
    
    # Python 问题模式
    PY_LEAK_PATTERNS = [
        r"open\([^)]+\)\s*:\s*$",  # 文件未关闭
        r"Connection\s*\(",  # 数据库连接未关闭
        r"socket\.socket\s*\(",  # Socket 未关闭
        r"pool\s*=\s*\[\s*\]",  # 无限增长的列表
    ]
    
    # 无限循环检测
    INFINITE_LOOPS = [
        r"while\s*\(true\)",
        r"while\s*\(1\)",
        r"for\s*\(\s*;\s*;\s*\)",
        r"while\s+\([^\)]+\)\s*:\s*$",  # Python 无限循环
    ]
    
    def __init__(self):
        self.issues = []
        
    def detect_language(self, file_path: Path) -> str:
        """检测文件语言"""
        suffix = file_path.suffix.lower()
        if suffix == ".py":
            return "python"
        elif suffix in [".js", ".ts", ".jsx", ".tsx"]:
            return "javascript"
        else:
            return "unknown"
    
    def scan_file(self, file_path: Path) -> list:
        """扫描单个文件"""
        issues = []
        try:
            content = file_path.read_text(encoding="utf-8")
        except:
            return issues
        
        lang = self.detect_language(file_path)
        patterns = self.JS_LEAK_PATTERNS if lang == "javascript" else self.PY_LEAK_PATTERNS
        
        for line_num, line in enumerate(content.splitlines(), 1):
            # 检查内存泄漏模式
            for pattern in patterns:
                if re.search(pattern, line):
                    issues.append({
                        "type": "MEMORY_LEAK",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"可能存在内存泄漏: {line.strip()[:60]}...",
                        "severity": "medium"
                    })
            
            # 检查无限循环
            for loop_pattern in self.INFINITE_LOOPS:
                if re.search(loop_pattern, line):
                    issues.append({
                        "type": "INFINITE_LOOP",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"可能存在无限循环: {line.strip()[:60]}...",
                        "severity": "high"
                    })
        
        return issues
    
    def scan_directory(self, dir_path: Path) -> list:
        """扫描目录"""
        all_issues = []
        for file in dir_path.rglob("*"):
            if file.is_file():
                suffix = file.suffix.lower()
                if suffix in [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp"]:
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
