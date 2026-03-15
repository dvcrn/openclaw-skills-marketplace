#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw RAG Manager Skill
用于管理多个RAG系统的技能插件
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class RAGManagerSkill:
    """
    OpenClaw技能：RAG管理系统
    用于管理多个RAG系统，按类别组织并支持动态创建新分类
    """
    
    def __init__(self, base_path: Optional[str] = None):
        self.skill_name = "rag_manager"
        self.description = "管理多个RAG系统，按类别组织并支持动态创建新分类"
        self.base_path = Path(base_path) if base_path else Path.home() / ".openclaw" / "rag_collections"
        self.config_file = self.base_path / "rag_config.json"
        
        # 确保基础目录存在
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化配置文件
        if not self.config_file.exists():
            self._init_default_config()
    
    def _init_default_config(self):
        """初始化默认配置"""
        default_config = {
            "collections": {
                "程式類": {
                    "type": "category",
                    "children": {
                        "Python": {"type": "subcategory", "items": []},
                        "JavaScript": {"type": "subcategory", "items": []},
                        "Java": {"type": "subcategory", "items": []},
                        "各種程式指令用法": {"type": "subcategory", "items": []}
                    }
                },
                "文章類": {
                    "type": "category",
                    "children": {
                        "新聞": {"type": "subcategory", "items": []},
                        "文章": {"type": "subcategory", "items": []},
                        "技術文檔": {"type": "subcategory", "items": []}
                    }
                }
            },
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_config(self, config: Dict[str, Any]):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def list_categories(self) -> Dict[str, Any]:
        """列出所有分类"""
        config = self.get_config()
        return {
            "categories": list(config["collections"].keys()),
            "count": len(config["collections"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def list_subcategories(self, category: str) -> Dict[str, Any]:
        """列出特定分类下的子分类"""
        config = self.get_config()
        
        if category not in config["collections"]:
            return {
                "error": f"分类 '{category}' 不存在",
                "available_categories": list(config["collections"].keys())
            }
        
        category_data = config["collections"][category]
        subcategories = list(category_data["children"].keys()) if "children" in category_data else []
        
        return {
            "category": category,
            "subcategories": subcategories,
            "count": len(subcategories),
            "timestamp": datetime.now().isoformat()
        }
    
    def list_items(self, category: str, subcategory: str) -> Dict[str, Any]:
        """列出特定子分类下的项目"""
        config = self.get_config()
        
        if category not in config["collections"]:
            return {
                "error": f"分类 '{category}' 不存在",
                "available_categories": list(config["collections"].keys())
            }
        
        category_data = config["collections"][category]
        if subcategory not in category_data["children"]:
            return {
                "error": f"子分类 '{subcategory}' 在分类 '{category}' 中不存在",
                "available_subcategories": list(category_data["children"].keys())
            }
        
        items = category_data["children"][subcategory]["items"]
        
        return {
            "category": category,
            "subcategory": subcategory,
            "items": items,
            "count": len(items),
            "timestamp": datetime.now().isoformat()
        }
    
    def create_category(self, category_name: str) -> Dict[str, Any]:
        """创建新分类"""
        config = self.get_config()
        
        if category_name in config["collections"]:
            return {
                "status": "error",
                "message": f"分类 '{category_name}' 已存在"
            }
        
        config["collections"][category_name] = {
            "type": "category",
            "children": {}
        }
        
        self.save_config(config)
        
        # 创建物理目录
        category_dir = self.base_path / category_name
        category_dir.mkdir(exist_ok=True)
        
        return {
            "status": "success",
            "message": f"分类 '{category_name}' 创建成功",
            "category": category_name,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_subcategory(self, category: str, subcategory_name: str) -> Dict[str, Any]:
        """创建子分类"""
        config = self.get_config()
        
        if category not in config["collections"]:
            return {
                "status": "error",
                "message": f"分类 '{category}' 不存在"
            }
        
        if subcategory_name in config["collections"][category]["children"]:
            return {
                "status": "error",
                "message": f"子分类 '{subcategory_name}' 在分类 '{category}' 中已存在"
            }
        
        config["collections"][category]["children"][subcategory_name] = {
            "type": "subcategory",
            "items": []
        }
        
        self.save_config(config)
        
        # 创建物理目录
        subcategory_dir = self.base_path / category / subcategory_name
        subcategory_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "status": "success",
            "message": f"子分类 '{subcategory_name}' 在分类 '{category}' 中创建成功",
            "category": category,
            "subcategory": subcategory_name,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_item(self, category: str, subcategory: str, item_title: str, item_content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """添加项目到指定子分类"""
        config = self.get_config()
        
        if category not in config["collections"]:
            return {
                "status": "error",
                "message": f"分类 '{category}' 不存在"
            }
        
        if subcategory not in config["collections"][category]["children"]:
            return {
                "status": "error",
                "message": f"子分类 '{subcategory}' 在分类 '{category}' 中不存在"
            }
        
        # 生成唯一ID
        item_id = str(uuid.uuid4())
        
        # 准备项目数据
        item_data = {
            "id": item_id,
            "title": item_title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # 添加到配置
        config["collections"][category]["children"][subcategory]["items"].append(item_data)
        self.save_config(config)
        
        # 创建项目文件
        subcategory_dir = self.base_path / category / subcategory
        item_file = subcategory_dir / f"{item_id}.txt"
        
        with open(item_file, 'w', encoding='utf-8') as f:
            f.write(item_content)
        
        return {
            "status": "success",
            "message": f"项目 '{item_title}' 添加到 '{category}/{subcategory}' 成功",
            "item_id": item_id,
            "category": category,
            "subcategory": subcategory,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_item(self, item_id: str) -> Dict[str, Any]:
        """根据ID获取项目内容"""
        config = self.get_config()
        
        # 遍历所有分类和子分类查找项目
        for category_name, category_data in config["collections"].items():
            for subcategory_name, subcategory_data in category_data["children"].items():
                for item in subcategory_data["items"]:
                    if item["id"] == item_id:
                        # 读取项目文件内容
                        item_file = self.base_path / category_name / subcategory_name / f"{item_id}.txt"
                        content = ""
                        if item_file.exists():
                            with open(item_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                        
                        return {
                            "status": "success",
                            "item": item,
                            "content": content,
                            "category": category_name,
                            "subcategory": subcategory_name,
                            "timestamp": datetime.now().isoformat()
                        }
        
        return {
            "status": "error",
            "message": f"找不到ID为 '{item_id}' 的项目"
        }
    
    def search_items(self, query: str) -> Dict[str, Any]:
        """搜索项目"""
        config = self.get_config()
        results = []
        
        # 遍历所有分类和子分类搜索项目
        for category_name, category_data in config["collections"].items():
            for subcategory_name, subcategory_data in category_data["children"].items():
                for item in subcategory_data["items"]:
                    # 搜索标题和项目ID
                    if query.lower() in item["title"].lower() or query.lower() in item["id"]:
                        results.append({
                            "item": item,
                            "category": category_name,
                            "subcategory": subcategory_name
                        })
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    
    def remove_item(self, item_id: str) -> Dict[str, Any]:
        """删除指定项目"""
        config = self.get_config()
        
        # 遍历所有分类和子分类查找项目
        for category_name, category_data in config["collections"].items():
            for subcategory_name, subcategory_data in category_data["children"].items():
                for i, item in enumerate(subcategory_data["items"]):
                    if item["id"] == item_id:
                        # 从配置中移除项目
                        removed_item = subcategory_data["items"].pop(i)
                        self.save_config(config)
                        
                        # 删除项目文件
                        item_file = self.base_path / category_name / subcategory_name / f"{item_id}.txt"
                        if item_file.exists():
                            item_file.unlink()
                        
                        return {
                            "status": "success",
                            "message": f"项目 '{removed_item['title']}' 已从 '{category_name}/{subcategory_name}' 删除",
                            "removed_item": removed_item,
                            "timestamp": datetime.now().isoformat()
                        }
        
        return {
            "status": "error",
            "message": f"找不到ID为 '{item_id}' 的项目"
        }


def run_skill(query: str = "") -> Dict[str, Any]:
    """
    OpenClaw技能入口函数
    """
    manager = RAGManagerSkill()
    
    # 解析查询
    query_lower = query.lower()
    
    if "列出分类" in query_lower or "所有分类" in query_lower:
        return manager.list_categories()
    
    elif "列出子分类" in query_lower or "子分类" in query_lower:
        # 提取分类名称
        import re
        category_match = re.search(r'(程式類|文章類|[\w\u4e00-\u9fff]+)', query)
        if category_match:
            category = category_match.group(1)
            return manager.list_subcategories(category)
        else:
            return {"status": "error", "message": "请指定要列出子分类的父分类名称"}
    
    elif "列出项目" in query_lower or "项目列表" in query_lower:
        import re
        matches = re.findall(r'([\w\u4e00-\u9fff]+)', query)
        if len(matches) >= 2:
            category = matches[0] if matches[0] in ['程式類', '文章類'] else matches[1]
            subcategory = matches[1] if matches[0] in ['程式類', '文章類'] else matches[2]
            return manager.list_items(category, subcategory)
        else:
            return {"status": "error", "message": "请指定分类和子分类名称"}
    
    elif "创建分类" in query_lower or "新建分类" in query_lower:
        import re
        category_match = re.search(r'(?:创建分类|新建分类)\s+([\w\u4e00-\u9fff]+)', query)
        if category_match:
            category_name = category_match.group(1)
            return manager.create_category(category_name)
        else:
            return {"status": "error", "message": "请指定要创建的分类名称，格式：创建分类 分类名"}
    
    elif "创建子分类" in query_lower or "新建子分类" in query_lower:
        import re
        matches = re.findall(r'([\w\u4e00-\u9fff]+)', query)
        if len(matches) >= 2:
            category = matches[0] if matches[0] in ['程式類', '文章類'] else matches[1]
            subcategory = matches[1] if matches[0] in ['程式類', '文章類'] else matches[2]
            return manager.create_subcategory(category, subcategory)
        else:
            return {"status": "error", "message": "请指定分类和子分类名称，格式：创建子分类 分类名 子分类名"}
    
    elif "添加项目" in query_lower or "新增项目" in query_lower:
        # 这里需要更复杂的解析逻辑，通常需要上下文
        return {
            "status": "info",
            "message": "添加项目需要提供分类、子分类、标题和内容，请使用更具体的指令"
        }
    
    elif "搜索" in query_lower:
        import re
        search_match = re.search(r'(?:搜索|查找)\s+(.+)', query)
        if search_match:
            query_term = search_match.group(1)
            return manager.search_items(query_term)
        else:
            return {"status": "error", "message": "请指定要搜索的内容"}
    
    elif "获取项目" in query_lower:
        import re
        id_match = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', query)
        if id_match:
            item_id = id_match.group(0)
            return manager.get_item(item_id)
        else:
            return {"status": "error", "message": "请提供有效的项目ID"}
    
    else:
        return {
            "status": "info",
            "message": "RAG管理器支持以下操作：列出分类、列出子分类、列出项目、创建分类、创建子分类、添加项目、搜索项目、获取项目",
            "usage": {
                "列出所有分类": "列出分类",
                "列出某分类下的子分类": "列出程式類的子分类",
                "创建新分类": "创建分类 新分类名",
                "创建子分类": "创建子分类 程式類 Python技巧",
                "搜索项目": "搜索 关键词"
            }
        }


if __name__ == "__main__":
    # 如果直接运行此脚本，则执行技能
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw RAG Manager Skill")
    parser.add_argument("--query", "-q", help="查询字符串", default="help")
    parser.add_argument("--output", "-o", help="输出文件路径", default=None)
    
    args = parser.parse_args()
    
    result = run_skill(args.query)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))