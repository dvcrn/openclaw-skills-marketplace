# Study Tutor Skill

**A complete learning system based on cognitive science — covering preview, note-taking, review, and spaced repetition.**

**基于认知科学的完整学习系统 —— 涵盖课前预习、课中笔记、课后复盘、间隔复习全流程。**

---

## 📖 Overview / 概述

**Study Tutor** is an AI-powered learning assistant skill that helps students and self-learners master any subject systematically. It's built on proven cognitive science principles including Active Recall, Spaced Repetition, Testing Effect, and Elaboration.

**Study Tutor** 是一个 AI 驱动的学习辅助技能，帮助学生和自学者系统化掌握任何学科。基于经过验证的认知科学原理，包括主动回忆、间隔重复、测试效应和精细化加工。

### Key Features / 核心功能

- ✅ **Pre-learning Diagnosis** - Understand goals, baseline, and available time
- ✅ **Teacher Preparation** - AI reads your textbooks/PDFs before teaching
- ✅ **4 Learning Modes** - Guided / Batch / Question-driven / Hybrid
- ✅ **Complete Workflow** - Preview → Note-taking → Review → Spaced Repetition → Weekly Review → Exam Prep
- ✅ **Memory Learning Profile** - Separate file to track progress, mistakes, and weak points
- ✅ **Next-day Review** - Automatic review suggestions when continuing on a new day
- ✅ **Milestone Review** - Comprehensive review after completing each chapter

- ✅ **学前诊断** - 了解目标、基础、可用时间
- ✅ **教师备课** - AI 先阅读教材/PDF 再教学
- ✅ **4 种学习模式** - 引导式 / 批量 / 问题驱动 / 混合
- ✅ **完整流程** - 预习→笔记→复盘→间隔复习→周复盘→考前冲刺
- ✅ **Memory 学习档案** - 独立文件追踪进度、错题、薄弱点
- ✅ **次日学习** - 新一天继续时自动提供复习建议
- ✅ **里程碑回顾** - 每章完成后全面回顾

---

## 🎯 Target Users / 目标人群

| User Group | Learning Characteristics | Teaching Focus | Example Scenarios |
|------------|-------------------------|----------------|-------------------|
| **Primary & Secondary Students** | Need more guidance, shorter attention span | Fun analogies, frequent checks, encouragement | Homework help, exam prep, entrance exams |
| **University Students** | Strong autonomy, good comprehension | Deep explanations, knowledge connections | Major courses, grad school prep, certifications |
| **Self-learners** | Clear goals, lack systematic planning | System planning, progress tracking, feedback | Programming, languages, skill building |
| **Exam Candidates** | Time-pressed, goal-oriented, anxious | Focus on key points, past papers, mindset | Gaokao, grad exams, civil service, language tests |

| 人群 | 学习特点 | 教学侧重点 | 示例场景 |
|------|---------|-----------|---------|
| **中小学生** | 需要引导，注意力短 | 趣味类比、频繁检验 | 作业辅导、升学备考 |
| **大学生** | 自主性强，理解力好 | 深度讲解、知识联系 | 专业课、考研复习 |
| **自学者** | 目标明确，易放弃 | 系统规划、正向反馈 | 编程、语言学习 |
| **备考人群** | 时间紧，焦虑感强 | 考点聚焦、真题训练 | 中高考、公考、证书 |

---

## 🚀 Usage / 使用方法

### Trigger Phrases / 触发词

- "I want to learn [subject/chapter]" / "我要学习 [科目/章节]"
- "I don't understand [concept]" / "[概念] 我不懂"
- "Help me with this homework" / "帮我看看这个作业"
- "I have an exam soon, help me review" / "要考试了帮我复习"
- "How can I study more efficiently?" / "怎么学习效率更高"
- "Help me organize my mistakes" / "帮我整理错题"

### Example Conversation / 对话示例

