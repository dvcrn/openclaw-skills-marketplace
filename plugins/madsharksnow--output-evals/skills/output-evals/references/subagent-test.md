# Sub-Agent Testing

用子 agent 做端到端黑盒测试：给子 agent 一个用户角色和测试任务，让它独立执行脚本、收集数据、发送真实产物（卡片/消息），输出结构化报告。

## 何时使用

- **体验层验证**：工具测试通过了但用户体验不确定时（R5 交互层测试）
- **跨模型验证**：用不同模型跑相同测试，验证 prompt/playbook 的鲁棒性
- **真实数据端到端**：需要从 API 获取真实数据 → 组装 → 发送真实产物
- **新功能冒烟**：新增脚本/卡片模板后，快速验证完整链路

## 任务模板

```
你是{公司}的{角色}"{人名}"，第{N}轮试用{产品名}。

**本轮重点：{测试主题}**

## A. 验证上轮修复
{列出上轮发现的问题，每个给出验证命令}

## B. 新场景测试
{列出新测试场景，每个给出具体执行步骤和预期}

## 输出要求
按固定格式输出结构化报告：
- 修复验证表（通过/失败）
- 新场景表（步骤/状态/备注）
- 整体评分
- 还有什么断点
```

## 设计原则

### 1. 给具体命令，不给抽象指令

❌ 差："测试催办功能"
✅ 好：
```bash
bash ai-pm/scripts/review-checker.sh PJ00003150 2>/dev/null | jq '.nudge_items[0]'
```

子 agent 没有你的上下文，必须给完整可执行的命令。

### 2. 区分工具问题 vs 用户问题

子 agent 会模拟"在终端跑脚本"的工程师视角，可能报告：
- "脚本 exit code 非零" — 可能是正常的（如无数据时返回 5）
- "--help 输出不够清晰" — 用户根本不跑脚本
- "JSON 字段名不直观" — 用户看卡片不看 JSON

**处理方式**：收到报告后，先过滤掉非用户视角的问题，只修真正影响用户体验的。

### 3. 真实产物发送

测试卡片/消息时，让子 agent 发送到**管理员的飞书**，不要发给被催人或其他用户：
```
发送命令中 receive_id 只用 {管理员open_id}
```

### 4. 数据处理注意事项

- IDM API 返回可能含控制字符 → 用 `json.loads(raw, strict=False)`
- `jq` 不支持控制字符 → 复杂数据处理改用 Python
- IDM `feishuUserId` 是飞书 `user_id`（已验证），可直接用于发消息

### 5. 评分标准建议

| 维度 | 权重 | 说明 |
|------|------|------|
| 数据获取 | 30% | API 调用成功率，数据完整性 |
| 产物质量 | 30% | 卡片/报告/消息内容准确，格式正确 |
| 链路完整 | 20% | 端到端无断点 |
| 错误降级 | 10% | API 失败/数据缺失时的降级处理 |
| 边界覆盖 | 10% | 无数据/多数据/特殊字符等边界 |

## spawn 参数

```
sessions_spawn:
  task: <测试任务描述>
  mode: run          # 一次性执行
  label: <测试标签>   # 如 pjm-ux-test-r6
  model: <模型名>     # 跨模型验证时指定（需在 allowedModels 中）
  runTimeoutSeconds: 300
```

**模型限制**：子 agent 只能用配置中 allowedModels 的模型。如需跨模型测试，先在 `openclaw.json` 的 `subagents.allowedModels` 中添加目标模型。

## 迭代模式

```
R1(基线) → R2(修P0) → R3(修P1) → R4(修P2) → R5(换视角:交互UX) → R6(验证修复) → R7(真实数据)
```

每轮：
1. 上轮问题全部验证
2. 新增 6-8 个未测场景
3. 评分对比（应单调递增，否则有回退）
4. 产出下一轮的修复清单

## 报告持久化（新增）

每轮子 agent 报告必须持久化到文件，不能只存在对话上下文中。

### 存储路径

```
tests/reports/
├── {label}/
│   ├── R1-baseline.md           # 第 1 轮报告
│   ├── R2-fix-p0.md             # 第 2 轮报告
│   ├── ...
│   ├── summary.json             # 汇总：各轮评分、问题趋势
│   └── issues.json              # 累积问题清单（含状态）
```

### summary.json 格式

```json
{
  "label": "pjm-ux-test",
  "rounds": [
    {"round": 1, "date": "2026-02-27", "model": "claude-opus-4-6", "score": 62, "p0": 3, "p1": 5, "p2": 2},
    {"round": 2, "date": "2026-02-28", "model": "claude-opus-4-6", "score": 78, "p0": 0, "p1": 3, "p2": 4}
  ],
  "trend": "improving"
}
```

### issues.json 格式

```json
{
  "issues": [
    {"id": "P0-001", "round": 1, "severity": "P0", "description": "周报数据全为空", "status": "fixed", "fixedInRound": 2, "rootCause": "jq 逗号运算符边界行为"},
    {"id": "P1-003", "round": 1, "severity": "P1", "description": "卡片日期显示昨天", "status": "open", "rootCause": null}
  ]
}
```

### 保存流程

收到子 agent 报告后，在执行后处理之前，先保存：

```bash
# 自动保存报告
mkdir -p tests/reports/${LABEL}
echo "$REPORT_CONTENT" > tests/reports/${LABEL}/R${ROUND}-${TOPIC}.md

# 更新 summary.json（追加本轮数据）
# 更新 issues.json（新增本轮发现的问题，更新已修复的状态）
```

## 超时与失败恢复（新增）

### 超时保护

```
sessions_spawn:
  runTimeoutSeconds: 300   # 5分钟超时
```

超时后的处理：
1. 检查子 agent 是否产生了部分输出（可能跑了一半）
2. 如果有部分输出，保存为 `R{N}-timeout-partial.md`
3. 分析超时原因：
   - API 响应慢 → 增加 timeout 或减少测试场景数
   - 模型卡住 → 换模型重试
   - 脚本死循环 → 修脚本
4. 不要自动重试整轮，先修超时原因再手动触发下一轮

### 子 agent 崩溃恢复

如果子 agent 返回错误（非正常完成）：
1. 记录错误信息到 `tests/reports/${LABEL}/R${N}-error.log`
2. 检查是否是已知问题（rate limit、context overflow、model unavailable）
3. 已知问题 → 等待/调整后重试
4. 未知问题 → 上报，不自动重试

## 报告后处理

收到子 agent 报告后：
1. **持久化**：保存报告文件和更新 issues.json
2. **过滤**：剔除工程师视角的假问题
3. **分级**：P0（阻塞）、P1（影响体验）、P2（改善）
4. **修复**：按优先级逐个修复
5. **回归**：跑已有测试套件确认没破坏（如 `run-tests.sh`）
6. **沉淀**：P0/P1 的根因存入 `memory_store`（见 root-cause.md）
7. **下一轮**：修完后再派子 agent 验证
