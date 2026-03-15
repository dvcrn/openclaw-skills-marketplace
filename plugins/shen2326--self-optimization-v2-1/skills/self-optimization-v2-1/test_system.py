#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Self-Optimization System V2
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from judge import LLMJudge
from prompt_optimizer import PromptOptimizer
from strategy_learner import StrategyLearner

print("=" * 60)
print("Testing Self-Optimization System V2")
print("=" * 60)

# Test 1: LLM-as-Judge
print("\n[TEST 1] LLM-as-Judge")
print("-" * 60)

task = "安装 AIRI 应用并配置桥接服务"
result = """
成功完成：
1. AIRI 已安装到 D:\AIRI
2. 桥接服务运行正常
3. 虚拟人物显示在屏幕中央
4. API 配置完成
"""

evaluation = LLMJudge.evaluate(task, result)

print(f"Task: {task}")
print(f"Score: {evaluation.score}/10")
print(f"Quality Level: {LLMJudge.get_quality_level(evaluation.score)}")
print(f"Dimensions:")
print(f"  - Accuracy: {evaluation.accuracy:.2f}")
print(f"  - Completeness: {evaluation.completeness:.2f}")
print(f"  - Efficiency: {evaluation.efficiency:.2f}")
print(f"  - Reliability: {evaluation.reliability:.2f}")
print(f"  - Maintainability: {evaluation.maintainability:.2f}")
print(f"Strengths: {evaluation.strengths}")
print(f"Weaknesses: {evaluation.weaknesses}")
print(f"Suggestions: {evaluation.suggestions}")
print(f"Should Optimize: {LLMJudge.should_optimize(evaluation.score)}")
print(f"Must Analyze Error: {LLMJudge.must_analyze_error(evaluation.score)}")

# Test 2: Prompt Optimizer
print("\n[TEST 2] Prompt Optimizer")
print("-" * 60)

optimizer = PromptOptimizer()
original_prompt = "帮我安装这个软件"

weaknesses = optimizer.analyze_weaknesses(original_prompt, result, evaluation.score)
optimized = optimizer.generate_optimized_prompt(original_prompt, weaknesses, [])

print(f"Original Prompt: {original_prompt}")
print(f"Optimized Prompt: {optimized}")
print(f"Weaknesses Found: {weaknesses}")

# Test 3: Strategy Learner
print("\n[TEST 3] Strategy Learner")
print("-" * 60)

learner = StrategyLearner()

# Record success
learner.record_strategy(
    task_type="software_installation",
    strategy={
        'steps': [
            'download_installer',
            'run_silent_install',
            'configure_bridge',
            'test_connection'
        ],
        'tools_used': ['exec', 'web_fetch'],
        'error_handling': 'retry_with_ui_automation'
    },
    success=True,
    quality_score=9.0,
    context={'platform': 'Windows', 'software': 'AIRI'}
)

# Record failure
learner.record_strategy(
    task_type="software_installation",
    strategy={
        'steps': ['run_installer_directly'],
        'tools_used': ['exec'],
        'error_handling': 'default'
    },
    success=False,
    quality_score=4.0,
    context={'platform': 'Windows', 'software': 'AIRI'}
)

# Get recommendation
recommendation = learner.get_strategy_for_task(
    task_type="software_installation",
    task_description="安装新的应用程序"
)

if recommendation:
    print(f"\nStrategy Recommendation:")
    print(f"  Confidence: {recommendation.confidence:.2f}")
    print(f"  Reason: {recommendation.reason}")
    print(f"  Steps: {recommendation.strategy.steps}")
    print(f"  Tools: {recommendation.strategy.tools_used}")

# Analyze patterns
analysis = learner.analyze_patterns("software_installation")
print(f"\nPattern Analysis:")
print(f"  Success Rate: {analysis['success_rate']:.2%}")
print(f"  Avg Quality: {analysis['avg_quality_score']:.1f}/10")
print(f"  Common Tools: {analysis['common_tools']}")

# Export strategies
learner.export_strategies()

print("\n" + "=" * 60)
print("All Tests Completed!")
print("=" * 60)
