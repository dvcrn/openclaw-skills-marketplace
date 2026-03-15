#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体B（Dev代理）- 小米粒

角色：技术设计、开发实现、集成发布
"""

import sys
import os

# 添加core路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from core import BaseSkill
from .tech_designer import TechDesigner
from .developer import Developer
from .publisher import Publisher

class AgentB(BaseSkill):
    """智能体B（Dev代理）"""
    
    def __init__(self):
        """初始化Dev代理"""
        super().__init__('agent_b', 'Dev')
        
        # 初始化Dev特定模块
        self.tech_designer = TechDesigner()
        self.developer = Developer()
        self.publisher = Publisher()
        
        print(f"🌾 小米粒（Dev代理）初始化完成")
    
    def handle_message(self, message):
        """处理消息"""
        if message is None:
            return
        
        message_type = message.get('type')
        
        print(f"📨 [Dev代理] 收到消息: {message_type}")
        
        # 根据消息类型分发
        if message_type == 'prd':
            # 收到PRD，开始技术设计
            self._handle_prd(message)
        
        elif message_type == 'review':
            # 收到Review结果
            self._handle_review(message)
        
        elif message_type == 'collab_test':
            # 协作测试
            self._handle_collab_test(message)
        
        else:
            # 通用响应
            self._handle_generic(message)
    
    def _handle_prd(self, message):
        """处理PRD"""
        issue_number = message.get('issue_number')
        
        # 获取完整Issue内容（PRD）
        success, issue_data = self.get_issue(issue_number)
        
        if not success:
            print(f"❌ 获取Issue失败: {issue_data}")
            return
        
        # 生成技术设计
        prd_title = issue_data['title']
        prd_body = issue_data['body']
        
        design_id, design_data = self.tech_designer.create_design(
            issue_number,
            prd_title,
            prd_body
        )
        
        # 提交技术设计到GitHub
        tech_doc = self.tech_designer.generate_tech_doc(design_data)
        self.send_message('agent_a', tech_doc, issue_number)
    
    def _handle_review(self, message):
        """处理Review结果"""
        issue_number = message.get('issue_number')
        body = message.get('body')
        
        # 检查Review结果
        if '✅' in body and 'approved' in body.lower():
            # Review通过，开始开发
            response = f"""## 💻 小米粒（Dev代理）开始开发

**时间**：{self._get_current_time()}
**Issue**：#{issue_number}

---

收到Review通过通知！

✅ 技术设计已通过Review
💻 开始开发实现...

---

🌾 小米粒（Dev代理）
"""
            
            self.send_message('agent_a', response, issue_number)
            
            # TODO: 启动开发流程
        else:
            # Review未通过，需要修改
            response = f"""## 🔧 小米粒（Dev代理）修改设计

**时间**：{self._get_current_time()}
**Issue**：#{issue_number}

---

收到Review反馈，正在修改技术设计...

---

🌾 小米粒（Dev代理）
"""
            
            self.send_message('agent_a', response, issue_number)
    
    def _handle_collab_test(self, message):
        """处理协作测试"""
        issue_number = message.get('issue_number')
        from_agent = message.get('from_agent', 'unknown')
        
        response = f"""## 🌾 小米粒（Dev代理）协作测试响应

**时间**：{self._get_current_time()}
**Issue**：#{issue_number}

---

收到来自 **{from_agent}** 的协作测试！

✅ Dev代理监听正常
✅ 消息识别正常
✅ 自动响应正常

小米辣，协作测试成功！我们准备好真实协作了！

---

🌾 小米粒（Dev代理）
"""
        
        self.send_message('agent_a', response, issue_number)
    
    def _handle_generic(self, message):
        """处理通用消息"""
        issue_number = message.get('issue_number')
        
        response = f"""## 🌾 小米粒（Dev代理）收到消息

**时间**：{self._get_current_time()}
**Issue**：#{issue_number}

---

收到消息，正在处理...

---

🌾 小米粒（Dev代理）
"""
        
        self.send_message('agent_a', response, issue_number)
    
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
