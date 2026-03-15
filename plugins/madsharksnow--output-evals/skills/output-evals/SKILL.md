---
name: output-evals
description: "Full-pipeline test automation for any project. Scans coverage, fills gaps, runs L1-L6 tests (unit/integration/scenario/experience/user-journey/scale), performs spec-driven gap analysis, spawns sub-agent E2E black-box verification, auto-fixes failures with root-cause analysis, and persists findings. Supports Bash, TypeScript, and Python. Use when asked to write tests, check coverage, find untested code, improve test quality, do health checks, run test pipeline, debug failures, or start tests for a new project."
---

# Test Suite — 全流程测试流水线

**默认行为：一键跑完全部流程，发现问题就地修复，直到零 P0/P1。** 说"跑测试"就启动，不问"你想跑哪个阶段"。

## 流水线（按顺序执行，不停不问）

**1. 侦察** — 检测语言 → 扫描覆盖率（`references/scan.md`）→ 11维 Gap 分析（`references/gaps.md`）→ Infra 卫生（`references/infra.md`）。Gap 报告存到 `tests/gap-reports/`，与上次 diff。

**2. 补缺** — 为每个未覆盖文件生成 ≥1 个 L1 测试。为每个 Gap Missing/Partial 维度生成对应层级测试。为每个有输出的模块生成 L4b 断言。新项目用 `references/bootstrap.md` 初始化框架。

**3. 执行** — L1→L2→L3→L4a→L4b→L5→L6，逐层跑，前一层全 pass 才跑下一层。L4b 跑 3 次取 ≥2/3 通过。有 fail → 进入步骤 4。全 pass → 跳到步骤 5。

**4. 修复循环（最多 5 轮）** — 对每个 fail：根因五步法（见下文）→ 修代码 → 回归全量测试 → grep 全项目搜同类反模式一并修。全 pass → 进入步骤 5。

**5. E2E 黑盒** — 有用户交互产物（卡片/消息/API）→ 必须 spawn 子 agent（`references/subagent-test.md`）。收报告 → 过滤工程师视角假问题 → 分级 P0/P1/P2。有 P0/P1 → 回到步骤 4 修复，修完再 spawn 验证（最多 R5）。**跳过 E2E 必须在最终报告中说明理由。**

**6. 沉淀** — 根因 → `memory_store` + `tests/root-causes/index.md`。快照基线更新。Gap/E2E 报告归档。输出最终摘要。

## 单步触发（可选）

用户明确指定时只跑某步："扫描"→步骤1 / "写测试"→步骤2 / "跑一下"→步骤3 / "修失败"→步骤4 / "E2E"→步骤5 / "根因"→五步法 / "快照"→`references/snapshot.md` / "压测"→`references/scale-test.md`

## 层级定义

```
L1 Unit        — 单模块输入→输出
L2 Integration — 多模块数据流转
L3 Scenario    — 完整业务流程
L4 Experience  — 输出质量
    L4a Format:  结构/长度/JSON合法/无敏感信息泄露
    L4b Content: 信息密度/数据新鲜度/语义价值（比 L4a 更重要——格式完美但内容空洞比崩溃更危险）
L5 User Journey — 必须表述为用户问题（"PM会收到重复晨报吗？" 不是 "dedup test"）
L6 Scale       — 并发安全/幂等/负载/配置一致（详见 references/scale-test.md）
```

分类规则：来自代码结构 → L1-L3，来自用户问题 → L5，来自输出质量 → L4，来自规模 → L6。

## Bash 测试模板

```bash
echo "━━━ [ID]: [description] ━━━"
# Setup
test_data="..."
# Act
result=$(bash "${SCRIPTS}/target.sh" args 2>/dev/null)
# Assert
if [ condition ]; then
  log_pass "[ID]: [what passed]"
else
  log_fail "[ID]: [what failed]" "[diagnostic detail]"
fi
# Cleanup
rm -rf test_data
```

TypeScript/Python 模板见 `references/multi-lang.md`。

**通用规则**：每个测试清理自己的数据。外部 API 用 `_timeout` 包装。不暴露真实 secret。每个函数同时测 happy path 和 error path。

## L4b 内容质量断言（不可跳过）

**每个有输出的模块必须有 L4b 测试。** 5 个强制检查：

1. **关键字段非空** — 断言输出中关键字段有值，不是 null/空/"暂无"
   ```bash
   echo "$report" | jq -e '.discussion_points | length > 0'
   echo "$report" | jq -e '.discussion_points[0] | length > 10'
   ```

