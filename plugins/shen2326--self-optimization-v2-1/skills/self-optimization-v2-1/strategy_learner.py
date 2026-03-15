#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strategy Learner - 策略学习器

记录任务执行策略，分析成功/失败模式，学习最佳实践，推荐策略给类似任务
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict


@dataclass
class Strategy:
    """策略"""
    task_type: str
    steps: List[str]
    tools_used: List[str]
    error_handling: str
    success: bool
    quality_score: float
    executed_at: str
    context: Dict[str, Any] = field(default_factory=dict)
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class StrategyRecommendation:
    """策略推荐"""
    strategy: Strategy
    confidence: float  # 置信度 0-1
    reason: str
    similar_tasks: int


class StrategyLearner:
    """策略学习器"""
    
    # 策略存储目录
    STRATEGIES_DIR = Path(__file__).parent.parent.parent / 'memory' / 'strategies'
    
    # 策略库
    def __init__(self):
        """初始化学习器"""
        self.STRATEGIES_DIR.mkdir(parents=True, exist_ok=True)
        self.strategy_history: List[Strategy] = []
        self.success_patterns: Dict[str, List[Strategy]] = defaultdict(list)
        self.failure_patterns: Dict[str, List[Strategy]] = defaultdict(list)
    
    def record_strategy(self, task_type: str, strategy: Dict[str, Any],
                        success: bool, quality_score: float,
                        context: Optional[Dict] = None):
        """
        记录任务执行策略
        
        Args:
            task_type: 任务类型
            strategy: 策略详情
            success: 是否成功
            quality_score: 质量分数
            context: 执行上下文
        """
        strat = Strategy(
            task_type=task_type,
            steps=strategy.get('steps', []),
            tools_used=strategy.get('tools_used', []),
            error_handling=strategy.get('error_handling', 'default'),
            success=success,
            quality_score=quality_score,
            executed_at=datetime.now().isoformat(),
            context=context or {},
            lessons_learned=[]
        )
        
        # 添加到历史
        self.strategy_history.append(strat)
        
        # 分类到成功/失败模式
        if success and quality_score >= 7.0:
            self.success_patterns[task_type].append(strat)
        else:
            self.failure_patterns[task_type].append(strat)
        
        # 提取经验教训
        strat.lessons_learned = self._extract_lessons(strat)
        
        # 保存到文件
        self._save_strategy(strat)
        
        print(f"[OK] Recorded strategy: {task_type} (Success: {success}, Score: {quality_score})")
    
    def _extract_lessons(self, strategy: Strategy) -> List[str]:
        """从策略中提取经验教训"""
        lessons = []
        
        if strategy.success:
            # 成功经验
            if strategy.quality_score >= 9.0:
                lessons.append(f"优秀实践：{', '.join(strategy.tools_used)} 组合使用效果好")
            
            if len(strategy.steps) <= 5:
                lessons.append("简洁的执行步骤更有效")
            
            if 'retry' in strategy.error_handling.lower():
                lessons.append("重试机制帮助克服了困难")
        else:
            # 失败教训
            lessons.append("需要改进执行策略")
            
            if not strategy.steps:
                lessons.append("缺乏明确的执行步骤")
            
            if strategy.error_handling == 'default':
                lessons.append("需要更好的错误处理策略")
        
        return lessons
    
    def _save_strategy(self, strategy: Strategy):
        """保存策略到文件"""
        # 按任务类型保存
        task_type_file = self.STRATEGIES_DIR / f"{strategy.task_type.replace(' ', '_')}.json"
        
        # 读取现有策略
        strategies_data = []
        if task_type_file.exists():
            with open(task_type_file, 'r', encoding='utf-8') as f:
                strategies_data = json.load(f)
        
        # 添加新策略
        strategies_data.append({
            'task_type': strategy.task_type,
            'steps': strategy.steps,
            'tools_used': strategy.tools_used,
            'error_handling': strategy.error_handling,
            'success': strategy.success,
            'quality_score': strategy.quality_score,
            'executed_at': strategy.executed_at,
            'context': strategy.context,
            'lessons_learned': strategy.lessons_learned
        })
        
        # 保留最近的 10 条策略
        strategies_data = strategies_data[-10:]
        
        # 保存
        with open(task_type_file, 'w', encoding='utf-8') as f:
            json.dump(strategies_data, f, ensure_ascii=False, indent=2)
    
    def get_strategy_for_task(self, task_type: str, 
                               task_description: str) -> Optional[StrategyRecommendation]:
        """
        为任务推荐策略
        
        Args:
            task_type: 任务类型
            task_description: 任务描述
        
        Returns:
            Optional[StrategyRecommendation]: 推荐的策略，如果没有则返回 None
        """
        # 查找类似任务的成功策略
        similar_strategies = self.success_patterns.get(task_type, [])
        
        if not similar_strategies:
            # 尝试从文件加载
            self._load_strategies_for_type(task_type)
            similar_strategies = self.success_patterns.get(task_type, [])
        
        if not similar_strategies:
            return None
        
        # 选择最佳策略（分数最高）
        best_strategy = max(similar_strategies, key=lambda s: s.quality_score)
        
        # 计算置信度
        confidence = min(1.0, len(similar_strategies) / 5.0)  # 5 个以上成功案例置信度为 1
        confidence *= (best_strategy.quality_score / 10.0)
        
        # 创建推荐
        recommendation = StrategyRecommendation(
            strategy=best_strategy,
            confidence=confidence,
            reason=f"基于 {len(similar_strategies)} 个成功案例，最佳质量分数 {best_strategy.quality_score}",
            similar_tasks=len(similar_strategies)
        )
        
        return recommendation
    
    def _load_strategies_for_type(self, task_type: str):
        """从文件加载某类型的策略"""
        task_type_file = self.STRATEGIES_DIR / f"{task_type.replace(' ', '_')}.json"
        
        if not task_type_file.exists():
            return
        
        with open(task_type_file, 'r', encoding='utf-8') as f:
            strategies_data = json.load(f)
        
        for data in strategies_data:
            strat = Strategy(
                task_type=data['task_type'],
                steps=data.get('steps', []),
                tools_used=data.get('tools_used', []),
                error_handling=data.get('error_handling', 'default'),
                success=data['success'],
                quality_score=data['quality_score'],
                executed_at=data['executed_at'],
                context=data.get('context', {}),
                lessons_learned=data.get('lessons_learned', [])
            )
            
            if strat.success and strat.quality_score >= 7.0:
                self.success_patterns[task_type].append(strat)
            else:
                self.failure_patterns[task_type].append(strat)
    
    def get_all_strategies(self, task_type: Optional[str] = None) -> List[Strategy]:
        """获取所有策略"""
        if task_type:
            return self.success_patterns.get(task_type, []) + \
                   self.failure_patterns.get(task_type, [])
        else:
            return self.strategy_history
    
    def get_success_rate(self, task_type: str) -> float:
        """获取某任务类型的成功率"""
        success_count = len(self.success_patterns.get(task_type, []))
        failure_count = len(self.failure_patterns.get(task_type, []))
        
        total = success_count + failure_count
        if total == 0:
            return 0.0
        
        return success_count / total
    
    def analyze_patterns(self, task_type: str) -> Dict[str, Any]:
        """分析某任务类型的模式"""
        success_strats = self.success_patterns.get(task_type, [])
        failure_strats = self.failure_patterns.get(task_type, [])
        
        analysis = {
            'task_type': task_type,
            'total_tasks': len(success_strats) + len(failure_strats),
            'success_rate': self.get_success_rate(task_type),
            'avg_quality_score': 0.0,
            'common_tools': [],
            'best_practices': [],
            'common_pitfalls': []
        }
        
        # 计算平均质量分数
        all_scores = [s.quality_score for s in success_strats + failure_strats]
        if all_scores:
            analysis['avg_quality_score'] = sum(all_scores) / len(all_scores)
        
        # 分析常用工具
        tool_counts = defaultdict(int)
        for strat in success_strats:
            for tool in strat.tools_used:
                tool_counts[tool] += 1
        
        analysis['common_tools'] = sorted(tool_counts.keys(), 
                                          key=lambda t: tool_counts[t], 
                                          reverse=True)[:5]
        
        # 提取最佳实践
        if success_strats:
            best = max(success_strats, key=lambda s: s.quality_score)
            analysis['best_practices'] = best.lessons_learned
        
        # 提取常见陷阱
        if failure_strats:
            analysis['common_pitfalls'] = [l for strat in failure_strats 
                                           for l in strat.lessons_learned]
        
        return analysis
    
    def export_strategies(self, filepath: Optional[str] = None):
        """导出所有策略到文件"""
        if not filepath:
            filepath = self.STRATEGIES_DIR / 'all_strategies.json'
        
        all_strategies = self.get_all_strategies()
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'total_count': len(all_strategies),
            'strategies': [
                {
                    'task_type': s.task_type,
                    'steps': s.steps,
                    'tools_used': s.tools_used,
                    'error_handling': s.error_handling,
                    'success': s.success,
                    'quality_score': s.quality_score,
                    'executed_at': s.executed_at,
                    'lessons_learned': s.lessons_learned
                }
                for s in all_strategies
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] Exported {len(all_strategies)} strategies to: {filepath}")


