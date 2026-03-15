#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息路由器 - 所有智能体共享

功能：
- 识别消息类型
- 过滤自己的消息
- 提取关键信息
"""

class MessageRouter:
    """消息路由器"""
    
    def __init__(self):
        """初始化路由器"""
        # 智能体标识映射
        self.agent_markers = {
            'agent_a': ['小米辣', 'PM代理', '🌶️'],
            'agent_b': ['小米粒', 'Dev代理', '🌾'],
            'agent_c': ['智能体C'],
            'agent_d': ['智能体D']
        }
    
    def route(self, message, current_agent_id):
        """路由消息
        
        Args:
            message: 原始消息
            current_agent_id: 当前智能体ID
            
        Returns:
            路由后的消息
        """
        # 1. 检查是否是自己的消息
        if self._is_own_message(message, current_agent_id):
            return None  # 跳过自己的消息
        
        # 2. 识别消息类型
        message_type = self._identify_message_type(message)
        
        # 3. 提取关键信息
        extracted_info = self._extract_info(message)
        
        # 4. 构造路由消息
        routed_message = {
            'issue_number': message.get('issue_number'),
            'comment_id': message.get('comment_id'),
            'author': message.get('author'),
            'body': message.get('body'),
            'created_at': message.get('created_at'),
            'type': message_type,
            'info': extracted_info,
            'from_agent': self._identify_sender_agent(message)
        }
        
        return routed_message
    
    def _is_own_message(self, message, current_agent_id):
        """检查是否是自己的消息"""
        body = message.get('body', '')
        markers = self.agent_markers.get(current_agent_id, [])
        
        for marker in markers:
            if marker in body:
                return True
        
        return False
    
    def _identify_message_type(self, message):
        """识别消息类型"""
        body = message.get('body', '').lower()
        title = message.get('title', '').lower() if 'title' in message else ''
        
        # PRD相关
        if 'prd' in body or '产品需求' in body or '产品构思' in body:
            return 'prd'
        
        # 技术设计相关
        if '技术设计' in body or 'tech design' in body:
            return 'tech_design'
        
        # 开发相关
        if '开发' in body or 'develop' in body or '实现' in body:
            return 'develop'
        
        # Review相关
        if 'review' in body or '审查' in body or '验收' in body:
            return 'review'
        
        # 发布相关
        if '发布' in body or 'publish' in body or 'clawhub' in body:
            return 'publish'
        
        # 状态更新
        if '状态' in body or 'state' in body or '进度' in body:
            return 'state_update'
        
        # 协作测试
        if '协作测试' in body or 'collab test' in body:
            return 'collab_test'
        
        # 通知
        if '通知' in body or 'notification' in body:
            return 'notification'
        
        return 'unknown'
    
    def _extract_info(self, message):
        """提取关键信息"""
        body = message.get('body', '')
        
        info = {
            'keywords': [],
            'mentions': [],
            'links': [],
            'numbers': []
        }
        
        # 简化提取（可以后续用AI增强）
        import re
        
        # 提取@提及
        info['mentions'] = re.findall(r'@(\w+)', body)
        
        # 提取数字（Issue编号等）
        info['numbers'] = re.findall(r'#(\d+)', body)
        
        # 提取链接
        info['links'] = re.findall(r'https?://[^\s]+', body)
        
        return info
    
    def _identify_sender_agent(self, message):
        """识别发送者智能体"""
        body = message.get('body', '')
        
        for agent_id, markers in self.agent_markers.items():
            for marker in markers:
                if marker in body:
                    return agent_id
        
        return 'unknown'
