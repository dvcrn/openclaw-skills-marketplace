# -*- coding: utf-8 -*-
"""
隐私检查工具
发布前必须运行，确保不包含任何真实隐私信息
"""

import os
import re
from pathlib import Path

# 禁止的关键词（隐私红线）
FORBIDDEN_PATTERNS = [
    r'gaowf@163\.com',
    r'1776480440',
    r'sukmgit.*@.*\.com',
    r'老高',
    r'高万峰',
    r'open\.feishu\.cn.*hook.*[a-zA-Z0-9]{32}',  # 真实飞书 webhook
]

# 允许的占位符
ALLOWED_PLACEHOLDERS = [
    'YOUR_NAME',
    'YOUR_EMAIL',
    'YOUR_PASSWORD',
    'YOUR_SMTP_HOST',
    'YOUR_WEBHOOK_URL',
    'YOUR_DEFAULT_PATH',
]


def check_file(file_path: Path) -> tuple:
    """检查单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查禁止的关键词
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    return False, f"发现隐私信息：{pattern}"
            
            # 检查是否是配置文件
            if file_path.name.endswith('.json'):
                # 确保是模板文件（包含占位符）
                if 'YOUR_' not in content and file_path.name != 'config.json':
                    return False, "配置文件应使用占位符（YOUR_*）"
            
            return True, "通过"
    except Exception as e:
        return False, f"无法读取文件：{e}"


def check_project(project_path: str) -> bool:
    """检查整个项目"""
    print("=" * 60)
    print("隐私安全检查")
    print("=" * 60)
    print()
    
    project_path = Path(project_path)
    issues = []
    checked_files = 0
    
    for root, dirs, files in os.walk(project_path):
        # 跳过隐藏目录和依赖目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for file in files:
            # 只检查代码和配置文件
            if not file.endswith(('.py', '.json', '.md', '.txt')):
                continue
            
            file_path = Path(root) / file
            
            # 跳过检查工具本身
            if file_path.name == 'check_privacy.py':
                continue
            
            checked_files += 1
            passed, msg = check_file(file_path)
            
            if not passed:
                issues.append(f"[FAIL] {file_path.relative_to(project_path)}: {msg}")
            else:
                print(f"[OK] {file_path.relative_to(project_path)}: {msg}")
    
    print()
    print("=" * 60)
    print(f"检查完成：共检查 {checked_files} 个文件")
    print("=" * 60)
    
    if issues:
        print()
        print("[FAIL] Found issues:")
        for issue in issues:
            print(issue)
        print()
        print("[FAIL] Privacy check failed. DO NOT publish!")
        return False
    else:
        print()
        print("[OK] Privacy check passed. Ready to publish!")
        return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python check_privacy.py <项目路径>")
        print("示例：python check_privacy.py D:\\OpenClawDocs\\releases\\enterprise-automation-v1.0-publish")
        sys.exit(1)
    
    project_path = sys.argv[1]
    success = check_project(project_path)
    sys.exit(0 if success else 1)
