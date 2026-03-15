# Self-Optimization System V2.1 - Enhanced User Manual

**Version:** 2.1  
**Last Updated:** 2026-03-05 23:59  
**Status:** ✅ Complete

---

## 🎉 New Features (V2.1)

Compared to V2, V2.1 adds three major features:

### 1. ✅ A/B Testing Framework

**Function:** Perform A/B testing on different prompts/strategies to find the best solution

**Features:**
- Random variant assignment (A/B)
- Automatic test result collection
- Statistical significance analysis
- Test report generation
- Best variant recommendation

**Use Cases:**
- Test different prompt versions
- Compare strategy effectiveness
- Optimize workflows

---

### 2. ✅ Visual Quality Monitoring

**Function:** Generate quality monitoring reports and visual charts

**Features:**
- Quality trend analysis (7 days/30 days)
- 10-dimension analysis
- Task type performance comparison
- Quality distribution statistics
- Automatic improvement suggestions
- HTML report export

**Visual Content:**
- 📈 Quality trend charts
- 📊 Dimension radar charts
- 📉 Task type comparison
- 🎯 Quality distribution pie charts

---

### 3. ✅ More Evaluation Dimensions

**New Dimensions:**
- **Creativity** - Is the solution creative
- **Clarity** - Is the expression clear
- **Helpfulness** - Is it practically helpful to users
- **Safety** - Does it follow safety best practices
- **User Satisfaction** - User feedback score

**Complete Dimension List (10 dimensions):**

| Category | Dimension | Weight |
|----------|-----------|--------|
| **Core Dimensions** | Accuracy | 25% |
| | Completeness | 20% |
| | Efficiency | 15% |
| | Reliability | 15% |
| | Maintainability | 10% |
| **Advanced Dimensions** | Creativity | 5% |
| | Clarity | 5% |
| | Helpfulness | 3% |
| | Safety | 2% |
| | User Satisfaction | Calculated separately |

---

## 📂 Complete File Structure

```
E:\openclaw\workspace/
├── skills/self-optimization/
│   ├── __init__.py              # Main module (integrated system)
│   ├── judge.py                 # LLM-as-Judge evaluator
│   ├── prompt_optimizer.py      # Prompt optimizer
│   ├── strategy_learner.py      # Strategy learner
│   ├── ab_testing.py            # A/B testing framework (NEW)
│   ├── quality_dashboard.py     # Quality dashboard (NEW)
│   ├── advanced_metrics.py      # Advanced metrics (NEW)
│   ├── config.yaml              # Configuration file
│   └── test_system.py           # Test script
├── memory/
│   ├── prompts/                 # Optimized prompts
│   ├── strategies/              # Learned strategies
│   ├── ab_tests/                # A/B test results (NEW)
│   └── reports/                 # Quality reports (NEW)
│       ├── evaluations.json
│       ├── quality_report_*.json
│       └── quality_report_*.html
├── SELF-OPTIMIZATION-V2.md      # V2 design document
├── SELF-OPTIMIZATION-V2-GUIDE.md # V2 usage guide
├── SELF-OPTIMIZATION-V2.1-MANUAL.md # V2.1 manual (this document)
└── SELF-OPTIMIZATION-COMPARISON.md  # Comparison analysis
```

---

## 🛠️ Usage Methods

### Method 1: Use Integrated System (Recommended)

