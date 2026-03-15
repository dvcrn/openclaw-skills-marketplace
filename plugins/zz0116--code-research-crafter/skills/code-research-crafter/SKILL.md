---
name: code-research-crafter
description: "A complete 6-phase workflow for researching codebases, designing enhancement proposals, and publishing RFCs to GitHub. Covers code analysis, academic research, solution design, documentation generation, and RFC publication."
---

# Code Research Crafter

Craft comprehensive research proposals from code analysis to GitHub RFC publication.

## Overview

This skill provides a complete 6-phase workflow for deep codebase research and professional proposal crafting:

1. **Code Analysis** - Understanding existing implementation through systematic exploration
2. **Academic Research** - Finding relevant papers, algorithms, and prior art
3. **Community Analysis** - Reviewing GitHub issues, discussions, and maintainer feedback
4. **Solution Design** - Architecture design with data models and phased implementation plans
5. **Documentation** - Generating structured technical documents (Chinese/English)
6. **RFC Publication** - Writing and submitting professional RFCs to GitHub

## When to Use

Use this skill when you need to:
- Analyze an open-source codebase and propose enhancements
- Research technical problems with academic rigor
- Design system architectures with evidence-based decisions
- Create professional RFCs for open-source communities
- Document complex technical proposals with proper citations

## Workflow

### Phase 1: Problem Discovery & Code Analysis

**Step 1: Identify the target area**
- Search for relevant files in the codebase using glob patterns
- Look for GitHub issues related to the topic
- Check existing documentation (docs/, README, etc.)

**Step 2: Deep code analysis**
```bash
# Find relevant source files
glob **/[module]*/**/*.ts
glob **/[component]*.ts

# Read key implementation files
read src/[module]/[key-file].ts

# Search for specific patterns
grep "[pattern]" src/**/*.ts
```

**Step 3: Document findings**
- Note current architecture limitations
- Identify specific code locations and their roles
- Quantify problems (e.g., "50% of files lack documentation")

### Phase 2: Academic & Community Research

**Step 1: Search for academic papers**
- Use WebSearch to find relevant research papers
- Focus on papers from 2024-2025
- Look for algorithms, data structures, and approaches

**Step 2: Analyze GitHub community**
- Search for related issues and discussions
- Check maintainer responses and feedback
- Identify pain points from user comments

**Step 3: Extract key insights**
- Document relevant algorithms and approaches
- Note community sentiment and feature requests
- Identify gaps between current implementation and best practices

### Phase 3: Solution Design

**Step 1: Define design principles**
- Evidence-based: Reference specific code locations
- Academic rigor: Cite recent papers
- Human-centered: Use organization analogies
- Cost-aware: Track token/performance implications

**Step 2: Architect the solution**
- Design layered architecture (Foundation → Enhancement → Intelligence → Governance)
- Define data models (dual-track: user-defined + system-learned)
- Plan visibility tiers (private/team/global)

**Step 3: Plan implementation phases**
- Phase 1: Foundation (data collection)
- Phase 2: Enhancement (builds on Phase 1)
- Phase 3: Intelligence (AI/ML on data)
- Phase 4: Governance (control/monitoring)

### Phase 4: Documentation Generation

**Step 1: Create structured documents**
- Use python-docx for professional formatting
- Include table of contents, headers, and proper structure
- Add citations and references

**Step 2: Generate bilingual versions**
- Create English version for international communities
- Create Chinese version for local stakeholders
- Ensure consistent terminology

### Phase 5: English RFC Writing

**Step 1: Structure the RFC**
```markdown
# RFC: [Title]

## Problem Statement
[Quantified problem with code evidence]

## Prior Art
[Academic research and existing solutions]

## Proposed Solution
[Architecture, data models, implementation phases]

## Trade-offs
[Cost analysis, migration path, risks]

## Call for Collaboration
[How to get involved]
```

**Step 2: Follow community conventions**
- Use existing RFCs as templates
- Reference GitHub issues and discussions
- Include code examples and diagrams

### Phase 6: GitHub Publication

**Step 1: Prepare the RFC**
- Create markdown file in appropriate location
- Ensure proper formatting and links
- Add relevant labels

**Step 2: Submit to GitHub**
- Create issue or discussion with RFC content
- Reference related issues
- Tag relevant maintainers

**Step 3: Engage the community**
- Respond to comments and questions
- Update RFC based on feedback
- Track implementation progress

## Output Examples

### Memory Consolidation RFC
Combines Zettelkasten + PPR + Sleep Consolidation approaches for knowledge management.

### Multi-Agent Collaboration RFC
Features Capability Profiling and Shared Blackboard architecture for agent coordination.

### Temporal Decay Bug Fixes
Expands date pattern recognition in configuration interfaces.

## Best Practices

1. **Quote specific code locations** - Always reference file paths and line numbers
2. **Quantify problems** - Use metrics like "50% of files" or "3x performance improvement"
3. **Cite recent research** - Prefer papers from 2024-2025
4. **Use analogies** - Make complex concepts accessible with organization/workflow analogies
5. **Design for adoption** - Include migration paths and gradual rollout plans
6. **Track costs** - Document token usage, performance implications, and resource requirements
7. **Engage early** - Reference existing issues and invite collaboration from the start

## Success Metrics

A successful Code Research Crafter output should:
- ✅ Receive community engagement (comments, reactions)
- ✅ Quantify problems with code evidence
- ✅ Reference academic research
- ✅ Provide phased, actionable implementation plans
- ✅ Be clear for all audiences (technical and non-technical)

## Tools & Resources

- **Code Analysis**: `glob`, `grep`, `read`
- **Academic Research**: `WebSearch`, `WebFetch`
- **Documentation**: `python-docx` for professional document generation
- **Publication**: `browser_use_desktop` for GitHub submission
- **Version Control**: `desktop_terminal_execute` for Git operations

## License

MIT License - See LICENSE.txt for details.
