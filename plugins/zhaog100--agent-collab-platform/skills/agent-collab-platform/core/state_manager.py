#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态管理器 - 所有智能体共享

功能：
- 状态定义
- 状态流转
- 状态验证
"""

import json
from datetime import datetime

class StateManager:
    """状态管理器"""
    
    def __init__(self):
        """初始化状态管理器"""
        # 4阶段26状态定义
        self.stages = {
            'product_ideation': {
                'name': '产品构思',
                'states': ['draft', 'reviewing', 'approved', 'rejected'],
                'next_stage': 'tech_design'
            },
            'tech_design': {
                'name': '技术设计',
                'states': ['designing', 'reviewing', 'approved', 'rejected'],
                'next_stage': 'develop_implement'
            },
            'develop_implement': {
                'name': '开发实现',
                'states': ['developing', 'testing', 'reviewing', 'approved', 'rejected'],
                'next_stage': 'release_delivery'
            },
            'release_delivery': {
                'name': '发布交付',
                'states': ['preparing', 'publishing', 'verifying', 'completed', 'failed'],
                'next_stage': None
            }
        }
        
        # 状态流转规则
        self.transitions = {
            ('product_ideation', 'approved'): 'tech_design',
            ('tech_design', 'approved'): 'develop_implement',
            ('develop_implement', 'approved'): 'release_delivery',
            ('release_delivery', 'completed'): None  # 结束
        }
    
    def get_current_stage(self, state):
        """获取当前阶段"""
        for stage_id, stage_info in self.stages.items():
            if state in stage_info['states']:
                return stage_id, stage_info
        return None, None
    
    def can_transition(self, current_stage, current_state):
        """检查是否可以流转"""
        key = (current_stage, current_state)
        return key in self.transitions
    
    def get_next_stage(self, current_stage, current_state):
        """获取下一阶段"""
        key = (current_stage, current_state)
        return self.transitions.get(key)
    
    def validate_state(self, stage, state):
        """验证状态是否有效"""
        if stage not in self.stages:
            return False
        
        return state in self.stages[stage]['states']
    
    def get_state_info(self, stage, state):
        """获取状态信息"""
        if not self.validate_state(stage, state):
            return None
        
        return {
            'stage': stage,
            'stage_name': self.stages[stage]['name'],
            'state': state,
            'can_transition': self.can_transition(stage, state),
            'next_stage': self.get_next_stage(stage, state)
        }
    
    def get_all_stages(self):
        """获取所有阶段"""
        return self.stages
    
    def get_status(self):
        """获取状态管理器状态"""
        return {
            'stages_count': len(self.stages),
            'transitions_count': len(self.transitions)
        }
