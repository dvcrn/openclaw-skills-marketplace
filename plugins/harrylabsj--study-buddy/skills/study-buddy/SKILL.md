---
name: study-buddy
description: "AI-powered learning companion for creating personalized study plans, tracking progress, and providing feedback. Use when user wants to start learning something new, create a study plan, track learning progress, get study reminders, or receive learning feedback. Triggers include \"帮我制定学习计划\", \"我要学XX\", \"追踪我的学习进度\", \"学习打卡\", \"study plan\", \"learn programming\", \"track my progress\"."
---

# Study Buddy - 智能学习伴侣

帮你制定学习计划、追踪进度、提供反馈的 AI 学习伴侣。

## 核心功能

1. **用户档案** - 交互式收集学习目标、时间、水平、偏好
2. **学习计划** - 基于背景生成个性化阶段性计划
3. **每日打卡** - 记录学习时长和内容
4. **进度跟踪** - 统计学习天数、连续打卡、阶段评估
5. **学习报告** - 生成周期性学习总结和评级
6. **错题本** - 记录、复习、掌握错题
7. **反馈建议** - 基于数据给出个性化建议

## 命令入口

```bash
# 开始学习之旅（交互式收集背景）
python3 scripts/study-buddy.py start

# 查看今日学习任务
python3 scripts/study-buddy.py today

# 学习打卡
python3 scripts/study-buddy.py checkin "学习了Python基础语法" --duration "45分钟"

# 查看学习进度
python3 scripts/study-buddy.py progress

# 查看学习计划
python3 scripts/study-buddy.py plan

# 生成学习报告
python3 scripts/study-buddy.py report

# 错题本管理
python3 scripts/study-buddy.py wrong add "二次函数求根错误"
python3 scripts/study-buddy.py wrong list
python3 scripts/study-buddy.py wrong review "错题ID"
python3 scripts/study-buddy.py wrong master "错题ID"

# 获取反馈建议
python3 scripts/study-buddy.py feedback

# 查看学习数据存储位置
python3 scripts/study-buddy.py data
```

## 数据存储

用户数据存储在: `~/.study-buddy/`
- `profile.json` - 学习背景档案
- `plans/` - 学习计划目录
- `logs/` - 学习记录日志
- `wrong_questions/` - 错题本
- `report_YYYYMMDD.json` - 学习报告

## 使用流程

1. **初始化**: 运行 `start` 创建学习档案
2. **制定计划**: 根据背景自动生成学习计划，使用 `plan` 查看
3. **每日执行**: 使用 `today` 查看任务，`checkin` 打卡
4. **定期复盘**: 使用 `progress` 查看进展，`report` 生成报告
5. **错题管理**: 使用 `wrong` 命令管理错题本

## 目标用户

优先聚焦：**高中生及家长**

## 安全边界

- ✅ 学习计划制定、进度跟踪、打卡、反馈、学习报告
- ❌ 不提供具体学科教学内容（如数学题解答）
- ❌ 不替代老师/家长决策
- ❌ 不接外部教育平台
- ❌ 不做夸张的学习效果承诺
- ❌ 不收集敏感隐私
- ✅ 尊重用户隐私，数据本地存储
- ✅ 建议用户结合真人教师或专业课程

## 扩展计划（未来规划，非当前版本）

以下功能为后续迭代方向，当前 MVP 版本未实现：

- [ ] Feishu集成
- [ ] 可视化报告
- [ ] 智能提醒功能
- [ ] 多计划管理
- [ ] 数据导出功能
- [ ] 更智能的计划生成算法

## 参考文档

- 命令详细说明: [references/commands.md](references/commands.md)
- 开发待办清单: [references/todo.md](references/todo.md)
