# AI主动检测机制 - 集成指南

## 🎯 核心概念

AI主动检测机制允许AI在每次回复时自动检查上下文使用率，并在达到阈值时主动提醒用户或自动切换模型。

---

## 🚀 集成方式

### 方式1：手动调用（推荐初期使用）

**在AI回复时主动调用：**

```bash
# AI回复前检查
~/.openclaw/workspace/skills/smart-model-switch/scripts/integrate-check.sh
```

**特点：**
- ✅ 简单直接
- ✅ AI自主控制
- ✅ 无需额外配置
- ⚠️ 依赖AI主动调用

**使用示例：**
```
用户：帮我分析项目
AI：[调用 integrate-check.sh]
    [检查通过，无输出]
    好的，开始分析...
```

### 方式2：自动注入（推荐长期使用）

**创建OpenClaw钩子：**

在 `~/.openclaw/hooks/pre-reply.sh` 中添加：

```bash
#!/bin/bash

# OpenClaw回复前钩子
# 自动调用AI主动检测

SKILL_DIR="$HOME/.openclaw/workspace/skills/smart-model-switch"

if [ -f "$SKILL_DIR/scripts/integrate-check.sh" ]; then
    CHECK_RESULT=$("$SKILL_DIR/scripts/integrate-check.sh" 2>/dev/null)
    
    if [ -n "$CHECK_RESULT" ]; then
        # 输出提醒信息
        echo "$CHECK_RESULT"
        echo ""
    fi
fi
```

**特点：**
- ✅ 完全自动化
- ✅ 无需AI主动调用
- ✅ 零感知
- ⚠️ 需要OpenClaw支持钩子

### 方式3：定时检查 + AI主动（推荐）

**结合定时任务和AI主动检测：**

```bash
# 1. 配置定时任务（每5分钟检查）
*/5 * * * * ~/.openclaw/workspace/skills/smart-model-switch/scripts/ai-proactive-check.sh

# 2. AI在回复时也主动检查
# 在SKILL.md中添加：
# 【AI行为规则】
# 每次回复前，调用 integrate-check.sh 检查上下文
```

**特点：**
- ✅ 双重保险
- ✅ 定时监控 + 实时检测
- ✅ 最高可靠性
- ✅ 防止遗漏

---

## 📊 工作原理

### 检测流程

```
AI准备回复
    ↓
调用 integrate-check.sh
    ↓
ai-proactive-check.sh
    ↓
├── 检查冷却期
├── 获取上下文使用率
├── 判断是否超过阈值（85%）
├── 更新连续命中次数
└── 达到连续2次？
    ↓
    ├── 是 → 输出提醒信息
    │        ↓
    │        ├── 手动处理（/new）
    │        └── 自动切换（可选）
    └── 否 → 静默返回
    ↓
AI继续回复
```

### 防骚扰机制

1. **冷却期：** 切换后10分钟内不再检测
2. **通知间隔：** 5分钟内不重复提醒
3. **连续性要求：** 连续2次超过阈值才提醒
4. **静默返回：** 无问题时无输出

---

## 🛠️ 配置选项

### 启用自动切换

编辑 `config/model-rules.json`：

```json
{
  "context_switch_strategy": {
    "auto_switch": true,
    "rules": [
      {
        "name": "长上下文切换",
        "threshold": 85,
        "consecutive_hits": 2,
        "target_model": "bailian/kimi-k2.5"
      }
    ],
    "cooldown": {
      "duration_minutes": 10
    },
    "notification": {
      "enabled": true,
      "interval_minutes": 5
    }
  }
}
```

### 调整阈值

| 场景 | 推荐阈值 | 说明 |
|------|----------|------|
| 频繁长对话 | 75% | 提前预警 |
| 常规使用 | 85% | 平衡模式 |
| 短对话为主 | 90% | 减少打扰 |

### 自定义提醒信息

编辑 `ai-proactive-check.sh` 中的提醒模板：

```bash
echo "⚠️  【AI主动提醒】"
echo "上下文使用率：${usage}%"
echo "建议操作：..."
```

---

## 📝 集成到SKILL.md

