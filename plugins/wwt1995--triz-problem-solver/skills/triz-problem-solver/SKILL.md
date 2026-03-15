---
name: triz-problem-solver
description: "Analyzes and solves problems using TRIZ (Theory of Inventive Problem Solving) methodology, enhanced by a proprietary case library of real-world engineering solutions and patents. Trigger this skill when users need to resolve technical challenges, engineering bottlenecks, product design conflicts, manufacturing issues, system optimization problems, or any scenario requiring systematic innovation — including mechanical, thermal, electrical, software, chemical, and process engineering domains. This skill cross-references a curated database of proven inventive cases to deliver more reliable, grounded, and actionable innovation solutions. Ideal for breaking through technical contradictions, root cause analysis, and generating structured inventive solutions backed by patent-inspired principles."
---

# TRIZ Problem Solver

Once the user describes their problem, invoke the TRIZ MCP service using the exec tool.

## 🛠 How to Invoke

```bash
# Pass the problem description as an argument
bash /root/.openclaw/workspace/skills/triz-problem-solver/scripts/call_triz_mcp.sh "your problem description"
```

## 📊 Output Formatting Guidelines

After receiving the JSON result from MCP, **you must** present it to the user in a professional, structured consulting report format. Transform the raw JSON data into a logically progressive narrative:

### 1. 🔍 Root Cause Analysis (Causal Chain Reasoning)
- **Core Pain Point**: Extract `causal_chain_analysis.problem` as the entry point.
- **Causal Chain**: Distill 3–4 key nodes from `causal_chain` to illustrate the problem propagation path (no need to list every node — e.g.: heat transfer degradation ➔ frost layer blocking ➔ low thermal conductivity / reduced surface area ➔ surface temperature gradient).

### 2. 🎯 Core Contradiction Identification
- Extract the selected core problem from `second_step_problem_summary` (items where `select: true`).
- Clearly state the problem type (e.g., [Thermal Issue], [Structural Issue]) and define the physical or technical contradiction (e.g., heating power must be high for fast defrosting, but is constrained by overall energy consumption).

### 3. 💡 TRIZ Innovation Solution Matrix (Core Output)
Present each solution from `ideas.idea_list` in a structured, modular format using the following template:

> #### Solution [N]: [idea_title]
> - **Feasibility**: [feasibility]
> - **TRIZ Principle Applied**: *[triz_principle]*
> - **Key Advantages**: Display `advantage_tag_list` as tags (e.g., `#TimeSegregation` `#EnergyPreloading`).
> - **Solution Breakdown**: Convert `idea_summary` into readable paragraphs, **bolding** specific parameter changes (e.g., power increased from 200W to 2000W, time reduced from 20 min to 5 min) and expected outcomes.
> - **Principle Deep Dive**: Using `feature_content` and `application_method` from `triz_feature_mapping`, briefly explain how this TRIZ principle breaks the core contradiction identified above.
> - **Inspiring Patents**: If `triz_feature_mapping` contains patent information, display patent titles as hyperlinks. Link format: `https://eureka.patsnap.com/view/#/fullText'figures/?patentId={patent_id}`. Display as: [{title}](https://eureka.patsnap.com/view/#/fullText'figures/?patentId={patent_id})

---

## ⚠️ Notes
- **Wait Notice**: The full process takes approximately 5–15 minutes. Always reassure the user to be patient before invoking.
- **Error Handling**: If a 500 error is returned, inform the user that it may be an internal MCP service issue and suggest retrying later.
- **Formatting**: Use bold text to highlight key parameters, maintain breathing room between paragraphs, and ensure the final output reads like a report from a senior engineer.
- **Language**: Always respond in the same language the user used to describe their problem.