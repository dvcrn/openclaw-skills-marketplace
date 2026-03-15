# Gaps — Spec-Driven Gap Analysis

Systematically find missing tests using the 11-dimension scan from SpecKit Clarify methodology.

## 11 Dimensions

For each dimension, assess: **Clear** (fully tested) / **Partial** (some coverage) / **Missing** (no tests).

### 1. Functional Scope & Behavior
- Every command/subcommand has ≥1 test?
- Both success and error paths tested?
- Boundary values (empty input, max length, special chars)?

### 2. Data Model
- CRUD operations all tested (create/read/update/delete)?
- Data format validated (required fields, types)?
- Relationships between entities tested (e.g., action → risk linkage)?

### 3. User Roles
- Different roles produce different results?
- Isolation between users/roles tested?
- Permission boundaries tested (A can't see B's data)?

### 4. Interaction & UX Flow
- Normal flow (happy path) tested?
- Error flow (invalid input, missing data, API failure)?
- Empty state (no data yet)?
- Timeout / slow response handling?

### 5. Non-Functional Quality
- Performance baseline recorded (N records in <Xs)?
- Output length/format constraints?
- Resource usage reasonable?

### 6. Integration & External Dependencies
- API failure → graceful degradation?
- Auth expiry handling?
- Rate limiting behavior?
- Continuous failure → notification?

### 7. Edge Cases & Error Handling
- Corrupted input data → doesn't crash?
- Concurrent access (if applicable)?
- Disk full / write failure?
- Partial data (some fields missing)?

### 8. Constraints & Tradeoffs
- Known limitations tested (documented limits)?
- Configuration constraints validated?

### 9. Terminology & Sensitivity
- Internal IDs not leaked in output?
- Sensitive data (passwords, tokens) not in test output?
- Consistent naming (no PJ号/PN号 mixing)?

### 10. Acceptance Criteria (L4a + L4b)
- L4a: Structured validation checklist for major outputs?
- L4a: Measurable criteria (not "looks good" but "contains sections X, Y, Z")?
- L4a: Date freshness, required sections, format compliance?
- **L4b: Content quality** — Key data fields populated (not null/empty/"暂无")?
- **L4b: Information density** — Output contains specific facts, not generic fillers?
- **L4b: Upstream data validity** — Data extraction scripts produce non-empty critical fields?
- **L4b: Cross-layer** — If output is empty/generic, is the data layer feeding it broken?

### 11. Lifecycle & State Transitions
- Every state transition tested (open→resolved, active→inactive)?
- State transition side effects (inactive group → excluded from reports)?
- Lifecycle edge cases (re-activate, re-open)?

## Procedure

1. Read all scripts and test files
2. Score each dimension: Clear / Partial / Missing
3. For Partial/Missing, calculate **Impact × Uncertainty**:
   - Impact: How bad if this breaks? (High/Medium/Low)
   - Uncertainty: How likely is this untested path hit? (High/Medium/Low)
4. Rank by Impact × Uncertainty, top 5 become priority gaps
5. For each gap, generate:
   - Which layer (L1-L5) the test belongs to
   - A test code skeleton ready to implement
   - The user question it answers (for L5)

## Output Format

```
Gap Analysis: [Project Name]
Date: YYYY-MM-DD

| # | Dimension | Status | Impact | Priority |
|---|-----------|--------|--------|----------|
| 1 | Functional | Clear  | -      | ✅       |
| 4 | Interaction | Missing | High | 🔴      |

Top Gaps:
1. [Dimension] — [Specific gap] → [Suggested test] → [Layer]
2. ...
```

## 结果持久化与历史 Diff（新增）

### 保存 Gap 报告

每次 gap 分析完成后，结果保存到文件：

```
tests/gap-reports/
├── 2026-02-20-gaps.md
├── 2026-02-27-gaps.md
└── latest.md → 2026-02-27-gaps.md (symlink)
```

### Diff 对比

下次运行 gap 分析时，自动与上次对比：

```
Gap Analysis Diff: 2026-02-20 → 2026-02-27
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

改善:
  ✅ Dimension 4 (Interaction): Missing → Partial (+3 tests added)
  ✅ Dimension 10 (Acceptance): Partial → Clear (+L4b tests added)

劣化:
  ⚠️ Dimension 6 (Integration): Clear → Partial (new API endpoint untested)

不变:
  Dimension 1-3, 5, 7-9, 11: unchanged

Top New Gaps:
  1. [Dimension 6] 新增的 review-checker API 无失败降级测试
```

### 保存流程

gap 分析完成后自动执行：
1. 生成报告 → 保存到 `tests/gap-reports/YYYY-MM-DD-gaps.md`
2. 如果存在 `latest.md`，与之 diff → 展示变化
3. 更新 `latest.md` 软链接

### 在 CI 中使用

```bash
# 如果有新增 Missing 维度（劣化），CI 返回非零
bash tests/run-gap-analysis.sh --fail-on-regression
```

## Known Patterns (from experience)

以下为项目特定经验。其他项目可能不适用，但模式有参考价值：

- **jq `//` operator**: `false // default` returns default because jq treats false as empty. Use `if has("field") then (.field | tostring) else "default" end`. （项目特定：jq 重度使用的 Bash 项目）
- **Existence-only tests**: `[ -f script.sh ]` is not a functional test. The script could be empty and still pass. （通用模式）
- **Config duplication**: Same value hardcoded in N files → one change needs N updates → silent drift. （通用模式）
- **AI 输出波动**: 同样的 prompt 不同时间结果不同 → 用 snapshot 多次采样而非单次断言. （通用模式：所有 LLM 输出）
- **平台差异**: macOS/Linux 工具行为不同（seq, date, sed） → 每个平台都要跑测试. （通用模式：跨平台 Bash 脚本）
