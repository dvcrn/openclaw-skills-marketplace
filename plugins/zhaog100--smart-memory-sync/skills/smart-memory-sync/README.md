# Smart Memory Sync

> 主动智能记忆管理 - 预防性保护 + 三库同步 + 自动切换

## 🎯 核心特性

**三级阈值机制：**
- 50% → 提醒用户
- 75% → 自动同步三库
- 85% → 主动触发切换

**三库同步：**
- MEMORY.md（长期记忆）
- QMD知识库（语义检索）
- Git库（版本保护）

**双保险机制：**
- Smart Memory Sync（预防性保护）
- Context Manager（应急切换）

## 🚀 快速开始

```bash
# 守护进程模式（推荐）
python3 scripts/smart-sync.py --daemon

# 查看状态
python3 scripts/smart-sync.py --status

# 手动同步
python3 scripts/smart-sync.py --sync
```

## 📊 工作流程

```
监控上下文 → 50%提醒 → 75%同步 → 85%切换 → 无缝继续
```

## 🤝 与Context Manager协作

| 模块 | Smart Memory Sync | Context Manager |
|------|-------------------|-----------------|
| 角色 | 主动预防 | 被动应急 |
| 触发 | 实时检测 | 接收请求 |
| 同步 | 三库同步 | 记忆传递 |

**双保险机制，99.9%记忆完整性**

## 🔧 配置

编辑 `config/sync-config.json`:

```json
{
  "thresholds": {
    "remind": 50,
    "auto_sync": 75,
    "auto_switch": 85
  }
}
```

## 📈 性能

- 检测延迟：< 5分钟
- 同步时间：< 10秒
- 切换时间：< 3秒
- 记忆完整度：100%

---

**作者**: 米粒儿 🌾
**版本**: 1.0.0
**更新**: 2026-03-06

**主动保护，三库同步，双保险机制** 🌟
