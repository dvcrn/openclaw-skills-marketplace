# Study Buddy 命令参考

## 核心命令清单

| 命令 | 功能 | 优先级 |
|------|------|--------|
| `start` | 初始化学习档案 | P0 |
| `plan` | 查看学习计划 | P0 |
| `today` | 查看今日任务 | P0 |
| `checkin` | 学习打卡 | P0 |
| `progress` | 查看进度 | P0 |
| `report` | 生成学习报告 | P0 |
| `wrong` | 错题本管理 | P0 |
| `feedback` | 获取反馈建议 | P1 |
| `data` | 查看数据位置 | - |

---

## 详细说明

### `/study-buddy start`
交互式初始化学习档案，收集用户背景信息。

**收集的信息：**
- 学习主题（如：Python编程、英语口语）
- 学习目标类型（兴趣/工作/考试/转行）
- 当前水平（零基础/基础/进阶/精通）
- 每日可用时间
- 偏好学习方式（视频/阅读/实践/混合）
- 完成时间节点（可选）

**输出：**
- 创建 `~/.study-buddy/profile.json`
- 自动生成初始学习计划

---

### `/study-buddy plan`
查看学习计划详情，包括各阶段任务和当前所处阶段。

**显示内容：**
- 计划创建时间
- 学习主题
- 阶段数量
- 各阶段详情（名称、时长、任务列表）
- 当前阶段标记

---

### `/study-buddy today`
查看今日学习任务和打卡状态。

**显示内容：**
- 今日是否已打卡
- 今日学习内容（如有）
- 建议任务列表

---

### `/study-buddy checkin "内容" [--duration "时长"]`
记录学习情况。

**参数：**
- `content`: 学习内容描述（必填）
- `--duration` / `-d`: 学习时长（可选，如：30分钟、1小时）

**示例：**
```bash
/study-buddy checkin "学习了Python基础语法" --duration "45分钟"
```

**输出：**
- 确认打卡成功
- 连续打卡天数统计

---

### `/study-buddy progress`
查看学习进度统计。

**显示内容：**
- 累计学习天数
- 本周学习天数
- 连续打卡天数
- 最近学习记录
- 可视化进度条

---

### `/study-buddy report`
生成正式的学习报告，包含评级和目标建议。

**显示内容：**
- 学习概况（累计天数、连续打卡、本周/本月）
- 学习评级（卓越/优秀/良好/进步/起步）
- 阶段评估（适应期/养成期/巩固期/进阶期）
- 下周目标建议

**评级标准：**
- 🌟 卓越：连续打卡 ≥30天
- ⭐ 优秀：连续打卡 ≥14天
- 👍 良好：连续打卡 ≥7天
- ✨ 进步：连续打卡 ≥3天
- 🌱 起步：有学习记录但不足3天
- 📝 未开始：无学习记录

---

### `/study-buddy wrong [action] [content]`
错题本管理，支持添加、查看、复习、标记掌握。

**子命令：**

#### `wrong add "错题内容" [--subject "学科"]`
添加错题到错题本。

**示例：**
```bash
/study-buddy wrong add "二次函数求根公式应用错误"
/study-buddy wrong add "英语时态混淆" --subject "英语"
```

#### `wrong list`
列出错题本中的所有题目，按掌握状态分组。

**显示：**
- 待复习题目（最近5题）
- 已掌握题目数量
- 复习次数统计

#### `wrong review "错题ID"`
记录错题复习，增加复习计数。

#### `wrong master "错题ID"`
标记错题为已掌握。

---

### `/study-buddy feedback`
获取个性化学习反馈和建议。

**基于：**
- 连续打卡天数
- 总学习天数
- 用户偏好设置

**输出：**
- 鼓励/建议信息
- 基于学习风格的推荐
- 下一步行动建议

---

### `/study-buddy data`
查看数据存储位置。

**显示：**
- 数据目录路径
- 各文件状态
- 统计数据

---

## 数据文件结构

```
~/.study-buddy/
├── profile.json          # 学习档案
├── plans/                # 学习计划
│   └── plan_YYYYMMDD.json
├── logs/                 # 学习日志
│   └── YYYY-MM-DD.json
├── wrong_questions/      # 错题本
│   └── wrong_questions.json
└── report_YYYYMMDD.json  # 学习报告
```

### profile.json 结构
```json
{
  "subject": "Python编程",
  "goal_type": "b",
  "level": "a",
  "daily_time": "1小时",
  "learning_style": "c",
  "deadline": null,
  "created_at": "2026-03-09T11:00:00",
  "updated_at": "2026-03-09T11:00:00"
}
```

### 日志文件结构
```json
{
  "date": "2026-03-09",
  "content": "学习了Python基础语法",
  "duration": "45分钟",
  "timestamp": "2026-03-09T11:30:00",
  "subject": "Python编程"
}
```

### 错题本结构
```json
[
  {
    "id": "20260309113000",
    "content": "二次函数求根公式应用错误",
    "subject": "数学",
    "added_at": "2026-03-09T11:30:00",
    "review_count": 2,
    "last_review": "2026-03-10T15:00:00",
    "mastered": false
  }
]
```
