#!/usr/bin/env python3
"""
FIS 3.1 Lite - 工卡图片生成示例
适用于 WhatsApp/Feishu 等不支持复杂排版的 Channel
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

def main():
    print("🎫 FIS 3.1 Lite - 工卡图片生成")
    print("=" * 50)
    
    manager = SubAgentLifecycleManager("cybermao")
    
    # 场景1: 创建并生成单张工卡
    print("\n📋 场景1: 创建 Worker 并生成工卡图片")
    print("-" * 40)
    
    worker = manager.spawn(
        name="小毛-Worker-001",
        role=SubAgentRole.WORKER,
        task_description="实现 PTVF 滤波算法",
        timeout_minutes=120
    )
    manager.activate(worker['employee_id'])
    
    # 生成工卡图片
    image_path = manager.generate_badge_image(worker['employee_id'])
    print(f"✅ 工号: {worker['employee_id']}")
    print(f"✅ 工卡图片: {image_path}")
    
    # 场景2: 批量生成多张工卡（平铺布局）
    print("\n📋 场景2: 批量生成工卡图片（避免消息轰炸）")
    print("-" * 40)
    
    # 创建更多子代理
    reviewer = manager.spawn(
        name="老毛-Reviewer-001",
        role=SubAgentRole.REVIEWER,
        task_description="审查 PTVF 实现",
        timeout_minutes=60
    )
    manager.activate(reviewer['employee_id'])
    
    researcher = manager.spawn(
        name="研毛-Researcher-001",
        role=SubAgentRole.RESEARCHER,
        task_description="调研最新滤波算法文献",
        timeout_minutes=90
    )
    manager.activate(researcher['employee_id'])
    
    # 批量生成 - 3张工卡平铺到一张图片
    multi_path = manager.generate_multi_badge_image([
        worker['employee_id'],
        reviewer['employee_id'],
        researcher['employee_id']
    ])
    
    print(f"✅ 批量工卡图片: {multi_path}")
    print(f"   包含: Worker + Reviewer + Researcher (3合1)")
    
    # 场景3: 获取所有活跃子代理并生成总览
    print("\n📋 场景3: 生成团队总览图片")
    print("-" * 40)
    
    active = manager.list_active()
    if len(active) > 1:
        # 最多4张平铺 (2x2 网格)
        team_image = manager.generate_multi_badge_image()
        print(f"✅ 团队总览: {team_image}")
        print(f"   包含 {len(active)} 个活跃子代理")
    
    # 输出使用建议
    print("\n" + "=" * 50)
    print("💡 使用建议")
    print("=" * 50)
    print("""
在 WhatsApp/Feishu 发送工卡:

1. 单张工卡 (1对1沟通):
   image_path = manager.generate_badge_image(card_id)
   # 发送 image_path

2. 批量工卡 (群组/广播):
   multi_path = manager.generate_multi_badge_image([id1, id2, id3])
   # 发送 multi_path (避免多条消息)

3. 团队总览:
   team_path = manager.generate_multi_badge_image()
   # 发送 team_path (所有活跃代理一览)

图片位置: ~/.openclaw/output/badges/
""")

if __name__ == "__main__":
    main()
