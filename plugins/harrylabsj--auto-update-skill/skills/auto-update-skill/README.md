# Auto Update Skill

智能 Skill 更新工具 - 按需检查、即时提醒、一键升级。

## 🎯 核心理念

**"在使用时更新"** - 当某个 skill 被触发时，自动检查并提醒更新，而不是定时批量更新。

## ✨ 特性

- **按需触发** - 只在 skill 被使用时检查更新
- **分级策略** - Patch自动、Minor建议、Major需确认
- **智能缓存** - 24小时内同一 skill 只检查一次
- **自动备份** - 升级前自动备份当前版本
- **失败回滚** - 升级失败自动恢复
- **黑名单** - 可指定某些 skill 不自动更新

## 📦 安装

```bash
clawhub install auto-update-skill
```

## 🚀 使用

### 方式一：CLI 命令

```bash
# 检查指定 skill
auto-update-skill check my-skill

# 检查所有 skills
auto-update-skill check --verbose

# 执行更新（交互式）
auto-update-skill update my-skill

# 强制更新
auto-update-skill update my-skill --force

# 配置管理
auto-update-skill config blacklist add my-skill
auto-update-skill config auto patch true

# 备份与回滚
auto-update-skill backup list
auto-update-skill rollback my-skill --version 1.0.0

# 刷新缓存
auto-update-skill refresh
```

### 方式二：集成到其他 Skill

```javascript
const { checkAndPrompt } = require('auto-update-skill/lib/checker');

async function main() {
  // 自动检查并提示更新
  await checkAndPrompt('my-skill');
  
  // 继续执行原 skill 逻辑...
}
```

## ⚙️ 更新原则

| 版本变化 | 策略 | 说明 |
|---------|------|------|
| **Patch** (1.0.1→1.0.2) | 自动升级 | Bug 修复，安全更新 |
| **Minor** (1.1→1.2) | 建议升级 | 新功能，向后兼容 |
| **Major** (1→2) | 需确认 | 重大变更，可能影响现有功能 |

## 🔧 配置

配置文件位置：`~/.openclaw/auto-update-skill.json`

```json
{
  "mode": "interactive",
  "cacheDuration": 86400000,
  "autoUpgrade": {
    "patch": true,
    "minor": false,
    "major": false
  },
  "remindInterval": 604800000,
  "blacklist": [],
  "quietHours": {
    "start": "22:00",
    "end": "08:00"
  }
}
```

## 📄 许可证

MIT
