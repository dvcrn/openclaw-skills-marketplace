"""
Structure Analyzer Module
结构分析模块
"""

import re
from typing import Dict, List, Optional

class StructureAnalyzer:
    """结构分析器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化分析器"""
        self.config = config or self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            "detect_headers": True,
            "detect_lists": True,
            "detect_code_blocks": True,
            "detect_tables": True,
            "header_patterns": [
                r'^\d+\.?\s',  # 数字编号
                r'^[一二三四五六七八九十]+、',  # 中文编号
                r'^[A-Z]{2,}',  # 全大写
                r'^#+\s'  # Markdown标题
            ]
        }
    
    def analyze(self, text: str, mode: str = "general") -> Dict:
        """
        分析文本结构
        
        Args:
            text: 原始文本
            mode: 分析模式
        
        Returns:
            结构化数据
        """
        lines = text.split('\n')
        
        structure = {
            "title": "",
            "sections": [],
            "current_section": None,
            "metadata": {
                "total_lines": len(lines),
                "mode": mode
            }
        }
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                continue
            
            # 检测标题
            if self.config["detect_headers"] and self._is_title(stripped, mode):
                self._add_section(structure, stripped)
            
            # 检测列表
            elif self.config["detect_lists"] and self._is_list_item(stripped):
                self._add_content(structure, "list_item", stripped)
            
            # 检测代码块
            elif self.config["detect_code_blocks"] and self._is_code_block(stripped):
                self._add_content(structure, "code", stripped)
            
            # 普通段落
            else:
                self._add_content(structure, "paragraph", stripped)
        
        # 添加最后一个section
        if structure["current_section"]:
            structure["sections"].append(structure["current_section"])
        
        return structure
    
    def _is_title(self, line: str, mode: str) -> bool:
        """判断是否为标题"""
        if not line or len(line) > 50:
            return False
        
        patterns = self.config.get("header_patterns", [])
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        
        # 终端模式的特殊检测
        if mode == "terminal":
            # 终端中通常是路径或命令，不算标题
            return False
        
        return False
    
    def _is_list_item(self, line: str) -> bool:
        """判断是否为列表项"""
        list_markers = ['•', '-', '*', '·', '○', '●', '►', '→']
        return any(line.startswith(marker) for marker in list_markers)
    
    def _is_code_block(self, line: str) -> bool:
        """判断是否为代码块"""
        # 简单判断：包含特殊字符
        code_patterns = [
            r'[{}\[\]();]',  # 编程符号
            r'^\s*\$',  # 命令行提示符
            r'^\s*#',  # 注释
            r'^\s*//',  # 注释
            r'^\s*/\*',  # 注释
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, line):
                return True
        
        return False
    
    def _add_section(self, structure: Dict, title: str):
        """添加新section"""
        # 保存当前section
        if structure["current_section"]:
            structure["sections"].append(structure["current_section"])
        
        # 创建新section
        structure["current_section"] = {
            "type": "section",
            "title": title,
            "content": []
        }
        
        # 设置总标题
        if not structure["title"]:
            structure["title"] = title
    
    def _add_content(self, structure: Dict, content_type: str, text: str):
        """添加内容"""
        if not structure["current_section"]:
            # 如果还没有section，创建一个默认的
            structure["current_section"] = {
                "type": "section",
                "title": "未分类内容",
                "content": []
            }
        
        structure["current_section"]["content"].append({
            "type": content_type,
            "text": text
        })
    
    def to_markdown(self, structure: Dict, add_metadata: bool = True, add_toc: bool = True) -> str:
        """
        转换为Markdown
        
        Args:
            structure: 结构化数据
            add_metadata: 是否添加元数据
            add_toc: 是否添加目录
        
        Returns:
            Markdown文本
        """
        md_lines = []
        
        # 元数据
        if add_metadata:
            md_lines.append(f"# {structure['title']}")
            md_lines.append("")
            md_lines.append(f"> 提取时间: {self._get_current_time()}")
            md_lines.append("")
        
        # 目录
        if add_toc and len(structure["sections"]) > 3:
            md_lines.append("## 目录")
            md_lines.append("")
            for i, section in enumerate(structure["sections"], 1):
                slug = self._slugify(section["title"])
                md_lines.append(f"{i}. [{section['title']}](#{slug})")
            md_lines.append("")
        
        # 内容
        for section in structure["sections"]:
            md_lines.append(f"## {section['title']}")
            md_lines.append("")
            
            for item in section["content"]:
                if item["type"] == "paragraph":
                    md_lines.append(item["text"])
                    md_lines.append("")
                
                elif item["type"] == "list_item":
                    # 去除原有的标记，统一使用-
                    text = item["text"].lstrip('•-*·○●►→ ')
                    md_lines.append(f"- {text}")
                
                elif item["type"] == "code":
                    md_lines.append(f"```")
                    md_lines.append(item["text"])
                    md_lines.append("```")
                    md_lines.append("")
            
            md_lines.append("")
        
        return '\n'.join(md_lines)
    
    def _slugify(self, text: str) -> str:
        """生成slug（用于锚点）"""
        # 简单处理：保留中文、字母、数字、连字符
        return re.sub(r'[^\w\u4e00-\u9fff-]', '-', text.lower()).strip('-')
    
    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M')
