#!/usr/bin/env python3
"""打包 skill 为 .skill 文件"""
import sys
import zipfile
from pathlib import Path

def validate_skill(skill_path):
    """验证 skill 目录结构"""
    required = ['SKILL.md']
    for f in required:
        if not (skill_path / f).exists():
            print(f"❌ 缺少必需文件：{f}")
            return False
    
    # 检查 SKILL.md 前缀
    skilmd = skill_path / 'SKILL.md'
    content = skilmd.read_text(encoding='utf-8')
    if not content.startswith('---'):
        print("❌ SKILL.md 缺少 YAML 前缀")
        return False
    if 'name:' not in content or 'description:' not in content:
        print("❌ SKILL.md 缺少 name 或 description")
        return False
    
    print("✅ 验证通过")
    return True

def package_skill(skill_path, output_dir=None):
    """打包 skill"""
    skill_path = Path(skill_path)
    
    if not validate_skill(skill_path):
        return False
    
    # 获取 skill 名称（改进的 YAML 解析）
    content = (skill_path / 'SKILL.md').read_text(encoding='utf-8')
    name = None
    description = None
    
    # 提取 YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            for line in frontmatter.split('\n'):
                line = line.strip()
                if line.startswith('name:'):
                    name = line.split(':', 1)[1].strip().strip('"\'')
                elif line.startswith('description:'):
                    description = line.split(':', 1)[1].strip().strip('"\'')
    
    if not name:
        print("❌ 无法获取 skill 名称")
        return False
    
    if not description:
        print("⚠️ 警告：缺少 description")
    
    # 输出文件
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = skill_path.parent
    
    output_file = output_dir / f"{name}.skill"
    
    # 打包
    print(f"📦 打包：{skill_path} -> {output_file}")
    
    # 排除的目录和文件
    exclude_patterns = {'__pycache__', 'logs', 'state', '.git', '.vscode', '.idea'}
    exclude_extensions = {'.log', '.pyc', '.pyo', '.swp', '.swo'}
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            arcname = file_path.relative_to(skill_path)
            arcname_str = str(arcname)
            
            # 跳过排除的目录
            if any(pattern in arcname_str for pattern in exclude_patterns):
                continue
            
            # 跳过排除的扩展名
            if file_path.suffix in exclude_extensions:
                continue
            
            # 跳过隐藏文件
            if file_path.name.startswith('.'):
                continue
            
            zf.write(file_path, arcname)
            print(f"  + {arcname}")
    
    print(f"✅ 完成：{output_file.name}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：package_skill.py <skill-path> [output-dir]")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not package_skill(skill_path, output_dir):
        sys.exit(1)
