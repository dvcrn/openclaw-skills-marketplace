---
name: job-hunter
description: "Job hunting assistant with resume generator & scoring. 求职助手、简历生成、简历评分、简历优化、简历模板、resume、markdown简历、简历打分、简历诊断、面试准备、面试问题、薪资谈判、找工作、跳槽、换工作、Boss直聘、拉勾网、猎聘、求职信、cover letter、自我介绍、电梯演讲、elevator pitch、求职追踪、offer谈判、offer对比、面试跟进邮件、follow-up email、职业规划、校招、社招、秋招春招、面经、八股文、JD匹配、简历匹配度、模拟面试、mock interview。Job search, resume file generator (markdown), resume scoring system (10 dimensions/100 points), interview prep, salary negotiation, application tracker, follow-up emails, offer comparison, JD skill matching analysis, mock interview (HR/Technical/Final rounds with 10 Q&A each). Use when: (1) generating a resume/CV file with smart skill matching by position, (2) scoring/evaluating an existing resume, (3) writing cover letters, (4) preparing for job interviews, (5) researching salary ranges, (6) tracking job applications, (7) crafting elevator pitches/self-introductions, (8) writing follow-up emails after interviews, (9) comparing multiple job offers, (10) analyzing JD to find skill gaps, (11) mock interview practice with coaching tips, (12) any job hunting or career transition task. 适用场景：一键生成markdown简历文件（根据职位智能匹配技能+项目）、简历评分诊断（10维度100分制）、写求职信、准备面试、查薪资、追踪求职进度、写自我介绍、面试跟进邮件、offer对比分析、JD匹配分析（投了没回复的痛点）、模拟面试（面试紧张的痛点）、跳槽准备。春招旺季必备！中英双语输出。本地运行，无需API。"
---

# Job Hunter — 求职管理助手

All commands via `scripts/job.sh`. Data stored in `~/.job-hunter/applications.json`.

## 为什么用这个 Skill？ / Why This Skill?

- **简历生成**：根据职位智能匹配技能集和项目模板，一键输出Markdown简历文件
- **简历评分**：10维度100分制评分系统，精准诊断简历问题并给出改进建议
- **中英双语**：所有输出都是中英对照，适合国内外求职
- **求职追踪器**：本地持久化存储求职状态，不用手动维护Excel
- **一站式**：简历→求职信→面试准备→薪资查询→进度追踪，完整求职链路
- Compared to asking AI directly: persistent application tracking, structured bilingual output, resume file generation with smart skill matching, and a 10-dimension scoring system

## Commands

```bash
# 📄 生成Markdown简历文件 (根据职位智能匹配)
job.sh resume "姓名" "职位"
# 输出: resume_姓名_职位.md

# 📊 简历评分 (10维度/100分/S~D等级)
job.sh score "简历文件路径"

# 求职信 Cover letter
job.sh cover-letter "公司" "职位"

# 面试准备 Interview prep
job.sh interview "职位"

# 薪资参考 Salary reference
job.sh salary "职位" "城市"

# 求职追踪 Application tracker
job.sh tracker add "公司" "职位" "状态"
job.sh tracker list
job.sh tracker update "ID" "新状态"

# 电梯演讲 Elevator pitch
job.sh elevator-pitch "职位"

# 面试跟进邮件 Follow-up emails
job.sh follow-up "公司"

# Offer对比分析 Compare offers
job.sh compare "公司1" "公司2"

# JD匹配分析 (痛点: 投了没回复)
job.sh match "JD文本或关键技能要求"
# → 提取JD技能要求，对比简历匹配度

# 模拟面试 (痛点: 面试紧张)
job.sh mock "职位" "轮次"
# → 轮次: HR轮 / 技术轮 / 终面
# → 10题+考察点+回答框架+避坑提示

# 帮助 Help
job.sh help
```

## Workflow

1. Run the appropriate `job.sh` subcommand based on user request.
2. Present the output directly — it is already bilingual (中英双语).
3. For tracker commands, data persists in `~/.job-hunter/applications.json`.

## Notes

- All output is bilingual Chinese/English.
- Python 3.6+ compatible (no f-strings).
- Tracker auto-generates incremental IDs.
