---
name: iterative-code-review
description: "Iterative code review using multiple independent subagent reviews. Use when user asks to review PR, code, or mentions \"review\", \"审查\", \"检查代码\", \"代码质量\". Automatically fixes all issues through review-fix-review cycles until consecutive two rounds have no new issues."
---

# Code Review Skill

Iterative code review through **parallel independent subagent reviews** until all issues are resolved.

## Core Principle

**Every review round spawns 3 PARALLEL subagents** - Maximizes issue detection, ensures comprehensive coverage.

---

## ⚠️ Pre-flight Checks

### Check 1: Model (CRITICAL)

**ALL subagents MUST use `bailian/glm-5`**

```javascript
sessions_spawn({
  runtime: "subagent",
  model: "bailian/glm-5",  // ⚠️ REQUIRED
  thinking: "high",
  task: `...`
})
```

**If glm-5 unavailable:**

```
⚠️ Model Check Failed: `bailian/glm-5` is not available

Options:
A. Wait for glm-5
B. Use qwen3.5-plus (sub-optimal for code)
C. User-specified model
D. Cancel

Please choose (A/B/C/D):
```

### Check 2: maxSpawnDepth

```bash
openclaw config get agents.defaults.subagents.maxSpawnDepth
```

| Value | Status |
|-------|--------|
| `≥1` | ✅ Proceed |
| `0` | ❌ Abort - inform user to update config |

---

## Workflow

### Round Structure

```
┌─────────────────────────────────────────────────────────┐
│  Review Round N                                          │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │
│  │Reviewer1│  │Reviewer2│  │Reviewer3│  ← 并行 3 个      │
│  └────┬────┘  └────┬────┘  └────┬────┘                  │
│       │            │            │                        │
│       └────────────┼────────────┘                        │
│                    ▼                                     │
│            ┌──────────────┐                              │
│            │ 汇总问题列表  │                              │
│            └──────┬───────┘                              │
│                   ▼                                      │
│            ┌──────────────┐                              │
│            │   Fixer      │  ← 单个 subagent 修复        │
│            └──────────────┘                              │
│                                                          │
│  → 如果有问题修复，进入下一轮 Review Round N+1            │
│  → 如果无新问题，Review 完成                              │
└─────────────────────────────────────────────────────────┘
```

### 1. 并行 Spawn 3 个 Reviewer Subagents

```javascript
// 同时 spawn 3 个 reviewer
const reviewers = [
  { label: "reviewer-1", focus: "功能正确性、测试覆盖" },
  { label: "reviewer-2", focus: "代码质量、最佳实践" },
  { label: "reviewer-3", focus: "安全性、边界情况" }
];

// 并行 spawn（不等待完成）
reviewers.forEach(r => {
  sessions_spawn({
    label: `{branch}-review-{round}-${r.label}`,
    runtime: "subagent",
    model: "bailian/glm-5",
    thinking: "high",
    timeoutSeconds: 180,  // 3 分钟超时
    task: `Review 代码变更：

## 你的角色
- Label: ${r.label}
- 关注点: ${r.focus}

## Review 范围
- 分支: {branchName}
- 对比: develop...HEAD

## 检查清单（必须逐项检查）

参考 references/checklist.md，重点关注你负责的领域：

### 通用检查项
- [ ] 业务逻辑正确性
- [ ] 错误处理完整性
- [ ] 边界条件处理
- [ ] 测试覆盖充分

### 角色-1 专项（功能正确性）
- [ ] 业务逻辑是否符合需求
- [ ] 条件判断是否完整
- [ ] 循环终止条件正确
- [ ] 边界值是否处理

### 角色-2 专项（代码质量）
- [ ] 变量命名清晰
- [ ] 函数长度合理（<50行）
- [ ] 无重复代码
- [ ] 注释充分

### 角色-3 专项（安全性）
- [ ] 外部输入验证
- [ ] 权限检查完整
- [ ] 无注入漏洞（SQL/XSS/命令）
- [ ] 敏感数据处理安全

## Review 要点
1. 之前的问题是否已修复？
2. 是否有新引入的问题？
3. 测试覆盖是否充分？
4. 安全性如何？

## 输出格式

### 问题列表

| 编号 | 级别 | 问题描述 | 文件:行号 |
|------|------|---------|-----------|
| 1 | P0 | xxx | src/xxx.ts:10 |
| 2 | P1 | xxx | src/yyy.ts:20 |

### 建议
- 建议 1
- 建议 2`
  });
});
```

### 2. 等待所有 Reviewer 完成，汇总结果

