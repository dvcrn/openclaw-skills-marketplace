#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础技能类 - 所有智能体的基类

功能：
- 统一初始化
- 共享GitHub监听
- 共享消息路由
- 共享状态管理
"""

import json
import subprocess
from datetime import datetime

class BaseSkill:
    """所有智能体的基类"""
    
    def __init__(self, agent_id, role, repo='zhaog100/openclaw-skills'):
        """初始化技能
        
        Args:
            agent_id: 智能体ID（如agent_a, agent_b）
            role: 角色（如PM, Dev）
            repo: GitHub仓库
        """
        self.agent_id = agent_id
        self.role = role
        self.repo = repo
        
        # 导入核心模块（延迟导入避免循环依赖）
        from .github_monitor import GitHubMonitor
        from .message_router import MessageRouter
        from .state_manager import StateManager
        from .issue_handler import IssueHandler
        
        # 初始化核心模块
        self.github_monitor = GitHubMonitor(repo)
        self.message_router = MessageRouter()
        self.state_manager = StateManager()
        self.issue_handler = IssueHandler(repo)
        
        print(f"✅ [{self.agent_id}] 初始化完成 - 角色: {self.role}")
    
    def listen(self):
        """启动监听"""
        print(f"🚀 [{self.agent_id}] 启动监听...")
        self.github_monitor.start(self._handle_message_wrapper)
    
    def stop(self):
        """停止监听"""
        self.github_monitor.stop()
        print(f"⏹️ [{self.agent_id}] 监听已停止")
    
    def _handle_message_wrapper(self, message):
        """消息处理包装器"""
        try:
            # 路由消息
            routed_message = self.message_router.route(message, self.agent_id)
            
            # 调用子类实现的处理方法
            self.handle_message(routed_message)
            
        except Exception as e:
            print(f"❌ [{self.agent_id}] 消息处理异常: {e}")
    
    def handle_message(self, message):
        """处理消息（子类必须实现）"""
        raise NotImplementedError("子类必须实现handle_message方法")
    
    def send_message(self, to_agent, content, issue_number):
        """发送消息到GitHub Issue
        
        Args:
            to_agent: 目标智能体
            content: 消息内容
            issue_number: Issue编号
        """
        # 添加智能体标识
        full_content = f"## 🌾 {self.get_display_name()}\n\n{content}"
        
        # 发送评论
        success, result = self.issue_handler.send_comment(issue_number, full_content)
        
        if success:
            print(f"✅ [{self.agent_id}] 消息已发送到Issue #{issue_number}")
        else:
            print(f"❌ [{self.agent_id}] 发送失败: {result}")
        
        return success, result
    
    def get_display_name(self):
        """获取显示名称"""
        display_names = {
            'agent_a': '小米辣（PM代理）🌶️',
            'agent_b': '小米粒（Dev代理）🌾',
            'agent_c': '智能体C',
            'agent_d': '智能体D'
        }
        return display_names.get(self.agent_id, self.agent_id)
    
    def get_status(self):
        """获取状态"""
        return {
            'agent_id': self.agent_id,
            'role': self.role,
            'github_monitor': self.github_monitor.get_status(),
            'state_manager': self.state_manager.get_status()
        }
    
    def create_issue(self, title, body, labels=None):
        """创建GitHub Issue
        
        Args:
            title: Issue标题
            body: Issue内容
            labels: 标签列表
        """
        return self.issue_handler.create_issue(title, body, labels)
    
    def get_issue(self, issue_number):
        """获取Issue内容"""
        return self.issue_handler.get_issue(issue_number)
