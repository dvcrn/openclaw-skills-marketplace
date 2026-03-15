---
name: self-optimization-v2-1
description: "Self-Optimization V2.1 - Enhanced"
---

# Self-Optimization V2.1

**Version:** 2.1.0  
**Release Date:** 2026-03-05  
**Author:** Shen (with AI assistant Yiyi)  
**License:** MIT

---

## 🎯 Skill Description

Self-Optimization V2.1 is an enhanced AI self-optimization framework that provides comprehensive quality evaluation, A/B testing, visual monitoring, and continuous learning capabilities.

---

## ✨ Core Features

### 1. LLM-as-Judge Automatic Evaluation
- 5 core dimension evaluation (Accuracy/Completeness/Efficiency/Reliability/Maintainability)
- 1-10 scoring system
- 5 quality level determination
- Automatic optimization trigger detection

### 2. A/B Testing Framework ⭐NEW
- Random variant assignment (A/B)
- Automatic test result collection
- Statistical significance analysis
- Test report generation
- Best variant recommendation

### 3. Visual Quality Monitoring ⭐NEW
- Quality trend analysis (7 days/30 days)
- 10-dimension analysis
- Task type performance comparison
- Quality distribution statistics
- Automatic improvement suggestions
- HTML report export

### 4. Advanced Metrics ⭐NEW
- Creativity evaluation
- Clarity evaluation
- Helpfulness evaluation
- Safety evaluation
- User satisfaction evaluation
- 10-dimension comprehensive scoring

### 5. Prompt Optimizer
- 7 optimization patterns
- Automatic weakness analysis
- Best prompt save/load

### 6. Strategy Learner
- Success/failure strategy recording
- Strategy recommendation
- Pattern analysis
- Strategy export

---

## 📦 Installation

### Method 1: OpenClaw CLI (Recommended)

```bash
openclaw skills install self-optimization-v2.1
```

### Method 2: Manual Installation

```bash
# Clone or copy to skills directory
git clone https://github.com/openclaw/openclaw.git
cp -r openclaw/skills/self-optimization /path/to/your/skills/
```

### Method 3: Download from ClawHub

Visit: https://clawhub.ai/skills/self-optimization-v2.1

---

## 🚀 Quick Start

### Basic Usage

```python
from skills.self_optimization import SelfOptimizationSystem

# Initialize system
system = SelfOptimizationSystem()

# Execute task with auto-optimization
result = system.execute_task(
    task="Your task description",
    result="Execution result...",
    context={
        'task_type': 'task_type',
        'steps': ['Step 1', 'Step 2'],
        'tools_used': ['Tool 1', 'Tool 2']
    },
    user_feedback={'satisfaction': 0.9}
)

# View evaluation results
print(f"Total Score: {result['advanced_evaluation']['overall_score']}/10")
print(f"Strengths: {result['advanced_evaluation']['strengths']}")
print(f"Weaknesses: {result['advanced_evaluation']['weaknesses']}")

# Generate quality report
report = system.dashboard.generate_report(days=7)
html_path = system.dashboard.export_html_report(report)
print(f"HTML Report: {html_path}")
```

---

## 📊 Usage Examples

### A/B Testing

```python
from skills.self_optimization import ABTestingFramework, ABTestVariant

ab = ABTestingFramework()

# Create test
ab.create_test(
    test_id='prompt_test_1',
    variant_a=ABTestVariant('A', 'Original Prompt', 'Help me install software'),
    variant_b=ABTestVariant('B', 'Optimized Prompt', '**Goal:** Help me install software...'),
    test_tasks=[{'id': i} for i in range(50)]
)

# Record results
for i in range(50):
    variant = ab.assign_variant('prompt_test_1')
    score = 8.5 if variant == 'B' else 7.5
    ab.record_result('prompt_test_1', f'task_{i}', variant, score)

# Analyze results
report = ab.analyze_test('prompt_test_1')
print(f"Winner: {report.winner}")
print(f"Confidence: {report.confidence:.2%}")
```

