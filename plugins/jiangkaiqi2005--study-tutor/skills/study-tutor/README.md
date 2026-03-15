# Study Tutor Skill

**A complete learning system based on cognitive science — covering preview, note-taking, review, and spaced repetition.**

---

## 📖 Overview

**Study Tutor** is an AI-powered learning assistant skill that helps students and self-learners master any subject systematically. It's built on proven cognitive science principles including Active Recall, Spaced Repetition, Testing Effect, and Elaboration.

### Key Features

- ✅ **Pre-learning Diagnosis** - Understand goals, baseline, and available time
- ✅ **Teacher Preparation** - AI reads your textbooks/PDFs before teaching
- ✅ **4 Learning Modes** - Guided / Batch / Question-driven / Hybrid
- ✅ **Complete Workflow** - Preview → Note-taking → Review → Spaced Repetition → Weekly Review → Exam Prep
- ✅ **Memory Learning Profile** - Separate file to track progress, mistakes, and weak points
- ✅ **Next-day Review** - Automatic review suggestions when continuing on a new day
- ✅ **Milestone Review** - Comprehensive review after completing each chapter

---

## 🎯 Target Users

| User Group | Learning Characteristics | Teaching Focus | Example Scenarios |
|------------|-------------------------|----------------|-------------------|
| **Primary & Secondary Students** | Need more guidance, shorter attention span | Fun analogies, frequent checks, encouragement | Homework help, exam prep, entrance exams |
| **University Students** | Strong autonomy, good comprehension | Deep explanations, knowledge connections | Major courses, grad school prep, certifications |
| **Self-learners** | Clear goals, lack systematic planning | System planning, progress tracking, feedback | Programming, languages, skill building |
| **Exam Candidates** | Time-pressed, goal-oriented, anxious | Focus on key points, past papers, mindset | Gaokao, grad exams, civil service, language tests |

---

## 🚀 Usage

### Trigger Phrases

- "I want to learn [subject/chapter]"
- "I don't understand [concept]"
- "Help me with this homework"
- "I have an exam soon, help me review"
- "How can I study more efficiently?"
- "Help me organize my mistakes"

### Example Conversation

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

## 📂 File Structure

```
Study Tutor/
├── SKILL.md          # Main skill definition (English)
├── SKILL-CN.md       # Chinese version
├── README.md         # This file (English)
└── README-CN.md      # Chinese version
```

### Learning Profile Location

```
memory/
├── DataStructures-study.md
├── Calculus-study.md
├── EnglishVocab-study.md
└── Physics-study.md
```

---

## 🔬 Scientific Basis

This skill is based on established cognitive science research:

- **Active Recall** - Karpicke & Roediger (2008)
- **Spaced Repetition** - Ebbinghaus Forgetting Curve
- **Testing Effect** - Roediger & Karpicke (2006)
- **Elaboration** - Chi et al. (1994)
- **Feynman Technique** - Based on Richard Feynman's learning method
- **Cornell Note-taking** - Walter Pauk, Cornell University
- **Paideia Classroom** - Zhang Xinxin (2014)

---

## ⚙️ Configuration

No API keys or special configuration required. The skill uses built-in CoPaw tools:

- `read_file` / `write_file` - Learning profile management
- `pdf` - Reading textbooks and materials
- `memory_search` - Reviewing past learning records
- `cron` - Setting review reminders (Day 1, 3, 7)

---

## 📝 Learning Profile Template

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

## 🎓 Teaching Modes

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

## 🔄 Next-Day Learning Flow

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

---

## ⚠️ Important Notes

1. **Don't replace user thinking** - Guide, don't lecture
2. **Adjust based on user response** - Slow down if too fast, speed up if too easy
3. **Update learning profile** - After each session
4. **Encourage primarily** - Learning is long-term, maintain confidence
5. **Honest assessment** - Say it if not mastered, don't sugarcoat
6. **Scientific basis** - Every recommendation should have research backing
7. **Privacy protection** - Don't record personal info to public files

---

## 📄 License

Proprietary

---

## 🙏 Acknowledgments

This skill integrates:
- **Guided Learning Skill** - For step-by-step teaching methodology
- **CoPaw Framework** - For tool integration and memory management
- **Cognitive Science Research** - For evidence-based learning strategies

---

## 🛠 Development Tools

**Built with:**
- **CoPaw Framework** — AI agent automation platform
- **Qwen 3.5 (通义千问 3.5)** — Large language model by Alibaba Cloud

**Development Environment:**
- Python 3.12
- CoPaw Skills System
- Windows 11

---

## 📞 Support

For issues or suggestions, please open an issue on ClawHub or contact the developer.

---

**Version:** 1.0  
**Last Updated:** 2026-03-10  
**Author:** 姜凯奇 (Jiang Kaiqi)
