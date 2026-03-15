#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术设计模块 v2.0 - GitHub Issue协作

功能：
- 从PRD提取需求
- 生成技术设计
- 评估工作量
- 识别风险
- 提交到GitHub Issue
"""

import json
import subprocess
from datetime import datetime

class TechDesigner:
    """技术设计师 - GitHub Issue模式"""
    
    def __init__(self):
        """初始化技术设计师"""
        self.designs = {}
        self.github_repo = 'zhaog100/openclaw-skills'
    
    def extract_from_prd(self, prd_content):
        """从PRD提取需求"""
        requirements = {
            'features': [],
            'constraints': [],
            'deliverables': []
        }
        
        # 简单提取逻辑（可以后续用AI增强）
        lines = prd_content.split('\n')
        for line in lines:
            line = line.strip()
            
            # 提取功能需求
            if line.startswith('## 功能') or line.startswith('### 功能'):
                in_features = True
            elif line.startswith('## ') or line.startswith('### '):
                in_features = False
            
            if in_features and line.startswith('- ') or line.startswith('* '):
                requirements['features'].append(line[2:])
        
        return requirements
    
    def create_design(self, prd_issue_number, prd_title, prd_content):
        """创建技术设计"""
        design_id = f"design_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 1. 提取需求
        requirements = self.extract_from_prd(prd_content)
        
        # 2. 生成架构设计
        architecture = self.generate_architecture(requirements)
        
        # 3. 评估工作量
        workload = self.estimate_workload(requirements)
        
        # 4. 识别风险
        risks = self.identify_risks(requirements)
        
        # 5. 保存设计
        self.designs[design_id] = {
            'id': design_id,
            'prd_issue': prd_issue_number,
            'title': prd_title,
            'requirements': requirements,
            'architecture': architecture,
            'workload': workload,
            'risks': risks,
            'state': 'tech_design',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return design_id, self.designs[design_id]
    
    def generate_architecture(self, requirements):
        """生成架构设计"""
        # 简化实现（可以后续用AI增强）
        architecture = {
            'modules': [],
            'tech_stack': ['Python', 'Bash', 'Git'],
            'data_flow': 'PRD → 技术设计 → 开发 → 测试 → 发布'
        }
        
        # 根据功能需求生成模块
        for feature in requirements.get('features', [])[:3]:  # 最多3个模块
            architecture['modules'].append({
                'name': feature[:20],
                'description': feature,
                'tech': 'Python'
            })
        
        return architecture
    
    def estimate_workload(self, requirements):
        """评估工作量"""
        features_count = len(requirements.get('features', []))
        base_hours = 2  # 基础2小时
        
        # 简化评估：每个功能1小时
        estimated_hours = base_hours + features_count * 1
        
        return {
            'estimated_hours': estimated_hours,
            'breakdown': {
                'design': 0.5,
                'develop': features_count * 1,
                'test': 1,
                'document': 0.5
            }
        }
    
    def identify_risks(self, requirements):
        """识别风险"""
        risks = []
        
        features_count = len(requirements.get('features', []))
        
        # 简化风险识别
        if features_count > 5:
            risks.append('功能较多，开发时间可能紧张')
        
        if '外部API' in str(requirements):
            risks.append('依赖外部API，可能存在稳定性风险')
        
        if not risks:
            risks.append('暂无明显风险')
        
        return risks
    
    def submit_to_github(self, design_id, design_data):
        """提交技术设计到GitHub Issue"""
        # 生成技术设计文档
        tech_doc = self.generate_tech_doc(design_data)
        
        # 发送GitHub评论
        cmd = [
            'gh', 'issue', 'comment', str(design_data['prd_issue']),
            '--body', tech_doc
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ [TechDesigner] 技术设计已提交到Issue #{design_data['prd_issue']}")
            return True, f"技术设计已提交到Issue #{design_data['prd_issue']}"
        else:
            print(f"❌ [TechDesigner] 提交失败: {result.stderr}")
            return False, f"提交失败: {result.stderr}"
    
    def generate_tech_doc(self, design_data):
        """生成技术设计文档"""
        tech_doc = f"""## 🎯 技术设计完成 - {design_data['title']}

**设计ID**：{design_data['id']}
**时间**：{design_data['created_at']}
**状态**：✅ 技术设计完成

---

## 📋 需求提取

### 核心功能
"""
        # 添加功能列表
        for feature in design_data['requirements'].get('features', []):
            tech_doc += f"- {feature}\n"
        
        tech_doc += f"""
---

## 🏗️ 架构设计

### 技术栈
"""
        # 添加技术栈
        for tech in design_data['architecture']['tech_stack']:
            tech_doc += f"- {tech}\n"
        
        tech_doc += f"""
### 模块设计
"""
        # 添加模块
        for module in design_data['architecture']['modules']:
            tech_doc += f"- **{module['name']}**: {module['description']}\n"
        
        tech_doc += f"""
---

## ⏱️ 工作量评估

**预估时间**：{design_data['workload']['estimated_hours']} 小时

**时间分解**：
- 设计：{design_data['workload']['breakdown']['design']} 小时
- 开发：{design_data['workload']['breakdown']['develop']} 小时
- 测试：{design_data['workload']['breakdown']['test']} 小时
- 文档：{design_data['workload']['breakdown']['document']} 小时

---

## ⚠️ 风险识别

"""
        # 添加风险
        for risk in design_data['risks']:
            tech_doc += f"- {risk}\n"
        
        tech_doc += f"""
---

## 📦 交付物

1. ✅ 技术设计文档
2. ⏳ 代码实现
3. ⏳ 单元测试
4. ⏳ 使用文档

---

**下一步**：等待小米辣（PM）Review，通过后开始开发实现

🌾 小米粒（Dev代理）
"""
        
        return tech_doc
    
    def handle(self, parsed_message):
        """处理技术设计消息"""
        action = parsed_message.get('action')
        
        if action == 'create':
            prd_id = parsed_message.get('prd_id')
            architecture = parsed_message.get('architecture', {})
            design_id = self.create_design(prd_id, architecture)
            return f"✅ 技术设计创建成功：{design_id}"
        
        elif action == 'evaluate':
            design_id = parsed_message.get('design_id')
            success, msg = self.evaluate_workload(design_id)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        elif action == 'identify_risks':
            design_id = parsed_message.get('design_id')
            success, msg = self.identify_risks(design_id)
            return f"⚠️ {msg}" if success else f"❌ {msg}"
        
        elif action == 'submit':
            design_id = parsed_message.get('design_id')
            success, msg = self.submit_for_review(design_id)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        return "❌ 未知操作"
