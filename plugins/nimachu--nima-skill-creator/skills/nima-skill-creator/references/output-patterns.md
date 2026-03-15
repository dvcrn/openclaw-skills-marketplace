# 输出格式模式 (Output Pattern Guide)

## 设计原则 (Design Principles)

### 1. 标准化 (Standardization)
- 固定格式 → 易于解析
- 可预测结构 → 降低认知负担

### 2. 简洁性 (Conciseness)
- 只包含必要信息
- 避免冗余描述

### 3. 可扩展性 (Extensibility)
- 易于添加新字段
- 向后兼容

## 常见模式 (Common Patterns)

### Pattern 1: 列表格式 (List Format)

```markdown
### Character Analysis

| Character | Role | Brief Description |
|-----------|------|-------------------|
| Alice | Protagonist | Young detective seeking truth |
| Bob | Antagonist | Criminal mastermind |
| Charlie | Ally | Tech expert and hacker |
```

**适用场景**:
- 特征对比
- 多选项比较
- 关系映射

### Pattern 2: 分段式 (Sectioned Format)

```markdown
## Project Structure

### Backend
- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation

### Frontend
- `components/` - Reusable components
- `pages/` - Page components
- `styles/` - CSS variables and styles
```

**适用场景**:
- 目录结构
- 多部分描述
- 层级关系

### Pattern 3: JSON/Code 格式 (JSON/Code Format)

```json
{
  "character": {
    "name": "Alice",
    "role": "protagonist",
    "traits": ["curious", "determined", "brave"],
    "favorite_color": "blue"
  }
}
```

**适用场景**:
- 配置信息
- 数据结构
- 技术规范

### Pattern 4: 对比表格 (Comparison Table)

```markdown
| Feature | Option A | Option B | Option C |
|---------|----------|----------|----------|
| Speed | ✅ High | ⚠️ Medium | ❌ Low |
| Quality | ✅ Excellent | ✅ Good | ⚠️ Fair |
| Ease of use | ✅ Simple | ⚠️ Complex | ❌ Very Complex |
```

**适用场景**:
- 方案对比
- 选项评估
- 属性比较

### Pattern 5: 流程图式 (Flow-style Format)

```markdown
### Workflow Logic

1. **Input**: User uploads image
   └─ Check file format

2. **Processing**: Resize to max 1920px
   └─ Apply compression

3. **Output**: Save as optimized JPEG
   └─ Return download link
```

**适用场景**:
- 处理流程
- 工作流描述
- 步骤说明

## 最佳实践 (Best Practices)

### 1. 选择正确模式 (Choose Right Pattern)

| Use Case | Recommended Format |
|----------|-------------------|
| Comparing 3-5 items | Table |
| Hierarchical data | Sectioned |
| Technical specification | JSON/Code |
| Process steps | Flow-style |
| Simple lists | Bullet points |

### 2. 一致性 (Consistency)

- 同一 Skill 中使用相同模式
- 固定字段名称
- 统一单位和格式

### 3. 清晰性 (Clarity)

- 添加标题和说明
- 使用表情符号增强可读性
- 合理分组和缩进

### 4. 可扫描性 (Scannability)

- 短行
- 适当换行
- 重点突出

## 反模式 (Anti-Patterns)

### ❌ 混合格式 (Mixed Formats)
```markdown
# Bad
- List item 1
  {
    "key": "value"
  }
- List item 2
```

### ❌ 过于复杂 (Overly Complex)
```markdown
# Bad (Too nested)
{
  "data": {
    "items": [
      {
        "properties": {
          "details": {
            "subdetails": {
              "even_more_details": "..."
            }
          }
        }
      }
    ]
  }
}
```

### ❌ 模糊不清 (Ambiguous)
```markdown
# Bad (No clear structure)
Some data here
Other data there
Maybe this too?
```

## 可用性检查清单 (Usability Checklist)

### 结构
- [ ] 格式与内容匹配
- [ ] 分层清晰
- [ ] 避免深层嵌套

### 可读性
- [ ] 短行
- [ ] 合适的间距
- [ ] 一致的缩进

### 可访问性
- [ ] 无需特殊工具查看
- [ ] 平台兼容 (Discord, WhatsApp, etc.)
- [ ] 避免平台特定格式

### 可执行性
- [ ] 可轻松复制
- [ ] 可直接使用
- [ ] 可解析 (if structured)

## 示例 (Examples)

### Example 1: Story Structure
```markdown
## Story Outline

### Characters
- **Alice**: Curious detective
- **Bob**: Mysterious stranger
- **Charlie**: Tech support friend

### Plot Arcs
1. **Discovery**: Alice finds strange object
2. **Investigation**: Follows clues
3. **Climax**: Confronts Bob
4. **Resolution**: Solves mystery
```

### Example 2: Character Details
```json
{
  "name": "Alice",
  "archetype": "the-hero",
  "abilities": ["investigation", "combat", "technology"],
  "motivation": "seeking-truth",
  "weaknesses": ["impulsiveness", "trustIssues"]
}
```

### Example 3: Scene Description
```markdown
### Scene: The Discovery

**Setting**: Abandoned warehouse at night
**Atmosphere**: Suspicious silence, dim lighting
**Characters**: Alice, Bob (mystery figure)

**Events**:
1. Alice enters warehouse
2. Discovers strange glowing object
3. Bob appears from shadows
4. Tense confrontation begins
```
