#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality Dashboard - 可视化质量监控

生成质量监控报告和可视化图表
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from collections import defaultdict


class QualityDashboard:
    """质量监控面板"""
    
    # 报告存储目录
    REPORTS_DIR = Path(__file__).parent.parent.parent / 'memory' / 'reports'
    
    def __init__(self):
        """初始化面板"""
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.evaluations: List[Dict] = []
    
    def record_evaluation(self, task: str, score: float, 
                          dimensions: Dict[str, float],
                          task_type: str = 'general',
                          metadata: Optional[Dict] = None):
        """
        记录评估结果
        
        Args:
            task: 任务描述
            score: 总分
            dimensions: 各维度分数
            task_type: 任务类型
            metadata: 元数据
        """
        evaluation = {
            'task': task,
            'score': score,
            'dimensions': dimensions,
            'task_type': task_type,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.evaluations.append(evaluation)
        self._save_evaluations()
    
    def get_quality_trend(self, days: int = 7) -> List[Dict]:
        """
        获取质量趋势
        
        Args:
            days: 天数
        
        Returns:
            List[Dict]: 每日平均分数
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in self.evaluations 
                  if datetime.fromisoformat(e['timestamp']) >= cutoff]
        
        # 按日期分组
        daily_scores = defaultdict(list)
        for e in recent:
            date = datetime.fromisoformat(e['timestamp']).date().isoformat()
            daily_scores[date].append(e['score'])
        
        # 计算每日平均
        trend = []
        for date in sorted(daily_scores.keys()):
            scores = daily_scores[date]
            trend.append({
                'date': date,
                'avg_score': sum(scores) / len(scores),
                'task_count': len(scores),
                'min_score': min(scores),
                'max_score': max(scores)
            })
        
        return trend
    
    def get_dimension_analysis(self) -> Dict[str, Any]:
        """
        获取维度分析
        
        Returns:
            Dict: 各维度统计
        """
        if not self.evaluations:
            return {'message': 'No data'}
        
        # 收集各维度分数
        dimension_scores = defaultdict(list)
        for e in self.evaluations:
            for dim, score in e['dimensions'].items():
                dimension_scores[dim].append(score)
        
        # 计算统计
        analysis = {}
        for dim, scores in dimension_scores.items():
            analysis[dim] = {
                'avg': sum(scores) / len(scores),
                'min': min(scores),
                'max': max(scores),
                'count': len(scores)
            }
        
        return analysis
    
    def get_task_type_performance(self) -> Dict[str, Any]:
        """
        获取任务类型表现
        
        Returns:
            Dict: 各任务类型统计
        """
        if not self.evaluations:
            return {'message': 'No data'}
        
        # 按任务类型分组
        type_scores = defaultdict(list)
        for e in self.evaluations:
            type_scores[e['task_type']].append(e['score'])
        
        # 计算统计
        performance = {}
        for task_type, scores in type_scores.items():
            performance[task_type] = {
                'avg_score': sum(scores) / len(scores),
                'task_count': len(scores),
                'success_rate': sum(1 for s in scores if s >= 7.0) / len(scores)
            }
        
        return performance
    
    def get_quality_distribution(self) -> Dict[str, int]:
        """
        获取质量分布
        
        Returns:
            Dict: 各等级数量
        """
        if not self.evaluations:
            return {'message': 'No data'}
        
        distribution = {
            'excellent': 0,  # 9-10
            'good': 0,       # 7-8
            'fair': 0,       # 5-6
            'poor': 0,       # 3-4
            'fail': 0        # 1-2
        }
        
        for e in self.evaluations:
            score = e['score']
            if score >= 9.0:
                distribution['excellent'] += 1
            elif score >= 7.0:
                distribution['good'] += 1
            elif score >= 5.0:
                distribution['fair'] += 1
            elif score >= 3.0:
                distribution['poor'] += 1
            else:
                distribution['fail'] += 1
        
        return distribution
    
    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """
        生成质量报告
        
        Args:
            days: 报告天数
        
        Returns:
            Dict: 完整报告
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'summary': self._generate_summary(days),
            'trend': self.get_quality_trend(days),
            'dimension_analysis': self.get_dimension_analysis(),
            'task_type_performance': self.get_task_type_performance(),
            'quality_distribution': self.get_quality_distribution(),
            'recommendations': self._generate_recommendations()
        }
        
        # 保存报告
        self._save_report(report)
        
        return report
    
    def _generate_summary(self, days: int) -> Dict[str, Any]:
        """生成摘要"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in self.evaluations 
                  if datetime.fromisoformat(e['timestamp']) >= cutoff]
        
        if not recent:
            return {'message': 'No data for this period'}
        
        scores = [e['score'] for e in recent]
        
        return {
            'total_tasks': len(recent),
            'avg_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'success_rate': sum(1 for s in scores if s >= 7.0) / len(scores),
            'excellent_rate': sum(1 for s in scores if s >= 9.0) / len(scores)
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if not self.evaluations:
            return recommendations
        
        # 分析维度
        dim_analysis = self.get_dimension_analysis()
        if dim_analysis and 'message' not in dim_analysis:
            # 找出最弱维度
            weakest_dim = min(dim_analysis.items(), 
                             key=lambda x: x[1]['avg'])
            if weakest_dim[1]['avg'] < 7.0:
                recommendations.append(
                    f"Focus on improving {weakest_dim[0]} "
                    f"(current avg: {weakest_dim[1]['avg']:.2f})"
                )
        
        # 分析任务类型
        type_perf = self.get_task_type_performance()
        if type_perf and 'message' not in type_perf:
            # 找出表现最差的任务类型
            worst_type = min(type_perf.items(),
                            key=lambda x: x[1]['avg_score'])
            if worst_type[1]['avg_score'] < 7.0:
                recommendations.append(
                    f"Review strategy for {worst_type[0]} "
                    f"(avg score: {worst_type[1]['avg_score']:.2f})"
                )
        
        # 分析趋势
        trend = self.get_quality_trend(7)
        if len(trend) >= 2:
            recent_avg = trend[-1]['avg_score']
            previous_avg = trend[-2]['avg_score']
            if recent_avg < previous_avg - 0.5:
                recommendations.append(
                    "Quality trend is declining, review recent changes"
                )
            elif recent_avg > previous_avg + 0.5:
                recommendations.append(
                    "Quality trend is improving, keep it up!"
                )
        
        return recommendations
    
    def _save_evaluations(self):
        """保存评估记录"""
        filepath = self.REPORTS_DIR / 'evaluations.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.evaluations, f, ensure_ascii=False, indent=2)
    
    def _save_report(self, report: Dict):
        """保存报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.REPORTS_DIR / f'quality_report_{timestamp}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def export_html_report(self, report: Dict = None) -> str:
        """
        导出 HTML 报告
        
        Args:
            report: 报告数据（可选，不指定则生成新报告）
        
        Returns:
            str: HTML 文件路径
        """
        if not report:
            report = self.generate_report()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Quality Dashboard Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }}
        .score {{ font-size: 2em; font-weight: bold; }}
        .excellent {{ color: #28a745; }}
        .good {{ color: #17a2b8; }}
        .fair {{ color: #ffc107; }}
        .poor {{ color: #fd7e14; }}
        .fail {{ color: #dc3545; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Quality Dashboard Report</h1>
    <p>Generated: {report['generated_at']}</p>
    <p>Period: {report['period_days']} days</p>
    
    <div class="card">
        <h2>Summary</h2>
        <p>Total Tasks: {report['summary'].get('total_tasks', 'N/A')}</p>
        <p>Average Score: <span class="score">{report['summary'].get('avg_score', 'N/A'):.2f}</span></p>
        <p>Success Rate: {report['summary'].get('success_rate', 0):.2%}</p>
        <p>Excellent Rate: {report['summary'].get('excellent_rate', 0):.2%}</p>
    </div>
    
    <div class="card">
        <h2>Dimension Analysis</h2>
        <table>
            <tr><th>Dimension</th><th>Average</th><th>Min</th><th>Max</th><th>Count</th></tr>
"""
        
        dim_analysis = report.get('dimension_analysis', {})
        if dim_analysis and 'message' not in dim_analysis:
            for dim, stats in dim_analysis.items():
                html_content += f"""
            <tr>
                <td>{dim}</td>
                <td>{stats['avg']:.2f}</td>
                <td>{stats['min']:.2f}</td>
                <td>{stats['max']:.2f}</td>
                <td>{stats['count']}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
    
    <div class="card">
        <h2>Quality Distribution</h2>
        <table>
            <tr><th>Level</th><th>Count</th></tr>
"""
        
        dist = report.get('quality_distribution', {})
        if dist and 'message' not in dist:
            for level, count in dist.items():
                html_content += f"""
            <tr><td>{level.upper()}</td><td>{count}</td></tr>
"""
        
        html_content += """
        </table>
    </div>
    
    <div class="card">
        <h2>Recommendations</h2>
        <ul>
"""
        
        for rec in report.get('recommendations', []):
            html_content += f"<li>{rec}</li>\n"
        
        html_content += """
        </ul>
    </div>
</body>
</html>
"""
        
        # 保存 HTML
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.REPORTS_DIR / f'quality_report_{timestamp}.html'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] HTML report saved to: {filepath}")
        return str(filepath)


# 使用示例
if __name__ == '__main__':
    import random
    
    dashboard = QualityDashboard()
    
    # 模拟评估数据
    task_types = ['software_installation', 'web_research', 'code_analysis', 'writing']
    for i in range(100):
        task_type = random.choice(task_types)
        score = random.uniform(5.0, 9.5)
        
        dashboard.record_evaluation(
            task=f"Task {i}",
            score=score,
            dimensions={
                'accuracy': min(1.0, score/10 + random.uniform(-0.1, 0.1)),
                'completeness': min(1.0, score/10 + random.uniform(-0.1, 0.1)),
                'efficiency': min(1.0, score/10 + random.uniform(-0.1, 0.1)),
                'reliability': min(1.0, score/10 + random.uniform(-0.1, 0.1)),
                'maintainability': min(1.0, score/10 + random.uniform(-0.1, 0.1))
            },
            task_type=task_type
        )
    
    # 生成报告
    report = dashboard.generate_report(days=7)
    
    print(f"Total tasks: {report['summary']['total_tasks']}")
    print(f"Average score: {report['summary']['avg_score']:.2f}")
    print(f"Success rate: {report['summary']['success_rate']:.2%}")
    
    # 导出 HTML
    html_path = dashboard.export_html_report(report)
    print(f"HTML report: {html_path}")
