#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小红书笔记生成脚本
整合蒙语 AI 和 xhs-note-creator，自动生成蒙古语主题的小红书笔记

使用方法:
  python3 xhs-generator.py --topic "蒙语 AI" --output ./output/
"""

import os
import sys
import argparse
import subprocess
import json
from datetime import datetime


def create_markdown_content(topic, output_dir):
    """
    创建 Markdown 笔记内容
    
    Args:
        topic: 笔记主题
        output_dir: 输出目录
    
    Returns:
        Markdown 文件路径
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    md_file = os.path.join(output_dir, f'{topic}_{timestamp}.md')
    
    # 创建 Markdown 内容
    content = f'''---
emoji: "🤖"
title: "{topic} - 蒙古语 AI"
subtitle: "传统蒙古文智能处理"
background: "professional.png"
logo: "logo-white.png"
---

# 🤖 {topic}

**ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ AI**

蒙古语智能助手，提供专业蒙语服务！

---

# 📝 核心功能

**ᠲᠣᠪᠴᠢᠶ᠎ᠠ ᠭᠦᠢᠴᠡᠳ:**

- 蒙汉智能翻译
- 传统文化问答
- 语音文字处理
- 蒙古文渲染

---

# 🎯 使用场景

**适合人群:**

1. 学习蒙古语的学生
2. 研究蒙古文化的学者
3. 需要蒙语翻译的用户
4. 对蒙古族文化感兴趣的人

---

# ⚡ 快速开始

**使用方法:**

```bash
# 翻译功能
node translate.js "ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨᠠ ᠤᠤ"

# 文化问答
node culture-qa.js "蒙古族有哪些传统节日？"
```

---

# 🌟 特色优势

**为什么选择蒙语 AI:**

- ✅ 专业准确的翻译
- ✅ 深厚的文化底蕴
- ✅ 便捷的使用方式
- ✅ 持续更新优化

---

# 📱 联系方式

**获取方式:**

微信小程序搜索「蒙语 AI」

或访问：
https://platform.mengguyu.cn

#蒙语 AI #传统蒙古文 #蒙古语翻译 #AI 翻译 #语言学习 #蒙古族文化
'''
    
    # 写入文件
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return md_file


def render_cards(md_file, output_dir):
    """
    渲染图片卡片
    
    Args:
        md_file: Markdown 文件路径
        output_dir: 输出目录
    """
    # 查找 xhs-note-creator 渲染脚本
    render_script = '/root/.openclaw/workspace/skills/xhs-note-creator/scripts/render_xhs.py'
    
    if not os.path.exists(render_script):
        print('⚠️  警告：未找到 xhs-note-creator 渲染脚本')
        print('   请先安装：clawhub install xhs-note-creator')
        return None
    
    # 执行渲染
    cmd = [
        'python3', render_script,
        md_file,
        '-m', 'separator',
        '-o', output_dir
    ]
    
    print(f'🎨 开始渲染卡片...')
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f'✅ 渲染完成！')
        print(result.stdout)
        return True
    else:
        print(f'❌ 渲染失败：{result.stderr}')
        return False


def main():
    parser = argparse.ArgumentParser(
        description='小红书笔记生成器 - 蒙语 AI 主题',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python3 xhs-generator.py --topic "蒙语 AI" --output ./output/
  python3 xhs-generator.py -t "蒙古语翻译" -o ./notes/

依赖:
  - xhs-note-creator (用于渲染卡片)
  - MENGGUYU_API_KEY (可选，用于生成自定义内容)
        '''
    )
    
    parser.add_argument('-t', '--topic', default='蒙语 AI',
                        help='笔记主题 默认：蒙语 AI')
    parser.add_argument('-o', '--output', default='./output',
                        help='输出目录 默认：./output')
    parser.add_argument('--no-render', action='store_true',
                        help='只生成 Markdown，不渲染图片')
    
    args = parser.parse_args()
    
    print(f'📝 开始生成笔记：{args.topic}')
    
    # 创建 Markdown 内容
    md_file = create_markdown_content(args.topic, args.output)
    print(f'✅ Markdown 已生成：{md_file}')
    
    # 渲染卡片
    if not args.no_render:
        render_cards(md_file, args.output)
    
    print(f'\n✨ 完成！笔记素材已保存到：{args.output}')


if __name__ == '__main__':
    main()
