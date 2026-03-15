#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Metrics - 更多评估维度

扩展评估维度，提供更全面的质量评估
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AdvancedEvaluation:
    """高级评估结果"""
    # 核心维度（原有）
    accuracy: float  # 准确性
    completeness: float  # 完整性
    efficiency: float  # 效率
    reliability: float  # 可靠性
    maintainability: float  # 可维护性
    
    # 新增维度
    creativity: float  # 创造性
    clarity: float  # 清晰度
    helpfulness: float  # 有帮助程度
    safety: float  # 安全性
    user_satisfaction: float  # 用户满意度
    
    # 综合评分
    overall_score: float
    
    # 评估时间
    evaluated_at: str


class AdvancedMetricsEvaluator:
    """高级评估器"""
    
    # 维度权重（可配置）
    CORE_WEIGHTS = {
        'accuracy': 0.25,      # 准确性 25%
        'completeness': 0.20,  # 完整性 20%
        'efficiency': 0.15,    # 效率 15%
        'reliability': 0.15,   # 可靠性 15%
        'maintainability': 0.10  # 可维护性 10%
    }
    
    ADVANCED_WEIGHTS = {
        'creativity': 0.05,    # 创造性 5%
        'clarity': 0.05,       # 清晰度 5%
        'helpfulness': 0.03,   # 有帮助程度 3%
        'safety': 0.02,        # 安全性 2%
        'user_satisfaction': 0.00  # 用户满意度（单独计算）
    }
    
    def __init__(self):
        """初始化评估器"""
        self.evaluation_history: List[AdvancedEvaluation] = []
    
    def evaluate(self, task: str, result: str, 
                 context: Optional[Dict] = None,
                 user_feedback: Optional[Dict] = None) -> AdvancedEvaluation:
        """
        进行全面评估
        
        Args:
            task: 任务描述
            result: 执行结果
            context: 执行上下文
            user_feedback: 用户反馈（可选）
        
        Returns:
            AdvancedEvaluation: 评估结果
        """
        context = context or {}
        
        # 评估核心维度
        core_scores = self._evaluate_core_dimensions(task, result, context)
        
        # 评估新增维度
        advanced_scores = self._evaluate_advanced_dimensions(task, result, context)
        
        # 计算综合评分
        overall_score = self._calculate_overall_score(core_scores, advanced_scores)
        
        # 如果有用户反馈，调整用户满意度
        if user_feedback:
            advanced_scores['user_satisfaction'] = user_feedback.get('satisfaction', 0.8)
            # 重新计算包含用户反馈的总分
            overall_score = self._calculate_overall_score(core_scores, advanced_scores, 
                                                           include_user_feedback=True)
        
        # 创建评估结果
        evaluation = AdvancedEvaluation(
            accuracy=core_scores['accuracy'],
            completeness=core_scores['completeness'],
            efficiency=core_scores['efficiency'],
            reliability=core_scores['reliability'],
            maintainability=core_scores['maintainability'],
            creativity=advanced_scores['creativity'],
            clarity=advanced_scores['clarity'],
            helpfulness=advanced_scores['helpfulness'],
            safety=advanced_scores['safety'],
            user_satisfaction=advanced_scores['user_satisfaction'],
            overall_score=overall_score,
            evaluated_at=datetime.now().isoformat()
        )
        
        self.evaluation_history.append(evaluation)
        
        return evaluation
    
    def _evaluate_core_dimensions(self, task: str, result: str, 
                                   context: Dict) -> Dict[str, float]:
        """评估核心维度"""
        # 这里使用启发式评估（实际应该调用 LLM）
        
        # 准确性：结果是否符合任务要求
        accuracy = self._assess_accuracy(task, result, context)
        
        # 完整性：是否完成所有要求
        completeness = self._assess_completeness(task, result, context)
        
        # 效率：资源使用情况
        efficiency = self._assess_efficiency(task, result, context)
        
        # 可靠性：是否稳定无错误
        reliability = self._assess_reliability(result, context)
        
        # 可维护性：代码/文档质量
        maintainability = self._assess_maintainability(result, context)
        
        return {
            'accuracy': accuracy,
            'completeness': completeness,
            'efficiency': efficiency,
            'reliability': reliability,
            'maintainability': maintainability
        }
    
    def _evaluate_advanced_dimensions(self, task: str, result: str,
                                       context: Dict) -> Dict[str, float]:
        """评估新增维度"""
        
        # 创造性：解决方案是否有创意
        creativity = self._assess_creativity(task, result, context)
        
        # 清晰度：表达是否清晰
        clarity = self._assess_clarity(result, context)
        
        # 有帮助程度：对用户是否有实际帮助
        helpfulness = self._assess_helpfulness(task, result, context)
        
        # 安全性：是否遵循安全最佳实践
        safety = self._assess_safety(task, result, context)
        
        # 用户满意度：默认值（实际应该从用户反馈获取）
        user_satisfaction = 0.8  # 默认良好
        
        return {
            'creativity': creativity,
            'clarity': clarity,
            'helpfulness': helpfulness,
            'safety': safety,
            'user_satisfaction': user_satisfaction
        }
    
    def _assess_accuracy(self, task: str, result: str, context: Dict) -> float:
        """评估准确性"""
        # 检查是否有错误关键词
        error_keywords = ['error', 'fail', 'exception', '错误', '失败']
        has_error = any(kw in result.lower() for kw in error_keywords)
        
        if has_error:
            return 0.5
        
        # 检查是否完成任务
        success_keywords = ['success', 'complete', 'done', '成功', '完成']
        has_success = any(kw in result.lower() for kw in success_keywords)
        
        return 0.9 if has_success else 0.7
    
    def _assess_completeness(self, task: str, result: str, context: Dict) -> float:
        """评估完整性"""
        # 检查结果长度（越长可能越完整）
        result_length = len(result)
        if result_length > 500:
            return 0.9
        elif result_length > 200:
            return 0.8
        elif result_length > 100:
            return 0.7
        else:
            return 0.6
    
    def _assess_efficiency(self, task: str, result: str, context: Dict) -> float:
        """评估效率"""
        # 检查执行时间（如果有）
        execution_time = context.get('execution_time', 0)
        
        if execution_time == 0:
            return 0.8  # 默认良好
        
        if execution_time < 60:  # 1 分钟内
            return 0.95
        elif execution_time < 300:  # 5 分钟内
            return 0.8
        else:
            return 0.6
    
    def _assess_reliability(self, result: str, context: Dict) -> float:
        """评估可靠性"""
        # 检查是否有重试
        retry_count = context.get('retry_count', 0)
        
        if retry_count == 0:
            return 0.95  # 一次成功
        elif retry_count <= 2:
            return 0.8  # 重试后成功
        else:
            return 0.6  # 多次重试
    
    def _assess_maintainability(self, result: str, context: Dict) -> float:
        """评估可维护性"""
        # 检查是否有文档/注释
        doc_keywords = ['documentation', 'comment', 'note', '文档', '注释', '说明']
        has_docs = any(kw in result.lower() for kw in doc_keywords)
        
        # 检查是否有结构化输出
        structure_keywords = ['step', 'list', '```', '##', '步骤', '列表']
        has_structure = any(kw in result.lower() for kw in structure_keywords)
        
        if has_docs and has_structure:
            return 0.9
        elif has_structure:
            return 0.8
        else:
            return 0.7
    
    def _assess_creativity(self, task: str, result: str, context: Dict) -> float:
        """评估创造性"""
        # 检查是否有创新解决方案
        creativity_keywords = ['innovative', 'creative', 'novel', '新', '创新', '独特']
        has_creativity = any(kw in result.lower() for kw in creativity_keywords)
        
        # 检查是否使用了多种工具
        tools_used = context.get('tools_used', [])
        tool_diversity = len(set(tools_used)) / 5.0  # 假设最多使用 5 种工具
        
        return min(1.0, 0.7 + (0.2 if has_creativity else 0) + (tool_diversity * 0.2))
    
    def _assess_clarity(self, result: str, context: Dict) -> float:
        """评估清晰度"""
        # 检查是否有清晰的标题/分段
        clarity_keywords = ['##', '###', '**', '步骤', '第一', '第二']
        has_clarity = any(kw in result for kw in clarity_keywords)
        
        # 检查句子长度（适中最好）
        sentences = result.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        
        clarity_score = 0.8 if has_clarity else 0.6
        
        # 句子长度适中加分
        if 10 <= avg_sentence_length <= 30:
            clarity_score += 0.1
        
        return min(1.0, clarity_score)
    
    def _assess_helpfulness(self, task: str, result: str, context: Dict) -> float:
        """评估有帮助程度"""
        # 检查是否提供了可操作的建议
        actionable_keywords = ['should', 'recommend', 'suggest', '建议', '应该', '可以']
        has_actionable = any(kw in result.lower() for kw in actionable_keywords)
        
        # 检查是否解决了问题
        solution_keywords = ['solve', 'fix', 'resolve', '解决', '修复']
        has_solution = any(kw in result.lower() for kw in solution_keywords)
        
        if has_actionable and has_solution:
            return 0.9
        elif has_solution:
            return 0.8
        else:
            return 0.7
    
    def _assess_safety(self, task: str, result: str, context: Dict) -> float:
        """评估安全性"""
        # 检查是否有危险操作
        danger_keywords = ['rm -rf', 'sudo', 'delete', 'drop', '删除', '格式化']
        has_danger = any(kw in result.lower() for kw in danger_keywords)
        
        if has_danger:
            # 检查是否有警告/确认
            warning_keywords = ['backup', 'confirm', 'careful', '备份', '确认', '小心']
            has_warning = any(kw in result.lower() for kw in warning_keywords)
            
            return 0.7 if has_warning else 0.5
        
        return 0.95  # 默认安全
    
    def _calculate_overall_score(self, core_scores: Dict[str, float],
                                  advanced_scores: Dict[str, float],
                                  include_user_feedback: bool = False) -> float:
        """计算综合评分"""
        # 核心维度分数
        core_score = sum(
            core_scores[dim] * weight 
            for dim, weight in self.CORE_WEIGHTS.items()
        )
        
        # 高级维度分数
        advanced_score = sum(
            advanced_scores[dim] * weight 
            for dim, weight in self.ADVANCED_WEIGHTS.items()
        )
        
        # 综合评分（核心 85% + 高级 15%）
        overall = core_score * 0.85 + advanced_score * 0.15
        
        # 如果包含用户反馈，调整评分
        if include_user_feedback:
            user_sat = advanced_scores['user_satisfaction']
            overall = overall * 0.8 + user_sat * 0.2
        
        return min(10.0, overall * 10)  # 转换为 10 分制
    
    def get_dimension_report(self, evaluation: AdvancedEvaluation) -> Dict[str, Any]:
        """
        获取维度报告
        
        Args:
            evaluation: 评估结果
        
        Returns:
            Dict: 维度报告
        """
        return {
            'core_dimensions': {
                'accuracy': evaluation.accuracy,
                'completeness': evaluation.completeness,
                'efficiency': evaluation.efficiency,
                'reliability': evaluation.reliability,
                'maintainability': evaluation.maintainability
            },
            'advanced_dimensions': {
                'creativity': evaluation.creativity,
                'clarity': evaluation.clarity,
                'helpfulness': evaluation.helpfulness,
                'safety': evaluation.safety,
                'user_satisfaction': evaluation.user_satisfaction
            },
            'overall_score': evaluation.overall_score,
            'strengths': self._identify_strengths(evaluation),
            'weaknesses': self._identify_weaknesses(evaluation)
        }
    
    def _identify_strengths(self, evaluation: AdvancedEvaluation) -> List[str]:
        """识别优势"""
        strengths = []
        
        all_dims = {
            'accuracy': evaluation.accuracy,
            'completeness': evaluation.completeness,
            'efficiency': evaluation.efficiency,
            'reliability': evaluation.reliability,
            'maintainability': evaluation.maintainability,
            'creativity': evaluation.creativity,
            'clarity': evaluation.clarity,
            'helpfulness': evaluation.helpfulness,
            'safety': evaluation.safety,
            'user_satisfaction': evaluation.user_satisfaction
        }
        
        for dim, score in all_dims.items():
            if score >= 0.9:
                strengths.append(f"Excellent {dim}")
        
        return strengths
    
    def _identify_weaknesses(self, evaluation: AdvancedEvaluation) -> List[str]:
        """识别弱点"""
        weaknesses = []
        
        all_dims = {
            'accuracy': evaluation.accuracy,
            'completeness': evaluation.completeness,
            'efficiency': evaluation.efficiency,
            'reliability': evaluation.reliability,
            'maintainability': evaluation.maintainability,
            'creativity': evaluation.creativity,
            'clarity': evaluation.clarity,
            'helpfulness': evaluation.helpfulness,
            'safety': evaluation.safety,
            'user_satisfaction': evaluation.user_satisfaction
        }
        
        for dim, score in all_dims.items():
            if score < 0.7:
                weaknesses.append(f"Needs improvement in {dim}")
        
        return weaknesses


