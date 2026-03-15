"""
Content Merger Module
内容合并模块
"""

from typing import List, Dict

class ContentMerger:
    """内容合并器"""
    
    def __init__(self, overlap_height: int = 100):
        """
        初始化合并器
        
        Args:
            overlap_height: 重叠区域高度（像素）
        """
        self.overlap_height = overlap_height
        # 估算重叠行数（假设每行约20像素高）
        self.overlap_lines = overlap_height // 20
    
    def merge(self, texts: List[str]) -> str:
        """
        智能合并文本
        
        Args:
            texts: 文本列表
        
        Returns:
            合并后的文本
        """
        if not texts:
            return ""
        
        if len(texts) == 1:
            return texts[0]
        
        # 智能合并
        merged = texts[0]
        
        for i in range(1, len(texts)):
            current = texts[i]
            merged = self._merge_two(merged, current)
        
        return merged
    
    def _merge_two(self, text1: str, text2: str) -> str:
        """合并两个文本块"""
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')
        
        # 查找最佳匹配（最大重叠）
        best_match = self._find_best_match(lines1, lines2)
        
        if best_match > 0:
            # 有重叠，去除重复部分
            merged_lines = lines1 + lines2[best_match:]
            return '\n'.join(merged_lines)
        else:
            # 无重叠，直接拼接
            return text1 + '\n\n' + text2
    
    def _find_best_match(self, lines1: List[str], lines2: List[str]) -> int:
        """
        查找最佳匹配位置
        
        Args:
            lines1: 第一个文本的行列表
            lines2: 第二个文本的行列表
        
        Returns:
            最佳匹配的行数（0表示无匹配）
        """
        best_match = 0
        max_search = min(len(lines1), len(lines2), self.overlap_lines * 2)
        
        for i in range(1, max_search + 1):
            # 检查后i行是否匹配前i行
            if self._lines_match(lines1[-i:], lines2[:i]):
                best_match = i
        
        return best_match
    
    def _lines_match(self, lines1: List[str], lines2: List[str]) -> bool:
        """
        检查两组行是否匹配
        
        Args:
            lines1: 第一组行
            lines2: 第二组行
        
        Returns:
            是否匹配
        """
        if len(lines1) != len(lines2):
            return False
        
        # 逐行比较（去除首尾空白）
        for l1, l2 in zip(lines1, lines2):
            if l1.strip() != l2.strip():
                return False
        
        return True
    
    def merge_with_confidence(self, results: List[Dict]) -> Dict:
        """
        带置信度的合并
        
        Args:
            results: OCR结果列表
        
        Returns:
            合并后的结果（包含置信度）
        """
        texts = [r["text"] for r in results if r.get("success")]
        confidences = [r.get("confidence", 0.9) for r in results if r.get("success")]
        
        if not texts:
            return {
                "success": False,
                "text": "",
                "confidence": 0
            }
        
        merged_text = self.merge(texts)
        
        # 计算平均置信度
        avg_confidence = sum(confidences) / len(confidences)
        
        return {
            "success": True,
            "text": merged_text,
            "confidence": avg_confidence,
            "blocks_merged": len(texts)
        }
