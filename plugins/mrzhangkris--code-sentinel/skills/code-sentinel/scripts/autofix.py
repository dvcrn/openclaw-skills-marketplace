#!/usr/bin/env python3
"""
自动修复入口
"""

import sys
from pathlib import Path

# 添加父目录到 sys.path
PARENT_DIR = Path(__file__).parent.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from autofix.core import autofix_file


def autofix_directory(dir_path: Path) -> list:
    """自动修复目录下的所有文件"""
    all_fixes = []
    
    for file in dir_path.rglob("*"):
        if file.is_file():
            suffix = file.suffix.lower()
            # 只处理代码文件
            if suffix in [".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".svelte"]:
                fixes = autofix_file(file)
                all_fixes.extend(fixes)
    
    return all_fixes


def main():
    if len(sys.argv) < 2:
        print("使用: python3 autofix.py <目标目录或文件>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if not target.exists():
        print(f"❌ 错误: 目标不存在 - {target}")
        sys.exit(1)
    
    print(f"🔧 开始自动修复: {target}")
    
    if target.is_file():
        fixes = autofix_file(target)
    else:
        fixes = autofix_directory(target)
    
    # 统计
    print(f"\n🔧 修复完成")
    print(f"修复建议: {len([f for f in fixes if f['type'] == 'FIX_SUGGESTED'])}")
    print(f"文件修改: {len([f for f in fixes if f['type'] == 'FILE_MODIFIED'])}")


if __name__ == "__main__":
    main()
