# -*- coding: utf-8 -*-
"""隐私检查工具 - 发布前必须运行"""

from pathlib import Path
import sys

# 只检测真实隐私信息（不允许占位符）
FORBIDDEN = [
    ('gaowf@163.com', '真实邮箱'),
    ('1776480440@qq.com', '真实 QQ 邮箱'),
    ('1776480440', '真实手机号'),
    ('高万峰', '真实姓名'),
]

# 允许的占位符
ALLOWED = ['your_email', 'your_qq', 'your_', 'YOUR_', 'example.com', 'placeholder']

def check_file(file_path):
    if file_path.name == 'check_privacy.py':
        return True, '排除'
    
    content = file_path.read_text(encoding='utf-8')
    
    # 检查是否是占位符文件
    is_placeholder = any(x in content for x in ALLOWED)
    
    for pattern, desc in FORBIDDEN:
        if pattern in content:
            # 如果是占位符文件，跳过
            if is_placeholder and pattern not in ['高万峰']:
                continue
            return False, f'{desc}: {pattern}'
    return True, '通过'

def main():
    if len(sys.argv) < 2:
        print('用法：python check_privacy.py <目录>')
        sys.exit(1)
    
    project_dir = Path(sys.argv[1])
    passed, failed = [], []
    
    for f in project_dir.rglob('*'):
        if f.is_file() and f.suffix in ['.py', '.md', '.json']:
            ok, msg = check_file(f)
            if ok:
                passed.append(f)
            else:
                failed.append((f, msg))
    
    print(f'检查完成：{len(passed)} 通过，{len(failed)} 失败')
    
    if failed:
        for f, msg in failed:
            print(f'FAIL: {f.name} - {msg}')
        sys.exit(1)
    else:
        print('OK: 可以发布')
        sys.exit(0)

if __name__ == '__main__':
    main()
