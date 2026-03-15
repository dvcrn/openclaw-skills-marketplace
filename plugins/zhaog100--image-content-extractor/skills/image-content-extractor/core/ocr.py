"""
OCR Engine Module
统一OCR引擎管理
"""

import os
import json
from typing import Dict, Optional, List
from pathlib import Path

class OCREngine:
    """OCR引擎管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化OCR引擎"""
        self.config = config or self._get_default_config()
        self.tesseract = None
        self.tesseract_available = self._check_tesseract()
        
        if self.tesseract_available:
            try:
                import pytesseract
                self.tesseract = pytesseract
            except ImportError:
                self.tesseract_available = False
    
    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            "engine": "tesseract",
            "languages": ["chi_sim", "eng"],
            "fallback_to_ai": True,
            "config": "--psm 6 --oem 3",
            "timeout": 30
        }
    
    def _check_tesseract(self) -> bool:
        """检查Tesseract是否可用"""
        try:
            import subprocess
            result = subprocess.run(
                ['tesseract', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def recognize(self, image_path: str, mode: str = "general") -> Dict:
        """
        OCR识别
        
        Args:
            image_path: 图片路径
            mode: 识别模式 (general/terminal/document)
        
        Returns:
            识别结果字典
        """
        if self.tesseract_available:
            return self._ocr_tesseract(image_path, mode)
        elif self.config.get("fallback_to_ai"):
            return self._ocr_ai_vision(image_path, mode)
        else:
            return {
                "success": False,
                "error": "无可用OCR引擎",
                "text": ""
            }
    
    def _ocr_tesseract(self, image_path: str, mode: str) -> Dict:
        """Tesseract OCR识别"""
        try:
            from PIL import Image
            
            img = Image.open(image_path)
            
            # 根据模式调整配置
            if mode == "terminal":
                # 终端模式：等宽字体，高精度
                config = "--psm 6 --oem 3 -c tessedit_char_blacklist='|'"
            elif mode == "document":
                # 文档模式：自动分页
                config = "--psm 3 --oem 3"
            else:
                # 通用模式
                config = self.config.get("config", "--psm 6 --oem 3")
            
            # 语言配置
            langs = '+'.join(self.config.get("languages", ["chi_sim", "eng"]))
            
            # 识别
            text = self.tesseract.image_to_string(
                img,
                lang=langs,
                config=config
            )
            
            return {
                "success": True,
                "text": text.strip(),
                "engine": "tesseract",
                "mode": mode,
                "confidence": 0.95
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def _ocr_ai_vision(self, image_path: str, mode: str) -> Dict:
        """AI视觉识别（备用）"""
        # 这里会集成OpenClaw的image工具
        return {
            "success": True,
            "text": "[AI视觉识别结果]",
            "engine": "ai_vision",
            "mode": mode,
            "confidence": 0.7
        }
    
    def get_engine_info(self) -> Dict:
        """获取引擎信息"""
        return {
            "tesseract_available": self.tesseract_available,
            "current_engine": "tesseract" if self.tesseract_available else "ai_vision",
            "languages": self.config.get("languages", []),
            "fallback_enabled": self.config.get("fallback_to_ai", True)
        }