**在技能文档中添加AI行为规则：**

```markdown
## 🤖 AI行为规则

### 自动上下文检测（强制）

**每次回复前必须执行：**

```bash
~/.openclaw/workspace/skills/smart-model-switch/scripts/integrate-check.sh
```

**执行时机：**
1. AI准备回复用户消息时
2. 在生成回复内容之前
3. 静默执行，无问题不输出

**检测到高上下文时：**
1. 输出提醒信息
2. 继续完成当前回复
3. 建议用户创建新会话或切换模型

**示例流程：**
```
用户：继续分析
AI：[执行 integrate-check.sh]
    [输出：⚠️ 上下文使用率87%...]
    好的，继续分析...（完成当前任务）
```

**注意事项：**
- ✅ 无输出 = 检查通过，正常回复
- ⚠️ 有输出 = 需要提醒，先输出提醒再回复
- 🔇 冷却期内 = 跳过检查
```

---

## 🔍 调试方法

### 查看检测日志

```bash
tail -f ~/.openclaw/logs/ai-proactive-check.log
```

### 手动触发检测

```bash
~/.openclaw/workspace/skills/smart-model-switch/scripts/ai-proactive-check.sh
```

### 查看状态

```bash
cat ~/.openclaw/workspace/skills/smart-model-switch/data/context-state.json | jq .
```

### 测试集成

```bash
# 1. 模拟高上下文（修改状态文件）
jq '.consecutive_hits = 2' data/context-state.json > /tmp/state.json
mv /tmp/state.json data/context-state.json

# 2. 触发检测
scripts/integrate-check.sh

# 3. 应该输出提醒信息
```

---

## 💡 最佳实践

### 1. 渐进式集成

**阶段1：** 手动调用（1-2天）
- AI主动调用 integrate-check.sh
- 观察效果和频率

**阶段2：** 定时任务（1周）
- 添加定时任务（每5分钟）
- 结合AI主动检测

**阶段3：** 自动注入（长期）
- 配置OpenClaw钩子
- 完全自动化

### 2. 配合Context Manager

**推荐组合：**
```
AI主动检测（实时） + Context Manager（自动切换）
```

**效果：**
- AI检测到高上下文 → 提醒用户
- Context Manager → 自动创建新会话
- 无缝体验，零感知

### 3. 用户教育

**在首次使用时告知用户：**
```
💡 我会在上下文接近限制时主动提醒您。
   建议：看到提醒后，使用 /new 创建新会话。
   或者：安装 Context Manager 实现自动切换。
```

---

## 🚨 常见问题

### Q1: 检测脚本无输出？

**原因：** 上下文使用率未超过阈值，或在冷却期内

**验证：**
```bash
# 查看当前上下文
scripts/get-context-usage.sh

# 查看状态
cat data/context-state.json | jq .
```

### Q2: 提醒太频繁？

**解决：**
1. 提高阈值（85% → 90%）
2. 增加连续次数（2 → 3）
3. 延长通知间隔（5分钟 → 10分钟）

### Q3: 如何完全禁用？

**方法1：** 删除钩子脚本
**方法2：** 配置中设置 `enabled: false`
**方法3：** AI不调用 integrate-check.sh

---

## 📊 效果评估

### 预期效果

| 指标 | 目标 |
|------|------|
| 检测准确率 | > 95% |
| 用户感知 | 无感知（正常时）|
| 提醒时机 | 阈值85%前5-10% |
| 误报率 | < 5% |

### 监控指标

```bash
# 查看检测次数
grep "开始AI主动检测" ~/.openclaw/logs/ai-proactive-check.log | wc -l

# 查看提醒次数
grep "已发送AI主动提醒" ~/.openclaw/logs/ai-proactive-check.log | wc -l

# 查看平均使用率
grep "当前上下文使用率" ~/.openclaw/logs/ai-proactive-check.log | \
  awk -F：'{print $2}' | awk '{sum+=$1; count++} END {print "平均:", sum/count"%"}'
```

---

*AI主动检测机制集成指南 v1.0*
*创建时间：2026-03-05 08:18*
*适用技能：smart-model-switch v1.0.0*
