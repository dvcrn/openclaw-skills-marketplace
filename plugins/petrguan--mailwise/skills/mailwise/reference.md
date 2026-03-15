# MailWise Command Reference

## Installation

```bash
pip install git+https://github.com/PetrGuan/MailWise.git
```

After install, clone the repo for config files:
```bash
git clone https://github.com/PetrGuan/MailWise.git && cd MailWise
cp config.example.yaml config.yaml
```

Edit `config.yaml`:
```yaml
eml_directory: emails
database: data/index.db
markdown_directory: markdown
embedding_model: all-MiniLM-L6-v2
expert_boost: 1.5
experts:
  - email: engineer@company.com
    name: Jane Doe
```

Then index: `mailwise index`

## Command Output Formats

### mailwise search

```
1. [0.884] Bug title here
   By: Engineer Name [Expert]
   Date: Tuesday, March 10, 2026 4:27 PM
   Email ID: 52
   Preview: First 300 chars of matching message...
```

- Score in brackets [0.0 - 1.0] — higher is more similar
- `[Expert]` tag appears for configured expert engineers
- Email ID can be used with `mailwise show <ID>`

### mailwise analyze

Outputs a Claude-generated analysis including:
- Root cause pattern identification
- Debugging approaches used by experts
- Suggested next steps
- Cross-issue pattern recognition

### mailwise stats

```
  Indexed emails:     114
  Thread messages:    569
  Expert messages:    54
  Configured experts: 8

  Avg replies/thread: 5.0
  Expert coverage:    9.5% of messages
```

### mailwise show <ID>

Outputs the full markdown thread:
```markdown
# Subject line

**Date:** Wed, 27 Aug 2025
**Participants:** Engineer A, Engineer B, Engineer C

---

## Reply 1 -- Engineer A (addr@company.com)
**Date:** Wed, 27 Aug 2025

Message body...

---

## Reply 2 -- Engineer B (addr@company.com) **[Expert]**
**Date:** Tue, 26 Aug 2025

Expert analysis here...
```

## Tips for Agents

- Always try `search` first with `--show-body` to assess relevance before running `analyze`
- For `analyze`, pass as much context as possible — full bug reports work better than short titles
- When multiple similar results appear, use `show` on the highest-scored one to read the full expert thread
- If search returns no results, check `stats` to confirm emails are indexed
- Expert-only search (`--expert-only`) is useful when the user specifically wants senior engineer insights
