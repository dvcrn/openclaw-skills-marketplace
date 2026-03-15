"""
Terminal Mode Module
终端模式 - 专门处理终端/命令行截图
"""

import re
from typing import Dict, List

class TerminalMode:
    """终端模式处理器"""
    
    def __init__(self):
        """初始化终端模式"""
        self.command_patterns = [
            r'^\s*\$',  # Bash提示符
            r'^\s*#',  # 注释或root提示符
            r'^\s*>',  # CMD提示符
            r'^\s*\.\.\.',  # Python提示符
        ]
    
    def is_terminal(self, img_array) -> bool:
        """
        检测是否为终端截图
        
        Args:
            img_array: 图片数组
        
        Returns:
            是否为终端
        """
        import cv2
        import numpy as np
        
        # 特征1：黑色背景为主
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        black_ratio = np.sum(gray < 50) / gray.size
        
        if black_ratio > 0.7:  # 70%以上是深色
            return True
        
        # 特征2：等宽字体（检测字符宽度一致性）
        # 这里简化处理，实际可以做更复杂的分析
        
        return False
    
    def post_process(self, text: str) -> str:
        """
        后处理终端文本
        
        Args:
            text: OCR识别的文本
        
        Returns:
            处理后的文本
        """
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            # 检测命令
            if self._is_command(line):
                processed_lines.append(f"```bash")
                processed_lines.append(line)
                processed_lines.append(f"```")
                processed_lines.append("")
            
            # 检测路径
            elif self._is_path(line):
                processed_lines.append(f"**{line}**")
                processed_lines.append("")
            
            # 检测错误信息
            elif self._is_error(line):
                processed_lines.append(f"❌ {line}")
                processed_lines.append("")
            
            # 普通输出
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _is_command(self, line: str) -> bool:
        """判断是否为命令"""
        for pattern in self.command_patterns:
            if re.match(pattern, line):
                return True
        return False
    
    def _is_path(self, line: str) -> bool:
        """判断是否为路径"""
        path_patterns = [
            r'^/',
            r'^[A-Z]:\\',
            r'^~',
        ]
        
        for pattern in path_patterns:
            if re.match(pattern, line.strip()):
                return True
        
        return False
    
    def _is_error(self, line: str) -> bool:
        """判断是否为错误信息"""
        error_keywords = [
            'error',
            'failed',
            'exception',
            '错误',
            '失败',
            '异常'
        ]
        
        line_lower = line.lower()
        return any(kw in line_lower for kw in error_keywords)
    
    def get_config(self) -> Dict:
        """获取终端模式配置"""
        return {
            "ocr": {
                "config": "--psm 6 --oem 3 -c tessedit_char_blacklist='|'"
            },
            "preprocessing": {
                "contrast_enhancement": 1.2,
                "use_adaptive_threshold": True
            },
            "structure": {
                "detect_commands": True,
                "detect_paths": True,
                "detect_errors": True
            }
        }