```
User: I want to learn Data Structures, starting from Binary Trees

AI: Great! I'll help you learn Data Structures - Binary Trees.

Before we start, let me understand your situation:

### 📊 Learning Diagnosis

1. **Learning Goal**
   - Is this for an exam / homework / self-study / interest?
   - If exam, what's your target score? When is it?

2. **Current Baseline**
   - Have you studied this before?
   - What feels unclear/difficult?

3. **Available Time**
   - How much time can you spend daily?
   - How long do you want to complete this?

---

(User responds)

---

### 📁 Creating Learning Profile

I'll create a learning profile to track your progress and weak points.

(Creates `memory/DataStructures-study.md`)

**Profile created!** Includes:
- Basic info (subject, start date, goals)
- Progress tracker
- Mistake tracker
- Review plan

---

### 🎓 Learning Mode Selection

Based on your situation, I recommend **Guided Learning Mode**...
```

---

## 📂 File Structure / 文件结构

```
Study Tutor/
├── SKILL.md          # Main skill definition (English)
├── SKILL-CN.md       # Chinese version (optional)
└── README.md         # This file
```

### Learning Profile Location / 学习档案位置

```
memory/
├── DataStructures-study.md
├── Calculus-study.md
├── EnglishVocab-study.md
└── Physics-study.md
```

---

## 🔬 Scientific Basis / 科学依据

This skill is based on established cognitive science research:

- **Active Recall** - Karpicke & Roediger (2008)
- **Spaced Repetition** - Ebbinghaus Forgetting Curve
- **Testing Effect** - Roediger & Karpicke (2006)
- **Elaboration** - Chi et al. (1994)
- **Feynman Technique** - Based on Richard Feynman's learning method
- **Cornell Note-taking** - Walter Pauk, Cornell University
- **Paideia Classroom** - Zhang Xinxin (2014)

本技能基于成熟的认知科学研究：

- **主动回忆** - Karpicke & Roediger (2008)
- **间隔重复** - 艾宾浩斯遗忘曲线
- **测试效应** - Roediger & Karpicke (2006)
- **精细化加工** - Chi et al. (1994)
- **费曼技巧** - 基于 Richard Feynman 学习方法
- **康奈尔笔记法** - Walter Pauk, Cornell University
- **对分课堂** - 张学新 (2014)

---

## ⚙️ Configuration / 配置

No API keys or special configuration required. The skill uses built-in CoPaw tools:

- `read_file` / `write_file` - Learning profile management
- `pdf` - Reading textbooks and materials
- `memory_search` - Reviewing past learning records
- `cron` - Setting review reminders (Day 1, 3, 7)

无需 API 密钥或特殊配置。技能使用 CoPaw 内置工具：

- `read_file` / `write_file` - 学习档案管理
- `pdf` - 阅读教材和资料
- `memory_search` - 回顾过往学习记录
- `cron` - 设置复习提醒（第 1、3、7 天）

---

## 📝 Learning Profile Template / 学习档案模板

```markdown
# Data Structures Learning Profile

## Basic Info
- **Start Date:** 2026-03-10
- **Last Study:** 2026-03-10
- **Current Progress:** Chapter 1 / X chapters
- **Overall Mastery:** X%

## Progress Tracker
| Chapter | Status | Mastery | Last Study | Last Review | Notes |
|---------|--------|---------|------------|-------------|-------|
| Ch1: Binary Trees | ✅ Done | 85% | 2026-03-10 | 2026-03-11 | Core focus |
| Ch2: BST | 🔄 In Progress | 60% | 2026-03-11 | - | Ongoing |

## Mistakes & Weak Points
| Date | Topic | Error Type | Cause | Review Status |
|------|-------|-----------|-------|---------------|
| 03-10 | Inorder Traversal | Concept confusion | Left-right order reversed | 🔄 Needs review |

## Tomorrow's Review Plan
- [ ] Inorder Traversal (weak point)
- [ ] Binary Tree Traversal comprehensive practice
```

