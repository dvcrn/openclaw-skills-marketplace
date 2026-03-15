#!/usr/bin/env python3
"""
命令注入检测器
"""

import re
from pathlib import Path


class CommandInjectionDetector:
    """检测命令注入风险"""
    
    # 危险函数（按语言分类）
    PYTHON_DANGER = [
        "os.system(",
        "os.popen(",
        "subprocess.call(",
        "subprocess.run(",
        "eval(",
        "exec(",
        "compile(",
    ]
    
    NODE_DANGER = [
        "child_process.exec(",
        "child_process.spawn(",
        "eval(",
        "Function(",
    ]
    
    PHP_DANGER = [
        "exec(",
        "shell_exec(",
        "system(",
        "passthru(",
        "proc_open(",
        "popen(",
    ]
    
    # 命令连接符
    CMD_CONNECTORS = [";", "|", "&", "||", "&&", "`", "$(."]
    
    def __init__(self):
        self.issues = []
        
    def detect_language(self, file_path: Path) -> str:
        """检测文件语言"""
        suffix = file_path.suffix.lower()
        mappings = {
            ".py": "python",
            ".js": "node",
            ".ts": "node",
            ".php": "php",
            ".sh": "shell",
            ".go": "go",
            ".rb": "ruby",
        }
        return mappings.get(suffix, "unknown")
    
    def scan_file(self, file_path: Path) -> list:
        """扫描单个文件"""
        issues = []
        try:
            content = file_path.read_text(encoding="utf-8")
        except:
            return issues
        
        lang = self.detect_language(file_path)
        danger_funcs = []
        
        if lang == "python":
            danger_funcs = self.PYTHON_DANGER
        elif lang in ["node", "javascript", "typescript"]:
            danger_funcs = self.NODE_DANGER
        elif lang == "php":
            danger_funcs = self.PHP_DANGER
        
        for line_num, line in enumerate(content.splitlines(), 1):
            # 检查危险函数
            for func in danger_funcs:
                if func in line:
                    issues.append({
                        "type": "COMMAND_INJECTION",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"存在命令注入风险: {func} 可能被利用",
                        "severity": "high"
                    })
            
            # 检查命令连接符
            for connector in self.CMD_CONNECTORS:
                if connector in line:
                    issues.append({
                        "type": "COMMAND_CONNECTOR",
                        "file": str(file_path),
                        "line": line_num,
                        "message": f"存在命令注入风险: {connector} 可能用于命令拼接",
                        "severity": "medium"
                    })
        
        return issues
    
    def scan_directory(self, dir_path: Path) -> list:
        """扫描目录"""
        all_issues = []
        for file in dir_path.rglob("*"):
            if file.is_file():
                suffix = file.suffix.lower()
                if suffix in [".py", ".js", ".ts", ".php", ".sh", ".go", ".rb"]:
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
