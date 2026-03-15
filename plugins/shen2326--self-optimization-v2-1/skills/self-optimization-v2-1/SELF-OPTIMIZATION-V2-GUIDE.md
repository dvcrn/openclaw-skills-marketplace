# Self-Optimization System V2 - Usage Guide

**Version:** 2.0  
**Completed:** 2026-03-05  
**Status:** ✅ Core features completed

---

## 🎉 New Features

Compared to V1, V2 adds three core features:

### 1. ✅ LLM-as-Judge (Automatic Evaluation Loop)

**Function:** Automatically evaluate task completion quality, give 1-10 score

**Evaluation Dimensions:**
- Accuracy (30%) - Does result meet expectations
- Completeness (25%) - Are all requirements completed
- Efficiency (20%) - Time and resource usage
- Reliability (15%) - Is it stable without errors
- Maintainability (10%) - Code/documentation quality

**Quality Levels:**
| Score | Level | Action |
|-------|-------|--------|
| 9-10 | Excellent | Record success strategy |
| 7-8 | Good | Optional optimization |
| 5-6 | Fair | Needs optimization |
| 3-4 | Poor | Must optimize + analyze error |
| 1-2 | Fail | Deep analysis + rollback |

---

### 2. ✅ Automatic Prompt Optimization

**Function:** Analyze prompts for low-quality tasks, generate optimized versions

**Optimization Patterns:**
- Add context information
- Add examples
- Add constraints
- Clarify goal
- Add execution steps
- Specify output format
- Add evaluation criteria

**Workflow:**
```
Original Prompt → Execute Task → LLM Evaluate → Score < 7?
                                              ↓ Yes
                                    Analyze Weaknesses → Generate Optimized Version
                                              ↓
                                    Save Best Version to memory/prompts/
```

---

### 3. ✅ Strategy Learning

**Function:** Learn best practices from success/failure, recommend strategies for similar tasks

**Strategy Types:**
- Tool selection (what tools to use)
- Execution order (what to do first/last)
- Error handling (what to do when errors occur)
- Resource management (how to allocate token budget)

**Learning Workflow:**
```
Task Complete → Record Strategy → LLM Evaluate → Success?
                                                    ↓ Yes
                                            Extract Success Pattern → Update Strategy Library
                                                    ↓
                                            Similar Task → Recommend Strategy
```

---

## 📂 File Structure

```
E:\openclaw\workspace/
├── skills/self-optimization/
│   ├── __init__.py              # Main module (integrated system)
│   ├── judge.py                 # LLM-as-Judge evaluator
│   ├── prompt_optimizer.py      # Prompt optimizer
│   ├── strategy_learner.py      # Strategy learner
│   ├── config.yaml              # Configuration file
│   └── test_system.py           # Test script
├── memory/
│   ├── prompts/                 # Optimized prompts
│   │   └── *.yaml
│   └── strategies/              # Learned strategies
│       └── *.json
├── SELF-OPTIMIZATION-V2.md      # Design document
└── SELF-OPTIMIZATION-V2-GUIDE.md # Usage guide (this document)
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
    }
)

# View evaluation results
print(f"Quality Score: {result['evaluation']['score']}/10")
print(f"Quality Level: {result['evaluation']['quality_level']}")
print(f"Strengths: {result['evaluation']['strengths']}")
print(f"Weaknesses: {result['evaluation']['weaknesses']}")

# View optimization suggestions
if result['optimized_prompts']:
    print(f"Optimized Prompt: {result['optimized_prompts'][0]}")

# Get quality report
report = system.get_quality_report('software_installation')
print(f"Success Rate: {report['success_rate']:.2%}")
print(f"Avg Quality: {report['average_quality_score']:.1f}/10")
```

---

### Method 2: Use Modules Separately

#### LLM-as-Judge

```python
from skills.self_optimization import LLMJudge

# Evaluate task
evaluation = LLMJudge.evaluate(
    task="Analyze log file",
    result="Analysis complete, found 3 errors...",
    expected="Find all errors and generate report"
)

print(f"Score: {evaluation.score}/10")
print(f"Quality Level: {LLMJudge.get_quality_level(evaluation.score)}")

# Check if optimization needed
if LLMJudge.should_optimize(evaluation.score):
    print("Need to optimize prompt")

# Check if error analysis required
if LLMJudge.must_analyze_error(evaluation.score):
    print("Must analyze error cause")
```

---

#### Prompt Optimizer

```python
from skills.self_optimization import PromptOptimizer

optimizer = PromptOptimizer()

# Analyze weaknesses
weaknesses = optimizer.analyze_weaknesses(
    prompt="Help me install software",
    result="Installation failed",
    evaluation_score=4.0
)

# Generate optimized version
optimized = optimizer.generate_optimized_prompt(
    original="Help me install software",
    weaknesses=weaknesses,
    suggestions=["Add specific steps", "Specify error handling"]
)

# Save best version
optimizer.save_best_prompt(
    task_type="software_installation",
    prompt=optimized,
    score=8.5
)

# Load best version
best_prompt = optimizer.load_best_prompt("software_installation")
```

---

#### Strategy Learner