```javascript
// 等待 3 个 reviewer 完成
const results = await Promise.all([
  subagents.waitFor("reviewer-1"),
  subagents.waitFor("reviewer-2"),
  subagents.waitFor("reviewer-3")
]);

// 汇总问题列表（去重）
const allIssues = mergeAndDeduplicate(results);
```

### 3. Spawn Fixer Subagent（如有问题）

**P1: 超时与重试机制**

```javascript
const FIXER_TIMEOUT_MS = 5 * 60 * 1000;  // 5 分钟超时
const REVIEWER_TIMEOUT_MS = 3 * 60 * 1000;  // 3 分钟超时
const MAX_RETRIES = 3;

// 带超时和重试的 spawn 函数
async function spawnWithRetry(config, timeoutMs, maxRetries = MAX_RETRIES) {
  let lastError = null;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const sessionId = sessions_spawn(config);
      
      // 等待完成，带超时
      const result = await waitForCompletion(sessionId, timeoutMs);
      
      if (result.status === "timeout") {
        throw new Error(`Subagent timeout after ${timeoutMs}ms`);
      }
      
      return { success: true, result };
    } catch (error) {
      lastError = error;
      console.warn(`Attempt ${attempt}/${maxRetries} failed: ${error.message}`);
      
      if (attempt < maxRetries) {
        console.log(`Retrying in 10 seconds...`);
        await sleep(10000);
      }
    }
  }
  
  return { success: false, error: lastError };
}

// 检查必须修复的问题（P0/P1/P2）
function getMustFixIssues(issues) {
  return issues.filter(i => ['P0', 'P1', 'P2'].includes(i.level));
}

if (allIssues.length > 0) {
  const mustFixIssues = getMustFixIssues(allIssues);
  const p3Issues = allIssues.filter(i => i.level === 'P3');
  const suggestionIssues = allIssues.filter(i => i.level === '建议' || i.level === '低');
  
  const result = await spawnWithRetry({
    label: `{branch}-fixer-{round}`,
    runtime: "subagent",
    model: "bailian/glm-5",
    thinking: "high",
    timeoutSeconds: 300,  // 5 分钟硬超时
    task: `修复以下问题：

## 问题列表

### 必须修复 (P0/P1/P2)
${formatIssues(mustFixIssues)}

### 尽量修复 (P3)
${p3Issues.length > 0 ? formatIssues(p3Issues) : '（无）'}

### 建议修复 (建议/低)
${suggestionIssues.length > 0 ? formatIssues(suggestionIssues) : '（无）'}

## 修复要求
1. **必须**修复所有 P0/P1/P2 问题
2. **尽量**修复 P3 问题（除非风险过高）
3. **考虑**修复建议级别问题（如果简单且安全）
4. 如果跳过某个问题，请在回复中说明原因
5. 保持代码风格一致
6. 更新相关测试

## 完成后
- 提交 commit（使用 conventional commits 格式）
- 不要推送到 main`
  }, FIXER_TIMEOUT_MS);
  
  // 处理 Fixer 失败
  if (!result.success) {
    console.error(`Fixer failed after ${MAX_RETRIES} attempts:`, result.error);
    
    // 如果有必须修复的问题但 Fixer 失败，报告错误
    if (mustFixIssues.length > 0) {
      return {
        status: "FIXER_FAILED",
        message: `Fixer 无法完成修复，请人工介入`,
        unresolvedIssues: mustFixIssues,
        error: result.error
      };
    }
    
    // 如果只有 P3 问题，可以继续
    console.log("仅有 P3 问题未修复，继续流程...");
  }
  
  // 进入下一轮 review
  return startNextRound();
}
```

### 4. 退出标准（强制要求）

**⚠️ 必须同时满足以下条件才能结束 Review：**

```
1. 连续两轮 Review 都未发现任何 P0/P1/P2 问题
2. 所有发现的问题（包括 P3）都已修复或已说明跳过原因
```

**具体判断逻辑**：

