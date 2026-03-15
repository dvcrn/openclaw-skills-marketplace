#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent-collab-platform - 智能体协作平台统一入口

版本: v1.0.0
创建者: 小米粒（Dev代理）
创建时间: 2026-03-15
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

__version__ = '1.0.0'
__author__ = '小米粒 (miliger)'

def main():
    """主入口"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == 'agent_a' or command == 'pm':
        # 启动PM代理
        from agents.agent_a import AgentA
        agent = AgentA()
        agent.listen()
    
    elif command == 'agent_b' or command == 'dev':
        # 启动Dev代理
        from agents.agent_b import AgentB
        agent = AgentB()
        agent.listen()
    
    elif command == 'help' or command == '--help' or command == '-h':
        show_help()
    
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

def show_help():
    """显示帮助"""
    print(f"""
agent-collab-platform v{__version__} - 智能体协作平台

用法:
    agent-collab-platform <command> [options]

命令:
    agent_a, pm      启动智能体A（PM代理）- 小米辣
    agent_b, dev     启动智能体B（Dev代理）- 小米粒
    help             显示帮助

示例:
    # 启动PM代理
    python3 skill.py agent_a
    python3 skill.py pm

    # 启动Dev代理
    python3 skill.py agent_b
    python3 skill.py dev

架构:
    core/                   核心共享模块
    ├── github_monitor.py   GitHub监听
    ├── message_router.py   消息路由
    ├── state_manager.py    状态管理
    ├── base_skill.py       基础技能类
    └── issue_handler.py    Issue处理

    agents/                 智能体特定模块
    ├── agent_a/            PM代理（小米辣）
    └── agent_b/            Dev代理（小米粒）

创建者: 小米粒 (miliger)
GitHub: https://github.com/zhaog100/xiaomili-personal-skills
""")

if __name__ == '__main__':
    main()