# 使用示例
if __name__ == '__main__':
    learner = StrategyLearner()
    
    # 记录成功策略
    learner.record_strategy(
        task_type="install_software",
        strategy={
            'steps': [
                'check_existing_installation',
                'download_installer',
                'run_with_silent_params',
                'verify_installation'
            ],
            'tools_used': ['exec', 'web_fetch'],
            'error_handling': 'retry_with_ui_automation'
        },
        success=True,
        quality_score=9.0,
        context={'platform': 'Windows', 'software': 'AIRI'}
    )
    
    # 记录失败策略
    learner.record_strategy(
        task_type="install_software",
        strategy={
            'steps': [
                'run_installer_directly'
            ],
            'tools_used': ['exec'],
            'error_handling': 'default'
        },
        success=False,
        quality_score=4.0,
        context={'platform': 'Windows', 'software': 'AIRI'}
    )
    
    # 获取推荐
    recommendation = learner.get_strategy_for_task(
        task_type="install_software",
        task_description="安装新的应用程序"
    )
    
    if recommendation:
        print(f"\n推荐策略:")
        print(f"置信度：{recommendation.confidence:.2f}")
        print(f"原因：{recommendation.reason}")
        print(f"步骤：{recommendation.strategy.steps}")
        print(f"工具：{recommendation.strategy.tools_used}")
    
    # 分析模式
    analysis = learner.analyze_patterns("install_software")
    print(f"\n模式分析:")
    print(f"成功率：{analysis['success_rate']:.2%}")
    print(f"平均质量：{analysis['avg_quality_score']:.1f}/10")
    print(f"常用工具：{analysis['common_tools']}")
    
    # 导出策略
    learner.export_strategies()