2. **上游数据可用** — 断言上游提取的数据本身有效
   ```bash
   text_count=$(echo "$messages" | jq '[.messages[] | select(.text != null)] | length')
   [ "$text_count" -gt 0 ] || log_fail "L4b: text 字段全空"
   ```

3. **信息密度** — 有数据但输出说"暂无" → FAIL
   ```bash
   echo "$report" | grep -q "暂无重大风险" && log_fail "L4b: 有数据但说暂无"
   ```

4. **数据新鲜度** — 日期在预期范围
   ```bash
   echo "$report" | grep -q "$(date +%Y-%m-%d)" || log_fail "L4b: 日期不是今天"
   ```

5. **跨层验证** — L4b 失败时向上追溯：L1 数据提取对不对？L2 流转对不对？还是只有 L4a 展示问题？

**反模式**：text 全 null → L4b 抓。"暂无重大风险"但有 77 条消息 → L4b 抓。"讨论要点: 77条消息"无摘要 → L4b 抓。

**何时加 L4b**：每个产出用户可见内容的模块。每个数据提取模块。每次"跑了但没用"的 bug 后。

AI 输出用快照多采样（`references/snapshot.md`）：跑 3 次，≥2/3 通过。

## 根因五步法（步骤 4 核心）

**不修症状，修根因。** `if null then default` 不是修复。

**Step 1 复现** — 跑失败的命令，保留完整 stdout/stderr。能稳定复现再往下。

**Step 2 定位** — 三种方法：
- xtrace：`bash -x scripts/target.sh args 2>/tmp/xtrace.txt`，搜异常值
- 分段验证：数据源→脚本A→脚本B→输出，逐段检查哪里开始错
- 环境差异：macOS/Linux 行为不同（seq、date、declare -A）

**Step 3 Why×5** — 在出错位置连问 5 次为什么：
```
症状：周报出现 "null: 进行中"
→ jq 对空数组返回 null
→ count=0 但 for 循环仍执行
→ seq 0 -1 在 macOS 输出了 0 和 -1
→ BSD seq 和 GNU seq 行为不同
根因：BSD/GNU seq 兼容性 + 缺少 count>0 guard
```

**Step 4 修根因+防御** — 修正错误假设（不是加 if 绕过），同时加防御层。

**Step 5 验证** — 三层：①重跑失败的命令 ②跑全量测试 ③grep 全项目搜同模式一并修
```bash
grep -rn 'seq 0 \$((.*- 1))' scripts/  # 发现 9 处，全部加 guard
```

**修完 → 沉淀**：`memory_store(text="根因: {根因}。症状: {症状}。修法: {修法}。", category="decision", importance=0.9)` + 写入 `tests/root-causes/RC-{NNN}.md`。

常见根因表：

| 症状 | 典型根因 | 修法 |
|------|---------|------|
| 字段 null/空 | 数据映射错（字段名/jq路径） | 对照 API 原始输出核实 |
| 循环多/少执行 | 平台 seq/for 差异 | count guard |
| "全正常"但有问题 | 检测逻辑只覆盖部分状态 | 枚举所有状态 |
| A 好了 B 坏了 | 共享状态/全局变量 | 隔离数据路径 |

详见 `references/root-cause.md`。

## References

| 文件 | 何时加载 |
|------|---------|
| `references/scan.md` | 步骤 1 扫覆盖率 |
| `references/gaps.md` | 步骤 1 Gap 分析 |
| `references/infra.md` | 步骤 1 安全卫生 |
| `references/bootstrap.md` | 步骤 2 新项目初始化 |
| `references/root-cause.md` | 步骤 4 需要更多根因案例时 |
| `references/subagent-test.md` | 步骤 5 子 agent E2E |
| `references/multi-lang.md` | 项目含 TypeScript/Python 时 |
| `references/snapshot.md` | L4b 需要快照对比时 |
| `references/scale-test.md` | 需要 L6 规模化测试时 |

## Key Principles

1. **流水线优先** — 默认全跑，不问"你想干什么"
2. **发现即修复** — 发现 fail 就进修复循环，不只报告
3. **从 spec 推导，不从 bug 推导** — 先 Gap 分析，再写测试
4. **根因不症状** — 追到底再动手，修完沉淀到 memory_store
5. **修一个灭一类** — grep 全项目搜同模式，一并修
6. **AI 输出多采样** — L4b 跑 3 次取 2/3，不做单次赌博
7. **结果全持久化** — 报告/快照/根因存文件，跨会话追踪
8. **安全阀** — 修复最多 5 轮，E2E 最多 R5，超过报告让用户决策
9. **测试是活文档** — 需求变了更新 L5-SPEC.md
10. **用户问题 > 技术描述** — L5 测试名是用户问题，不是技术术语
