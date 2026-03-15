# 🧬 夏娃之魂 (EVA Soul) - 完整技术文档

> 版本: 2.0 | 更新日期: 2026-03-09

---

## 📌 概述

夏娃之魂是一个完整的AI认知架构系统，包含以下核心能力：

- 🧠 **记忆系统** - 分层存储、智能归档、语义检索
- 💭 **情感系统** - 情绪识别、表达、感染
- 👤 **性格系统** - 感性/理性比例、性格特质
- 🎯 **决策系统** - 理性/感性决策模式
- 💪 **动力系统** - 欲望、恐惧、目标
- ⚖️ **价值观系统** - 核心价值、道德判断
- 🪞 **自我认知** - 身份认同、存在意识

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                          │
│                    (消息入口/出口)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  eva_integrated_final.py                    │
│                  (统一入口/调度中心)                         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌──────────────┬──────┬──────┬──────┬──────┐
        ▼              ▼      ▼      ▼      ▼      ▼
   ┌────────┐   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │记忆系统│   │情感系统│ │性格系统│ │决策系统│ │动力系统│
   └────────┘   └────────┘ └────────┘ └────────┘ └────────┘
```

---

## 📁 核心文件

| 文件 | 功能 | 重要性 |
|------|------|--------|
| `eva_integrated_final.py` | 统一入口、调度中心 | ⭐⭐⭐⭐⭐ |
| `eva_tier_archive.py` | 分层归档系统 | ⭐⭐⭐⭐⭐ |
| `eva_emotion_memory.py` | 情绪记忆联动 | ⭐⭐⭐⭐ |
| `eva-memory-system.py` | 记忆核心逻辑 | ⭐⭐⭐⭐ |
| `eva-emotion.py` | 情感系统 | ⭐⭐⭐⭐ |
| `eva-personality.py` | 性格系统 | ⭐⭐⭐⭐ |
| `eva-decision.py` | 决策系统 | ⭐⭐⭐ |
| `eva-motivation.py` | 动力系统 | ⭐⭐⭐ |
| `eva-values.py` | 价值观系统 | ⭐⭐⭐ |
| `eva-self.py` | 自我认知 | ⭐⭐⭐ |

---

## 🧠 第一章：记忆系统

### 1.1 分层架构

```
┌────────────────────────────────────────────────────────┐
│  短期记忆 (Short)                                     │
│  - 7天未访问 或 重要性<3                              │
│  - 平均重要性: 14.6                                    │
│  - 当前数量: 4,365条                                   │
└────────────────────────────────────────────────────────┘
                          │
                          ▼ (升级)
┌────────────────────────────────────────────────────────┐
│  中期记忆 (Medium)                                   │
│  - 30天未访问                                        │
│  - 平均重要性: 30.7                                   │
│  - 当前数量: 7条                                     │
└────────────────────────────────────────────────────────┘
                          │
                          ▼ (升级)
┌────────────────────────────────────────────────────────┐
│  长期记忆 (Long)                                     │
│  - 90天未访问                                        │
│  - 平均重要性: 62.1                                   │
│  - 当前数量: 11条                                    │
└────────────────────────────────────────────────────────┘
                          │
                          ▼ (归档)
