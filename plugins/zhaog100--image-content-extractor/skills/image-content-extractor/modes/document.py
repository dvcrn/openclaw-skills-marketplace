"""
Document Mode Module
文档模式 - 专门处理文档截图
"""

import re
from typing import Dict

class DocumentMode:
    """文档模式处理器"""
    
    def __init__(self):
        """初始化文档模式"""
        self.title_patterns = [
            r'^#\s+',  # Markdown标题
            r'^\d+\.\s+',  # 数字编号
            r'^[一二三四五六七八九十]+、',  # 中文编号
            r'^[A-Z][A-Z\s]+$',  # 全大写标题
        ]
    
    def is_document(self, img_array) -> bool:
        """
        检测是否为文档截图
        
        Args:
            img_array: 图片数组
        
        Returns:
            是否为文档
        """
        import cv2
        import numpy as np
        
        # 特征1：白色/浅色背景
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        white_ratio = np.sum(gray > 200) / gray.size
        
        if white_ratio > 0.6:  # 60%以上是浅色
            return True
        
        # 特征2：有明显的段落结构（空白行分隔）
        # 这里简化处理
        
        return False
    
    def post_process(self, text: str) -> str:
        """
        后处理文档文本
        
        Args:
            text: OCR识别的文本
        
        Returns:
            处理后的文本
        """
        lines = text.split('\n')
        processed_lines = []
        in_code_block = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检测代码块开始/结束
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                processed_lines.append(line)
                continue
            
            # 代码块内不处理
            if in_code_block:
                processed_lines.append(line)
                continue
            
            # 检测标题
            if self._is_title(stripped):
                # 判断标题级别
                level = self._detect_title_level(stripped, i)
                processed_lines.append(f"{'#' * level} {stripped.lstrip('# ')}")
                processed_lines.append("")
            
            # 检测列表
            elif self._is_list_item(stripped):
                processed_lines.append(f"- {self._clean_list_item(stripped)}")
            
            # 检测引用
            elif stripped.startswith('>'):
                processed_lines.append(stripped)
            
            # 检测表格分隔符
            elif re.match(r'^[\|\-\s]+$', stripped):
                processed_lines.append(stripped)
            
            # 普通段落
            else:
                processed_lines.append(stripped)
        
        return '\n'.join(processed_lines)
    
    def _is_title(self, line: str) -> bool:
        """判断是否为标题"""
        if not line or len(line) > 50:
            return False
        
        for pattern in self.title_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _detect_title_level(self, line: str, line_index: int) -> int:
        """
        检测标题级别
        
        Args:
            line: 文本行
            line_index: 行索引
        
        Returns:
            标题级别（1-6）
        """
        # Markdown标题
        if line.startswith('#'):
            count = len(re.match(r'^#+', line).group())
            return min(count, 6)
        
        # 一级标题：第一个标题，或全大写
        if line_index < 5 or line.isupper():
            return 1
        
        # 数字编号
        if re.match(r'^\d+\.', line):
            return 2
        
        # 中文编号
        if re.match(r'^[一二三四五六七八九十]+、', line):
            return 2
        
        # 默认三级
        return 3
    
    def _is_list_item(self, line: str) -> bool:
        """判断是否为列表项"""
        list_markers = ['•', '-', '*', '·', '○', '●', '►', '→', '1.', '2.', '3.']
        return any(line.startswith(marker) for marker in list_markers)
    
    def _clean_list_item(self, line: str) -> str:
        """清理列表项"""
        # 去除原有的标记
        return line.lstrip('•-*·○●►→0123456789. ')
    
    def get_config(self) -> Dict:
        """获取文档模式配置"""
        return {
            "ocr": {
                "config": "--psm 3 --oem 3"  # 自动分页
            },
            "preprocessing": {
                "contrast_enhancement": 2.0,
                "denoise": True
            },
            "structure": {
                "detect_headers": True,
                "detect_lists": True,
                "detect_code_blocks": True,
                "detect_tables": True
            }
        }
