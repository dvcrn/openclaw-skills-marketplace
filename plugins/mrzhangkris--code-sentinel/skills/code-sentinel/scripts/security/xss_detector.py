#!/usr/bin/env python3
"""
XSS 检测器
"""

import re
from pathlib import Path


class XSSDetector:
    """检测 XSS（跨站脚本）风险"""
    
    # 危险 HTML 事件属性
    EVENT_ATTRIBUTES = [
        "onload", "onclick", "onerror", "onmouseover", "onfocus",
        "onblur", "onsubmit", "onchange", "onkeydown", "onkeyup",
        "ondblclick", "oncontextmenu", "ondrag", "ondrop",
        "onresize", "onscroll", "onunload", "onmouseout",
    ]
    
    # 危险标签
    DANGEROUS_TAGS = ["script", "iframe", "img", "object", "embed", "link"]
    
    # 危险函数
    DANGEROUS_FUNCTIONS = [
        "eval(", "document.write", "textContent", "outerHTML",
        "document.location", "window.open", "setTimeout(",
        "setInterval(", "Function(", "atob(", "btoa(",
    ]
    
    # URL 协议白名单
    SAFE_PROTOCOLS = ["http://", "https://", "/"]
    
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
            # 检查危险事件属性
            for attr in self.EVENT_ATTRIBUTES:
                if attr in line:
                    issues.append({
                        "type": "XSS_EVENT_HANDLER",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"存在 XSS 风险：{attr} 事件处理器",
                        "severity": "high"
                    })
            
            # 检查危险标签
            for tag in self.DANGEROUS_TAGS:
                pattern = rf"<{tag}[^>]*>"
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "type": "XSS_DANGEROUS_TAG",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"存在 XSS 风险：不安全的 <{tag}> 标签",
                        "severity": "high"
                    })
            
            # 检查危险函数
            for func in self.DANGEROUS_FUNCTIONS:
                if func in line:
                    issues.append({
                        "type": "XSS_DANGEROUS_FUNCTION",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"存在 XSS 风险：{func} 可能导致 XSS",
                        "severity": "high"
                    })
        
        return issues
    
    def scan_directory(self, dir_path: Path) -> list:
        """扫描目录"""
        all_issues = []
        for file in dir_path.rglob("*"):
            if file.is_file() and file.suffix in [".html", ".js", ".ts", ".vue", ".jsx", ".tsx"]:
                issues = self.scan_file(file)
                all_issues.extend(issues)
        
        # 重复项去重
        seen = set()
        unique_issues = []
        for issue in all_issues:
            key = (issue["file"], issue["line"], issue["type"])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues