#!/usr/bin/env python3

"""
Image Content Extractor v2.0 - Unified Version
统一图片内容提取技能
支持模式：terminal（终端）、document（文档）、general（通用）
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# 添加core和modes到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import OCREngine, ImagePreprocessor, ContentMerger, StructureAnalyzer
from modes.terminal import TerminalMode
from modes.document import DocumentMode
from modes.general import GeneralMode

class ImageContentExtractor:
    """统一图片内容提取器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化提取器"""
        self.config = self._load_config(config_path)
        
        # 初始化组件
        self.ocr = OCREngine(self.config.get("ocr"))
        self.preprocessor = ImagePreprocessor(self.config.get("preprocessing"))
        self.merger = ContentMerger(self.config.get("preprocessing", {}).get("overlap_height", 100))
        self.analyzer = StructureAnalyzer(self.config.get("structure"))
        
        # 初始化模式处理器
        self.terminal_mode = TerminalMode()
        self.document_mode = DocumentMode()
        self.general_mode = GeneralMode()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "config",
                "extractor-config.json"
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            "ocr": {
                "engine": "tesseract",
                "languages": ["chi_sim", "eng"],
                "fallback_to_ai": True
            },
            "preprocessing": {
                "block_height": 2000,
                "overlap_height": 100
            },
            "output": {
                "format": "markdown",
                "add_metadata": True,
                "add_toc": True
            }
        }
    
    def extract(self, image_path: str, mode: str = "auto") -> Dict:
        """
        提取内容主函数
        
        Args:
            image_path: 图片路径
            mode: 提取模式 (auto/terminal/document/general)
        
        Returns:
            提取结果
        """
        print(f"🚀 开始提取: {image_path}")
        
        # 验证文件
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"文件不存在: {image_path}"
            }
        
        # 自动检测模式
        if mode == "auto":
            mode = self._detect_mode(image_path)
            print(f"🔍 检测模式: {mode}")
        
        # 获取模式特定配置
        mode_config = self._get_mode_config(mode)
        
        # 1. 预处理
        print("📋 预处理图片...")
        processed_blocks = self.preprocessor.preprocess(image_path, mode)
        
        # 2. OCR识别
        print(f"🔍 OCR识别 ({len(processed_blocks)} 块)...")
        ocr_results = []
        for i, block_path in enumerate(processed_blocks, 1):
            print(f"   识别块 {i}/{len(processed_blocks)}")
            result = self.ocr.recognize(block_path, mode)
            ocr_results.append(result)
        
        # 3. 合并内容
        print("🔗 合并内容...")
        merged = self.merger.merge_with_confidence(ocr_results)
        
        if not merged["success"]:
            return merged
        
        # 4. 结构分析
        print("📊 分析结构...")
        structure = self.analyzer.analyze(merged["text"], mode)
        
        # 5. 生成Markdown
        print("📝 生成Markdown...")
        markdown = self.analyzer.to_markdown(
            structure,
            add_metadata=self.config["output"].get("add_metadata", True),
            add_toc=self.config["output"].get("add_toc", True)
        )
        
        # 6. 模式特定后处理
        if mode == "terminal":
            markdown = self.terminal_mode.post_process(markdown)
        elif mode == "document":
            markdown = self.document_mode.post_process(markdown)
        
        print("✅ 提取完成！")
        
        return {
            "success": True,
            "markdown": markdown,
            "structure": structure,
            "metadata": {
                "source": image_path,
                "mode": mode,
                "extracted_at": datetime.now().isoformat(),
                "blocks_processed": len(processed_blocks),
                "confidence": merged["confidence"]
            }
        }
    
    def _detect_mode(self, image_path: str) -> str:
        """自动检测图片模式"""
        import cv2
        import numpy as np
        from PIL import Image
        
        # 读取图片
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # 尝试终端模式检测
        if self.terminal_mode.is_terminal(img_array):
            return "terminal"
        
        # 尝试文档模式检测
        if self.document_mode.is_document(img_array):
            return "document"
        
        # 默认通用模式
        return "general"
    
    def _get_mode_config(self, mode: str) -> Dict:
        """获取模式特定配置"""
        if mode == "terminal":
            return self.terminal_mode.get_config()
        elif mode == "document":
            return self.document_mode.get_config()
        else:
            return self.general_mode.get_config()
    
    def save_to_knowledge_base(
        self,
        markdown: str,
        title: str,
        category: str = "uncategorized"
    ) -> str:
        """保存到知识库"""
        knowledge_dir = os.path.expanduser("~/.openclaw/workspace/knowledge")
        
        # 创建分类目录
        category_dir = os.path.join(knowledge_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 生成文件名
        filename = f"{title}.md"
        filepath = os.path.join(category_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"✅ 已保存到知识库: {filepath}")
        
        # 更新QMD索引
        self._update_qmd_index()
        
        return filepath
    
    def _update_qmd_index(self):
        """更新QMD索引"""
        import subprocess
        
        try:
            subprocess.run(
                ["qmd", "update"],
                cwd=os.path.expanduser("~/.openclaw/workspace"),
                timeout=60,
                capture_output=True
            )
            print("✅ QMD索引已更新")
        except Exception as e:
            print(f"⚠️  QMD索引更新失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Image Content Extractor v2.0 - 统一图片内容提取",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 自动检测模式
  python3 extract.py /path/to/image.png

  # 指定终端模式
  python3 extract.py /path/to/terminal.png --mode terminal

  # 保存到知识库
  python3 extract.py /path/to/image.png -k -c testing -t "测试用例设计"

  # 批量处理
  python3 extract.py /path/to/images/ --batch
        """
    )
    
    parser.add_argument("image_path", help="图片路径或目录（批量模式）")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-m", "--mode", 
                       choices=["auto", "terminal", "document", "general"],
                       default="auto",
                       help="提取模式（默认：auto）")
    parser.add_argument("-k", "--knowledge-base", action="store_true",
                       help="保存到知识库")
    parser.add_argument("-c", "--category", default="uncategorized",
                       help="知识库分类")
    parser.add_argument("-t", "--title", help="文档标题")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="详细输出")
    parser.add_argument("--batch", action="store_true",
                       help="批量处理模式")
    
    args = parser.parse_args()
    
    # 初始化提取器
    extractor = ImageContentExtractor()
    
    # 批量处理
    if args.batch:
        if not os.path.isdir(args.image_path):
            print("❌ 批量模式需要指定目录")
            return 1
        
        # 支持的图片格式
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        image_files = [
            f for f in os.listdir(args.image_path)
            if os.path.splitext(f)[1].lower() in extensions
        ]
        
        print(f"📦 批量处理: {len(image_files)} 个文件")
        
        for i, img_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] {img_file}")
            img_path = os.path.join(args.image_path, img_file)
            
            result = extractor.extract(img_path, args.mode)
            
            if result["success"]:
                # 保存到知识库
                if args.knowledge_base:
                    title = args.title or os.path.splitext(img_file)[0]
                    extractor.save_to_knowledge_base(
                        result["markdown"],
                        title,
                        args.category
                    )
        
        print(f"\n✅ 批量处理完成！共 {len(image_files)} 个文件")
        return 0
    
    # 单个文件处理
    result = extractor.extract(args.image_path, args.mode)
    
    if not result["success"]:
        print(f"❌ 提取失败: {result.get('error', '未知错误')}")
        return 1
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result["markdown"])
        print(f"✅ 已保存: {args.output}")
    
    elif args.knowledge_base:
        title = args.title or os.path.splitext(os.path.basename(args.image_path))[0]
        extractor.save_to_knowledge_base(result["markdown"], title, args.category)
    
    # 详细输出
    if args.verbose:
        print("\n" + "=" * 50)
        print("📄 提取结果:")
        print("=" * 50)
        print(result["markdown"])
        print("\n" + "=" * 50)
        print(f"📊 统计:")
        print(f"   模式: {result['metadata']['mode']}")
        print(f"   块数: {result['metadata']['blocks_processed']}")
        print(f"   置信度: {result['metadata']['confidence']:.1%}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