---

## 🎓 Teaching Modes / 教学模式

### Mode 1: Guided Learning (Recommended)
**Pace:** One concept at a time → Check → Proceed if correct

**Best for:** Beginners, deep mastery, high-score goals

### Mode 2: Batch Learning
**Pace:** 3-5 related concepts → Comprehensive check → Next batch

**Best for:** Review with baseline, time-pressed, pass-only goals

### Mode 3: Question-Driven
**Pace:** You ask → I explain → Follow-up → Next question

**Best for:** Specific concept gaps, homework help, exam Q&A

### Mode 4: Hybrid Mode
**Pace:** Dynamic adjustment based on difficulty

**Best for:** Most situations, balanced efficiency and depth

---

## 🔄 Next-Day Learning Flow / 次日学习流程

When you continue learning on a new day, the AI will:

1. **Check your learning profile** - Read `memory/{subject}-study.md`
2. **Compare dates** - Determine if it's a new day
3. **Offer two options:**
   - **Option 1:** Continue with new content
   - **Option 2:** Review first, then learn new (Recommended)
4. **Review includes:**
   - Yesterday's content (5-10 min)
   - Content from 3 days ago (forgetting curve peak)
   - Your weak points (from mistake tracker)

当你第二天继续学习时，AI 会：

1. **检查学习档案** - 读取 `memory/{科目}-study.md`
2. **对比日期** - 判断是否新的一天
3. **提供两个选项：**
   - **选项 1：** 直接开始新内容
   - **选项 2：** 先复习再学新的（推荐）
4. **复习内容：**
   - 昨天学的内容（5-10 分钟）
   - 三天前学的内容（遗忘曲线高峰）
   - 你的薄弱点（来自错题追踪）

---

## ⚠️ Important Notes / 注意事项

1. **Don't replace user thinking** - Guide, don't lecture
2. **Adjust based on user response** - Slow down if too fast, speed up if too easy
3. **Update learning profile** - After each session
4. **Encourage primarily** - Learning is long-term, maintain confidence
5. **Honest assessment** - Say it if not mastered, don't sugarcoat
6. **Scientific basis** - Every recommendation should have research backing
7. **Privacy protection** - Don't record personal info to public files

1. **不替代用户思考** - 引导而非灌输
2. **根据用户反应调整** - 太快就慢一点，太简单就加快
3. **更新学习档案** - 每次学习后
4. **鼓励为主** - 学习是长期的，保持信心
5. **诚实评估** - 没掌握就说没掌握，不要敷衍
6. **科学依据** - 每个建议都要有研究支持
7. **保护隐私** - 不记录个人信息到公开文件

---

## 📄 License / 许可证

Proprietary

---

## 🙏 Acknowledgments / 致谢

This skill integrates:
- **Guided Learning Skill** - For step-by-step teaching methodology
- **CoPaw Framework** - For tool integration and memory management
- **Cognitive Science Research** - For evidence-based learning strategies

本技能整合了：
- **Guided Learning Skill** - 逐步教学方法
- **CoPaw Framework** - 工具集成和记忆管理
- **认知科学研究** - 循证学习策略

---

## 📞 Support / 支持

For issues or suggestions, please open an issue on ClawHub or contact the developer.

如有问题或建议，请在 ClawHub 上提交 issue 或联系开发者。

---

**Version / 版本:** 1.0  
**Last Updated / 最后更新:** 2026-03-10  
**Author / 作者:** 姜凯奇 (Jiang Kaiqi)


---

## 🛠 Development Tools / 开发工具

**Built with / 开发框架:**
- **CoPaw Framework** — AI agent automation platform / AI 智能体自动化平台
- **Qwen 3.5 (通义千问 3.5)** — Large language model by Alibaba Cloud / 阿里巴巴云大语言模型

**Development Environment / 开发环境:**
- Python 3.12
- CoPaw Skills System
- Windows 11
