# Study Buddy - 智能学习伴侣

> AI-powered learning companion for creating personalized study plans, tracking progress, and providing feedback.

一个轻量级的命令行学习管理工具，帮你制定学习计划、追踪进度、管理错题本。

## ✨ 核心特性

- 📋 **学习档案** - 交互式收集学习目标、时间、水平、偏好
- 📅 **学习计划** - 自动生成三阶段学习计划（入门→核心→实践）
- ✅ **每日打卡** - 记录学习时长和内容，追踪连续打卡
- 📊 **进度统计** - 学习天数、连续打卡、可视化进度条
- 📈 **学习报告** - 生成评级报告，评估学习阶段
- 📝 **错题本** - 添加、复习、标记掌握错题
- 💡 **反馈建议** - 基于学习数据提供个性化建议

## 🚀 快速开始

### 安装

```bash
# 克隆或下载到本地
cd ~/.openclaw/workspace/skills/study-buddy

# 确保有 Python 3
python3 --version
```

### 使用

```bash
# 1. 开始学习之旅（交互式创建档案）
python3 scripts/study-buddy.py start

# 2. 查看今日学习任务
python3 scripts/study-buddy.py today

# 3. 学习打卡
python3 scripts/study-buddy.py checkin "学习了Python列表操作" --duration "45分钟"

# 4. 查看学习进度
python3 scripts/study-buddy.py progress

# 5. 查看学习计划
python3 scripts/study-buddy.py plan

# 6. 生成学习报告
python3 scripts/study-buddy.py report

# 7. 错题本管理
python3 scripts/study-buddy.py wrong add "二次函数求根错误"
python3 scripts/study-buddy.py wrong list
python3 scripts/study-buddy.py wrong review "错题ID"
python3 scripts/study-buddy.py wrong master "错题ID"

# 8. 获取反馈建议
python3 scripts/study-buddy.py feedback

# 9. 查看数据位置
python3 scripts/study-buddy.py data
```

## 📁 数据存储

所有数据存储在本地 `~/.study-buddy/` 目录：

```
~/.study-buddy/
├── profile.json           # 学习档案
├── plans/                 # 学习计划
│   └── plan_YYYYMMDD.json
├── logs/                  # 学习日志
│   └── YYYY-MM-DD.json
├── wrong_questions/       # 错题本
│   └── wrong_questions.json
└── report_YYYYMMDD.json   # 学习报告
```

## 🎯 目标用户

- 高中生及家长
- 自学者
- 需要系统学习规划的学习者

## 🛡️ 安全边界

- ✅ 学习计划制定、进度跟踪、打卡、反馈、学习报告
- ❌ 不提供具体学科教学内容（如数学题解答）
- ❌ 不替代老师/家长决策
- ❌ 不接外部教育平台
- ❌ 不做夸张的学习效果承诺
- ✅ 尊重用户隐私，数据本地存储

## 📚 文档

- [命令详细说明](references/commands.md)
- [开发待办清单](references/todo.md)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！