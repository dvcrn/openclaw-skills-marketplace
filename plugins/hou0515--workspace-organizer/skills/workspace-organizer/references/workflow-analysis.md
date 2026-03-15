# Workflow Analysis Guide

How to analyze tasks and decompose them into logical steps for folder structure creation.

## Core Analysis Questions

Before creating any directories, ask:

### 1. Task Understanding
- **What's the ultimate deliverable?** (Report, code, design, analysis, etc.)
- **Who is the end user/audience?** (Technical team, business stakeholders, public, etc.)
- **What does "done" look like?** (Specific outputs, quality criteria, success metrics)

### 2. Workflow Identification
- **What are the natural phases?** Most tasks break into 3-5 major phases
- **What depends on what?** Sequence constraints and dependencies
- **What could be done in parallel?** Independent sub-tasks
- **Where are the decision points?** Places where approach might change

### 3. Resource Analysis
- **What inputs are needed?** (Data files, documents, APIs, user input)
- **What tools/scripts will be used?** (Python, specialized software, custom code)
- **What intermediate artifacts are created?** (Processed data, analysis results, drafts)
- **What final outputs are produced?** (Reports, code, visualizations, etc.)

## Common Workflow Patterns

### Analysis & Research Tasks
```
Typical flow: Gather → Clean → Analyze → Visualize → Report
Example: 01_数据收集 → 02_数据清洗 → 03_分析建模 → 04_可视化 → 05_报告生成
```

### Development & Engineering Tasks
```
Typical flow: Plan → Implement → Test → Deploy → Document
Example: 01_需求分析 → 02_编码实现 → 03_测试验证 → 04_部署上线 → 05_文档编写
```

### Creative & Content Tasks
```
Typical flow: Research → Plan → Create → Refine → Publish
Example: 01_素材研究 → 02_内容规划 → 03_创作生成 → 04_优化调整 → 05_发布分发
```

### Process & Automation Tasks
```
Typical flow: Understand → Design → Build → Test → Monitor
Example: 01_流程分析 → 02_方案设计 → 03_自动化构建 → 04_测试验证 → 05_监控维护
```

**Remember**: These are patterns, not prescriptions. Your task might need a different structure.

## Step Creation Guidelines

### Good Step Names
- **Action-oriented**: "ExtractData" not "DataExtractionPhase"
- **Specific**: "CleanCustomerRecords" not "ProcessData"
- **Consistent style**: Mixing "Data_Cleaning" and "DataPreprocessing" is confusing
- **Appropriate granularity**: One major activity per step

### Step Count Considerations
- **3-7 steps** is usually optimal
- **Too few** (1-2): Might be missing important phases
- **Too many** (8+): Might be over-segmenting; consider grouping
- **Adjust as you work**: It's OK to split or merge steps later

### Handling Uncertainty
When you're not sure about the workflow:
1. **Start with broad steps**: "Preparation", "Execution", "Delivery"
2. **Document assumptions**: Note what you think the workflow will be
3. **Be ready to adjust**: Rename, split, or merge as understanding improves
4. **Use placeholder names**: "Step1_InitialAnalysis" can become "01_数据探索" later

## Decision Framework

### When to Create a New Step
- When there's a clear handoff between phases
- When different skills/tools are needed
- When work could be paused and resumed later
- When outputs from this phase are inputs to the next

### When to Combine Steps
- When activities are tightly coupled
- When no intermediate artifacts are produced
- When the same person/tool does both
- When separation creates unnecessary complexity

### When to Reorder Steps
- When dependencies dictate a different sequence
- When iterative work is needed (e.g., draft → feedback → revise)
- When parallel work is possible

## Practical Examples

### Example: Customer Segmentation Analysis

**Initial understanding**: "Analyze customer data to identify segments"

**Analysis process**:
1. Deliverables: Segmentation report with recommendations
2. Natural phases: 
   - Get and understand data
   - Clean and prepare data  
   - Explore patterns and features
   - Apply clustering algorithms
   - Interpret and name segments
   - Create actionable recommendations
3. Resources: Customer database, Python for analysis, visualization tools

**Resulting structure**:
```
01_数据获取理解/
02_数据清洗准备/
03_特征探索分析/
04_聚类算法应用/
05_细分市场解释/
06_行动建议生成/
```

### Example: API Integration Project

**Initial understanding**: "Integrate with external payment API"

**Analysis process**:
1. Deliverables: Working integration with documentation
2. Natural phases:
   - Study API documentation
   - Design integration architecture
   - Implement core connectivity
   - Handle edge cases and errors
   - Test thoroughly
   - Document usage
3. Resources: API docs, development environment, testing tools

**Resulting structure**:
```
01_API文档研究/
02_架构设计规划/
03_核心功能实现/
04_异常处理优化/
05_全面测试验证/
06_使用文档编写/
```

## Iterative Refinement

Workflow analysis isn't a one-time activity:

### Phase 1: Initial Structure
Based on initial understanding of the task

### Phase 2: Mid-task Adjustment
As you learn more about what's actually involved

### Phase 3: Final Optimization
Reflecting the actual work done, not just the plan

### Phase 4: Retrospective Learning
What worked well? What would you do differently next time?

## Tools & Techniques

### Mind Mapping
Visualize tasks and their relationships before creating folders

### Dependency Graphs
Map what must happen before what else can happen

### Time Estimation
Consider how long each phase might take (affects granularity)

### Risk Assessment
Identify uncertain areas that might need flexible structure

## Common Pitfalls to Avoid

### Over-engineering
Creating 10+ steps for a simple task

### Under-structuring
Putting everything in one "Processing" folder

### Premature optimization
Designing complex structure before understanding the task

### Rigidity
Refusing to change structure when it's clearly not working

### Category thinking
"All data tasks must have these 5 steps" instead of thinking from first principles

## Adaptive Mindset

The best structure:
1. **Emerges from the task**, not applied to it
2. **Evolves with understanding**, not fixed at the start
3. **Serves the work**, not dictates the work
4. **Documents the process**, not just organizes files

Your goal isn't to create the "perfect" structure upfront, but to create a **useful** structure that can **adapt** as you work.