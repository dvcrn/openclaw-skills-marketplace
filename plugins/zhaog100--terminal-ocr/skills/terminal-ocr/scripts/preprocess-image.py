#!/usr/bin/env python3

"""
终端截图预处理脚本
功能：分块、增强、二值化处理
"""

import cv2
import numpy as np
from PIL import Image
import os
import sys

def preprocess_terminal_image(image_path, output_dir=None, block_height=2000):
    """
    预处理终端截图
    
    Args:
        image_path: 输入图片路径
        output_dir: 输出目录
        block_height: 每块的高度（像素）
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(image_path), "processed")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载图片
    img = Image.open(image_path)
    width, height = img.size
    print(f"原图尺寸: {width}x{height}")
    
    # 计算分块数量
    num_blocks = (height + block_height - 1) // block_height
    print(f"将分为 {num_blocks} 块处理")
    
    # 分块处理
    processed_blocks = []
    for i in range(num_blocks):
        top = i * block_height
        bottom = min((i + 1) * block_height, height)
        block = img.crop((0, top, width, bottom))
        
        # 转换为OpenCV格式
        block_cv = cv2.cvtColor(np.array(block), cv2.COLOR_RGB2BGR)
        
        # 灰度化
        gray = cv2.cvtColor(block_cv, cv2.COLOR_BGR2GRAY)
        
        # 对比度增强
        enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        
        # 二值化
        _, binary = cv2.threshold(enhanced, 150, 255, cv2.THRESH_BINARY)
        
        # 保存处理后的块
        block_name = f"block_{i:03d}_processed.png"
        block_path = os.path.join(output_dir, block_name)
        cv2.imwrite(block_path, binary)
        processed_blocks.append(block_path)
        print(f"✅ 处理块 {i+1}/{num_blocks}: {block_name}")
    
    return processed_blocks

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python preprocess-image.py <image_path> [output_dir]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        blocks = preprocess_terminal_image(image_path, output_dir)
        print(f"\n🎉 预处理完成！共生成 {len(blocks)} 个处理块")
        print(f"输出目录: {os.path.dirname(blocks[0])}")
    except Exception as e:
        print(f"❌ 预处理失败: {str(e)}")
        sys.exit(1)