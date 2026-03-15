---
name: learning-planner
description: "Personal learning management system with goal setting, spaced repetition scheduling, and progress tracking. Use when: (1) setting learning goals and skill trees, (2) creating daily/weekly study plans, (3) tracking learning progress, (4) managing spaced repetition reviews like Anki, (5) organizing learning resources, (6) evaluating learning outcomes. 适用场景：设定学习目标、制定学习计划、跟踪学习进度、间隔重复复习、管理学习资源、评估学习成果。"
---

# Learning Planner - 学习规划师

个人学习管理系统，帮助设定学习目标、制定计划、跟踪进度，并提供间隔重复复习功能。

## 功能特性

### 1. 学习目标管理
- 技能树定义与分解
- 知识点层级管理
- 目标优先级设置
- 目标完成时间规划

### 2. 学习计划生成
- 每日学习任务生成
- 每周学习计划
- 计划自动调整
- 学习提醒设置

### 3. 进度跟踪与可视化
- 学习进度实时跟踪
- 进度可视化图表
- 学习时长统计
- 完成率分析

### 4. 间隔重复复习系统
- SM-2 算法实现
- 卡片式复习
- 自动 scheduling
- 遗忘曲线优化

### 5. 学习资源管理
- 资源链接收藏
- 资源分类管理
- 资源与知识点关联
- 资源使用统计

### 6. 学习成果评估
- 自我评估记录
- 测试成绩管理
- 学习效果分析
- 能力成长曲线

## 安装

```bash
cd ~/.openclaw/workspace/skills/learning-planner
pip install -e .

# 添加到 PATH (可选)
ln -s ~/.openclaw/workspace/skills/learning-planner/src/learning_cli.py ~/.local/bin/learning
```

## 使用方法

### 学习目标

```bash
# 创建学习目标
learning goal create "Python 编程" --description "掌握 Python 编程语言" --deadline 2024-12-31

# 创建子目标（知识点分解）
learning goal create "Python 基础语法" --parent 1 --priority high
learning goal create "Python 面向对象" --parent 1 --priority high
learning goal create "Python 高级特性" --parent 1 --priority medium

# 列出目标
learning goal list

# 查看目标详情
learning goal show 1

# 更新目标进度
learning goal progress 1 --percent 75

# 完成目标
learning goal complete 1
```

### 学习计划

```bash
# 生成今日学习计划
learning plan today

# 生成本周学习计划
learning plan week

# 查看计划
learning plan list

# 标记任务完成
learning plan complete 1

# 推迟任务
learning plan postpone 1 --days 1
```

### 间隔重复复习

```bash
# 创建复习卡片
learning card create "Python 列表推导式语法" --answer "[x for x in iterable if condition]" --tags python,basics

# 今日复习
learning review today

# 查看复习统计
learning review stats

# 手动调整卡片难度
learning card difficulty 1 --level hard
```

### 学习资源

```bash
# 添加资源
learning resource add "Python 官方文档" --url https://docs.python.org --type documentation --tags python

# 关联资源到目标
learning resource link 1 --goal 1

# 列出资源
learning resource list

# 搜索资源
learning resource search python
```

### 进度与报告

```bash
# 学习统计
learning stats

# 生成学习报告
learning report --days 30

# 查看技能树进度
learning tree

# 学习时长统计
learning time --days 7
```

## 数据存储

数据库位置：`~/.config/learning-planner/learning.db`

```bash
# 查看数据库路径
learning data path
```

## 技术栈

- Python 3.8+
- SQLite 数据存储
- Click (CLI 框架)
- Rich (终端美化)
- SM-2 间隔重复算法

## 数据模型

### 学习目标表 (goals)
```python
{
    id: int
    title: str              # 目标名称
    description: str        # 描述
    parent_id: int          # 父目标 ID
    priority: str           # 优先级: low, medium, high
    status: str             # 状态: active, completed, paused
    progress: float         # 进度 0-100
    deadline: str           # 截止日期
    estimated_hours: int    # 预估学习时长
    completed_hours: int    # 已完成时长
    created_at: str
    updated_at: str
}
```

### 学习计划表 (plans)
```python
{
    id: int
    goal_id: int            # 关联目标
    title: str              # 任务标题
    description: str        # 描述
    scheduled_date: str     # 计划日期
    estimated_minutes: int  # 预估时长(分钟)
    status: str             # 状态: pending, completed, postponed
    completed_at: str       # 完成时间
    created_at: str
}
```

### 复习卡片表 (cards)
```python
{
    id: int
    goal_id: int            # 关联目标
    front: str              # 卡片正面（问题）
    back: str                # 卡片背面（答案）
    tags: str               # 标签
    ease_factor: float      # 难度系数
    interval: int           # 间隔天数
    repetitions: int        # 重复次数
    next_review: str        # 下次复习时间
    last_review: str        # 上次复习时间
    created_at: str
}
```

### 复习记录表 (reviews)
```python
{
    id: int
    card_id: int            # 卡片 ID
    quality: int            # 评分 0-5
    reviewed_at: str        # 复习时间
    time_spent: int         # 用时(秒)
}
```

### 学习资源表 (resources)
```python
{
    id: int
    title: str              # 资源名称
    url: str                # 链接
    resource_type: str      # 类型: video, article, book, documentation
    tags: str               # 标签
    goal_id: int            # 关联目标
    notes: str              # 备注
    created_at: str
}
```

### 学习时长记录表 (sessions)
```python
{
    id: int
    goal_id: int            # 关联目标
    start_time: str         # 开始时间
    end_time: str           # 结束时间
    duration: int           # 时长(分钟)
    notes: str              # 备注
}
```

## SM-2 算法说明

间隔重复算法基于 SuperMemo-2 算法：

1. **评分 (Quality)**: 0-5 分
   - 5: 完美回答
   - 4: 正确回答，犹豫
   - 3: 正确回答，困难
   - 2: 不正确，接近正确
   - 1: 不正确，记得一点
   - 0: 完全忘记

2. **难度系数 (EF)**: 初始 2.5，范围 1.3-2.5
   - EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))

3. **间隔天数**:
   - 第1次: 1天
   - 第2次: 6天
   - 第n次: 前间隔 * EF
