#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A/B Testing Framework - A/B 测试框架

对不同的提示词/策略进行 A/B 测试，找出最佳方案
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict


@dataclass
class ABTestVariant:
    """A/B 测试变体"""
    id: str  # 变体 ID（A 或 B）
    name: str  # 变体名称
    content: str  # 内容（提示词/策略）
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTestResult:
    """A/B 测试结果"""
    variant_id: str
    task_id: str
    score: float
    metrics: Dict[str, float]
    completed_at: str


@dataclass
class ABTestReport:
    """A/B 测试报告"""
    test_id: str
    variant_a_wins: int
    variant_b_wins: int
    total_tests: int
    winner: str
    confidence: float
    avg_score_a: float
    avg_score_b: float
    statistical_significance: bool
    recommendation: str
    completed_at: str


class ABTestingFramework:
    """A/B 测试框架"""
    
    # 测试存储目录
    TESTS_DIR = Path(__file__).parent.parent.parent / 'memory' / 'ab_tests'
    
    # 最小样本量（达到统计显著性）
    MIN_SAMPLE_SIZE = 30
    
    # 置信度阈值
    CONFIDENCE_THRESHOLD = 0.95
    
    def __init__(self):
        """初始化框架"""
        self.TESTS_DIR.mkdir(parents=True, exist_ok=True)
        self.active_tests: Dict[str, Dict] = {}
        self.completed_tests: List[ABTestReport] = []
    
    def create_test(self, test_id: str, variant_a: ABTestVariant, 
                    variant_b: ABTestVariant, test_tasks: List[Dict],
                    metrics: Optional[List[str]] = None) -> Dict:
        """
        创建 A/B 测试
        
        Args:
            test_id: 测试 ID
            variant_a: 变体 A
            variant_b: 变体 B
            test_tasks: 测试任务列表
            metrics: 评估指标列表
        
        Returns:
            Dict: 测试配置
        """
        test_config = {
            'test_id': test_id,
            'variant_a': {
                'id': variant_a.id,
                'name': variant_a.name,
                'content': variant_a.content,
                'metadata': variant_a.metadata
            },
            'variant_b': {
                'id': variant_b.id,
                'name': variant_b.name,
                'content': variant_b.content,
                'metadata': variant_b.metadata
            },
            'test_tasks': test_tasks,
            'metrics': metrics or ['score', 'accuracy', 'efficiency'],
            'results': [],
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.active_tests[test_id] = test_config
        self._save_test(test_config)
        
        print(f"[OK] Created A/B test: {test_id}")
        print(f"  Variant A: {variant_a.name}")
        print(f"  Variant B: {variant_b.name}")
        print(f"  Test tasks: {len(test_tasks)}")
        
        return test_config
    
    def assign_variant(self, test_id: str) -> str:
        """
        为任务分配变体（随机）
        
        Args:
            test_id: 测试 ID
        
        Returns:
            str: 分配的变体 ID（A 或 B）
        """
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")
        
        return random.choice(['A', 'B'])
    
    def record_result(self, test_id: str, task_id: str, variant_id: str,
                      score: float, metrics: Dict[str, float] = None):
        """
        记录测试结果
        
        Args:
            test_id: 测试 ID
            task_id: 任务 ID
            variant_id: 变体 ID（A 或 B）
            score: 质量评分
            metrics: 详细指标
        """
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")
        
        result = ABTestResult(
            variant_id=variant_id,
            task_id=task_id,
            score=score,
            metrics=metrics or {'score': score},
            completed_at=datetime.now().isoformat()
        )
        
        # 添加到测试
        self.active_tests[test_id]['results'].append({
            'variant_id': variant_id,
            'task_id': task_id,
            'score': score,
            'metrics': metrics or {'score': score},
            'completed_at': result.completed_at
        })
        
        # 保存
        self._save_test(self.active_tests[test_id])
        
        print(f"[OK] Recorded result for {test_id}: {variant_id} scored {score}")
    
    def analyze_test(self, test_id: str) -> Optional[ABTestReport]:
        """
        分析测试结果
        
        Args:
            test_id: 测试 ID
        
        Returns:
            Optional[ABTestReport]: 测试报告，如果测试未完成则返回 None
        """
        if test_id not in self.active_tests:
            return None
        
        test = self.active_tests[test_id]
        results = test['results']
        
        # 分离 A/B 结果
        results_a = [r for r in results if r['variant_id'] == 'A']
        results_b = [r for r in results if r['variant_id'] == 'B']
        
        # 检查样本量
        total = len(results_a) + len(results_b)
        if total < self.MIN_SAMPLE_SIZE:
            print(f"[INFO] Not enough samples: {total}/{self.MIN_SAMPLE_SIZE}")
            return None
        
        # 计算平均分
        avg_score_a = sum(r['score'] for r in results_a) / len(results_a) if results_a else 0
        avg_score_b = sum(r['score'] for r in results_b) / len(results_b) if results_b else 0
        
        # 确定获胜者
        if avg_score_a > avg_score_b:
            winner = 'A'
            wins_a = len(results_a)
            wins_b = len(results_b)
        else:
            winner = 'B'
            wins_a = len(results_a)
            wins_b = len(results_b)
        
        # 计算置信度（简化版）
        score_diff = abs(avg_score_a - avg_score_b)
        confidence = min(1.0, score_diff / 2.0 + (total / 100.0))
        
        # 统计显著性（简化版 t 检验）
        statistical_significance = confidence >= self.CONFIDENCE_THRESHOLD
        
        # 生成建议
        if statistical_significance:
            recommendation = f"Variant {winner} is significantly better (confidence: {confidence:.2%})"
        else:
            recommendation = "Need more samples for statistical significance"
        
        # 创建报告
        report = ABTestReport(
            test_id=test_id,
            variant_a_wins=wins_a,
            variant_b_wins=wins_b,
            total_tests=total,
            winner=winner,
            confidence=confidence,
            avg_score_a=avg_score_a,
            avg_score_b=avg_score_b,
            statistical_significance=statistical_significance,
            recommendation=recommendation,
            completed_at=datetime.now().isoformat()
        )
        
        # 标记测试完成
        test['status'] = 'completed'
        self.completed_tests.append(report)
        self._save_test(test)
        self._save_report(report)
        
        print(f"[OK] A/B Test Analysis for {test_id}:")
        print(f"  Winner: Variant {winner}")
        print(f"  Avg Score A: {avg_score_a:.2f}")
        print(f"  Avg Score B: {avg_score_b:.2f}")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Statistically Significant: {statistical_significance}")
        
        return report
    
    def get_best_variant(self, test_id: str) -> Optional[str]:
        """
        获取最佳变体
        
        Args:
            test_id: 测试 ID
        
        Returns:
            Optional[str]: 最佳变体 ID，如果测试未完成则返回 None
        """
        report = self.analyze_test(test_id)
        if report and report.statistical_significance:
            return report.winner
        return None
    
    def _save_test(self, test_config: Dict):
        """保存测试配置"""
        filepath = self.TESTS_DIR / f"{test_config['test_id']}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
    
    def _save_report(self, report: ABTestReport):
        """保存测试报告"""
        filepath = self.TESTS_DIR / f"{report.test_id}_report.json"
        report_dict = {
            'test_id': report.test_id,
            'variant_a_wins': report.variant_a_wins,
            'variant_b_wins': report.variant_b_wins,
            'total_tests': report.total_tests,
            'winner': report.winner,
            'confidence': report.confidence,
            'avg_score_a': report.avg_score_a,
            'avg_score_b': report.avg_score_b,
            'statistical_significance': report.statistical_significance,
            'recommendation': report.recommendation,
            'completed_at': report.completed_at
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
    
    def get_all_tests(self) -> List[Dict]:
        """获取所有测试"""
        return list(self.active_tests.values()) + [
            {'test_id': r.test_id, 'winner': r.winner, 'completed_at': r.completed_at}
            for r in self.completed_tests
        ]
    
    def export_summary(self) -> Dict:
        """导出测试摘要"""
        return {
            'total_tests': len(self.active_tests) + len(self.completed_tests),
            'active_tests': len(self.active_tests),
            'completed_tests': len(self.completed_tests),
            'completed_reports': [
                {
                    'test_id': r.test_id,
                    'winner': r.winner,
                    'confidence': r.confidence,
                    'completed_at': r.completed_at
                }
                for r in self.completed_tests
            ]
        }


# 使用示例
if __name__ == '__main__':
    ab_framework = ABTestingFramework()
    
    # 创建测试
    test_config = ab_framework.create_test(
        test_id='prompt_optimization_test_1',
        variant_a=ABTestVariant(
            id='A',
            name='Original Prompt',
            content='帮我安装这个软件'
        ),
        variant_b=ABTestVariant(
            id='B',
            name='Optimized Prompt',
            content='''**目标:** 帮我安装这个软件

**约束:**
- 必须先查文档确认安装参数
- 使用静默安装或 UI 自动化
- 避免使用中文（编码问题）

**输出格式:** 按步骤执行并报告进度'''
        ),
        test_tasks=[{'id': f'task_{i}'} for i in range(50)],
        metrics=['score', 'accuracy', 'efficiency']
    )
    
    # 模拟测试结果
    for i in range(50):
        variant = ab_framework.assign_variant('prompt_optimization_test_1')
        score = 7.5 if variant == 'A' else 8.5  # B 版本更好
        ab_framework.record_result(
            test_id='prompt_optimization_test_1',
            task_id=f'task_{i}',
            variant_id=variant,
            score=score,
            metrics={'score': score, 'accuracy': score/10, 'efficiency': 0.8}
        )
    
    # 分析结果
    report = ab_framework.analyze_test('prompt_optimization_test_1')
    
    if report:
        print(f"\nRecommendation: {report.recommendation}")
        print(f"Best variant: {ab_framework.get_best_variant('prompt_optimization_test_1')}")
    
    # 导出摘要
    summary = ab_framework.export_summary()
    print(f"\nTotal tests: {summary['total_tests']}")