### Quality Monitoring

```python
from skills.self_optimization import QualityDashboard

dashboard = QualityDashboard()

# Record evaluation
dashboard.record_evaluation(
    task="Task Name",
    score=8.5,
    dimensions={
        'accuracy': 0.9,
        'completeness': 0.85,
        'efficiency': 0.8,
        'reliability': 0.9,
        'maintainability': 0.8,
        'creativity': 0.7,
        'clarity': 0.85,
        'helpfulness': 0.9,
        'safety': 0.95,
        'user_satisfaction': 0.9
    },
    task_type='task_type'
)

# Generate report
report = dashboard.generate_report(days=7)
print(f"Average Score: {report['summary']['avg_score']:.2f}")
print(f"Success Rate: {report['summary']['success_rate']:.2%}")

# Export HTML
html_path = dashboard.export_html_report(report)
```

### Advanced Evaluation

```python
from skills.self_optimization import AdvancedMetricsEvaluator

evaluator = AdvancedMetricsEvaluator()

evaluation = evaluator.evaluate(
    task="Task description",
    result="Execution result",
    context={
        'execution_time': 120,
        'retry_count': 0,
        'tools_used': ['exec', 'web_fetch']
    },
    user_feedback={'satisfaction': 0.9}
)

print(f"Total Score: {evaluation.overall_score:.2f}/10")
print(f"Creativity: {evaluation.creativity:.2f}")
print(f"Clarity: {evaluation.clarity:.2f}")
print(f"Helpfulness: {evaluation.helpfulness:.2f}")
```

---

## 📁 File Structure

```
self-optimization/
├── __init__.py              # Main module
├── judge.py                 # LLM-as-Judge evaluator
├── prompt_optimizer.py      # Prompt optimizer
├── strategy_learner.py      # Strategy learner
├── ab_testing.py            # A/B testing framework ⭐
├── quality_dashboard.py     # Quality dashboard ⭐
├── advanced_metrics.py      # Advanced metrics ⭐
├── config.yaml              # Configuration file
├── test_system.py           # Test script
├── package.json             # Package metadata
├── README.md                # Usage documentation
└── SKILL.md                 # This file
```

---

## 🧪 Testing

```bash
# Run all tests
cd skills/self-optimization
python test_system.py

# Test individual modules
python ab_testing.py
python quality_dashboard.py
python advanced_metrics.py
```

---

## 📈 Performance Metrics

| Metric | V2 | V2.1 | Improvement |
|--------|-----|------|-------------|
| Evaluation Dimensions | 5 | **10** | +100% |
| A/B Testing | ❌ | **✅** | New |
| Visualization | ❌ | **HTML Reports** | New |
| User Feedback | ❌ | **✅** | New |
| Statistical Significance | ❌ | **✅** | New |

---

## 🔄 Changelog

### v2.1.0 (2026-03-05)
- ✨ Added A/B Testing Framework
- ✨ Added Visual Quality Monitoring (HTML Reports)
- ✨ Added Advanced Metrics (5 new dimensions)
- ✨ Integrated User Feedback Support
- ✨ Added Statistical Significance Analysis
- 📝 Improved Documentation

### v2.0.0 (2026-03-05)
- ✨ Initial V2 Release
- ✨ LLM-as-Judge Evaluation
- ✨ Prompt Optimizer
- ✨ Strategy Learner
- ✨ Error Tracking Integration

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a Pull Request

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🙏 Acknowledgments

- Built for OpenClaw ecosystem
- Inspired by self-improving agent patterns
- Created with love by Shen and Yiyi 💕

---

**Homepage:** https://clawhub.ai/skills/self-optimization-v2.1  
**Repository:** https://github.com/openclaw/openclaw  
**Issues:** https://github.com/openclaw/openclaw/issues
