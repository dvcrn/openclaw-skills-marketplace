# Root Cause — 层层追踪根因分析

修 bug 修症状是无限循环。这个方法论强制你追到根因再动手。

## 核心原则

**不修症状，修根因。** 一个 bug 你修了，类似的 bug 还会冒出来——说明你修的是表面。

## 五步法

### Step 1: 复现（Reproduce）

先亲眼看到问题，不靠猜。

```bash
# 直接跑出问题的命令，保留完整输出
bash scripts/target.sh args 2>/tmp/debug_stderr.txt | tee /tmp/debug_stdout.txt

# 用 Python 检查输出中的异常
python3 -c "
import json
with open('/tmp/debug_stdout.txt') as f:
    data = json.loads(f.read())
# 找到异常值
for key, val in data.items():
    if val is None or val == 'null':
        print(f'⚠️ {key} = {val}')
"
```

**标准：能稳定复现再进入下一步。** 偶发的先找复现条件。

### Step 2: 定位（Locate）

从输出往回追，找到第一个出错的位置。

**方法 A: xtrace 追踪**（适合 shell 脚本）
```bash
bash -x scripts/target.sh args 2>/tmp/xtrace.txt
# 在 xtrace 里搜异常值
grep "null\|error\|异常关键词" /tmp/xtrace.txt | head -20
```

**方法 B: 分段验证**（适合数据流）
```
数据源 → 脚本A → 脚本B → 脚本C → 输出
   ✅       ✅       ❌       ❌
                     ^--- 问题在这
```

每个环节独立跑，看输出是否正确：
```bash
# 数据源正确吗？
bash scripts/idm-api.sh reviews PJ00009224 | jq '.result[0].fatherReview.state'
# → "待提交" ✅

# 脚本A的输出正确吗？
bash scripts/project-snapshot.sh PJ00009224 | jq '.review_summary.reviews[0].status'
# → null ❌  <--- 问题在这！
```

**方法 C: 环境差异**（跨平台 bug）
```bash
# macOS vs Linux 行为差异是常见根因
seq 0 -1        # macOS: 输出 0, -1; Linux: 空
date -j -f ...  # macOS BSD date vs GNU date
declare -A       # bash 3.x (macOS default) 不支持
```

### Step 3: 挖根因（Why × 5）

找到出错位置后，连续问 5 次"为什么"：

```
症状：周报出现 "null: 进行中"
为什么？→ jq 对空数组返回 null
为什么对空数组？→ ip_count=0 但 for 循环仍执行
为什么循环执行？→ seq 0 -1 在 macOS 输出了 0 和 -1
为什么 seq 0 -1 有输出？→ BSD seq 和 GNU seq 行为不同
根因：BSD/GNU seq 兼容性问题 + 缺少 count>0 guard
```

```
症状：健康分 100 但 TR3 逾期 75 天
为什么？→ review_summary.reviews[].status 全是 null
为什么 null？→ jq 逗号运算符 (A, B) 在 B 为空时影响 A 的输出
为什么用逗号？→ 把 fatherReview 和 childReview 展平到同一数组
根因：jq 逗号运算符对空迭代器的边界行为 + 没有分开处理两种 review
```

**根因特征：**
- 改了这一处，同类问题全部消失
- 不是"加个 if 绕过"，而是修正了错误的假设
- 能解释为什么之前没发现（测试只用了 childReview 非空的项目）

### Step 4: 修根因 + 防御

修根因，同时加防御层：

```bash
# ❌ 修症状（绕过）
if [ "$status" = "null" ]; then status="待提交"; fi

# ✅ 修根因（正确的 jq 结构）
# 拆成两个独立数组再合并，避免逗号运算符的边界行为
reviews='[...fatherReview...] + [...childReview...]'

# ✅ 加防御层（即使根因再次出现也不会输出 null）
for i in $([ "$count" -gt 0 ] && seq 0 $((count - 1))); do
```

### Step 5: 验证（Verify）

三层验证：

