# Snapshot — L4b 输出快照对比与多次采样

解决 AI 输出的不确定性问题：同样的输入，每次输出不完全一样。单次断言不可靠，需要快照基线 + 多次采样。

## 核心概念

```
传统测试:  input → function → output == expected  ✅/❌
AI 输出:   input → LLM → output ≈ expected        需要模糊匹配 + 多次采样
```

## 快照存储

所有快照存在 `tests/snapshots/` 目录：

```
tests/snapshots/
├── L4b-weekly-report.snapshot        # 纯文本快照
├── L4b-weekly-report.meta.json       # 元数据（创建时间、采样次数、通过率）
├── L4b-morning-card.snapshot
├── L4b-morning-card.meta.json
└── ...
```

### 快照文件格式

```
# Snapshot: L4b-weekly-report
# Created: 2026-02-27
# Updated: 2026-02-27
# Samples: 3
# Pass rate: 3/3

## Structure Markers (must exist)
- 本周进展
- 风险与问题
- 下周计划
- 讨论要点

## Content Quality Markers (at least 60% must exist)
- 具体项目名称（非"某项目"）
- 具体日期或时间范围
- 具体数据或数量
- 具体人名或角色
- 具体行动项

## Anti-patterns (must NOT exist)
- 暂无重大风险
- 持续跟踪
- 正常推进中
- 无特殊情况
```

### 元数据文件格式

```json
{
  "testId": "L4b-weekly-report",
  "createdAt": "2026-02-27T10:00:00Z",
  "updatedAt": "2026-02-27T10:00:00Z",
  "totalRuns": 5,
  "passCount": 4,
  "failCount": 1,
  "passRate": 0.8,
  "lastResults": [
    {"timestamp": "2026-02-27T10:00:00Z", "pass": true, "structureScore": 4, "contentScore": 3, "antiPatternHits": 0},
    {"timestamp": "2026-02-27T10:01:00Z", "pass": true, "structureScore": 4, "contentScore": 4, "antiPatternHits": 0},
    {"timestamp": "2026-02-27T10:02:00Z", "pass": false, "structureScore": 4, "contentScore": 1, "antiPatternHits": 2}
  ]
}
```

## 断言流程

### 首次运行（建立基线）

```bash
# 1. 生成输出
output=$(bash scripts/weekly-report.sh PJ00003150)

# 2. 交互确认：展示输出给用户
echo "首次运行，请确认此输出是否符合预期作为快照基线："
echo "$output"

# 3. 用户确认后，提取 markers 保存快照
# Structure Markers: 从输出中提取固定结构（标题、必要段落）
# Content Quality Markers: 提取内容质量特征
# Anti-patterns: 定义不应出现的模式
```

### 后续运行（对比快照）

```bash
snapshot_file="tests/snapshots/L4b-weekly-report.snapshot"

# === 结构断言（必须全部满足）===
structure_markers=$(grep '^- ' "$snapshot_file" | sed -n '/Structure Markers/,/Content Quality/p' | grep '^- ')
structure_pass=0
structure_total=0
while IFS= read -r marker; do
  marker_text=$(echo "$marker" | sed 's/^- //')
  structure_total=$((structure_total + 1))
  if echo "$output" | grep -q "$marker_text"; then
    structure_pass=$((structure_pass + 1))
  fi
done <<< "$structure_markers"

# 结构必须 100% 匹配
[ "$structure_pass" -eq "$structure_total" ] || log_fail "L4b: 结构缺失 ($structure_pass/$structure_total)"

# === 内容质量断言（≥60% 满足）===
content_markers=$(grep '^- ' "$snapshot_file" | sed -n '/Content Quality/,/Anti-patterns/p' | grep '^- ')
content_pass=0
content_total=0
while IFS= read -r marker; do
  marker_text=$(echo "$marker" | sed 's/^- //')
  content_total=$((content_total + 1))
  # 内容 marker 是模式匹配，不是精确匹配
  if echo "$output" | grep -qE "$marker_text"; then
    content_pass=$((content_pass + 1))
  fi
done <<< "$content_markers"

content_rate=$(echo "scale=2; $content_pass / $content_total" | bc)
[ "$(echo "$content_rate >= 0.6" | bc)" -eq 1 ] || log_fail "L4b: 内容质量不足 ($content_pass/$content_total = $content_rate)"

# === 反模式断言（必须全部不出现）===
anti_markers=$(grep '^- ' "$snapshot_file" | sed -n '/Anti-patterns/,//p' | grep '^- ')
while IFS= read -r marker; do
  marker_text=$(echo "$marker" | sed 's/^- //')
  if echo "$output" | grep -q "$marker_text"; then
    log_fail "L4b: 命中反模式: $marker_text"
  fi
done <<< "$anti_markers"
```

