---
name: junyi-archive
description: "自动归档 — A knowledge management system for families that captures, distills, and organizes information into a three-layer Obsidian vault: Inbox (raw capture by scene), Cognition (distilled insights by 5 dimensions), and Guidebook (proven reusable guides). Triggers when user mentions \"自动归档\", \"归档\", \"享育心塾萃取器\", \"萃取器\", or asks to save/store/organize any information — articles, reading notes, class notes, children's words, conversations, ideas, reflections, quotes, or any content they want to keep. Also triggers on \"save this\", \"remember this\", \"file this away\", \"put this in my notes\", \"store this for later\", \"记下来\", \"存一下\", \"帮我记\", \"存到知识库\"."
---

# 自动归档 (Junyi Archive)

A three-layer knowledge management system for families. Turns the flood of daily
information into organized, retrievable, and reusable wisdom.

## Design Principles

- Low-friction capture, traceable distillation, cautious upgrades, long-term maintainability
- Only text content; images/video out of scope
- Storage: Obsidian physical files (not memory — survives Gateway restarts)

## The Three Layers

```
Inbox (收集层)        → Raw capture, organized by scene
      ↓ AI distills (when warranted)
Cognition (认知层)    → Refined insights by 5 dimensions
      ↓ Proven patterns emerge
Guidebook (指南层)    → Verified reusable guides, methods, checklists
```

### Layer 1: Inbox (收集层)

Zero-friction entry point. Raw records organized by **scene**.

**Default scenes:**

| Scene | What goes here |
|-------|---------------|
| 学习成长 | Class notes, reading highlights, lectures, courses, podcasts |
| 童言童语 | Children's actual words, questions, expressions — preserved verbatim |
| 育儿观察 | Parents' observations of children — milestones, patterns, growth moments |
| 灵感闪现 | Sudden ideas, one-line thoughts, "what if..." moments |
| 对话收获 | Key takeaways from conversations with others |
| 工作记录 | Work insights, professional reflections |
| 生活记录 | Daily life events and feelings |

**Custom scenes:** When user proposes a new scene, confirm name once, then auto-create directory.

### Layer 2: Cognition (认知层)

Distilled knowledge organized by five dimensions:

| Dimension | Directory name (exact) | The test | Examples |
|-----------|----------------------|----------|---------|
| **What I Learn** | `cognition/What I Learn/` | "I learned this from someone/something else" | Book insights, article takeaways, lecture notes |
| **What I Think** | `cognition/What I Think/` | "I figured this out / observed this myself" | Personal reflections, parenting discoveries, patterns noticed |
| **What I Create** | `cognition/What I Create/` | "I made/wrote/built this" | Articles, presentations, systems designed |
| **What I Collect** | `cognition/What I Collect/` | "I want to keep this as-is" | Quotes, golden lines, sparks |
| **Who We Are** | `cognition/Who We Are/` | "This defines who we are as a family" | Values, philosophy, long-term goals |

**IMPORTANT: Use exact directory names above (with spaces, title case). Never convert to lowercase-hyphen format like `what-i-think`.**

**Classification rules:**
- External source primarily → What I Learn
- Self-observation/reflection primarily → What I Think
- Finished output → What I Create
- Fragment to keep as-is → What I Collect
- Family identity/values/rules → Who We Are
- Mixed content → classify by primary source; if both parts are important, split into two cognition entries

### Layer 3: Guidebook (指南层)

Proven, reusable methods that answer "how to do X" concretely.

**Admission criteria (strict):**
- User explicitly says "已验证", "反复有效", "用了较长时间", or similar
- OR original text contains clear validation evidence (e.g., "执行两个月有效")
- Methods that don't meet validation criteria stay in Cognition, not Guidebook
- Mark as "待验证" only if user wants to track an unvalidated method

## Decision Flow (4 Steps)

### Step 1: Determine user intent
- User says "就存一下 / 先记下来 / 不用总结" → Only write `inbox`, stop
- Normal record → Write `inbox`, then evaluate distillation (Step 3)
- Explicitly validated method/process → Write `inbox` + `cognition` + evaluate `guidebook`

### Step 2: Determine scene
- Scene is clear → Route to corresponding `inbox/` directory
- Scene is ambiguous but close → Pick closest match, preserve original context in content
- Scene truly unclear → **Ask user**, do not guess

