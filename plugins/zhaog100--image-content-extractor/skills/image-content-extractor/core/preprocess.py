"""
Image Preprocessing Module
图片预处理模块
"""

import os
import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional, Dict

class ImagePreprocessor:
    """图片预处理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化预处理器"""
        self.config = config or self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            "block_height": 2000,
            "overlap_height": 100,
            "min_block_height": 500,
            "contrast_enhancement": 1.5,
            "binary_threshold": 150
        }
    
    def preprocess(self, image_path: str, mode: str = "general") -> List[str]:
        """
        预处理图片
        
        Args:
            image_path: 图片路径
            mode: 处理模式
        
        Returns:
            处理后的图片块路径列表
        """
        img = Image.open(image_path)
        width, height = img.size
        
        print(f"📊 图片: {width}x{height} ({os.path.getsize(image_path) // 1024}KB)")
        
        # 检查是否需要分块
        block_height = self.config["block_height"]
        
        if height <= block_height:
            # 不分块
            return [self._process_single(img, image_path, mode)]
        else:
            # 分块处理
            return self._process_blocks(img, image_path, mode)
    
    def _process_single(self, img: Image.Image, source_path: str, mode: str) -> str:
        """处理单个图片"""
        # 创建临时目录
        temp_dir = os.path.join(os.path.dirname(source_path), "temp_processed")
        os.makedirs(temp_dir, exist_ok=True)
        
        # 根据模式调整预处理
        if mode == "terminal":
            processed = self._preprocess_terminal(img)
        elif mode == "document":
            processed = self._preprocess_document(img)
        else:
            processed = self._preprocess_general(img)
        
        # 保存
        output_path = os.path.join(temp_dir, "processed_single.png")
        cv2.imwrite(output_path, processed)
        
        return output_path
    
    def _process_blocks(self, img: Image.Image, source_path: str, mode: str) -> List[str]:
        """分块处理"""
        width, height = img.size
        block_height = self.config["block_height"]
        overlap = self.config["overlap_height"]
        
        # 计算分块数量
        num_blocks = (height - overlap) // (block_height - overlap)
        
        print(f"✂️  分块: {num_blocks} 块")
        
        # 创建临时目录
        temp_dir = os.path.join(os.path.dirname(source_path), "temp_blocks")
        os.makedirs(temp_dir, exist_ok=True)
        
        blocks = []
        for i in range(num_blocks):
            top = i * (block_height - overlap)
            bottom = min(top + block_height, height)
            
            # 裁剪块
            block = img.crop((0, top, width, bottom))
            
            # 检测内容边界
            content_bounds = self._detect_content_bounds(np.array(block))
            if content_bounds:
                block = block.crop(content_bounds)
            
            # 预处理
            if mode == "terminal":
                processed = self._preprocess_terminal(block)
            elif mode == "document":
                processed = self._preprocess_document(block)
            else:
                processed = self._preprocess_general(block)
            
            # 保存
            block_path = os.path.join(temp_dir, f"block_{i:03d}.png")
            cv2.imwrite(block_path, processed)
            blocks.append(block_path)
            
            print(f"✅ 块 {i+1}/{num_blocks}: {os.path.basename(block_path)}")
        
        return blocks
    
    def _detect_content_bounds(self, img_array: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """检测内容边界"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        coords = cv2.findNonZero(binary)
        
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            # 添加一些边距
            margin = 10
            return (
                max(0, x - margin),
                max(0, y - margin),
                min(img_array.shape[1], x + w + margin),
                min(img_array.shape[0], y + h + margin)
            )
        
        return None
    
    def _preprocess_general(self, img: Image.Image) -> np.ndarray:
        """通用预处理"""
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 对比度增强
        alpha = self.config.get("contrast_enhancement", 1.5)
        enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=0)
        
        # 二值化
        threshold = self.config.get("binary_threshold", 150)
        _, binary = cv2.threshold(enhanced, threshold, 255, cv2.THRESH_BINARY)
        
        return binary
    
    def _preprocess_terminal(self, img: Image.Image) -> np.ndarray:
        """终端专用预处理"""
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 终端图片通常对比度高，不需要过度增强
        alpha = 1.2
        enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=0)
        
        # 自适应二值化（更适合终端）
        binary = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        return binary
    
    def _preprocess_document(self, img: Image.Image) -> np.ndarray:
        """文档专用预处理"""
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 文档图片需要更强的对比度
        alpha = 2.0
        enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=0)
        
        # 降噪
        denoised = cv2.fastNlMeansDenoising(enhanced)
        
        # 二值化
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
