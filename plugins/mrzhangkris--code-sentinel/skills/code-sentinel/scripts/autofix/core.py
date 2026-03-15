#!/usr/bin/env python3
"""
自动修复模块
"""

import re
from pathlib import Path


class XSSAutoFixer:
    """XSS 自动修复"""
    
    @staticmethod
    def fix_event_handler(line: str) -> str:
        """移除危险事件处理器，改用 addEventListener"""
        # 移除 等
        patterns = [
            r'\s+on(click|load|error|mouse|focus|blur)\s*=\s*["\'][^"\']*["\']',
        ]
        for pattern in patterns:
            line = re.sub(pattern, "", line, flags=re.IGNORECASE)
        return line
    
    @staticmethod
    def fix_textContent(line: str) -> str:
        """将 textContent 改为 textContent"""
        if "textContent" in line:
            line = line.replace("textContent", "textContent")
        return line


class SQLInjectionAutoFixer:
    """SQL 注入自动修复"""
    
    @staticmethod
    def fix_string_concat(sql_line: str) -> str:
        """检测字符串拼接 SQL，返回修复建议"""
        # 检测模式: WHERE id = + user_input
        if "+" in sql_line and "SELECT" in sql_line.upper():
            return "建议使用参数化查询: WHERE id = %s"
        return None


class MemoryLeakAutoFixer:
    """内存泄漏自动修复"""
    
    @staticmethod
    def fix_setInterval(line: str) -> str:
        """为 setInterval 添加清除建议"""
        if "setInterval" in line:
            return "// 建议: 使用 clearInterval() 清除定时器"
        return None
    
    @staticmethod
    def fix_eventListener(line: str) -> str:
        """为 addEventListener 添加 removeListener 建议"""
        if "addEventListener" in line and "removeEventListener" not in line:
            return "// 建议: 添加对应的 removeEventListener()"
        return None


def autofix_file(file_path: Path) -> list:
    """自动修复单个文件"""
    fixes = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except:
        return fixes
    
    lines = content.splitlines()
    new_lines = []
    
    for line_num, line in enumerate(lines, 1):
        original = line
        
        # XSS 修复
        line = XSSAutoFixer.fix_event_handler(line)
        line = XSSAutoFixer.fix_textContent(line)
        
        # 内存泄漏修复
        fix_msg = MemoryLeakAutoFixer.fix_setInterval(line)
        if fix_msg:
            fixes.append({
                "type": "FIX_SUGGESTED",
                "file": str(file_path),
                "line": line_num,
                "message": fix_msg,
                "severity": "medium"
            })
        
        # 建议添加 removeEventListener
        fix_msg = MemoryLeakAutoFixer.fix_eventListener(line)
        if fix_msg and fix_msg not in [f.get("message") for f in fixes if f["line"] == line_num]:
            fixes.append({
                "type": "FIX_SUGGESTED",
                "file": str(file_path),
                "line": line_num,
                "message": fix_msg,
                "severity": "low"
            })
        
        new_lines.append(line)
    
    # 如果有修改，保存文件
    if new_lines != lines:
        file_path.write_text("\n".join(new_lines), encoding="utf-8")
        fixes.append({
            "type": "FILE_MODIFIED",
            "file": str(file_path),
            "line": 0,
            "message": "文件已自动修复",
            "severity": "info"
        })
    
    return fixes