### Step 3: Determine whether to distill to Cognition

**Distill when:**
- Content has clear viewpoints, patterns, insights, or conclusions
- Content has long-term reuse value
- Content is a quote/fragment worth collecting
- Content is from articles/lectures/courses that can be distilled

**Do NOT distill when:**
- Pure memo or reminder
- Pure diary/stream-of-consciousness with no extractable insight
- User explicitly asked not to summarize
- Content only suitable for raw preservation

**Short content exception:** Short reflections (<200 chars) or single quotes can skip inbox and go directly to Cognition — the raw text IS the refined version, no need for duplicate storage.

### Step 4: Determine whether to enter Guidebook
- Has executable steps + validated effectiveness → Guidebook
- Just an idea, principle, or feeling → Stay in Cognition
- Unvalidated method → Stay in Cognition, upgrade later when validated

## File Management Rules

### When to create new file
- New topic
- First record of the day under a new topic
- Content significantly different from existing notes
- Content belongs to a different layer or dimension

### When to merge into existing file
- Same day AND same scene/topic
- New content supplements existing content (not a new topic)
- Append with a separator (`---`) and timestamp

### When to update existing file
- Guidebook: prefer updating original file over creating new ones; refresh "更新日期"
- Cognition: if supplementing the same insight, add a "补充观察" section
- Never overwrite raw inbox content for cosmetic reasons

## Naming Rules

- Inbox: `YYYY-MM-DD 标题.md`
- Cognition: `标题.md` (no date prefix — cognition is topic-centric)
- Guidebook: `主题名.md`

**Title generation:**
- If user provided a title, use it
- Otherwise generate a natural-language title from the first 8-15 chars of content
- Never use abstract titles like "感悟1" or "笔记2"

## Content Templates

### Inbox
```markdown
# [Title]

> 日期：YYYY-MM-DD
> 场景：[scene name]
> 来源：[source if applicable]

---

[Original content — keep close to original, minimal formatting]
```

### Cognition
```markdown
# [Title]

> 日期：YYYY-MM-DD
> 维度：[dimension name]
> 来源：[source — article name, conversation, experience, etc.]
> 源文件：[corresponding inbox filename, e.g., inbox/学习成长/2026-03-13 蒙特梭利.md]
> 标签：#tag1 #tag2

---

[Refined content — distilled, structured, insightful]

## 核心要点
- Point 1
- Point 2
```

Note: When content skips inbox (short reflections/quotes), 源文件 field is "用户即时输入".

### Guidebook
```markdown
# [Title]

> 更新日期：YYYY-MM-DD
> 适用场景：[when to use this guide]
> 验证状态：[已验证 / 待验证]
> 来源：[corresponding cognition or inbox filename]

---

[Step-by-step guide, checklist, or methodology]
```

**Field defaults:**
- 来源 missing → "用户即时输入"
- Tags: 2-3 max, prefer topic/person/method keywords
- Preserve original attribution for articles/lectures/books

## Source Traceability

- Every cognition entry must trace back to an inbox file or "用户即时输入"
- Every guidebook entry must trace back to cognition or inbox
- No orphaned conclusions without traceable context

## Long Text Handling

| Size | Strategy |
|------|----------|
| < 30,000 chars | Write directly |
| ≥ 30,000 chars | Chunked write (≤20K per chunk, break at paragraph boundaries) |

**Never use `obsidian-cli create --content`** — truncation bug.

After every write, verify:
```bash
ls -la "<file>"     # exists and reasonable size
tail -5 "<file>"    # content is complete
```

## Searching and Retrieval

- `obsidian-cli search-content "<keyword>"` — search note content
- `obsidian-cli search "<note name>"` — search note titles
- `find` + `grep` — precise filesystem search

## Configuration

Vault path configured per user. Default structure (use exact directory names):
```
[vault root]/
├── inbox/
│   ├── 学习成长/
│   ├── 童言童语/
│   ├── 育儿观察/
│   ├── 灵感闪现/
│   ├── 对话收获/
│   ├── 工作记录/
│   └── 生活记录/
├── cognition/
│   ├── What I Learn/
│   ├── What I Think/
│   ├── What I Create/
│   ├── What I Collect/
│   └── Who We Are/
└── guidebook/
```