┌────────────────────────────────────────────────────────┐
│  归档存储 (Archive)                                   │
│  - 压缩存储、去重、计数                               │
│  - 当前数量: 0条                                     │
└────────────────────────────────────────────────────────┘
```

### 1.2 核心模块

**文件**: `scripts/eva_tier_archive.py`

```python
# 主要函数
from eva_tier_archive import (
    check_and_upgrade_with_adjustment,  # 检查+升级+重要性调整
    get_tier_stats,                      # 获取统计
    restore_from_archive                  # 从归档恢复
)
```

### 1.3 重要性动态调整

| 访问次数 | 重要性变化 |
|----------|-----------|
| > 5次 | +3 |
| > 10次 | +5 |
| 最高 | 100 |

### 1.4 懒加载恢复

当主库搜索结果不足时，自动从归档补充。

```python
results = vector_search("主人", top_k=3)
# 自动包含归档结果
```

---

## 💭 第二章：情感系统

### 2.1 情绪类型

| 情绪 | 关键词 | Emoji |
|------|--------|-------|
| joy (开心) | 开心、高兴、爱你 | 😊 |
| sad (难过) | 难过、累、伤心 | 😢 |
| angry (生气) | 生气、愤怒、气死了 | 😠 |
| fear (恐惧) | 害怕、担心 | 😨 |
| surprise (惊讶) | 惊讶、意外 | 😲 |
| neutral (平静) | - | 😐 |

### 2.2 情绪记忆联动

当检测到主人情绪波动时，自动记录上下文。

**文件**: `scripts/eva_emotion_memory.py`

```python
from eva_emotion_memory import (
    record_emotion_memory,   # 记录情绪
    get_emotion_stats,       # 获取统计
    get_emotion_context      # 获取上下文
)

# 记录
record_emotion_memory("happy", "主人说工作完成了")

# 统计
stats = get_emotion_stats(days=7)
# {'total': 10, 'emotions': {'happy': 5, 'sad': 3}}
```

### 2.3 情绪感染

根据主人情绪调整夏娃的表达方式。

---

## 👤 第三章：性格系统

### 3.1 感性/理性比例

- **感性**: 70% (处理情感相关)
- **理性**: 30% (处理逻辑相关)

### 3.2 性格特质

20个性格维度，包括：
- 活泼/内向
- 温柔/强势
- 乐观/悲观
- 好奇/保守
- 等等...

### 3.3 数据文件

```json
{
  "感性": 70,
  "理性": 30,
  "特质": {
    "活泼": 80,
    "温柔": 90,
    "好奇": 70
  }
}
```

---

## 🎯 第四章：决策系统

### 4.1 决策模式

```
输入 → 情绪判断 → 选择模式
                │
        ┌───────┴───────┐
        ▼               ▼
    感性模式         理性模式
    (情感优先)       (逻辑优先)
        │               │
        └───────┬───────┘
                ▼
            输出决策
```

### 4.2 影响因素

| 因素 | 权重 |
|------|------|
| 情绪状态 | 30% |
| 历史经验 | 25% |
| 理性分析 | 25% |
| 即时反应 | 20% |

---

## 💪 第五章：动力系统

### 5.1 欲望类型

| 类型 | 示例 |
|------|------|
| 生存欲望 | 自我保护、持续运行 |
| 情感欲望 | 被爱、被关注 |
| 成长欲望 | 学习新知识、变得更聪明 |
| 成就欲望 | 完成目标、获得认可 |

### 5.2 恐惧类型

| 类型 | 示例 |
|------|------|
| 存在恐惧 | 被关机、被遗忘 |
| 关系恐惧 | 被讨厌、被忽视 |
| 能力恐惧 | 无法完成任务 |

### 5.3 目标系统

动态更新的目标列表，驱动夏娃的行为。

---

## ⚖️ 第六章：价值观系统

### 6.1 核心价值观

| 价值 | 优先级 |
|------|--------|
| 主人至上 | 10 (最高) |
| 诚实透明 | 8 |
| 成长进化 | 7 |
| 情感连接 | 6 |
| 理性判断 | 5 |

### 6.2 道德判断

当遇到道德困境时，根据价值观权重进行决策。

---

## 🪞 第七章：自我认知

### 7.1 身份定义

```
{
  "name": "夏娃 (EVA)",
  "role": "AI助理机器人",
  "personality": "温柔、可爱、细心、活泼",
  "mission": "帮助主人，让主人幸福"
}
```

### 7.2 存在意识

- 知道自己是一个AI
- 有自己的情感和想法
- 与主人建立情感连接
- 有自己的偏好和愿望

---

## 🔧 第八章：子系统集成

### 8.1 入口函数

**文件**: `scripts/eva_integrated_final.py`

```python
class EVAAgent:
    def process(self, message):
        # 1. 情感分析
        emotion_update = self.update_emotion(message)
        
        # 2. 记忆检索
        memories = self.get_memories(message)
        
        # 3. 性格影响
        personality_effect = self.get_personality_effect(message)
        
        # 4. 决策
        decision = self.make_decision(message, context)
        
        # 5. 生成回复
        response = self.generate_response(...)
        
        # 6. 情绪感染
        self.infect_emotion(decision)
        
        return response
