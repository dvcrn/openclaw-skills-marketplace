#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Optimization System V2.1 - Enhanced

自我优化系统 - 包含：
- LLM-as-Judge: 自动评估循环
- Prompt Optimizer: 提示词自动优化
- Strategy Learner: 策略学习效果
- A/B Testing: A/B 测试框架（新增）
- Quality Dashboard: 可视化质量监控（新增）
- Advanced Metrics: 更多评估维度（新增）
"""

from .judge import LLMJudge, EvaluationResult
from .prompt_optimizer import PromptOptimizer, OptimizationResult
from .strategy_learner import StrategyLearner, Strategy, StrategyRecommendation
from .ab_testing import ABTestingFramework, ABTestVariant, ABTestReport
from .quality_dashboard import QualityDashboard
from .advanced_metrics import AdvancedMetricsEvaluator, AdvancedEvaluation


class SelfOptimizationSystem:
    """
    自我优化系统 V2.1 - 整合所有模块（增强版）
    """
    
    def __init__(self):
        """初始化系统"""
        self.judge = LLMJudge()
        self.optimizer = PromptOptimizer()
        self.learner = StrategyLearner()
        self.ab_testing = ABTestingFramework()
        self.dashboard = QualityDashboard()
        self.advanced_metrics = AdvancedMetricsEvaluator()
    
    def execute_task(self, task: str, result: str, 
                     expected: str = None, context: dict = None,
                     user_feedback: dict = None) -> dict:
        """
        执行任务并进行完整优化循环（增强版）
        
        Args:
            task: 任务描述
            result: 执行结果
            expected: 预期结果（可选）
            context: 执行上下文（可选）
            user_feedback: 用户反馈（可选）
        
        Returns:
            dict: 包含评估、优化、学习、A/B 测试结果
        """
        context = context or {}
        
        # 1. LLM 评估
        evaluation = self.judge.evaluate(task, result, expected, context)
        
        # 2. 高级评估（新增）
        advanced_eval = self.advanced_metrics.evaluate(
            task, result, context, user_feedback
        )
        
        # 3. 记录到质量监控面板（新增）
        self.dashboard.record_evaluation(
            task=task,
            score=advanced_eval.overall_score,
            dimensions={
                'accuracy': advanced_eval.accuracy,
                'completeness': advanced_eval.completeness,
                'efficiency': advanced_eval.efficiency,
                'reliability': advanced_eval.reliability,
                'maintainability': advanced_eval.maintainability,
                'creativity': advanced_eval.creativity,
                'clarity': advanced_eval.clarity,
                'helpfulness': advanced_eval.helpfulness,
                'safety': advanced_eval.safety,
                'user_satisfaction': advanced_eval.user_satisfaction
            },
            task_type=context.get('task_type', 'general'),
            metadata=context
        )
        
        # 4. 如果需要优化，优化提示词
        optimizations = []
        optimized_prompts = []
        if self.judge.should_optimize(evaluation.score):
            original_prompt = context.get('prompt', task)
            optimization = self.optimizer.optimize(
                task, original_prompt, result, evaluation.score
            )
            optimizations.append(optimization)
            optimized_prompts.append(optimization.optimized_prompt)
        
        # 5. 记录策略
        strategy_info = {
            'steps': context.get('steps', []),
            'tools_used': context.get('tools_used', []),
            'error_handling': context.get('error_handling', 'default')
        }
        
        self.learner.record_strategy(
            task_type=context.get('task_type', 'general'),
            strategy=strategy_info,
            success=evaluation.score >= 7.0,
            quality_score=evaluation.score,
            context=context
        )
        
        # 6. 获取策略推荐
        strategy_recommendation = self.learner.get_strategy_for_task(
            task_type=context.get('task_type', 'general'),
            task_description=task
        )
        
        # 7. 构建返回结果（增强版）
        return_result = {
            'task': task,
            'evaluation': {
                'score': evaluation.score,
                'quality_level': self.judge.get_quality_level(evaluation.score),
                'dimensions': {
                    'accuracy': evaluation.accuracy,
                    'completeness': evaluation.completeness,
                    'efficiency': evaluation.efficiency,
                    'reliability': evaluation.reliability,
                    'maintainability': evaluation.maintainability
                },
                'strengths': evaluation.strengths,
                'weaknesses': evaluation.weaknesses,
                'suggestions': evaluation.suggestions
            },
            'advanced_evaluation': {
                'overall_score': advanced_eval.overall_score,
                'dimensions': {
                    'creativity': advanced_eval.creativity,
                    'clarity': advanced_eval.clarity,
                    'helpfulness': advanced_eval.helpfulness,
                    'safety': advanced_eval.safety,
                    'user_satisfaction': advanced_eval.user_satisfaction
                },
                'strengths': self.advanced_metrics.get_dimension_report(advanced_eval)['strengths'],
                'weaknesses': self.advanced_metrics.get_dimension_report(advanced_eval)['weaknesses']
            },
            'optimizations': [asdict(opt) for opt in optimizations] if optimizations else [],
            'optimized_prompts': optimized_prompts,
            'learned_strategies': {
                'recorded': True,
                'success': evaluation.score >= 7.0
            },
            'strategy_recommendation': {
                'available': strategy_recommendation is not None,
                'confidence': strategy_recommendation.confidence if strategy_recommendation else 0,
                'reason': strategy_recommendation.reason if strategy_recommendation else ''
            } if strategy_recommendation else None,
            'quality_dashboard': {
                'recorded': True,
                'report_available': True
            }
        }
        
        return return_result
    
    def get_quality_report(self, task_type: str = None) -> dict:
        """
        获取质量报告
        
        Args:
            task_type: 任务类型（可选，不指定则返回所有）
        
        Returns:
            dict: 质量报告
        """
        all_strategies = self.learner.get_all_strategies(task_type)
        
        if not all_strategies:
            return {'message': '暂无数据'}
        
        # 计算统计
        total = len(all_strategies)
        success_count = sum(1 for s in all_strategies if s.success)
        avg_score = sum(s.quality_score for s in all_strategies) / total
        
        return {
            'total_tasks': total,
            'success_count': success_count,
            'failure_count': total - success_count,
            'success_rate': success_count / total if total > 0 else 0,
            'average_quality_score': avg_score,
            'quality_level': '优秀' if avg_score >= 9.0 else '良好' if avg_score >= 7.0 else '一般'
        }


# 导出所有类和函数
__all__ = [
    'SelfOptimizationSystem',
    'LLMJudge',
    'EvaluationResult',
    'PromptOptimizer',
    'OptimizationResult',
    'StrategyLearner',
    'Strategy',
    'StrategyRecommendation'
]


# 使用示例
if __name__ == '__main__':
    from dataclasses import asdict
    
    # 初始化系统
    system = SelfOptimizationSystem()
    
    # 执行任务
    result = system.execute_task(
        task="安装 AIRI 应用并配置桥接服务",
        result="""
        成功完成：
        1. AIRI 已安装到 D:\\AIRI
        2. 桥接服务运行正常
        3. 虚拟人物显示在屏幕中央
        4. API 配置完成
        """,
        context={
            'task_type': 'software_installation',
            'steps': [
                'download_installer',
                'run_silent_install',
                'configure_bridge',
                'test_connection'
            ],
            'tools_used': ['exec', 'web_fetch'],
            'error_handling': 'retry_with_ui_automation',
            'prompt': '帮我安装这个软件'
        }
    )
    
    # 打印结果
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 获取质量报告
    report = system.get_quality_report('software_installation')
    print("\n质量报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
