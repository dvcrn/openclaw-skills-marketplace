---
name: scholarsearch
description: "Academic literature search and briefing generation with Tavily API, PubMed, and Google Scholar. Use when you need to search for latest academic papers on specific topics, generate Top 10 literature briefing with relevance rankings, save reports to Obsidian vault in daily format, or send summaries via Feishu. Accepts multiple keywords separated by comma or space."
---

# Scholar Search 🔬📚

Automated academic literature discovery and briefing generation. This skill searches PubMed, Google Scholar, and other academic databases using Tavily API, generates relevance-ranked Top 10 reports, and delivers them to your Obsidian vault and Feishu.

## Quick Start

```bash
# Search papers on specific topic
scholarsearch 关键词：房颤，导管消融，脉冲电场消融
```

Or multiple keywords separated by comma or space:
```bash
scholarsearch 房颤，afib, 心房颤动，catheter ablation，消融，pulsed field ablation
```

## What It Does

1. **Multi-source search**: Queries PubMed, Google Scholar, and academic web sources via Tavily API
2. **Relevance ranking**: Evaluates papers based on:
   - Recency (2025-2026 priority)
   - Clinical significance (human trials, RCTs)
   - Author/institution credibility
   - Journal/publisher reputation
   - Direct topic relevance
3. **Top 10 curation**: Selects most relevant papers with scores 0.0-1.0
4. **Report generation**: Creates formatted briefing with links, abstracts, and key findings
5. **Dual delivery**: Saves to Obsidian + sends complete content via Feishu

## When to Use

- ✅ Morning academic briefings (configurable timing, defaults to 5:00 AM)
- ✅ Literature review on specific medical/technical topics
- ✅ Tracking emerging research in a field
- ✅ Getting curated "Top 10" lists with context

## Parameters

Accept **comma-separated or space-separated** keywords:

```
scholarsearch 房颤，心房颤动，pulased field ablation，catheter ablation
scholarsearch AFib, atrial fibrillation, ablation, electrogram
scholarsearch 机器学习，深度学习，神经网络，大模型
```

## Output Format

```markdown
# 每日学术更新 - [Topic] 研究简报

**日期:** YYYY-MM-DD  
**更新时间:** HH:MM Asia/Shanghai  
**关键词:** [your keywords]

---

## 📊 Top 10 精选文献

按相关性评分排序 (0.0-1.0):

### 1️⃣ [Paper Title]
**评分:** 0.XX  
**链接:** https://...  
**摘要:** [Brief summary with key findings]

... (10 papers)

---

## 📝 本期要点总结

### 🔥 核心发现

[Bullet points of major breakthroughs/trends]

### 🎯 临床/研究关注重点

[What to watch for]

---

## 🔄 配置说明

**检索频率:** [Set to user preference]  
**来源:** Tavily API (PubMed, Google Scholar, etc.)  
**保存路径:** Obsidian 每日学术更新/YYYY-MM-DD.md  
**排序方式:** 相关性评分 + 发表时间

---

*自动生成 | ☕🐕 CoffeeDog | [Topic] | YYYY-MM-DD*
```

## Error Handling

- **No results**: Adjust keywords, widen search terms
- **Low-quality links**: Skip non-academic sources, prioritize peer-reviewed
- **API limits**: Retry with backoff, rate limit protection

## Integration Points

- **Tavily API**: Academic web search with PubMed/Scholar support
- **Feishu**: Daily delivery of complete briefing content
- **Obsidian**: Auto-save to `Obsidian 每日学术更新/YYYY-MM-DD.md`

## Notes

- For automatic scheduling: Use cron or heartbeat to run at 5:00 AM daily
- Use English keywords for better PubMed results
- Mix Chinese + English terms for comprehensive coverage
- Consider topic-specific parameters: "房颤 2026，PFA 临床试验"

---

*Academic discovery automated. CoffeeDog knows the papers. ☕🐕*
