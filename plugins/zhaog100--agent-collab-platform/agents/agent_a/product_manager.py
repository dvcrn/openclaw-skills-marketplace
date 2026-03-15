#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品管理模块 - PM代理专用

功能：
- 创建PRD
- 编辑PRD
- 删除PRD
"""

from datetime import datetime

class ProductManager:
    """产品管理器"""
    
    def __init__(self):
        """初始化产品管理器"""
        self.prds = {}
    
    def create_prd(self, title, requirements):
        """创建PRD
        
        Args:
            title: PRD标题
            requirements: 需求内容
            
        Returns:
            PRD文档
        """
        prd_id = f"prd_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        prd = {
            'id': prd_id,
            'title': title,
            'requirements': requirements,
            'state': 'draft',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.prds[prd_id] = prd
        
        # 生成PRD文档
        prd_doc = self._generate_prd_doc(prd)
        
        return prd_doc
    
    def _generate_prd_doc(self, prd):
        """生成PRD文档"""
        prd_doc = f"""## 📋 PRD - {prd['title']}

**PRD ID**：{prd['id']}
**创建时间**：{prd['created_at']}
**状态**：{prd['state']}

---

## 📌 产品需求

{prd['requirements']}

---

## 🎯 功能清单

（待补充）

---

## 📅 交付时间

（待确定）

---

**下一步**：提交给小米粒（Dev代理）进行技术设计

🌶️ 小米辣（PM代理）
"""
        
        return prd_doc
    
    def edit_prd(self, prd_id, updates):
        """编辑PRD"""
        if prd_id not in self.prds:
            return False, "PRD不存在"
        
        self.prds[prd_id].update(updates)
        return True, "PRD已更新"
    
    def delete_prd(self, prd_id):
        """删除PRD"""
        if prd_id not in self.prds:
            return False, "PRD不存在"
        
        del self.prds[prd_id]
        return True, "PRD已删除"
