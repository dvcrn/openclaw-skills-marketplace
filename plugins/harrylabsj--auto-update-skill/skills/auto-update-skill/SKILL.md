---
name: auto-update-skill
description: "Auto Update Skill"
---

# Auto Update Skill

智能 Skill 更新工具 - 按需检查、即时提醒、一键升级。

## 核心理念

**"在使用时更新"** - 当某个 skill 被触发时，自动检查并提醒更新，而不是定时批量更新。

## 工作流程

```
用户触发 Skill
       ↓
检查 clawhub 最新版本
       ↓
┌─────────────────┐
│ 版本对比        │
└─────────────────┘
       ↓
   ┌─────────┬─────────┐
   │ 有更新   │ 最新版   │
   ↓         ↓
提醒用户    静默通过
   ↓
┌─────────┬─────────┐
│ 确认升级 │ 暂不升级 │
↓         ↓
执行更新   记录跳过
   ↓
继续执行原 skill
```

## 更新原则

### 1. 按需触发
- 只在 skill 被使用时检查更新
- 避免不必要的网络请求
- 24小时内同一 skill 只检查一次

### 2. 分级提醒策略

| 版本变化 | 提醒方式 | 用户操作 |
|---------|---------|---------|
| **Patch** (1.0.1→1.0.2) | 静默提示，不中断 | 可选升级 |
| **Minor** (1.1→1.2) | 温和提醒 | 建议升级 |
| **Major** (1→2) | 明确提醒 | 需确认后升级 |

### 3. 智能缓存
- 缓存版本检查结果 24 小时
- 避免频繁请求 clawhub
- 可手动强制刷新

### 4. 无缝升级
- 升级前自动备份当前版本
- 升级失败自动回滚
- 升级成功后继续执行原任务

## 使用方法

### 方式一：包装器模式（推荐）

在 skill 的 SKILL.md 中添加自动更新检查：

```markdown
---
name: my-skill
autoUpdate: true    # 启用自动更新检查
---

# My Skill

使用前会自动检查更新...
```

### 方式二：命令行调用

```bash
# 检查指定 skill 是否有更新
auto-update-skill check my-skill

# 交互式更新（询问用户）
auto-update-skill update my-skill --interactive

# 强制更新（不询问）
auto-update-skill update my-skill --force

# 查看更新历史
auto-update-skill history my-skill

# 手动刷新缓存
auto-update-skill refresh
```

### 方式三：编程调用

```javascript
const autoUpdate = require('auto-update-skill');

// 在 skill 入口处调用
async function main() {
  // 检查并提示更新
  const updateInfo = await autoUpdate.check('my-skill', {
    interactive: true,      // 交互式询问
    autoUpgradePatch: true, // Patch 版本自动升级
    cacheHours: 24          // 缓存时间
  });
  
  if (updateInfo.shouldUpdate) {
    await autoUpdate.upgrade('my-skill', updateInfo.latestVersion);
  }
  
  // 继续执行 skill 逻辑...
}
```

## 配置

```json
{
  "mode": "interactive",     // interactive | auto | manual
  "cacheDuration": "24h",    // 版本检查缓存时间
  "autoUpgrade": {
    "patch": true,           // Patch 自动升级
    "minor": false,          // Minor 询问用户
    "major": false           // Major 明确提醒
  },
  "remindInterval": "7d",    // 跳过更新后多久再次提醒
  "blacklist": [],           // 不检查更新的 skill
  "quietHours": {            // 安静时段不提醒
    "start": "22:00",
    "end": "08:00"
  }
}
```

## 用户交互示例

### Patch 更新（自动）
```
[ℹ️] summarize 1.0.1 → 1.0.2 (patch, bug fix)
[✓] 已自动升级，继续执行任务...
```

### Minor 更新（建议）
```
[📦] stock-analysis 有更新: 6.2.0 → 6.3.0
     更新内容: 新增技术指标、优化性能

是否升级? [Y/n] (5秒后默认 Y): 
[✓] 升级完成，继续执行任务...
```

### Major 更新（需确认）
```
[⚠️] self-improving-agent 重大版本更新: 3.0.0 → 4.0.0
     ⚠️ 此更新包含重大变更，可能影响现有功能
     
     更新内容:
     - 重构核心架构
     - API 重大变更
     - 需要修改配置
     
     建议: 查看更新文档后再决定

是否升级? [y/N]: n
[ℹ️] 保持当前版本 3.0.0，继续执行任务...
[ℹ️] 7天后再次提醒
```

## 更新日志

```
~/.openclaw/logs/auto-update-skill.log

[2026-03-12 11:30:15] INFO: summarize@1.0.1 → 1.0.2 (patch, auto)
[2026-03-12 11:35:22] INFO: stock-analysis@6.2.0 → 6.3.0 (minor, user confirmed)
[2026-03-12 11:40:08] SKIP: self-improving-agent 4.0.0 (major, user declined, remind at 2026-03-19)
```

## 备份与回滚

```bash
# 查看备份
auto-update-skill backup list

# 手动回滚
auto-update-skill rollback my-skill --version 1.0.0

# 清理旧备份（保留最近10个）
auto-update-skill backup cleanup --keep 10
```

## 集成到现有 Skill

### 方法：在 SKILL.md 中添加前置检查

```markdown
---
name: my-skill
preCheck:
  - auto-update-skill check $SKILL_NAME --quiet
---

# My Skill

内容...
```

### 方法：在脚本入口处调用

```javascript
#!/usr/bin/env node

// skill 入口文件开头
const { checkAndPrompt } = require('../auto-update-skill/lib/checker');

async function main() {
  // 自动检查更新并提示
  await checkAndPrompt('my-skill');
  
  // 原 skill 逻辑...
}

main();
```
