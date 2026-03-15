#!/usr/bin/env python3
"""
虾码 (ShrimpCode) 快速测试脚本
Quick Test Script for ShrimpCode
"""

import asyncio
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from agent_controller import AutonomousCodingController


async def test_minimal():
    """最小化测试 - 模拟模式"""
    print("="*60)
    print("🧪 虾码 (ShrimpCode) 最小化测试")
    print("="*60)
    
    # 创建控制器
    controller = AutonomousCodingController(
        project_name="test-quick",
        requirements="测试项目"
    )
    
    # 运行 (模拟模式，不实际调用 AI)
    result = await controller.run_full_cycle(max_iterations=2)
    
    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)
    print(f"状态：{result['status']}")
    print(f"完成：{result['completed']}/{result['total']} 个任务")
    print(f"进度：{result['percentage']}%")
    print("="*60)
    
    if result['status'] in ('completed', 'partial'):
        print("\n✅ 测试通过！自主编码 Agent 工作正常")
        return True
    else:
        print(f"\n❌ 测试失败：{result.get('message', '未知错误')}")
        return False


async def test_with_real_project():
    """真实项目测试 - 创建一个简单的 Todo 应用"""
    print("\n" + "="*60)
    print("🚀 真实项目测试 - Todo 应用")
    print("="*60)
    
    controller = AutonomousCodingController(
        project_name="todo-app-demo",
        requirements="创建一个简单的 Todo 应用，包含添加、删除、标记完成功能",
        workspace_dir="/tmp/auto-coding-projects"
    )
    
    # 只运行 3 次迭代作为演示
    result = await controller.run_full_cycle(max_iterations=3)
    
    print("\n" + "="*60)
    print("📊 项目生成结果")
    print("="*60)
    print(f"状态：{result['status']}")
    print(f"完成：{result['completed']}/{result['total']} 个任务")
    print(f"项目位置：{controller.project_dir}")
    print("="*60)
    
    # 检查生成的文件
    if controller.project_dir.exists():
        print("\n📁 生成的文件:")
        for file in controller.project_dir.glob("**/*"):
            if file.is_file():
                print(f"  - {file.relative_to(controller.project_dir)}")
    
    return result['status'] in ('completed', 'partial')


async def main():
    """主测试流程"""
    print("\n🎯 选择测试模式:\n")
    print("1. 最小化测试 (快速，模拟模式)")
    print("2. 真实项目测试 (较慢，创建实际文件)")
    print("3. 运行全部测试")
    print()
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("请输入选择 (1/2/3): ").strip()
    
    success = False
    
    if choice == "1":
        success = await test_minimal()
    elif choice == "2":
        success = await test_with_real_project()
    elif choice == "3":
        print("\n运行全部测试...\n")
        success1 = await test_minimal()
        success2 = await test_with_real_project()
        success = success1 and success2
    else:
        print("❌ 无效选择")
        return 1
    
    print("\n" + "="*60)
    if success:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败")
    print("="*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