## 多次采样策略

AI 输出每次不同，单次断言不可靠。对关键 L4b 测试做多次采样：

```bash
# 采样 3 次，≥ 2 次通过才算 pass
SAMPLES=3
PASS_THRESHOLD=2
pass_count=0

for i in $(seq 1 $SAMPLES); do
  output=$(bash scripts/weekly-report.sh PJ00003150 2>/dev/null)
  if run_l4b_assertions "$output" "$snapshot_file"; then
    pass_count=$((pass_count + 1))
  fi
  [ "$i" -lt "$SAMPLES" ] && sleep 2  # 避免限流
done

if [ "$pass_count" -ge "$PASS_THRESHOLD" ]; then
  log_pass "L4b: 周报质量 ($pass_count/$SAMPLES 通过)"
else
  log_fail "L4b: 周报质量不稳定 ($pass_count/$SAMPLES 通过)" "多次采样未达阈值"
fi

# 更新元数据
update_snapshot_meta "$snapshot_file" "$pass_count" "$SAMPLES"
```

### TypeScript 版本

```typescript
describe('L4b: weekly report quality', () => {
  it('passes content quality check in ≥2/3 samples', async () => {
    const snapshot = loadSnapshot('L4b-weekly-report');
    let passCount = 0;

    for (let i = 0; i < 3; i++) {
      const output = await generateWeeklyReport('PJ00003150');
      if (assertSnapshot(output, snapshot)) {
        passCount++;
      }
    }

    expect(passCount).toBeGreaterThanOrEqual(2);
    updateSnapshotMeta('L4b-weekly-report', passCount, 3);
  });
});
```

## 快照管理命令

在 Core Workflow 触发表中，用户说 "快照对比" / "snapshot" 时执行：

| 操作 | 说明 |
|------|------|
| **snapshot create** `<test-id>` | 运行测试，交互确认后保存为基线快照 |
| **snapshot update** `<test-id>` | 重新运行并更新快照（需确认） |
| **snapshot diff** `<test-id>` | 对比当前输出与快照的差异 |
| **snapshot list** | 列出所有快照及其通过率 |
| **snapshot prune** | 删除过期快照（>30天未更新且通过率100%） |

## 什么时候用快照，什么时候不用

| 场景 | 用快照？ | 理由 |
|------|---------|------|
| 固定函数输入输出 | 不用 | 用精确断言更好 |
| AI 生成的报告/卡片 | **用** | 输出不确定，需要模糊匹配 |
| 模板渲染结果 | 看情况 | 模板固定部分用精确断言，动态部分用快照 |
| API 返回值 | 不用 | mock 掉或用精确断言 |

## 快照劣化告警

如果连续 3 次运行的通过率低于历史平均值，触发告警：

```
⚠️ L4b 质量劣化告警
测试: L4b-weekly-report
历史通过率: 90%
最近3次: 33% (1/3)
可能原因: 上游数据变化 / prompt 变更 / 模型更新
建议: 运行根因分析（references/root-cause.md）
```