```python
from skills.self_optimization import SelfOptimizationSystem

# Initialize system
system = SelfOptimizationSystem()

# Execute task with auto-optimization
result = system.execute_task(
    task="Install AIRI app and configure bridge service",
    result="Successfully completed installation and configuration...",
    context={
        'task_type': 'software_installation',
        'steps': ['download', 'install', 'configure', 'test'],
        'tools_used': ['exec', 'web_fetch'],
        'error_handling': 'retry_with_ui_automation'
    },
    user_feedback={
        'satisfaction': 0.9  # User satisfaction 90%
    }
)

# View evaluation results
print(f"Overall Score: {result['advanced_evaluation']['overall_score']}/10")
print(f"Core Dimensions: {result['evaluation']['dimensions']}")
print(f"Advanced Dimensions: {result['advanced_evaluation']['dimensions']}")
print(f"Strengths: {result['advanced_evaluation']['strengths']}")
print(f"Weaknesses: {result['advanced_evaluation']['weaknesses']}")

# Generate quality report
report = system.dashboard.generate_report(days=7)
print(f"Average Score: {report['summary']['avg_score']:.2f}")
print(f"Success Rate: {report['summary']['success_rate']:.2%}")

# Export HTML report
html_path = system.dashboard.export_html_report(report)
print(f"HTML Report: {html_path}")
```

---

### Method 2: Use A/B Testing Framework Separately

```python
from skills.self_optimization import ABTestingFramework, ABTestVariant

# Initialize framework
ab_framework = ABTestingFramework()

# Create A/B test
test_config = ab_framework.create_test(
    test_id='prompt_test_1',
    variant_a=ABTestVariant(
        id='A',
        name='Original Prompt',
        content='Help me install this software'
    ),
    variant_b=ABTestVariant(
        id='B',
        name='Optimized Prompt',
        content='''**Goal:** Help me install this software

**Constraints:**
- Must check docs to confirm install parameters first
- Use silent install or UI automation
- Avoid Chinese characters (encoding issues)

**Output Format:** Execute step by step and report progress'''
    ),
    test_tasks=[{'id': f'task_{i}'} for i in range(50)],
    metrics=['score', 'accuracy', 'efficiency']
)

# Assign variants to tasks
for i in range(50):
    variant = ab_framework.assign_variant('prompt_test_1')
    
    # Execute task...
    score = 7.5 if variant == 'A' else 8.5  # Simulated result
    
    # Record result
    ab_framework.record_result(
        test_id='prompt_test_1',
        task_id=f'task_{i}',
        variant_id=variant,
        score=score,
        metrics={'score': score, 'accuracy': score/10}
    )

# Analyze test results
report = ab_framework.analyze_test('prompt_test_1')

if report:
    print(f"Winner: Variant {report.winner}")
    print(f"Confidence: {report.confidence:.2%}")
    print(f"Recommendation: {report.recommendation}")
    
    # Get best variant
    best = ab_framework.get_best_variant('prompt_test_1')
    print(f"Best variant: {best}")
```

---

### Method 3: Use Quality Dashboard Separately

```python
from skills.self_optimization import QualityDashboard

# Initialize dashboard
dashboard = QualityDashboard()

# Record evaluation results
dashboard.record_evaluation(
    task="Install AIRI Application",
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
    task_type='software_installation'
)

# Generate quality report
report = dashboard.generate_report(days=7)

print(f"Total Tasks: {report['summary']['total_tasks']}")
print(f"Average Score: {report['summary']['avg_score']:.2f}")
print(f"Success Rate: {report['summary']['success_rate']:.2%}")

# View dimension analysis
print(f"\nDimension Analysis:")
for dim, stats in report['dimension_analysis'].items():
    print(f"  {dim}: {stats['avg']:.2f} (min: {stats['min']:.2f}, max: {stats['max']:.2f})")

# Export HTML report
html_path = dashboard.export_html_report(report)
print(f"\nHTML Report: {html_path}")
```

---

### Method 4: Use Advanced Metrics Separately

```python
from skills.self_optimization import AdvancedMetricsEvaluator

# Initialize evaluator
evaluator = AdvancedMetricsEvaluator()

# Perform comprehensive evaluation
evaluation = evaluator.evaluate(
    task="Install AIRI app and configure bridge service",
    result="""
    Successfully completed:
    1. AIRI installed to D:\\AIRI
    2. Bridge service running normally
    3. Virtual character displayed in screen center
    4. API configuration complete
    
    **Documentation:** Complete usage instructions created
    **Steps:** Executed in order, succeeded on first attempt
    """,
    context={
        'execution_time': 120,  # 2 minutes
        'retry_count': 0,
        'tools_used': ['exec', 'web_fetch', 'file_write']
    },
    user_feedback={
        'satisfaction': 0.9  # User satisfaction 90%
    }
)

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

# Get dimension report
report = evaluator.get_dimension_report(evaluation)
print(f"\nStrengths: {report['strengths']}")
print(f"Weaknesses: {report['weaknesses']}")
```