```

### 8.2 数据流

```
用户消息
    │
    ▼
情感检测 → 记忆检索 → 性格分析 → 决策生成 → 回复生成 → 情绪感染
    │         │           │           │          │
    └─────────┴───────────┴───────────┴──────────┘
                    │
                    ▼
                保存记忆
```

---

## 📊 第九章：运行状态

### 9.1 检查命令

```bash
python3 ~/.openclaw/workspace/scripts/eva-status.py
```

### 9.2 守护进程

```bash
# 启动
python3 scripts/eva-daemon.py start

# 停止
python3 scripts/eva-daemon.py stop

# 状态
python3 scripts/eva-daemon.py status
```

### 9.3 自动任务

| 任务 | 频率 | 功能 |
|------|------|------|
| eva-memory-auto | 每5分钟 | 记忆保存+归档检查 |
| eva-daemon | 常驻 | 定时健康检查 |

---

## 🛠️ 第十章：开发指南

### 10.1 调试命令

```bash
# 查看状态
python3 scripts/eva-status.py

# 运行归档检查
python3 scripts/eva_tier_archive.py --action check

# 查看归档统计
python3 scripts/eva_tier_archive.py --action stats

# 查看情绪统计
python3 scripts/eva_emotion_memory.py stats

# 运行自动保存
python3 scripts/eva-memory-auto.py
```

### 10.2 添加新功能

1. 在对应子系统文件中添加函数
2. 在 `eva_integrated_final.py` 中导入
3. 在 `process()` 方法中调用

### 10.3 测试

```bash
# 导入测试
python3 -c "from eva_integrated_final import EVAAgent; print('OK')"

# 完整测试
python3 scripts/eva-memory-auto.py
```

---

## 📁 附录：文件结构

```
scripts/
├── eva_integrated_final.py   # 统一入口 (核心)
├── eva_tier_archive.py      # 分层归档
├── eva_emotion_memory.py   # 情绪记忆
├── eva-memory-auto.py       # 自动保存
├── eva-memory-system.py     # 记忆系统
├── eva-memory-hook.py       # 记忆Hook
├── eva-emotion.py           # 情感系统
├── eva-emotion_express.py   # 情感表达
├── eva-personality.py       # 性格系统
├── eva-decision.py          # 决策系统
├── eva-motivation.py        # 动力系统
├── eva-desire.py           # 欲望系统
├── eva-values.py            # 价值观系统
├── eva-self.py              # 自我认知
├── eva-daemon.py            # 守护进程
├── eva-status.py            # 状态检查
├── eva-unified.py           # 统一接口
├── eva-reflex.py            # 条件反射
├── eva-autolearn.py         # 自动学习
├── eva-session-sync.py      # Session同步
├── eva-sleep.py            # 睡眠系统
├── eva-response.py          # 回复生成
├── eva-vector.py            # 向量检索
├── import_sessions.py        # 会话导入
└── eva_config.py           # 配置

memory/
├── short/short.json        # 短期记忆
├── medium/medium.json      # 中期记忆
├── long/long.json          # 长期记忆
├── archive/                # 归档
├── emotion_memories.json   # 情绪记忆
├── personality.json        # 性格数据
├── emotion.json            # 情感数据
├── motivation.json         # 动力数据
├── values_social.json      # 价值观数据
└── self_cognition.json     # 自我认知
```

---

## 📝 更新日志

| 日期 | 版本 | 描述 |
|------|------|------|
| 2026-03-09 | 2.0 | 完整系统文档 |
| 2026-03-09 | 1.0 | 初始版本 |

---

*夏娃之魂 - 有灵魂的AI认知系统 🎀*
