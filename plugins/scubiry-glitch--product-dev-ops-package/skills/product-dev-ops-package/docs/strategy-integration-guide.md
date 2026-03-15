# 产品研讨会 - 战略顾问集成指南

> 说明 product-dev-ops 与 strategy-consultant 如何协作

## 集成架构

```
product-dev-ops v3.1              strategy-consultant v1.0
        │                                   │
        │  1. 启动外部访谈                   │
        │ ───────────────────────────────>  │
        │                                   │
        │  2. 输出战略材料                   │
        │ <───────────────────────────────  │
        │     - insights.md                 │
        │     - benchmark-report.md         │
        │     - strategic-recommendations.md│
        │                                   │
        │  3. 自动检测（/研讨）              │
        │ ─────────────────────────────────>│
        │     检测到战略材料 → 加载          │
        │     未检测到 → 提示建议            │
        │                                   │
        │  4. 研讨会（四角色+战略输入）      │
        │                                   │
        └───────────────────────────────────┘
```

## 标准输入格式

战略顾问必须输出以下文件到 `00-work/interview/workshop/`：

```
00-work/interview/workshop/
├── insights.md                    # 外部洞察汇总（必须）
├── benchmark-report.md            # 行业Benchmark报告（推荐）
├── business-model-canvas.md       # 商业模式画布（推荐）
├── financial-summary.md           # 财务预测摘要（推荐）
├── strategic-recommendations.md   # 战略建议（必须）
└── workshop-agenda.md             # 研讨会议程建议（可选）
```

### 文件格式规范

**insights.md 必须包含**：
```markdown
# 外部洞察汇总

## 关键洞察（3-5条）
1. [洞察1]
2. [洞察2]
3. [洞察3]

## 战略验证
- **外部认同度**: [高/中/低]
- **市场机会**: [描述]

## 对研讨会的建议
1. [建议讨论的问题]
```

**strategic-recommendations.md 必须包含**：
```markdown
# 战略建议

## 建议结论
- **建议**: [Go / No-go / 调整]
- **理由**: [简要说明]

## 关键决策点
- [决策点1]
- [决策点2]
```

## 自动检测机制

### 检测逻辑

当执行 `/研讨` 时，系统自动检测：

```python
# 伪代码
def check_strategy_input():
    workshop_dir = "00-work/interview/workshop/"
    
    # 必须文件
    required_files = ["insights.md", "strategic-recommendations.md"]
    # 推荐文件
    recommended_files = ["benchmark-report.md", "business-model-canvas.md", "financial-summary.md"]
    
    missing_required = []
    missing_recommended = []
    
    for file in required_files:
        if not exists(workshop_dir + file):
            missing_required.append(file)
    
    for file in recommended_files:
        if not exists(workshop_dir + file):
            missing_recommended.append(file)
    
    if missing_required:
        return {
            "status": "MISSING_REQUIRED",
            "message": f"缺少必需文件: {missing_required}",
            "action": "建议先完成外部客户访谈（使用 strategy-consultant 技能）"
        }
    elif missing_recommended:
        return {
            "status": "MISSING_RECOMMENDED",
            "message": f"缺少推荐文件: {missing_recommended}",
            "action": "可以继续研讨会，但建议补充"
        }
    else:
        return {
            "status": "READY",
            "message": "战略顾问输入完整",
            "action": "加载外部洞察到研讨会"
        }
```

### 用户提示

**情况1：缺少必需文件**
```
⚠️ 检测到缺少战略顾问输入材料

缺少文件:
- insights.md
- strategic-recommendations.md

建议操作:
1. 使用 strategy-consultant 技能完成外部客户访谈
   /strategy-consultant/interview

2. 生成战略分析材料
   /strategy-consultant/benchmark
   /strategy-consultant/bp

3. 完成后再次执行 /研讨

是否继续 without 战略顾问输入? [Y/n]
```

**情况2：缺少推荐文件**
```
⚠️ 战略顾问输入部分缺失

已有:
✓ insights.md
✓ strategic-recommendations.md

缺失（推荐补充）:
- benchmark-report.md
- financial-summary.md

是否继续研讨会? [Y/n]
建议: 补充缺失材料可获得更全面的战略视角
```

**情况3：输入完整**
```
✅ 检测到战略顾问输入材料

已加载:
✓ insights.md
✓ benchmark-report.md
✓ business-model-canvas.md
✓ financial-summary.md
✓ strategic-recommendations.md

研讨会将包含外部洞察和战略建议
```

## 研讨会流程（集成版）

### Phase 1: Why 陈述 + 外部洞察（15分钟）

**王校长（产品经理）**：
> 陈述项目 Why

**系统自动加载**（如有战略顾问输入）：
```
【外部洞察摘要】（来自 insights.md）
- 关键发现1: ...
- 关键发现2: ...
- 市场机会: ...
```

```
【战略建议】（来自 strategic-recommendations.md）
- 建议: Go / No-go / 调整
- 关键决策点: ...
```

### Phase 2-4: 常规流程

继续四角色（产品经理、架构师、开发助手、运营经理）的讨论，但可参考战略顾问输入。

## 使用指南

### 何时启用战略顾问？

| 项目特征 | 建议 |
|----------|------|
| 全新业务方向 | ✅ 强烈建议 |
| 需要融资 | ✅ 强烈建议 |
| 复杂商业模式 | ✅ 强烈建议 |
| 高度竞争市场 | ✅ 强烈建议 |
| 内部工具/系统 | ⚠️ 可选 |
| 快速迭代试错 | ⚠️ 可选 |
| 技术重构 | ❌ 通常不需要 |
| 小功能优化 | ❌ 通常不需要 |

### 快速启动流程

**方式1：完整流程（推荐用于重要项目）**
```bash
# Step 1: 启动项目
/开工 项目名

# Step 2: 产品经理访谈
/interview

# Step 3: 战略顾问外部访谈（使用 strategy-consultant 技能）
/strategy-consultant/interview
/strategy-consultant/benchmark
/strategy-consultant/bp

# Step 4: 启动研讨会（自动检测战略顾问输入）
/研讨

# Step 5: Why 冻结
/freeze
```

**方式2：精简流程（用于常规项目）**
```bash
# Step 1: 启动项目
/开工 项目名

# Step 2: 产品经理访谈
/interview

# Step 3: 直接研讨会（四角色）
/研讨

# Step 4: Why 冻结
/freeze
```

## 注意事项

1. **战略顾问输入是可选的**，但强烈建议在重要项目中使用
2. **输入文件格式必须规范**，否则无法被正确加载
3. **战略顾问技能可独立使用**，不依赖 product-dev-ops
4. **两个技能版本需匹配**，建议同时更新

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 研讨会未加载战略洞察 | 文件路径错误 | 确保文件在 `00-work/interview/workshop/` |
| 文件格式解析失败 | 格式不规范 | 参照模板格式重新生成 |
| 战略顾问技能未识别 | 未安装技能 | 安装 strategy-consultant 技能 |
| 集成提示不显示 | 检测逻辑关闭 | 检查配置 `enable_strategy_check: true` |

---

_方案3：保持灵活性，增强集成，降低使用门槛_