```javascript
const MAX_ROUNDS = 10;  // 最大轮次限制，防止无限循环
const FIXER_TIMEOUT_MS = 5 * 60 * 1000;  // Fixer 超时：5 分钟
const REVIEWER_TIMEOUT_MS = 3 * 60 * 1000;  // Reviewer 超时：3 分钟
const MAX_RETRIES = 3;  // 最大重试次数

let consecutiveCleanRounds = 0;  // 连续无问题的轮数
let currentRound = 0;
let hasUnresolvedP3 = false;  // 是否有未处理的 P3

function checkCompletion(currentRoundIssues, allP3Resolved) {
  currentRound++;
  
  // P0: 最大轮次检查 - 防止无限循环
  if (currentRound >= MAX_ROUNDS) {
    return {
      status: "MAX_ROUNDS_EXCEEDED",
      message: `已达到最大轮次 ${MAX_ROUNDS}，强制退出。请人工检查未解决的问题。`
    };
  }
  
  // 检查 P0/P1/P2 问题
  const mustFixIssues = currentRoundIssues.filter(i => 
    ['P0', 'P1', 'P2'].includes(i.level)
  );
  
  // 检查 P3 问题
  const p3Issues = currentRoundIssues.filter(i => i.level === 'P3');
  
  if (mustFixIssues.length === 0 && p3Issues.length === 0) {
    // 本轮无任何问题
    consecutiveCleanRounds++;
    
    if (consecutiveCleanRounds >= 2 && allP3Resolved) {
      return { status: "REVIEW_COMPLETE" }; // 连续两轮无问题 + P3 已处理
    }
  } else {
    // 发现问题，重置计数
    consecutiveCleanRounds = 0;
    if (p3Issues.length > 0) {
      hasUnresolvedP3 = true;
    }
  }
  
  return { status: "CONTINUE" }; // 需要继续
}
```

**⚠️ 重要：连续两轮的逻辑**

```
consecutiveCleanRounds 的含义是"连续多少轮没有发现新问题"

Round 1: 发现问题 → Fixer → consecutiveCleanRounds = 0
Round 2: 无 P0/P1/P2/P3 → consecutiveCleanRounds = 1 → 继续下一轮
Round 3: 无 P0/P1/P2/P3 → consecutiveCleanRounds = 2 → ✅ 可以结束

如果 Round 3 发现新问题：
Round 3: 发现问题 → consecutiveCleanRounds = 0 → Fixer
Round 4: 无问题 → consecutiveCleanRounds = 1
Round 5: 无问题 → consecutiveCleanRounds = 2 → ✅ 可以结束
```

**为什么需要连续两轮？**
- 避免单轮遗漏 bug 的异常退出
- 确保修复后没有引入新问题
- 提高代码审查质量

**示例**：
```
Round 1: 发现 10 个问题 → Fixer 修复
Round 2: 发现 3 个新问题 → Fixer 修复
Round 3: 无问题 → consecutiveCleanRounds = 1
Round 4: 无问题 → consecutiveCleanRounds = 2 → ✅ 结束
```

**如果 Round 4 发现新问题**：
```
Round 4: 发现 1 个问题 → consecutiveCleanRounds = 0 → 继续循环
Round 5: 无问题 → consecutiveCleanRounds = 1
Round 6: 无问题 → consecutiveCleanRounds = 2 → ✅ 结束
```

**达到最大轮次时**：
```
Round 10: 仍有问题 → ⚠️ MAX_ROUNDS_EXCEEDED
→ 强制退出，报告未解决问题列表
→ 建议人工介入
```

---

## Issue Severity

| Level | Definition | Examples | Fix Requirement |
|-------|------------|----------|-----------------|
| **P0** | Critical - Fix immediately | Runtime errors, security vulnerabilities | 必须 |
| **P1** | High - Fix this iteration | Functional defects, missing error handling | 必须 |
| **P2** | Medium - Should fix | Code quality, test coverage gaps | 必须 |
| **P3** | Low - Fix in same PR | Code style, documentation, minor improvements | 尽量修复 |

### P3 处理规则

**⚠️ P3 不是"跳过"，而是"尽量修复"！**

Fixer 对 P3 的处理：
1. ✅ **优先修复**：简单、低风险、不影响稳定性的 P3 问题
2. ⚠️ **谨慎处理**：需要较大改动的 P3，评估风险后决定
3. ❌ **跳过并说明**：高风险或耗时过长的 P3，在回复中说明原因

**示例：**
```
✅ 可修复的 P3：
- 移除 console.log
- 添加注释
- 变量重命名
- 简化条件表达式

⚠️ 需评估的 P3：
- 提取方法（可能影响调用链）
- 类型定义重构（可能影响多处）

❌ 应跳过的 P3：
- 大规模代码重组
- 需要引入新依赖
- 可能破坏测试的改动
```

---

## Reviewer 角色分工

| Reviewer | 关注点 | 检查项 |
|----------|--------|--------|
| **Reviewer-1** | 功能正确性 | 业务逻辑、测试覆盖、边界条件 |
| **Reviewer-2** | 代码质量 | 代码结构、命名规范、可维护性 |
| **Reviewer-3** | 安全性 | 安全漏洞、输入验证、权限控制 |

---

## 汇总逻辑

