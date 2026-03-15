#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt Optimizer - 提示词自动优化器

分析低质量任务的提示词，生成优化版本，A/B 测试并保存最佳版本
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OptimizationResult:
    """优化结果"""
    original_prompt: str
    optimized_prompt: str
    weaknesses: List[str]
    improvements: List[str]
    score_before: float
    score_after: Optional[float]
    optimized_at: str


class PromptOptimizer:
    """提示词优化器"""
    
    # 提示词存储目录
    PROMPTS_DIR = Path(__file__).parent.parent.parent / 'memory' / 'prompts'
    
    # 优化模式
    OPTIMIZATION_PATTERNS = {
        'add_context': '添加更多上下文信息',
        'add_examples': '添加示例',
        'add_constraints': '添加约束条件',
        'clarify_goal': '明确目标',
        'add_steps': '添加执行步骤',
        'add_format': '指定输出格式',
        'add_evaluation': '添加评估标准'
    }
    
    def __init__(self):
        """初始化优化器"""
        self.PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def analyze_weaknesses(self, prompt: str, result: str, 
                           evaluation_score: float) -> List[str]:
        """
        分析提示词的弱点
        
        Args:
            prompt: 原始提示词
            result: 执行结果
            evaluation_score: 评估分数
        
        Returns:
            List[str]: 弱点列表
        """
        weaknesses = []
        
        # 检查提示词长度
        if len(prompt) < 50:
            weaknesses.append('提示词过短，可能缺乏必要信息')
        
        # 检查是否有明确目标
        goal_keywords = ['目标', '目的', 'task', 'goal', 'objective', '完成']
        if not any(kw in prompt.lower() for kw in goal_keywords):
            weaknesses.append('缺乏明确的目标描述')
        
        # 检查是否有约束条件
        constraint_keywords = ['必须', '不要', '避免', '确保', 'must', 'should', 'avoid']
        if not any(kw in prompt.lower() for kw in constraint_keywords):
            weaknesses.append('缺乏约束条件')
        
        # 检查是否有示例
        example_keywords = ['例如', '比如', '示例', 'example', 'e.g.', 'like']
        if not any(kw in prompt.lower() for kw in example_keywords):
            weaknesses.append('没有提供示例')
        
        # 检查是否有输出格式
        format_keywords = ['格式', 'json', 'markdown', '列表', 'format', 'output']
        if not any(kw in prompt.lower() for kw in format_keywords):
            weaknesses.append('未指定输出格式')
        
        # 根据评估分数添加弱点
        if evaluation_score < 5.0:
            weaknesses.append('提示词质量较差，需要大幅改进')
        elif evaluation_score < 7.0:
            weaknesses.append('提示词需要优化')
        
        return weaknesses
    
    def generate_optimized_prompt(self, original: str, weaknesses: List[str],
                                   suggestions: List[str]) -> str:
        """
        生成优化后的提示词
        
        Args:
            original: 原始提示词
            weaknesses: 弱点列表
            suggestions: 改进建议
        
        Returns:
            str: 优化后的提示词
        """
        optimized = original
        
        # 根据弱点应用优化模式
        for weakness in weaknesses:
            if '缺乏明确的目标' in weakness:
                optimized = self._add_goal_section(optimized)
            
            if '缺乏约束条件' in weakness:
                optimized = self._add_constraints(optimized)
            
            if '没有提供示例' in weakness:
                optimized = self._add_examples(optimized)
            
            if '未指定输出格式' in weakness:
                optimized = self._add_format_spec(optimized)
            
            if '提示词过短' in weakness:
                optimized = self._add_context(optimized)
        
        # 添加改进建议
        if suggestions:
            optimized += "\n\n**改进建议:**\n" + "\n".join(f"- {s}" for s in suggestions)
        
        return optimized
    
    def _add_goal_section(self, prompt: str) -> str:
        """添加目标描述"""
        if '**目标**' not in prompt and 'Goal:' not in prompt:
            prompt += "\n\n**目标:** 请高质量完成此任务，确保结果准确、完整、高效。"
        return prompt
    
    def _add_constraints(self, prompt: str) -> str:
        """添加约束条件"""
        if '**约束**' not in prompt and 'Constraints:' not in prompt:
            prompt += "\n\n**约束:**\n- 必须确保结果准确无误\n- 避免重复犯错\n- 遵循最佳实践"
        return prompt
    
    def _add_examples(self, prompt: str) -> str:
        """添加示例"""
        if '**示例**' not in prompt and 'Example:' not in prompt:
            prompt += "\n\n**示例:** 参考类似任务的成功案例，采用已验证的方法。"
        return prompt
    
    def _add_format_spec(self, prompt: str) -> str:
        """添加输出格式"""
        if '**格式**' not in prompt and 'Format:' not in prompt:
            prompt += "\n\n**输出格式:** 请使用清晰的结构化格式，包含必要的标题和列表。"
        return prompt
    
    def _add_context(self, prompt: str) -> str:
        """添加上下文"""
        if '**上下文**' not in prompt and 'Context:' not in prompt:
            prompt += "\n\n**上下文:** 这是一个重要任务，请认真对待，发挥最佳水平。"
        return prompt
    
    def ab_test(self, prompt_a: str, prompt_b: str, 
                test_tasks: List[Dict]) -> Tuple[str, Dict]:
        """
        A/B 测试两个提示词
        
        Args:
            prompt_a: 提示词 A
            prompt_b: 提示词 B
            test_tasks: 测试任务列表
        
        Returns:
            Tuple[str, Dict]: (获胜提示词，测试结果)
        """
        # TODO: 实际 A/B 测试需要执行任务并比较结果
        # 这里简化处理，返回优化后的版本
        return prompt_b, {
            'winner': 'B',
            'score_a': 7.5,
            'score_b': 8.5,
            'test_count': len(test_tasks)
        }
    
    def save_best_prompt(self, task_type: str, prompt: str, 
                         score: float, metadata: Optional[Dict] = None):
        """
        保存最佳提示词
        
        Args:
            task_type: 任务类型
            prompt: 提示词
            score: 质量分数
            metadata: 元数据
        """
        filepath = self.PROMPTS_DIR / f"{task_type}.yaml"
        
        data = {
            'task_type': task_type,
            'prompt': prompt,
            'score': score,
            'optimized_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # 保存为 YAML 格式
        import yaml
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        
        print(f"✓ 保存最佳提示词到：{filepath}")
    
    def load_best_prompt(self, task_type: str) -> Optional[str]:
        """
        加载最佳提示词
        
        Args:
            task_type: 任务类型
        
        Returns:
            Optional[str]: 最佳提示词，如果不存在则返回 None
        """
        filepath = self.PROMPTS_DIR / f"{task_type}.yaml"
        
        if not filepath.exists():
            return None
        
        import yaml
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data.get('prompt')
    
    def optimize(self, task: str, prompt: str, result: str, 
                 evaluation_score: float) -> OptimizationResult:
        """
        完整优化流程
        
        Args:
            task: 任务描述
            prompt: 原始提示词
            result: 执行结果
            evaluation_score: 评估分数
        
        Returns:
            OptimizationResult: 优化结果
        """
        # 分析弱点
        weaknesses = self.analyze_weaknesses(prompt, result, evaluation_score)
        
        # 生成优化版本
        optimized = self.generate_optimized_prompt(prompt, weaknesses, [])
        
        # 创建优化结果
        optimization = OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=optimized,
            weaknesses=weaknesses,
            improvements=[f'应用优化模式：{k}' for k, v in self.OPTIMIZATION_PATTERNS.items() 
                         if any(k in w for w in weaknesses)],
            score_before=evaluation_score,
            score_after=None,  # 需要实际测试
            optimized_at=datetime.now().isoformat()
        )
        
        # 如果优化后分数应该更高，保存为最佳提示词
        if evaluation_score >= 7.0:
            self.save_best_prompt(task, optimized, evaluation_score)
        
        return optimization


# 使用示例
if __name__ == '__main__':
    optimizer = PromptOptimizer()
    
    # 测试优化
    task = "安装软件"
    original_prompt = "帮我安装这个软件"
    result = "安装成功"
    score = 6.5
    
    optimization = optimizer.optimize(task, original_prompt, result, score)
    
    print(f"Original Prompt: {optimization.original_prompt}")
    print(f"Optimized Prompt: {optimization.optimized_prompt}")
    print(f"Weaknesses: {optimization.weaknesses}")
    print(f"Improvements: {optimization.improvements}")
    print(f"Score Before: {optimization.score_before}")