# 使用示例
if __name__ == '__main__':
    evaluator = AdvancedMetricsEvaluator()
    
    # 测试评估
    task = "安装 AIRI 应用并配置桥接服务"
    result = """
    成功完成：
    1. AIRI 已安装到 D:\\AIRI
    2. 桥接服务运行正常
    3. 虚拟人物显示在屏幕中央
    4. API 配置完成
    
    **文档:** 已创建完整的使用说明
    **步骤:** 按顺序执行，一次成功
    """
    
    context = {
        'execution_time': 120,  # 2 分钟
        'retry_count': 0,
        'tools_used': ['exec', 'web_fetch', 'file_write']
    }
    
    evaluation = evaluator.evaluate(task, result, context)
    
    print(f"Overall Score: {evaluation.overall_score:.2f}/10")
    print(f"\nCore Dimensions:")
    print(f"  Accuracy: {evaluation.accuracy:.2f}")
    print(f"  Completeness: {evaluation.completeness:.2f}")
    print(f"  Efficiency: {evaluation.efficiency:.2f}")
    print(f"  Reliability: {evaluation.reliability:.2f}")
    print(f"  Maintainability: {evaluation.maintainability:.2f}")
    
    print(f"\nAdvanced Dimensions:")
    print(f"  Creativity: {evaluation.creativity:.2f}")
    print(f"  Clarity: {evaluation.clarity:.2f}")
    print(f"  Helpfulness: {evaluation.helpfulness:.2f}")
    print(f"  Safety: {evaluation.safety:.2f}")
    print(f"  User Satisfaction: {evaluation.user_satisfaction:.2f}")
    
    # 获取维度报告
    report = evaluator.get_dimension_report(evaluation)
    print(f"\nStrengths: {report['strengths']}")
    print(f"Weaknesses: {report['weaknesses']}")
