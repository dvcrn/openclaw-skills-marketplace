# AI Talent Recruiter Skill

A comprehensive Claude Code skill for AI/ML talent discovery, profiling, and personalized outreach.

## Features

- **Multi-source Search**: Search candidates via web search, academic sites, and professional networks
- **Dual Scraping Approach**: Support both BrightData MCP (paid) and Python (free) scraping
- **Chinese Candidate Identification**: Multi-dimensional scoring using surnames and institutions
- **Smart Classification**: Categorize candidates as PhD/PostDoc/Professor/Industry
- **7-Level Deduplication**: Remove duplicate candidates using email, Scholar, LinkedIn, etc.
- **22 Standardized Fields**: Map research directions to standard categories
- **Personalized Emails**: Generate customized outreach using field-specific templates

## Installation

### Step 1: Copy to Claude Skills Directory

```bash
# Copy the entire ai-talent-search folder to your Claude skills directory
cp -r ai-talent-search ~/.claude/skills/
```

### Step 2: Configure Prerequisites

**Option A: BrightData MCP (Paid, Recommended)**

```bash
claude mcp add --transport sse --scope user brightdata "https://mcp.brightdata.com/sse?token=<your-api-token>"
```

**Option B: Python Scraping (Free)**

```bash
pip install requests beautifulsoup4 httpx python-dotenv
```

### Step 3: Verify Installation

In Claude Code, type `/ai-talent-recruiter` to invoke the skill.

## Quick Start

### Example 1: Search RL PhD Students

```
User: Use the ai-talent-recruiter skill to find PhD students working on reinforcement learning at top universities
```

Claude will:
1. Generate search queries for RL PhD students
2. Execute searches and collect URLs
3. Scrape profiles (using BrightData or Python)
4. Extract and classify candidates
5. Generate personalized emails

### Example 2: Lab-Targeted Search

```
User: Find all PhD students at Stanford AI Lab working on multimodal learning
```

### Example 3: Chinese Candidate Discovery

```
User: Find Chinese researchers who published at NeurIPS 2024 on LLM alignment
```

## File Structure

```
ai-talent-search/
├── SKILL.md                           # Main workflow document
├── README.md                          # This file
│
├── references/                        # Reference documentation
│   ├── search-templates.md            # Search query templates
│   ├── top-ai-labs.md                 # Top AI labs list
│   ├── profile-schema.md              # Candidate profile structure
│   ├── candidate-classifier.md        # Classification rules
│   ├── chinese-surnames.md            # Chinese surname database
│   ├── deduplication-rules.md         # Deduplication rules
│   ├── email-templates.md             # Email templates (22 fields)
│   ├── field-mappings.md              # Research field mappings
│   ├── talk-tracks.md                 # Technical talk tracks
│   ├── python-scraping-guide.md       # Python scraping guide (NEW)
│   ├── url-priority-rules.md          # URL filtering rules (NEW)
│   └── anti-scraping-solutions.md     # Anti-scraping solutions (NEW)
│
└── scripts/                           # Reference scripts
    ├── README.md                      # Scripts usage guide
    ├── serper_search.py               # Serper API search
    ├── httpx_scraper.py               # Async HTTP scraper
    ├── cloudflare_email_decoder.py    # Cloudflare email decoder
    └── lab_member_scraper.py          # Lab member scraper
```

## Scraping Approach Comparison

| Aspect | BrightData MCP | Python Scraping |
|--------|---------------|-----------------|
| Cost | Paid (~$50+/month) | Free |
| LinkedIn Support | ✅ Yes | ❌ No |
| Academic Sites | ✅ Yes | ✅ Yes |
| Anti-Scraping | Auto-handled | Manual handling |
| Speed | Fast | Depends on implementation |

### When to Use Which

- **Use BrightData MCP**: LinkedIn profiles, Twitter, high-anti-scraping sites
- **Use Python Scraping**: Academic websites (.edu), personal homepages (.github.io)

## 22 Standardized Research Fields

1. RL (Reinforcement Learning)
2. NLP (Natural Language Processing)
3. Multimodal
4. MOE (Mixture of Experts)
5. Pre-training
6. Post-training
7. Alignment
8. Reasoning
9. Agent & RAG
10. MLSys (Machine Learning Systems)
11. LLM4Code
12. Computer Vision
13. Embodiment (Embodied AI)
14. Audio
15. EVAL (Evaluation)
16. Data
17. AI4S (AI for Science)
18. Interpretable AI
19. Recommendation System
20. Federated Learning
21. Trustworthy AI
22. Pre/Post-train × RL

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Talent Recruiter                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Generate Search Queries                             │
│      │                                                       │
│      ▼                                                       │
│  Step 2: Execute Searches (BrightData / Python)              │
│      │                                                       │
│      ▼                                                       │
│  Step 3: Scrape Profiles (BrightData / Python)               │
│      │                                                       │
│      ▼                                                       │
│  Step 4: Extract Profile Data                                │
│      │                                                       │
│      ▼                                                       │
│  Step 5: Identify Chinese Candidates                         │
│      │                                                       │
│      ▼                                                       │
│  Step 6: Classify Candidate Type                             │
│      │                                                       │
│      ▼                                                       │
│  Step 7: Deduplicate Candidates                              │
│      │                                                       │
│      ▼                                                       │
│  Step 8: Standardize Research Field                          │
│      │                                                       │
│      ▼                                                       │
│  Step 9: Generate Personalized Email                         │
│      │                                                       │
│      ▼                                                       │
│  Step 10: Present Results                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Version History

- **v2.0.0** (Current) - Added Python scraping support, 3 new reference docs, 4 reference scripts
- **v1.0.0** - Initial release with BrightData MCP support

## Contributing

To contribute to this skill:
1. Fork the repository
2. Make your changes
3. Submit a pull request

## License

MIT License - See LICENSE file for details.
