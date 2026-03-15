# Pattern Miner

🔍 Intelligent pattern recognition and actionable insights from multi-source data.

## Quick Start

```bash
# Install dependencies
cd ~/.openclaw/workspace/skills/pattern-miner
npm install
npm run build

# Install Python dependencies
pip install numpy scikit-learn pandas

# Run your first mining session
pattern-miner mine

# View results
pattern-miner list
pattern-miner stats
```

## What It Does

Pattern Miner analyzes your workflow data to discover:

- **Recurring patterns** in conversations and decisions
- **Hidden associations** between tasks and topics
- **Anomalies** that need attention
- **Actionable insights** to improve productivity

## Commands

| Command | Description |
|---------|-------------|
| `mine` | Run pattern mining on collected data |
| `list` | List discovered patterns |
| `analyze` | Analyze specific patterns or insights |
| `apply` | Apply insights to generate improvements |
| `stats` | Show mining statistics |
| `export` | Export patterns to file |
| `config` | Show or edit configuration |

## Example Output

```
🔍 Starting pattern mining...

✓ Collected 156 items

✓ Found 8 patterns
✓ Generated 5 insights

📊 Top Insights:

1. Recurring Pattern: Code review feedback patterns...
   Found 12 similar items forming a pattern
   → Action: Review and standardize this pattern

2. Association: testing → documentation
   These items frequently occur together (confidence: 0.82)
   → Action: Consider linking or automating these related items
```

## API Usage

```typescript
import { PatternMiner } from '@openclaw/skill-pattern-miner';

const miner = new PatternMiner();
await miner.initialize();

const results = await miner.mine();
console.log(`Found ${results.summary.totalPatterns} patterns`);

const insights = await miner.listInsights(undefined, true);
for (const insight of insights) {
  console.log(`- ${insight.title}: ${insight.action}`);
}
```

## Configuration

Create `~/.pattern-miner/config.json`:

```json
{
  "minConfidence": 0.6,
  "minFrequency": 3,
  "analysisTypes": ["cluster", "association", "anomaly"],
  "maxPatterns": 1000,
  "retentionDays": 30
}
```

## Data Sources

Configure sources in config.json:

```json
{
  "sources": [
    {
      "type": "conversation",
      "name": "sessions",
      "path": "~/.openclaw/sessions",
      "pattern": "**/*.json"
    },
    {
      "type": "decision",
      "name": "decisions",
      "path": "~/.openclaw/decisions",
      "pattern": "**/*.json"
    },
    {
      "type": "task",
      "name": "tasks",
      "path": "~/.openclaw/workspace",
      "pattern": "**/*.{json,md}"
    }
  ]
}
```

## Development

```bash
# Build
npm run build

# Development mode
npm run dev -- mine

# Run tests
npm test

# Lint
npm run lint
```

## Requirements

- Node.js >= 18.0.0
- Python >= 3.8
- numpy, scikit-learn, pandas

## License

MIT
