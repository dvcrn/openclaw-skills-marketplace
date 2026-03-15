# 多步骤流程设计指南 (Multi-Step Workflow Design)

## 设计原则 (Design Principles)

### 1. 清晰的阶段划分 (Clear Phase Division)

每个流程应该有明确的阶段:

```
Phase 1: Input Validation
   └─ Check required parameters

Phase 2: Data Processing
   └─ Transform input data

Phase 3: Output Generation
   └─ Produce final output

Phase 4: Validation
   └─ Verify output quality
```

### 2. 条件逻辑 (Conditional Logic)

每一步都要考虑:
- 成功 → 下一步
- 失败 → 错误处理
- 特殊情况 → 旁路处理

### 3. 用户确认点 (User Confirmation Points)

重要决策点要用户确认:
- 技术方案选择
- 整繁琐细节
- 预期输出格式

## 常见模式 (Common Patterns)

### Pattern 1: 顺序工作流 (Sequential Workflow)

```
Step 1 → Step 2 → Step 3 → Output
```

适用场景:
- 线性任务 (data extraction → transformation → loading)
- 依赖性强的任务

### Pattern 2: 条件分支 (Conditional Branching)

```
Step 1
   ├─ Case A → steps for A
   └─ Case B → steps for B
```

适用场景:
- 多种输入格式
- 复杂业务逻辑

### Pattern 3: 迭代优化 (Iterative Refinement)

```
Initial Output → Feedback → Refinement → Final Output
```

适用场景:
- 需要用户确认的设计任务
- 逐步完善的处理流程

## 阶段设计模板 (Phase Design Template)

### Phase 1: 需求验证 (Validation)

```markdown
## Phase 1: Input Validation

### Required Inputs
- Input 1: Description
- Input 2: Description

### Validation Rules
1. Rule 1
2. Rule 2

### Error Messages
- [Error 1]: [Suggested message]
- [Error 2]: [Suggested message]
```

### Phase 2: 核心处理 (Processing)

```markdown
## Phase 2: Core Processing

### Step 1: [Step Name]
**Input**: What's needed
**Output**: What it produces
**Special Cases**: If X, do Y

### Step 2: [Step Name]
...

### Processing Logic
1. [Logic step 1]
2. [Logic step 2]
3. [Logic step 3]
```

### Phase 3: 输出生成 (Output)

```markdown
## Phase 3: Output Generation

### Output Format
```[format]
[Example output]
```

### Output Validation
- Check 1
- Check 2
- Check 3
```

### Phase 4: 反馈循环 (Feedback Loop)

```markdown
## Phase 4: Feedback and Iteration

### User Confirmation Points
1. "对第 X 步的结果满意吗?"
   - [ ] 满意,继续
   - [ ] 需要调整

### Iteration Triggers
- [Trigger 1]
- [Trigger 2]

### Quality Checks
- Check 1
- Check 2
```

## 错误处理 (Error Handling)

### 错误类型 (Error Types)

1. **输入错误** (Input Error)
   - 表现: 用户提供的输入不符合要求
   - 处理: 明确的错误消息 + 正确示例

2. **处理错误** (Processing Error)
   - 表现: 处理过程中遇到技术问题
   - 处理: 降级方案 + 用户确认

3. **输出错误** (Output Error)
   - 表现: 输出不符合预期
   - 处理: 可用性检查 + 质量反馈

### 错误处理模板 (Error Handling Template)

```markdown
### Error Handling

#### Error Type 1: [Name]
**Symptoms**: What the user sees
**Root Causes**: Why it happens
**Solutions**: How to fix
1. [Solution 1]
2. [Solution 2]
```

## 质量保证 (Quality Assurance)

### 内部检查 (Internal Checks)

- [ ] 每个阶段有清晰的输入/输出
- [ ] 每个分支有明确的触发条件
- [ ] 错误处理完整
- [ ] 有用户确认点

### 用户导向 (User-Oriented)

- [ ] 中文引导 + 英文技术标准
- [ ] 每个步骤都有明确的目标
- [ ] 用户可以随时确认进度
- [ ] 可以回退/重新选择

### 可测试性 (Testability)

- [ ] 每个阶段可单独测试
- [ ] 有典型的测试用例
- [ ] 有边缘情况测试
- [ ] 有错误输入测试

## 实施检查清单 (Implementation Checklist)

### Phase 1: 规划 (Planning)
- [ ] 定义所有阶段
- [ ] 确定分支条件
- [ ] 设计用户确认点

### Phase 2: 文档 (Documentation)
- [ ] 编写每个阶段的指令
- [ ] 添加错误处理说明
- [ ] 创建测试用例

### Phase 3: 验证 (Validation)
- [ ] 测试典型流程
- [ ] 测试分支流程
- [ ] 测试错误处理
- [ ] 测试用户体验

### Phase 4: 优化 (Optimization)
- [ ] 简化描述
- [ ] 移除冗余
- [ ] 优化举例
- [ ] 明确触发条件