1. **直接验证**：重新跑出问题的命令，确认修复
2. **回归测试**：跑完整测试套件，确认没破坏别的
3. **同类检查**：全项目搜同样模式，防遗漏

```bash
# 同类检查：搜所有脚本里的 seq 循环
grep -rn 'seq 0 \$((.*- 1))' scripts/ | grep -v '.bak'
# → 发现 9 处，全部加 guard
```

## 常见根因模式

| 症状 | 典型根因 | 修法 |
|------|---------|------|
| 字段值为 null/空 | 数据映射错误（字段名不匹配、jq 路径错误） | 对照 API 原始输出逐字段核实 |
| 循环多执行/少执行 | 平台 seq/for 行为差异 | 加 count guard，或用 jq range() |
| "全部正常"但实际有问题 | 检测逻辑只覆盖部分状态 | 枚举所有状态值，确认每个都有分支处理 |
| 数据正确但输出错误 | 多数据源未交叉引用 | 画数据流图，检查每个节点的输入来源 |
| 间歇性失败 | 并行竞态/缓存/环境变量 | 串行复现 + 清缓存 + 检查环境 |
| A 修好了 B 又坏了 | 共享状态/全局变量/文件锁 | 隔离状态，每个模块独立数据路径 |

## 输出格式

```
## 根因分析报告

### 症状
[用户看到了什么]

### 追踪路径
1. 输出层: [什么值不对]
2. 处理层: [哪个脚本/函数出错]
3. 数据层: [数据从哪来，为什么错]
4. 平台层: [有没有环境/兼容性因素]

### 根因
[一句话说清根因]

### 修复
- 修了什么: [具体改动]
- 防御层: [加了什么保护]
- 同类检查: [搜了哪些类似模式，修了几处]

### 验证
- 直接验证: ✅/❌
- 回归测试: X/Y pass
- 同类处理: N 处已修
```

## 根因沉淀到记忆（新增）

修完 bug 后，将根因存入 `memory_store`，下次类似症状出现时自动召回。

### 存储格式

```
memory_store:
  text: "根因: {一句话根因}。症状: {症状描述}。修法: {修复方式}。防御: {防御措施}。"
  category: "decision"
  importance: 0.9
```

### 示例

```
memory_store(
  text="根因: BSD/GNU seq 兼容性——seq 0 -1 在 macOS 输出 0 和 -1，在 Linux 输出空。症状: 循环多执行导致 null 值。修法: 所有 seq 循环前加 count>0 guard。防御: bootstrap 模板中默认包含 guard。",
  category="decision",
  importance=0.9
)
```

### 自动召回

下次遇到类似症状时，`memory_recall` 会自动匹配：
- 用户说"循环多跑了" → 召回 seq 兼容性根因
- 用户说"字段是 null" → 召回 jq 逗号运算符根因
- 用户说"macOS 能跑 Linux 不行" → 召回平台兼容性根因库

### 根因文件归档

除了 memory_store，同时在项目内维护根因文件：

```
tests/root-causes/
├── RC-001-seq-compat.md
├── RC-002-jq-comma-operator.md
└── index.md              # 汇总表：症状→根因→修法
```

`index.md` 格式：

```markdown
| ID | 症状 | 根因 | 修法 | 日期 |
|----|------|------|------|------|
| RC-001 | 循环多执行/null值 | BSD/GNU seq 行为差异 | count>0 guard | 2026-02-20 |
| RC-002 | 字段值 null 但 API 有数据 | jq 逗号运算符空迭代器 | 拆数组再合并 | 2026-02-22 |
```

每次修完根因后，同时更新 index.md 和 memory_store。这样既有结构化归档（文件），又有语义检索（向量记忆）。

## When to Use

- Sub-agent 测试报告中的 P0/P1 问题
- 用户反馈"这个不对"
- 测试突然失败（之前 pass）
- 任何涉及"数据不对"的问题——先追根因再动手
- **新增**：修复任何 bug 后，检查根因库是否已有类似模式。有 → 合并。没有 → 新增。
