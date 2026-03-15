"""
Feishu 文档索引管理器
负责管理 memory/feishu-docs-index.md 文件
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class IndexManager:
    """飞书文档索引管理器"""
    
    DEFAULT_INDEX_PATH = os.path.expanduser("~/.openclaw/workspace/memory/feishu-docs-index.md")
    
    def __init__(self, index_path: str = None):
        self.index_path = index_path or self.DEFAULT_INDEX_PATH
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """确保索引文件存在"""
        if not os.path.exists(self.index_path):
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            self._create_empty_index()
    
    def _create_empty_index(self):
        """创建空索引文件"""
        content = """# 飞书云文档索引

**用途：** 快速定位和管理所有飞书云文档

---

## 📊 文档列表

| 序号 | 文档名 | 类型 | 链接 | 内容摘要 | 状态 | 最后更新 | 标签 | 所有者 |
|------|--------|------|------|----------|------|----------|------|--------|

---

## 📂 按类型分类

### 项目管理

### 技术文档

### 每日归档

### 更新记录

### 数据分析

---

## 🔍 快速查找

*暂无关键词索引*

---

## 📝 使用说明

**添加新文档时：**
1. 复制表格中的一行
2. 填写所有字段
3. 更新分类索引

**查找文档时：**
1. 先搜索本文档中的关键词
2. 找到对应链接
3. 用 `feishu_doc` 工具读取内容