```python
from skills.self_optimization import StrategyLearner

learner = StrategyLearner()

# Record success strategy
learner.record_strategy(
    task_type="software_installation",
    strategy={
        'steps': ['download', 'install', 'configure', 'test'],
        'tools_used': ['exec', 'web_fetch'],
        'error_handling': 'retry_with_ui_automation'
    },
    success=True,
    quality_score=9.0,
    context={'platform': 'Windows'}
)

# Get strategy recommendation
recommendation = learner.get_strategy_for_task(
    task_type="software_installation",
    task_description="Install new application"
)

if recommendation:
    print(f"Recommended Strategy: {recommendation.strategy.steps}")
    print(f"Confidence: {recommendation.confidence:.2f}")

# Analyze patterns
analysis = learner.analyze_patterns("software_installation")
print(f"Success Rate: {analysis['success_rate']:.2%}")
print(f"Avg Quality: {analysis['avg_quality_score']:.1f}/10")
```

---

## 🔄 Complete Optimization Loop

```
1. Accept Task
   ↓
2. [Strategy Learner] Get Strategy Recommendation
   ↓
3. Execute Task (use recommended strategy)
   ↓
4. [LLM-Judge] Evaluate Quality
   ↓
5. Score >= 7?
   ├─ Yes → [Strategy Learner] Record Success Strategy
   └─ No → [Prompt Optimizer] Optimize Prompt
   ↓
6. [Error Tracking] Check for Errors
   ├─ Has Errors → Record and Analyze
   └─ No Errors → Record Success Experience
   ↓
7. Update MEMORY.md and Strategy Library
   ↓
8. Task Complete
```

---

## 📊 Configuration Options

Configure in `skills/self-optimization/config.yaml`:

```yaml
# LLM Evaluation Thresholds
judge:
  score_thresholds:
    excellent: 9.0  # 9-10 points: Excellent
    good: 7.0       # 7-8 points: Good
    fair: 5.0       # 5-6 points: Fair
  
  # Auto-optimization trigger
  auto_optimize:
    enabled: true
    threshold: 7.0  # Auto-optimize below 7 points

# Prompt Optimization
prompt_optimizer:
  patterns:
    add_context: true    # Add context
    add_examples: true   # Add examples
    add_constraints: true # Add constraints

# Strategy Learning
strategy_learner:
  learning:
    from_success: true   # Learn from success
    from_failure: true   # Learn from failure
```

---

## 📈 Expected Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Avg Quality Score** | 7.5 | 8.5+ | +13% |
| **Error Recurrence** | 15% | <5% | -67% |
| **Task Completion Time** | Baseline | -20% | Efficiency Gain |
| **Prompt Quality** | Manual | Auto | Continuous Improvement |
| **Strategy Reuse Rate** | 0% | 60%+ | Knowledge Retention |

---

## 🧪 Testing

Run test script:

```bash
cd E:\openclaw\workspace\skills\self-optimization
python test_system.py
```

**Test Results:**
- ✅ LLM-as-Judge tests passed
- ✅ Prompt Optimizer tests passed
- ✅ Strategy Learner tests passed
- ✅ Strategy export successful

---

## 📝 Real-World Cases

### Case 1: AIRI Integration Project

**Task:** Install AIRI and configure bridge service

**Execution Process:**
1. First attempt: Silent install failed (Score: 4.0)
   - Record failure strategy
   - Analyze error: Didn't confirm install parameters
   - Optimize prompt: Add "check docs first" step

2. Second attempt: UI automation success (Score: 9.0)
   - Record success strategy
   - Extract best practice: Simplicity first principle
   - Save to strategy library

3. Third attempt and beyond:
   - Auto-recommend success strategy
   - Success rate improved from 50% to 100%

**Lessons Learned:**
- Always check install parameters first
- Simple methods (SendKeys) are more reliable than complex scripts
- Avoid Chinese characters in Windows PowerShell scripts

---

### Case 2: Shortcuts Creation

**Task:** Create desktop shortcut for OpenClaw

**Execution Process:**
1. First attempt: PowerShell script failed (Score: 3.0)
2. Second attempt: VBScript success (Score: 8.5)
3. Strategy saved for future use

**Strategy Extracted:**
- Use VBScript for Windows shortcuts (more reliable)
- Fallback to PowerShell if VBScript fails

---

## 🎯 Best Practices

### 1. Always Record Strategies

Whether success or failure, record the strategy:
```python
learner.record_strategy(task_type, strategy, success, score)
```

### 2. Review Quality Reports Regularly

Check weekly quality reports to identify patterns:
```python
report = system.get_quality_report(task_type, days=7)
```

### 3. Optimize Proactively

Don't wait for failures - optimize when score < 7:
```python
if score < 7.0:
    optimizer.generate_optimized_prompt(...)
```

### 4. Share Successful Strategies

Export successful strategies to share with team:
```python
learner.export_strategies("strategies_export.json")
```

---

## 📚 Additional Resources

- **Design Document:** `SELF-OPTIMIZATION-V2.md`
- **Comparison Analysis:** `SELF-OPTIMIZATION-COMPARISON.md`
- **V2.1 Manual:** `SELF-OPTIMIZATION-V2.1-MANUAL.md`

---

**Guide Version:** 2.0  
**Last Updated:** 2026-03-05  
**Authors:** Shen (with AI assistant Yiyi)
