#!/usr/bin/env python3
"""
FIS Badge Generator Demo - 工卡图片生成示例
适用于即时通讯等不支持复杂排版的 Channel
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加 lib 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from badge_generator import BadgeGenerator, generate_badge_with_task, generate_multi_badge


def main():
    print("🎫 FIS Badge Generator Demo")
    print("=" * 50)
    
    # 场景1: 生成单张工卡
    print("\n📋 场景1: 生成单个 Worker 工卡")
    print("-" * 40)
    
    badge_path = generate_badge_with_task(
        agent_name="Worker-001",
        role="WORKER",
        task_desc="实现核心算法模块",
        task_requirements=[
            "1. 设计算法架构",
            "2. 实现核心功能",
            "3. 编写单元测试",
        ]
    )
    print(f"✅ 工卡已生成: {badge_path}")
    
    # 场景2: 批量生成多张工卡
    print("\n📋 场景2: 批量生成多张工卡（2x2 网格）")
    print("-" * 40)
    
    cards_data = [
        {
            'agent_name': 'Worker-001',
            'role': 'worker',
            'task_desc': '实现核心算法模块',
            'task_requirements': ['设计架构', '实现功能', '编写测试']
        },
        {
            'agent_name': 'Reviewer-001',
            'role': 'reviewer',
            'task_desc': '审查算法实现',
            'task_requirements': ['代码审查', '性能评估', '提出改进建议']
        },
        {
            'agent_name': 'Researcher-001',
            'role': 'researcher',
            'task_desc': '调研相关技术文献',
            'task_requirements': ['文献检索', '技术对比', '撰写报告']
        },
    ]
    
    multi_path = generate_multi_badge(cards_data, "team_badges.png")
    print(f"✅ 批量工卡已生成: {multi_path}")
    print(f"   包含: Worker + Reviewer + Researcher (3合1)")
    
    # 场景3: 直接使用 BadgeGenerator 类
    print("\n📋 场景3: 使用 BadgeGenerator 类自定义工卡")
    print("-" * 40)
    
    generator = BadgeGenerator()
    
    agent_data = {
        'name': 'Custom-Agent-001',
        'id': f'AGENT-{datetime.now().year}-{datetime.now().strftime("%m%d%H%M")}',
        'role': 'WORKER',
        'task_id': f'#TASK-{datetime.now().strftime("%m%d")}',
        'soul': '"Execute with precision"',
        'responsibilities': [
            "Complete assigned tasks",
            "Report progress promptly",
            "Follow best practices",
        ],
        'output_formats': 'MARKDOWN | JSON | TXT',
        'task_requirements': [
            "1. Analyze requirements",
            "2. Implement solution",
            "3. Document changes",
        ],
        'status': 'ACTIVE',
    }
    
    custom_path = generator.create_badge(agent_data, output_path="custom_badge.png")
    print(f"✅ 自定义工卡已生成: {custom_path}")
    
    # 输出使用建议
    print("\n" + "=" * 50)
    print("💡 使用建议")
    print("=" * 50)
    print("""
在即时通讯工具发送工卡:

1. 单张工卡:
   from badge_generator import generate_badge_with_task
   path = generate_badge_with_task(name, role, task, requirements)
   # 发送生成的图片路径

2. 批量工卡:
   from badge_generator import generate_multi_badge
   path = generate_multi_badge([card1, card2, card3], "team.png")
   # 发送生成的拼接图片

3. 自定义工卡:
   from badge_generator import BadgeGenerator
   generator = BadgeGenerator()
   path = generator.create_badge(agent_data_dict)

图片保存位置: ~/.openclaw/output/badges/
""")


if __name__ == "__main__":
    main()