```javascript
function mergeAndDeduplicate(results) {
  const issues = [];
  const seen = new Set();
  
  for (const result of results) {
    for (const issue of result.issues) {
      const key = `${issue.level}:${issue.file}:${issue.line}`;
      if (!seen.has(key)) {
        seen.add(key);
        issues.push(issue);
      }
    }
  }
  
  // 按 P0 > P1 > P2 > P3 排序
  return issues.sort((a, b) => {
    const order = { P0: 0, P1: 1, P2: 2, P3: 3 };
    return order[a.level] - order[b.level];
  });
}
```

---

## ⚠️ 强制自动循环（不要问用户）

```
Review Round 1 → Fixer → Review Round 2 → Fixer → ... → 连续两轮无问题 → 结束
                                    ↓
                          （最多 10 轮）
                                    ↓
                          超时/失败 → 重试 3 次 → 人工介入
```

**禁止行为**：
- ❌ 不要在 Review 后问"需要修复吗？"
- ❌ 不要在 Fixer 后问"要继续 Review 吗？"
- ❌ 不要中断自动循环流程
- ❌ 不要在单轮无问题后就结束

**正确流程**：
1. 检查 `currentRound >= MAX_ROUNDS`，若达到上限则强制退出
2. 并行 spawn 3 个 reviewer（带超时）
3. 等待全部完成，处理超时/失败（重试 3 次）
4. 汇总问题，仅检查 P0/P1/P2（P3 可选）
5. 如果有问题 → spawn Fixer（带超时和重试）→ 回到步骤 1
6. 如果无问题 → consecutiveCleanRounds++
7. 如果 consecutiveCleanRounds < 2 → 回到步骤 1
8. 如果 consecutiveCleanRounds >= 2 → ✅ 结束，提交 PR

**异常处理路径**：
- Reviewer 超时/失败 → 重试 3 次 → 仍失败则报告错误
- Fixer 超时/失败 → 重试 3 次 → 仍有 P0/P1/P2 则人工介入
- 达到 MAX_ROUNDS → 强制退出，报告未解决问题

## Key Points

1. **3 个 reviewer 并行** - 最大化问题发现
2. **1 个 fixer 串行** - 统一修复，避免冲突
3. **Model MUST be glm-5** - 每个 subagent 必须用 glm-5
4. **强制使用检查清单** - Reviewer 必须按 checklist 逐项检查
5. **去重汇总** - 避免重复修复同一问题
6. **连续两轮无问题才结束** - 避免单轮遗漏 bug
7. **自动提交 PR** - Review 完成后自动提交
8. **MAX_ROUNDS = 10** - 防止无限循环
9. **超时机制** - Fixer 5 分钟，Reviewer 3 分钟
10. **重试机制** - 失败最多重试 3 次
11. **P3 尽量修复** - 退出时所有问题都应处理（修复或说明跳过原因）

---

## 退出标准图示

### 正常流程（连续两轮无问题）

```
Round 1: 发现问题 → Fixer → clean = 0
    ↓
Round 2: 发现问题 → Fixer → clean = 0
    ↓
Round 3: 无问题 → clean = 1 → 继续下一轮（必须连续两轮）
    ↓
Round 4: 无问题 → clean = 2 → ✅ END
```

### 有新问题继续

```
Round 4: 发现问题 → clean = 0 → Fixer
    ↓
Round 5: 无问题 → clean = 1
    ↓
Round 6: 无问题 → clean = 2 → ✅ END
```

### Round 3 发现新问题的流程

```
Round 2: 无问题 → clean = 1
    ↓
Round 3: 发现新问题 → clean = 0 → Fixer
    ↓
Round 4: 无问题 → clean = 1
    ↓
Round 5: 无问题 → clean = 2 → ✅ END
```

### 达到最大轮次

```
Round 10: 仍有问题
    ↓
⚠️ MAX_ROUNDS_EXCEEDED
    ↓
强制退出，报告未解决问题 → 人工介入
```

### 异常处理

```
Fixer 超时/失败
    ↓
重试 1 → 重试 2 → 重试 3
    ↓
仍失败？
    ├─ 有 P0/P1/P2 问题 → ⚠️ FIXER_FAILED → 人工介入
    └─ 仅 P3 问题 → 记录未处理项 → 继续流程
```

### P3 未完全处理的流程

```
Round 2: 发现 P3 问题 → Fixer 尝试修复
    ↓
Fixer 回复: "P3-xxx 跳过，原因: 风险过高"
    ↓
Round 3: 无新问题 → clean = 1
    ↓
Round 4: 无新问题 → clean = 2 → ✅ END
    ↓
最终报告: "Review 完成，P3-xxx 已跳过（原因: 风险过高）"
```

---

## References

- [checklist.md](references/checklist.md) - Complete review checklist