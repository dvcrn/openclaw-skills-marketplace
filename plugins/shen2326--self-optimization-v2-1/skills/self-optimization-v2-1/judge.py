#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-as-Judge - 自动评估任务质量

使用 LLM 自动评估任务完成质量，给出评分和改进建议
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class EvaluationResult:
    """评估结果"""
    score: float  # 1-10 分
    accuracy: float  # 准确性 0-1
    completeness: float  # 完整性 0-1
    efficiency: float  # 效率 0-1
    reliability: float  # 可靠性 0-1
    maintainability: float  # 可维护性 0-1
    strengths: List[str]  # 优点
    weaknesses: List[str]  # 缺点
    suggestions: List[str]  # 改进建议
    evaluated_at: str  # 评估时间


class LLMJudge:
    """LLM-as-Judge 评估器"""
    
    # 评估维度权重
    WEIGHTS = {
        'accuracy': 0.30,      # 准确性 30%
        'completeness': 0.25,  # 完整性 25%
        'efficiency': 0.20,    # 效率 20%
        'reliability': 0.15,   # 可靠性 15%
        'maintainability': 0.10  # 可维护性 10%
    }
    
    # 评分标准
    SCORE_THRESHOLDS = {
        'excellent': 9.0,  # 9-10 分：优秀
        'good': 7.0,       # 7-8 分：良好
        'fair': 5.0,       # 5-6 分：一般
        'poor': 3.0,       # 3-4 分：较差
        'fail': 0.0        # 1-2 分：失败
    }
    
    @classmethod
    def evaluate(cls, task: str, result: str, expected: Optional[str] = None, 
                 context: Optional[Dict] = None) -> EvaluationResult:
        """
        评估任务完成质量
        
        Args:
            task: 任务描述
            result: 实际结果
            expected: 预期结果（可选）
            context: 执行上下文（可选）
        
        Returns:
            EvaluationResult: 评估结果
        """
        # 构建评估提示词
        prompt = cls._build_evaluation_prompt(task, result, expected, context)
        
        # 调用 LLM 进行评估（这里使用预设逻辑，实际应该调用 LLM）
        # TODO: 集成实际 LLM 调用
        evaluation_data = cls._simulate_llm_evaluation(task, result, expected, context)
        
        # 创建评估结果
        evaluation = EvaluationResult(
            score=evaluation_data['score'],
            accuracy=evaluation_data['dimensions']['accuracy'],
            completeness=evaluation_data['dimensions']['completeness'],
            efficiency=evaluation_data['dimensions']['efficiency'],
            reliability=evaluation_data['dimensions']['reliability'],
            maintainability=evaluation_data['dimensions']['maintainability'],
            strengths=evaluation_data['strengths'],
            weaknesses=evaluation_data['weaknesses'],
            suggestions=evaluation_data['suggestions'],
            evaluated_at=datetime.now().isoformat()
        )
        
        return evaluation
    
    @classmethod
    def _build_evaluation_prompt(cls, task: str, result: str, 
                                  expected: Optional[str], 
                                  context: Optional[Dict]) -> str:
        """构建评估提示词"""
        prompt = f"""You are an expert evaluator. Please evaluate the following task completion:

**Task:** {task}

**Result:**
{result}

"""
        if expected:
            prompt += f"""**Expected:**
{expected}

"""
        
        if context:
            prompt += f"""**Context:**
{json.dumps(context, indent=2)}

"""
        
        prompt += """**Evaluation Criteria:**
1. Accuracy (30%): Does the result match the requirements?
2. Completeness (25%): Are all requirements fulfilled?
3. Efficiency (20%): Was time and resources used wisely?
4. Reliability (15%): Is the result stable and error-free?
5. Maintainability (10%): Is the code/documentation well-organized?

**Output Format (JSON):**
{
    "score": 8.5,
    "dimensions": {
        "accuracy": 0.9,
        "completeness": 0.8,
        "efficiency": 0.85,
        "reliability": 0.9,
        "maintainability": 0.8
    },
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "suggestions": ["Suggestion 1", "Suggestion 2"]
}

Please provide your evaluation in the JSON format above."""
        
        return prompt
    
    @classmethod
    def _simulate_llm_evaluation(cls, task: str, result: str, 
                                   expected: Optional[str],
                                   context: Optional[Dict]) -> Dict:
        """
        模拟 LLM 评估（临时实现）
        
        TODO: 替换为实际 LLM 调用
        """
        # 简单启发式评估（临时方案）
        score = 7.5  # 默认良好
        
        # 检查是否有错误
        error_keywords = ['error', 'fail', 'exception', '错误', '失败']
        has_error = any(keyword in result.lower() for keyword in error_keywords)
        
        if has_error:
            score = 4.0
            dimensions = {
                'accuracy': 0.5,
                'completeness': 0.6,
                'efficiency': 0.5,
                'reliability': 0.3,
                'maintainability': 0.5
            }
            strengths = ['尝试了解决问题']
            weaknesses = ['存在错误', '需要改进']
            suggestions = ['分析错误原因', '修复问题后重试']
        else:
            # 成功完成
            score = 8.5
            dimensions = {
                'accuracy': 0.9,
                'completeness': 0.85,
                'efficiency': 0.8,
                'reliability': 0.9,
                'maintainability': 0.8
            }
            strengths = ['任务完成', '无明显错误', '结果合理']
            weaknesses = ['可能有优化空间']
            suggestions = ['可以考虑性能优化', '添加更多文档']
        
        return {
            'score': score,
            'dimensions': dimensions,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions
        }
    
    @classmethod
    def get_quality_level(cls, score: float) -> str:
        """根据分数获取质量等级"""
        if score >= cls.SCORE_THRESHOLDS['excellent']:
            return '优秀 (Excellent)'
        elif score >= cls.SCORE_THRESHOLDS['good']:
            return '良好 (Good)'
        elif score >= cls.SCORE_THRESHOLDS['fair']:
            return '一般 (Fair)'
        elif score >= cls.SCORE_THRESHOLDS['poor']:
            return '较差 (Poor)'
        else:
            return '失败 (Fail)'
    
    @classmethod
    def should_optimize(cls, score: float) -> bool:
        """判断是否需要优化"""
        return score < cls.SCORE_THRESHOLDS['good']
    
    @classmethod
    def must_analyze_error(cls, score: float) -> bool:
        """判断是否必须分析错误"""
        return score < cls.SCORE_THRESHOLDS['fair']


# 使用示例
if __name__ == '__main__':
    # 测试评估
    task = "安装 AIRI 应用并配置桥接服务"
    result = """
    成功完成：
    1. AIRI 已安装到 D:\\AIRI
    2. 桥接服务运行正常
    3. 虚拟人物显示在屏幕中央
    4. API 配置完成
    """
    
    evaluation = LLMJudge.evaluate(task, result)
    
    print(f"Task: {task}")
    print(f"Score: {evaluation.score}/10")
    print(f"Quality Level: {LLMJudge.get_quality_level(evaluation.score)}")
    print(f"Dimensions:")
    print(f"  Accuracy: {evaluation.accuracy}")
    print(f"  Completeness: {evaluation.completeness}")
    print(f"  Efficiency: {evaluation.efficiency}")
    print(f"  Reliability: {evaluation.reliability}")
    print(f"  Maintainability: {evaluation.maintainability}")
    print(f"Strengths: {evaluation.strengths}")
    print(f"Weaknesses: {evaluation.weaknesses}")
    print(f"Suggestions: {evaluation.suggestions}")
    print(f"Should Optimize: {LLMJudge.should_optimize(evaluation.score)}")
    print(f"Must Analyze Error: {LLMJudge.must_analyze_error(evaluation.score)}")