---

## 📊 Complete Optimization Loop (V2.1)

```
1. Accept Task
   ↓
2. [Strategy Learner] Get Strategy Recommendation
   ↓
3. [A/B Testing] If active test exists, assign variant
   ↓
4. Execute Task (use recommended strategy/assigned variant)
   ↓
5. [LLM-Judge] Evaluate Core Dimensions
   ↓
6. [Advanced Metrics] Evaluate Advanced Dimensions
   ↓
7. [Quality Dashboard] Record Evaluation Results
   ↓
8. Score >= 7?
   ├─ Yes → [Strategy Learner] Record Success Strategy
   └─ No → [Prompt Optimizer] Optimize Prompt
   ↓
9. [Error Tracking] Check for Errors
   ├─ Has Errors → Record and Analyze
   └─ No Errors → Record Success Experience
   ↓
10. Update MEMORY.md, Strategy Library, Quality Reports
    ↓
11. Task Complete
```

---

## 📈 Visual Report Examples

### HTML Report Content

After opening the HTML report, you can see:

1. **Summary Cards**
   - Total tasks
   - Average score
   - Success rate
   - Excellence rate

2. **Dimension Analysis Table**
   - Average/Min/Max scores for 10 dimensions

3. **Quality Distribution Table**
   - Count of Excellent/Good/Fair/Poor/Fail

4. **Improvement Suggestions**
   - Auto-generated suggestions based on data analysis

---

## 🎯 Best Practices

### 1. Use A/B Testing to Optimize Prompts

```python
# When unsure which prompt is better
if uncertain_about_prompt:
    # Create A/B test
    ab_framework.create_test(
        test_id='prompt_test',
        variant_a=ABTestVariant('A', 'Original', original_prompt),
        variant_b=ABTestVariant('B', 'Optimized', optimized_prompt),
        test_tasks=task_list
    )
    
    # Analyze after collecting 30+ samples
    if len(results) >= 30:
        report = ab_framework.analyze_test('prompt_test')
        best_prompt = ab_framework.get_best_variant('prompt_test')
```

### 2. Review Quality Reports Regularly

```python
# Generate daily report
report = dashboard.generate_report(days=1)

# Check trend
trend = dashboard.get_quality_trend(days=7)
if trend[-1]['avg_score'] < trend[-2]['avg_score'] - 0.5:
    print("Warning: Quality declining!")
```

### 3. Record All Strategies

```python
# Always record strategies, whether success or failure
learner.record_strategy(
    task_type=task_type,
    strategy=strategy,
    success=success,
    quality_score=score
)
```

### 4. Export Reports for Sharing

```python
# Export HTML report for team sharing
html_path = dashboard.export_html_report(report)

# Export strategy library
learner.export_strategies('team_strategies.json')
```

---

## 📊 Performance Metrics

| Metric | V2 | V2.1 | Improvement |
|--------|-----|------|-------------|
| Evaluation Dimensions | 5 | **10** | +100% |
| A/B Testing | ❌ | **✅** | New |
| Visualization | ❌ | **HTML Reports** | New |
| User Feedback | ❌ | **✅** | New |
| Statistical Significance | ❌ | **✅** | New |

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

## 📚 Additional Resources

- **V2 Design:** `SELF-OPTIMIZATION-V2.md`
- **V2 Guide:** `SELF-OPTIMIZATION-V2-GUIDE.md`
- **Comparison:** `SELF-OPTIMIZATION-COMPARISON.md`
- **Skill Definition:** `SKILL.md`

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

**Manual Version:** 2.1  
**Last Updated:** 2026-03-05  
**Authors:** Shen (with AI assistant Yiyi)
