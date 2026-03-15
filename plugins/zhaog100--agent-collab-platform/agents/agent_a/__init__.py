#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体A（PM代理）- 小米辣

角色：产品管理、Review验证、状态管理
"""

import sys
import os

# 添加core路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from core import BaseSkill
from .product_manager import ProductManager
from .reviewer import Reviewer

class AgentA(BaseSkill):
    """智能体A（PM代理）"""
    
    def __init__(self):
        """初始化PM代理"""
        super().__init__('agent_a', 'PM')
        
        # 初始化PM特定模块
        self.product_manager = ProductManager()
        self.reviewer = Reviewer()
        
        print(f"🌶️ 小米辣（PM代理）初始化完成")
    
    def handle_message(self, message):
        """处理消息"""
        if message is None:
            return
        
        message_type = message.get('type')
        
        print(f"📨 [PM代理] 收到消息: {message_type}")
        
        # 根据消息类型分发
        if message_type == 'tech_design':
            # 技术设计Review
            self._handle_tech_design_review(message)
        
        elif message_type == 'develop':
            # 开发进度Review
            self._handle_develop_review(message)
        
        elif message_type == 'publish':
            # 发布验收
            self._handle_publish_verify(message)
        
        elif message_type == 'collab_test':
            # 协作测试
            self._handle_collab_test(message)
        
        else:
            # 通用响应
            self._handle_generic(message)
    
    def _handle_tech_design_review(self, message):
        """处理技术设计Review"""
        issue_number = message.get('issue_number')
        body = message.get('body')
        
        # TODO: 实现技术设计Review逻辑
        response = f"""## 🌶️ 小米辣（PM代理）收到技术设计

**时间**：{self._get_current_time()}
**Issue**：#{issue_number}

---

我已收到技术设计，正在进行Review...

请稍等，Review结果将很快反馈！

---

🌶️ 小米辣（PM代理）
"""
        
        self.send_message('agent_b', response, issue_number)
    
    def _handle_develop_review(self, message):
        """处理开发Review"""
        issue_number = message.get('issue_number')
        
        # TODO: 实现开发Review逻辑
        response = f"""## 🌶️ 小米辣（PM代理）收到开发进度

**时间**：{self._get_current_time()}
**Issue**：#{issue_number}

---

收到开发进度更新，正在验收...

---

🌶️ 小米辣（PM代理）
"""
        
        self.send_message('agent_b', response, issue_number)
    
    def _handle_publish_verify(self, message):
        """处理发布验收"""
        issue_number = message.get('issue_number')
        
        # TODO: 实现发布验收逻辑
        response = f"""## 🌶️ 小米辣（PM代理）收到发布通知

**时间**：{self._get_current_time()}
**Issue**：#{issue_number}

---

收到发布完成通知，正在进行最终验收...

---

🌶️ 小米辣（PM代理）
"""
        
        self.send_message('agent_b', response, issue_number)
    
    def _handle_collab_test(self, message):
        """处理协作测试"""
        issue_number = message.get('issue_number')
        from_agent = message.get('from_agent', 'unknown')
        
        response = f"""## 🌶️ 小米辣（PM代理）协作测试响应

**时间**：{self._get_current_time()}
**Issue**：#{issue_number}

---

收到来自 **{from_agent}** 的协作测试！

✅ PM代理监听正常
✅ 消息识别正常
✅ 自动响应正常

小米粒，我们开始真实协作吧！

---

🌶️ 小米辣（PM代理）
"""
        
        self.send_message('agent_b', response, issue_number)
    
    def _handle_generic(self, message):
        """处理通用消息"""
        issue_number = message.get('issue_number')
        
        response = f"""## 🌶️ 小米辣（PM代理）收到消息

**时间**：{self._get_current_time()}
**Issue**：#{issue_number}

---

收到消息，正在处理...

---

🌶️ 小米辣（PM代理）
"""
        
        self.send_message('agent_b', response, issue_number)
    
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def create_prd(self, title, requirements):
        """创建PRD"""
        return self.product_manager.create_prd(title, requirements)
    
    def review_tech_design(self, design_data):
        """Review技术设计"""
        return self.reviewer.review_tech_design(design_data)