---
*创建时间：{date}*
*最后更新：{date}*
""".format(date=datetime.now().strftime("%Y-%m-%d"))
        
        with open(self.index_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def add_or_update_doc(self, name: str, doc_type: str, url: str, token: str,
                         summary: str = "", status: str = "已完成", 
                         tags: List[str] = None, owner: str = "") -> bool:
        """
        添加或更新文档到索引
        
        Args:
            name: 文档名称
            doc_type: 文档类型 (docx, sheet, bitable 等)
            url: 文档链接
            token: 文档token
            summary: 内容摘要
            status: 文档状态
            tags: 标签列表
            owner: 所有者
        
        Returns:
            是否成功
        """
        try:
            # 读取现有索引
            with open(self.index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文档是否已存在（通过token判断）
            existing_index = self._find_doc_index(content, token)
            
            # 获取当前序号
            if existing_index:
                doc_index = existing_index
            else:
                doc_index = self._get_next_index(content)
            
            # 准备标签字符串
            tags_str = ", ".join(tags) if tags else ""
            
            # 准备表格行
            now = datetime.now().strftime("%Y-%m-%d")
            new_row = f"| {doc_index} | {name} | {doc_type} | {url} | {summary} | {status} | {now} | {tags_str} | {owner} |"
            
            # 更新表格
            if existing_index:
                # 更新现有行
                content = self._replace_table_row(content, token, new_row)
            else:
                # 添加新行
                content = self._insert_table_row(content, new_row)
            
            # 更新分类（如果新文档）
            if not existing_index and tags:
                content = self._update_categories(content, name, tags)
            
            # 更新关键词索引
            if not existing_index:
                content = self._update_keywords(content, name, summary, tags)
            
            # 更新最后更新时间
            content = self._update_last_modified(content)
            
            # 写回文件
            with open(self.index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"更新索引失败: {e}")
            return False
    
    def search_docs(self, keyword: str, search_in: List[str] = None) -> List[Dict]:
        """
        搜索文档
        
        Args:
            keyword: 搜索关键词
            search_in: 在哪些字段中搜索 (name, summary, tags)
        
        Returns:
            匹配的文档列表
        """
        if search_in is None:
            search_in = ["name", "summary", "tags"]
        
        results = []
        docs = self._parse_table()
        
        keyword_lower = keyword.lower()
        
        for doc in docs:
            match = False
            if "name" in search_in and keyword_lower in doc.get("name", "").lower():
                match = True
            if "summary" in search_in and keyword_lower in doc.get("summary", "").lower():
                match = True
            if "tags" in search_in and keyword_lower in doc.get("tags", "").lower():
                match = True
            
            if match:
                results.append(doc)
        
        return results
    
    def list_docs(self, tag: str = None, status: str = None, limit: int = None) -> List[Dict]:
        """
        列出文档
        
        Args:
            tag: 按标签筛选
            status: 按状态筛选
            limit: 限制数量
        
        Returns:
            文档列表
        """
        docs = self._parse_table()
        
        # 筛选
        if tag:
            docs = [d for d in docs if tag in d.get("tags", "")]
        
        if status:
            docs = [d for d in docs if d.get("status") == status]
        
        # 限制数量
        if limit:
            docs = docs[:limit]
        
        return docs
    
    def get_doc_by_token(self, token: str) -> Optional[Dict]:
        """通过token获取文档信息"""
        docs = self._parse_table()
        for doc in docs:
            if token in doc.get("link", ""):
                return doc
        return None
    
    def _parse_table(self) -> List[Dict]:
        """解析索引表格"""
        docs = []
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 找到表格部分
            lines = content.split('\n')
            in_table = False
            
            for line in lines:
                if line.startswith('| 序号 '):
                    in_table = True
                    continue
                if in_table and line.startswith('|---'):
                    continue
                if in_table and line.startswith('|') and not line.startswith('|------'):
                    # 解析表格行
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    if len(parts) >= 8:
                        # 兼容8列表格格式（序号、文档名、类型、链接、摘要、状态、更新时间、备注）
                        docs.append({
                            "index": parts[0],
                            "name": parts[1],
                            "type": parts[2],
                            "link": parts[3],
                            "summary": parts[4],
                            "status": parts[5],
                            "updated": parts[6],
                            "tags": parts[7],  # 使用"备注"列作为标签
                            "owner": ""  # 所有者信息暂时为空
                        })
        
        except Exception as e:
            print(f"解析索引失败: {e}")
        
        return docs
    
    def _find_doc_index(self, content: str, token: str) -> Optional[str]:
        """查找文档是否已存在，返回序号"""
        pattern = r'\| (\d+) \| [^|]+ \| [^|]+ \| [^/]+/docx/' + re.escape(token) + r'[^|]* \|'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        return None
    
    def _get_next_index(self, content: str) -> int:
        """获取下一个序号"""
        pattern = r'\| (\d+) \|'
        matches = re.findall(pattern, content)
        if matches:
            return max([int(m) for m in matches]) + 1
        return 1
    
    def _replace_table_row(self, content: str, token: str, new_row: str) -> str:
        """替换表格中的某一行"""
        pattern = r'(\| \d+ \| [^|]+ \| [^|]+ \| [^/]+/docx/' + re.escape(token) + r'[^|]* \|[^\n]+)'
        return re.sub(pattern, new_row, content)
    
    def _insert_table_row(self, content: str, new_row: str) -> str:
        """插入新行到表格"""
        # 在表格头部后插入
        lines = content.split('\n')
        insert_index = -1
        
        for i, line in enumerate(lines):
            if line.startswith('| 序号 '):
                insert_index = i + 2  # 跳过表头和分隔线
                break
        
        if insert_index > 0:
            lines.insert(insert_index, new_row)
        
        return '\n'.join(lines)
    
    def _update_categories(self, content: str, name: str, tags: List[str]) -> str:
        """更新分类列表"""
        # 简单实现：在对应分类下添加文档名
        # 这里可以扩展更复杂的逻辑
        return content
    
    def _update_keywords(self, content: str, name: str, summary: str, tags: List[str]) -> str:
        """更新关键词索引"""
        # 提取关键词
        keywords = []
        if tags:
            keywords.extend(tags)
        
        # 这里可以添加更智能的关键词提取
        # 暂时保持简单
        
        return content
    
    def _update_last_modified(self, content: str) -> str:
        """更新最后修改时间"""
        now = datetime.now().strftime("%Y-%m-%d")
        pattern = r'\*最后更新：[^*]+\*'
        replacement = f'*最后更新：{now}*'
        return re.sub(pattern, replacement, content)


# 便捷函数
def add_doc_to_index(name: str, url: str, token: str, summary: str = "", 
                     tags: List[str] = None, owner: str = "") -> bool:
    """便捷函数：添加文档到索引"""
    manager = IndexManager()
    return manager.add_or_update_doc(
        name=name,
        doc_type="docx",
        url=url,
        token=token,
        summary=summary,
        status="已完成",
        tags=tags,
        owner=owner
    )


def search_docs(keyword: str) -> List[Dict]:
    """便捷函数：搜索文档"""
    manager = IndexManager()
    return manager.search_docs(keyword)


def list_all_docs(tag: str = None) -> List[Dict]:
    """便捷函数：列出所有文档"""
    manager = IndexManager()
    return manager.list_docs(tag=tag)