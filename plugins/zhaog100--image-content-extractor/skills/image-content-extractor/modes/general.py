"""
General Mode Module
通用模式 - 适用于各种类型的图片
"""

from typing import Dict

class GeneralMode:
    """通用模式处理器"""
    
    def __init__(self):
        """初始化通用模式"""
        pass
    
    def detect_mode(self, img_array) -> str:
        """
        自动检测图片模式
        
        Args:
            img_array: 图片数组
        
        Returns:
            检测到的模式 (terminal/document/general)
        """
        # 尝试终端模式
        from .terminal import TerminalMode
        terminal = TerminalMode()
        if terminal.is_terminal(img_array):
            return "terminal"
        
        # 尝试文档模式
        from .document import DocumentMode
        document = DocumentMode()
        if document.is_document(img_array):
            return "document"
        
        # 默认通用模式
        return "general"
    
    def post_process(self, text: str) -> str:
        """
        后处理通用文本
        
        Args:
            text: OCR识别的文本
        
        Returns:
            处理后的文本
        """
        # 通用模式的后处理较简单
        # 主要是清理多余空行
        lines = text.split('\n')
        processed_lines = []
        prev_empty = False
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                # 避免连续空行
                if not prev_empty:
                    processed_lines.append("")
                    prev_empty = True
            else:
                processed_lines.append(line)
                prev_empty = False
        
        return '\n'.join(processed_lines)
    
    def get_config(self) -> Dict:
        """获取通用模式配置"""
        return {
            "ocr": {
                "config": "--psm 6 --oem 3"  # 默认配置
            },
            "preprocessing": {
                "contrast_enhancement": 1.5,
                "binary_threshold": 150
            },
            "structure": {
                "detect_headers": True,
                "detect_lists": True,
                "detect_code_blocks": False,
                "detect_tables": False
            }
        }
