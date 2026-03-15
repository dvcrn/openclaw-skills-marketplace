---
name: time-analyzer
description: "Time tracking and analysis skill for automatic activity monitoring and productivity insights. Use when the user wants to track time spent on activities, analyze time usage patterns, get productivity suggestions, or generate time reports. Triggers on phrases like \"track my time\", \"analyze my time\", \"time report\", \"productivity analysis\", \"how am I spending my time\", \"time tracking\", \"start tracking\", \"stop tracking\", \"time suggestions\", \"time optimization\"."
---

# Time Analyzer

Time Analyzer 是一个时间追踪和分析工具，帮助用户记录活动、分析时间使用模式，并提供优化建议。

## 功能特性

- **时间记录**: 自动追踪活动开始/结束，支持手动添加记录
- **活动分类**: 8种预设分类（工作、学习、会议、休息、运动、娱乐、睡眠、其他）
- **时间分析**: 分类统计、活跃时段分析、高频活动识别
- **优化建议**: 基于数据生成个性化的时间管理建议
- **报告生成**: 生成完整的时间使用报告

## 使用方法

### CLI 命令

```bash
# 开始记录活动
time-analyzer start <category> [description] [tags]

# 停止当前活动
time-analyzer stop

# 查看当前状态
time-analyzer status

# 分析时间数据（默认过去7天）
time-analyzer analyze [days]

# 生成优化建议
time-analyzer suggest

# 生成完整报告
time-analyzer report [days]

# 手动添加记录
time-analyzer add <category> <description> <minutes>

# 列出所有分类
time-analyzer categories

# 显示帮助
time-analyzer help
```

### 活动分类

| 分类 | 说明 | 图标 |
|------|------|------|
| work | 工作 | 💼 |
| study | 学习 | 📚 |
| meeting | 会议 | 👥 |
| break | 休息 | ☕ |
| exercise | 运动 | 🏃 |
| entertainment | 娱乐 | 🎮 |
| sleep | 睡眠 | 😴 |
| other | 其他 | 📌 |

### 使用示例

```bash
# 开始记录工作
time-analyzer start work "开发新功能"

# 开始记录学习
time-analyzer start study "阅读技术文档"

# 结束当前活动
time-analyzer stop

# 分析过去30天
time-analyzer analyze 30

# 获取优化建议
time-analyzer suggest

# 手动添加1小时的会议记录
time-analyzer add meeting "周会" 60
```

## 数据存储

数据存储在用户主目录下的 `.time-analyzer/` 文件夹：
- `records.json`: 所有活动记录
- `config.json`: 配置和当前会话状态

## 报告内容

分析报告包含：
1. **概览**: 总活动数、总时长、日均统计
2. **分类详情**: 各类别时间占比和频次
3. **活跃时段**: 一天中最活跃的时间段
4. **高频活动**: 最常进行的活动TOP 5
5. **优化建议**: 基于数据的时间管理建议

## 自动追踪

当前版本支持手动启动/停止追踪。可以通过定时任务实现自动报告：

```bash
# 添加到 crontab，每天22:00生成报告
echo "0 22 * * * /usr/local/bin/time-analyzer report" | crontab -
```

## 依赖

- Node.js >= 18.0.0
- 无需外部依赖（纯Node.js实现）

## 安装

```bash
# 全局安装
npm install -g time-analyzer

# 或使用 npx
npx time-analyzer
```
