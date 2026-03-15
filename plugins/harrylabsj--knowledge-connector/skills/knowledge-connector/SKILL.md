---
name: knowledge-connector
description: "Extract concepts from documents, notes, and conversations; connect them into a knowledge graph; support relationship-aware queries, recommendations, and graph export. Use when the user wants to build structured knowledge from source material, connect concepts, inspect related ideas, or visualize a knowledge map."
---

# Knowledge Connector

Build a lightweight knowledge graph from documents and conversations.

## Core capabilities

- Extract concepts and entities from text
- Create relationships between concepts
- Store and query a knowledge graph
- Recommend related concepts
- Export graph views for inspection

## Commands

### Extract knowledge

```bash
kc extract -f document.txt
kc extract -t "Artificial intelligence is a branch of computer science"
kc extract -f document.txt --save
```

### Create or import connections

```bash
kc connect --auto
kc connect --from "Artificial Intelligence" --to "Machine Learning" --relation "includes"
kc connect --file relations.json
```

### Query knowledge

```bash
kc query "Artificial Intelligence"
kc query --concept "Deep Learning" --detail
kc query --concept "Neural Network" --related
kc query --ask "What is Machine Learning?"
```

### Visualize the graph

```bash
kc visualize
kc visualize --format html --output graph.html
kc visualize --format json --output graph.json
kc visualize --concept "Artificial Intelligence" --depth 2
```

### Manage the knowledge base

```bash
kc stats
kc export --output backup.json
kc import --file backup.json
kc clear --confirm
```

## Core data structures

### Concept

```json
{
  "id": "uuid",
  "name": "Artificial Intelligence",
  "type": "domain",
  "aliases": ["AI"],
  "description": "A branch of computer science",
  "source": "document.txt",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "metadata": {}
}
```

### Relation

```json
{
  "id": "uuid",
  "from": "concept-id-1",
  "to": "concept-id-2",
  "type": "includes",
  "weight": 0.85,
  "source": "auto-extract",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

## Common relation types

- `includes`
- `is-a`
- `related-to`
- `causes`
- `follows`
- `opposite`
- `similar`

## Configuration

Default config file:

```json
{
  "dataDir": "~/.local/share/knowledge-connector",
  "autoExtract": true,
  "autoConnect": true,
  "defaultDepth": 2,
  "maxResults": 20,
  "language": "en"
}
```

## Example workflow

```bash
# Extract and save
echo "Python is an interpreted programming language. Java is an object-oriented programming language." | kc extract --save

# Add relations
kc connect --from "Python" --to "Programming Language" --relation "is-a"
kc connect --from "Java" --to "Programming Language" --relation "is-a"

# Inspect graph
kc visualize --format html --output languages.html
kc query --concept "Python" --related
```

## Programmatic usage

```javascript
const KnowledgeConnector = require('knowledge-connector');
const kc = new KnowledgeConnector();

const concepts = await kc.extract('JavaScript is a dynamically typed language');
await kc.connect({ from: 'JavaScript', to: 'Dynamically Typed Language', type: 'is-a' });
const results = await kc.query('JavaScript');
const recommendations = await kc.recommend('JavaScript');
```

## Notes

- Create regular backups when the graph becomes important.
- Query performance may slow down as the graph grows.
- Concept names may be case-sensitive depending on implementation.

## License

MIT
