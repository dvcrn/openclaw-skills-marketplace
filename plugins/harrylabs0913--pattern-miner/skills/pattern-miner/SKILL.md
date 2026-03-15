---
name: pattern-miner
description: "Pattern Miner"
---

# pattern-miner Skill

Intelligent pattern recognition and actionable insights from multi-source data.

## Description

The `pattern-miner` skill discovers hidden patterns in your workflow data (conversations, decisions, tasks) using machine learning techniques. It identifies recurring themes, associations, and anomalies, then generates actionable insights to improve productivity and decision-making.

## Installation

```bash
cd ~/.openclaw/workspace/skills/pattern-miner
npm install
npm run build
```

### Python Dependencies

```bash
pip install numpy scikit-learn pandas tree-sitter
```

## Usage

### CLI Commands

```bash
# Run pattern mining
pattern-miner mine

# Incremental mining (only new data)
pattern-miner mine --incremental

# List discovered patterns
pattern-miner list
pattern-miner list --type cluster
pattern-miner list --verbose

# Analyze specific patterns/insights
pattern-miner analyze
pattern-miner analyze --pattern <id>
pattern-miner analyze --insight <id>
pattern-miner analyze --category optimization

# Apply insights
pattern-miner apply --confirm
pattern-miner apply --insight <id> --confirm
pattern-miner apply --category automation --dry-run

# Show statistics
pattern-miner stats

# Export patterns
pattern-miner export --format json --output patterns.json
pattern-miner export --format csv --output patterns.csv

# Configuration
pattern-miner config --show
pattern-miner config --init
```

### Node.js API

```typescript
import { PatternMiner } from '@openclaw/skill-pattern-miner';

const miner = new PatternMiner({
  minConfidence: 0.7,
  minFrequency: 5,
  analysisTypes: ['cluster', 'association', 'anomaly']
});

await miner.initialize();

// Run mining
const results = await miner.mine();
console.log(`Found ${results.summary.totalPatterns} patterns`);
console.log(`Generated ${results.summary.totalInsights} insights`);

// List patterns
const patterns = await miner.listPatterns();
const clusterPatterns = await miner.listPatterns('cluster', 10);

// List insights
const insights = await miner.listInsights(undefined, true); // pending only

// Get stats
const stats = await miner.getStats();

// Apply insight
await miner.applyInsight('insight_123');

// Export
const json = await miner.exportPatterns('json');
const csv = await miner.exportPatterns('csv');
```

## Core Features

### Multi-Source Data Collection

Automatically collects data from:
- **Conversations**: Session logs from `context-preserver`
- **Decisions**: Decision records from `decision-recorder`
- **Tasks**: Task files in workspace (JSON, Markdown)
- **Files**: Any file patterns you configure

### Intelligent Pattern Recognition

Three analysis types:

1. **Clustering** (`cluster`)
   - Groups similar items using KMeans
   - Identifies recurring themes and topics
   - TF-IDF vectorization for text similarity

2. **Association Rules** (`association`)
   - Finds items that frequently occur together
   - Calculates confidence and support metrics
   - Discovers hidden relationships

3. **Anomaly Detection** (`anomaly`)
   - Identifies outliers using Local Outlier Factor
   - Flags unusual patterns for review
   - Helps catch edge cases and issues

### Pattern Scoring System

Each pattern is scored on:
- **Confidence**: How reliable the pattern is (0-1)
- **Frequency**: How often the pattern appears
- **Importance**: Composite score based on:
  - Pattern confidence
  - Frequency normalized to max
  - Item priority metadata

### Actionable Insights

Generated insights include:
- **Title**: Clear description of the finding
- **Description**: Context and metrics
- **Action**: Specific recommendation
- **Priority**: high/medium/low
- **Expected Impact**: Estimated value (0-1)
- **Category**: optimization/automation/risk

## Configuration

Default config is stored at `~/.pattern-miner/config.json`:

```json
{
  "dataDir": "~/.openclaw/workspace",
  "patternDir": "~/.pattern-miner",
  "minConfidence": 0.6,
  "minFrequency": 3,
  "analysisTypes": ["cluster", "association", "anomaly"],
  "sources": [
    {
      "type": "conversation",
      "name": "conversations",
      "path": "~/.openclaw/sessions",
      "pattern": "**/*.json"
    }
  ],
  "autoScan": false,
  "scanInterval": 60,
  "maxPatterns": 1000,
  "retentionDays": 30
}
```

## Data Storage

Patterns and insights are stored in `~/.pattern-miner/`:
- `patterns.json` - Discovered patterns
- `insights.json` - Generated insights
- `config.json` - Configuration

## Integration

### With context-preserver

The skill automatically reads conversation logs if `context-preserver` is installed:

```json
{
  "sources": [
    {
      "type": "conversation",
      "name": "sessions",
      "path": "~/.openclaw/sessions",
      "pattern": "**/*.json"
    }
  ]
}
```

### With decision-recorder

Integrates with decision logs:

```json
{
  "sources": [
    {
      "type": "decision",
      "name": "decisions",
      "path": "~/.openclaw/decisions",
      "pattern": "**/*.json"
    }
  ]
}
```

## Scheduled Mining

For automatic periodic scanning, add to your crontab:

```bash
# Run pattern mining every hour
0 * * * * cd ~/.openclaw/workspace/skills/pattern-miner && pattern-miner mine --incremental
```

Or enable auto-scan in config:

```json
{
  "autoScan": true,
  "scanInterval": 60
}
```

## Output Examples

### Pattern Output

```json
{
  "id": "cluster_0_1710234567",
  "type": "cluster",
  "items": ["...", "..."],
  "confidence": 0.85,
  "frequency": 12,
  "importance": 0.78,
  "metadata": { "centroid": [...] },
  "createdAt": "2024-03-12T09:00:00Z",
  "source": "clustering"
}
```

### Insight Output

```json
{
  "id": "insight_cluster_0_1710234567",
  "patternId": "cluster_0_1710234567",
  "title": "Recurring Pattern: Code review feedback...",
  "description": "Found 12 similar items forming a pattern",
  "action": "Review and standardize this pattern",
  "priority": "high",
  "expectedImpact": 0.7,
  "category": "optimization"
}
```

## Troubleshooting

### Python not found

Ensure Python 3.8+ is installed and in PATH:
```bash
python3 --version
```

### No patterns found

- Check that data sources are configured correctly
- Ensure there's enough data (minFrequency defaults to 3)
- Try running with `--verbose` to see collection details

### Low confidence scores

- Increase data volume
- Adjust `minConfidence` in config
- Check data quality and consistency

## Technical Details

### Algorithms

- **Clustering**: KMeans with TF-IDF features
- **Association**: Apriori-style rule mining
- **Anomaly**: Local Outlier Factor (LOF)

### Performance

- Incremental scanning for large datasets
- Configurable pattern retention (default 30 days)
- Max pattern limit (default 1000)

## License

MIT
