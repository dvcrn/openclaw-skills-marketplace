#!/usr/bin/env python3
"""差异分析报告模块"""

import json
from datetime import datetime
from difflib import SequenceMatcher, unified_diff
from pathlib import Path
from typing import Dict, List, Optional


class DiffAnalyzer:
    """差异分析器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "diff_reports"
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def analyze_outputs(
        self,
        outputs: List[str],
        labels: List[str] = None,
        prompt: str = ""
    ) -> Dict:
        """分析多个输出的差异
        
        Args:
            outputs: 输出文本列表
            labels: 输出标签（可选）
            prompt: 原始提示词
        
        Returns:
            差异分析报告
        """
        if len(outputs) < 2:
            return {
                "error": "至少需要2个输出进行对比",
                "outputs_count": len(outputs)
            }
        
        if labels is None:
            labels = [f"输出{i+1}" for i in range(len(outputs))]
        
        # 计算两两相似度
        similarity_matrix = []
        for i in range(len(outputs)):
            row = []
            for j in range(len(outputs)):
                if i == j:
                    row.append(100.0)
                else:
                    similarity = SequenceMatcher(None, outputs[i], outputs[j]).ratio() * 100
                    row.append(round(similarity, 2))
            similarity_matrix.append(row)
        
        # 计算平均相似度
        avg_similarities = []
        for i in range(len(outputs)):
            other_sims = [similarity_matrix[i][j] for j in range(len(outputs)) if i != j]
            avg_similarities.append(round(sum(other_sims) / len(other_sims), 2) if other_sims else 0)
        
        # 找出最相似和最不相似的输出对
        max_similarity = 0
        min_similarity = 100
        max_pair = (0, 1)
        min_pair = (0, 1)
        
        for i in range(len(outputs)):
            for j in range(i+1, len(outputs)):
                sim = similarity_matrix[i][j]
                if sim > max_similarity:
                    max_similarity = sim
                    max_pair = (i, j)
                if sim < min_similarity:
                    min_similarity = sim
                    min_pair = (i, j)
        
        # 生成详细差异报告
        detailed_diffs = []
        for i in range(len(outputs)):
            for j in range(i+1, len(outputs)):
                diff = self._generate_diff(outputs[i], outputs[j], labels[i], labels[j])
                detailed_diffs.append({
                    "pair": (labels[i], labels[j]),
                    "similarity": similarity_matrix[i][j],
                    "diff_preview": diff[:500]  # 预览前500字符
                })
        
        return {
            "prompt": prompt[:200],
            "outputs_count": len(outputs),
            "labels": labels,
            "similarity_matrix": similarity_matrix,
            "average_similarities": avg_similarities,
            "overall_similarity": round(sum(avg_similarities) / len(avg_similarities), 2),
            "most_similar": {
                "pair": (labels[max_pair[0]], labels[max_pair[1]]),
                "similarity": max_similarity
            },
            "least_similar": {
                "pair": (labels[min_pair[0]], labels[min_pair[1]]),
                "similarity": min_similarity
            },
            "detailed_diffs": detailed_diffs,
            "consistency_level": self._get_consistency_level(
                sum(avg_similarities) / len(avg_similarities)
            )
        }
    
    def _generate_diff(self, text1: str, text2: str, label1: str, label2: str) -> str:
        """生成差异文本"""
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        diff = unified_diff(
            lines1, lines2,
            fromfile=label1,
            tofile=label2,
            lineterm=""
        )
        
        return ''.join(diff)
    
    def _get_consistency_level(self, avg_similarity: float) -> str:
        """获取一致性等级"""
        if avg_similarity >= 95:
            return "优秀"
        elif avg_similarity >= 85:
            return "良好"
        elif avg_similarity >= 70:
            return "一般"
        else:
            return "较差"
    
    def generate_report(
        self,
        outputs: List[str],
        labels: List[str] = None,
        prompt: str = "",
        output_format: str = "text"
    ) -> Dict:
        """生成完整报告
        
        Args:
            outputs: 输出文本列表
            labels: 输出标签
            prompt: 原始提示词
            output_format: 输出格式（text/json/html）
        
        Returns:
            报告生成结果
        """
        analysis = self.analyze_outputs(outputs, labels, prompt)
        
        if "error" in analysis:
            return analysis
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "json":
            report_path = self.output_dir / f"diff_report_{timestamp}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            return {
                "format": "json",
                "path": str(report_path),
                "analysis": analysis
            }
        
        elif output_format == "text":
            report_path = self.output_dir / f"diff_report_{timestamp}.txt"
            report_text = self._format_text_report(analysis)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            return {
                "format": "text",
                "path": str(report_path),
                "preview": report_text[:500],
                "analysis": analysis
            }
        
        elif output_format == "html":
            report_path = self.output_dir / f"diff_report_{timestamp}.html"
            report_html = self._format_html_report(analysis)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_html)
            
            return {
                "format": "html",
                "path": str(report_path),
                "analysis": analysis
            }
        
        else:
            return {"error": f"不支持的输出格式: {output_format}"}
    
    def _format_text_report(self, analysis: Dict) -> str:
        """格式化文本报告"""
        lines = [
            "=" * 60,
            "差异分析报告",
            "=" * 60,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"提示词: {analysis['prompt']}",
            f"输出数量: {analysis['outputs_count']}",
            f"整体相似度: {analysis['overall_similarity']}%",
            f"一致性等级: {analysis['consistency_level']}",
            "",
            "-" * 60,
            "相似度矩阵:",
            "-" * 60,
        ]
        
        # 添加矩阵表头
        header = "          " + "  ".join([f"{label:>10}" for label in analysis['labels']])
        lines.append(header)
        
        # 添加矩阵内容
        for i, row in enumerate(analysis['similarity_matrix']):
            row_str = f"{analysis['labels'][i]:>10} " + "  ".join([f"{val:>10.2f}" for val in row])
            lines.append(row_str)
        
        lines.extend([
            "",
            "-" * 60,
            "关键发现:",
            "-" * 60,
            f"最相似输出: {analysis['most_similar']['pair'][0]} & {analysis['most_similar']['pair'][1]}",
            f"  相似度: {analysis['most_similar']['similarity']}%",
            "",
            f"最不相似输出: {analysis['least_similar']['pair'][0]} & {analysis['least_similar']['pair'][1]}",
            f"  相似度: {analysis['least_similar']['similarity']}%",
            "",
            "-" * 60,
            "详细差异预览:",
            "-" * 60,
        ])
        
        for diff in analysis['detailed_diffs'][:3]:  # 只显示前3个
            lines.append(f"\n{diff['pair'][0]} vs {diff['pair'][1]}:")
            lines.append(f"相似度: {diff['similarity']}%")
            lines.append(f"差异预览:\n{diff['diff_preview']}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def _format_html_report(self, analysis: Dict) -> str:
        """格式化HTML报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>差异分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background-color: #4CAF50; color: white; }}
        .excellent {{ background-color: #4CAF50; color: white; }}
        .good {{ background-color: #2196F3; color: white; }}
        .average {{ background-color: #FFC107; color: black; }}
        .poor {{ background-color: #f44336; color: white; }}
        pre {{ background-color: #f5f5f5; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>差异分析报告</h1>
    <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>提示词:</strong> {analysis['prompt']}</p>
    <p><strong>输出数量:</strong> {analysis['outputs_count']}</p>
    <p><strong>整体相似度:</strong> {analysis['overall_similarity']}%</p>
    <p><strong>一致性等级:</strong> {analysis['consistency_level']}</p>
    
    <h2>相似度矩阵</h2>
    <table>
        <tr>
            <th></th>
            {''.join([f'<th>{label}</th>' for label in analysis['labels']])}
        </tr>
        {''.join([f'<tr><th>{analysis["labels"][i]}</th>' + ''.join([f'<td>{val:.2f}</td>' for val in row]) + '</tr>' for i, row in enumerate(analysis['similarity_matrix'])])}
    </table>
    
    <h2>关键发现</h2>
    <p><strong>最相似输出:</strong> {analysis['most_similar']['pair'][0]} & {analysis['most_similar']['pair'][1]} ({analysis['most_similar']['similarity']}%)</p>
    <p><strong>最不相似输出:</strong> {analysis['least_similar']['pair'][0]} & {analysis['least_similar']['pair'][1]} ({analysis['least_similar']['similarity']}%)</p>
</body>
</html>
"""
        return html


# ========== CLI命令 ==========

def diff_command(outputs: List[str], labels: List[str] = None, prompt: str = "", output_format: str = "text"):
    """差异分析命令"""
    analyzer = DiffAnalyzer()
    
    result = analyzer.generate_report(outputs, labels, prompt, output_format)
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return result
    
    print(f"\n📊 差异分析报告\n")
    print(f"输出数量: {result['analysis']['outputs_count']}")
    print(f"整体相似度: {result['analysis']['overall_similarity']}%")
    print(f"一致性等级: {result['analysis']['consistency_level']}")
    print(f"\n报告已保存: {result['path']}\n")
    
    if "preview" in result:
        print("报告预览:")
        print(result['preview'])
    
    return result
