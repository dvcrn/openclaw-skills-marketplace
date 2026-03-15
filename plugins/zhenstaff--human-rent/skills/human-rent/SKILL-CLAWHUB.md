---
name: human-rent
display_name: Human-Rent
version: 0.1.0
author: ZhenStaff
category: integration
subcategory: physical-world
license: MIT
description: Human-as-a-Service for OpenClaw - Dispatch verified human agents to perform physical world tasks and sensory validation
tags: [human-as-a-service, physical-verification, mcp, ai-agent, async-function-calling, hybrid-intelligence, human-in-the-loop]
repository: https://github.com/ZhenRobotics/openclaw-human-rent
homepage: https://github.com/ZhenRobotics/openclaw-human-rent
documentation: https://github.com/ZhenRobotics/openclaw-human-rent/blob/main/README.md
icon: https://raw.githubusercontent.com/ZhenRobotics/openclaw-human-rent/main/docs/icon.png
---

# Human-Rent

**The World's First Human-as-a-Service Platform for AI Agents**

Transform your AI agents from "digital-only" to "hybrid intelligence" by enabling them to dispatch real human workers for physical world tasks.

## 🎯 What It Does

Human-Rent bridges the gap between digital AI and physical reality. When your AI agent needs something done in the real world—verify an address, inspect equipment, take a photo—it dispatches a verified human worker to handle it.

```
AI Agent → Human-Rent → Human Worker → Physical Task → Verified Result → AI Agent
```

**Key Innovation**: Async function calling for human operations

## ✨ Key Features

- 🌍 **Physical World Access** - AI agents can interact with real environments
- ⚡ **Async Task Dispatch** - Non-blocking, minutes-to-hours completion
- 🎯 **Geographic Matching** - Automatically finds nearby human workers
- 🔐 **Multi-layer Verification** - AI + cross-check + manual review
- 💰 **Pay-per-Task** - $15-50 per task, only pay on completion
- 🤖 **MCP Protocol** - Native OpenClaw integration

## 📦 Installation

### Prerequisites

- Node.js >= 18.0.0
- npm >= 8.0.0
- OpenClaw >= 1.0.0

### Install via ClawHub

```bash
clawhub install human-rent
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/ZhenRobotics/openclaw-human-rent.git ~/openclaw-human-rent

# Install dependencies
cd ~/openclaw-human-rent
npm install

# Verify installation
./agents/human-rent-cli.sh help
```

### Test Installation

```bash
# Run complete test
./agents/human-rent-cli.sh test

# Check available humans
./agents/human-rent-cli.sh humans
```

Expected output: 5 available workers in San Francisco

## 🚀 Quick Start

### Basic Usage

```bash
# Dispatch a simple task
human-rent dispatch "Take a photo of 123 Main Street"

# Check task status
human-rent status <task_id>

# List available humans
human-rent humans
```

### Agent Integration

When your OpenClaw agent detects a physical task need:

```bash
# Example: User asks to verify an address
~/openclaw-human-rent/agents/human-rent-cli.sh dispatch "Verify that 123 Market Street, SF exists. Take photo of building entrance."
```

## 📋 Task Types

| Type | Use Case | Latency | Cost |
|------|----------|---------|------|
| `photo_verification` | Take photos | 5-15 min | $10-20 |
| `address_verification` | Verify addresses | 10-20 min | $15-25 |
| `document_scan` | Scan documents | 10-20 min | $15-25 |
| `visual_inspection` | Detailed inspection | 15-30 min | $20-40 |
| `voice_verification` | Phone calls | 5-10 min | $10-20 |
| `purchase_verification` | Check availability | 15-30 min | $20-40 |

## 💡 Use Cases

### 1. Investment Due Diligence

**Scenario**: AI agent evaluating $1M investment

```bash
human-rent dispatch "Visit company office at 456 Oak Ave. Verify: business operations active, company signage visible, professional environment. Take 5+ photos."
```

**Value**: $75 saves hours of manual work, prevents bad investments

### 2. E-commerce Quality Control

**Scenario**: AI purchasing agent considering $50K bulk order

```bash
human-rent dispatch "Inspect supplier warehouse at 789 Industrial Pkwy. Check: storage conditions, inventory levels, product samples. Take detailed photos."
```

**Value**: $140 protects $50K order (357:1 ROI)

### 3. Fraud Detection

**Scenario**: AI fraud detector checking business legitimacy

```bash
human-rent dispatch "Verify business at 321 Pine St. Check: signage, active operations, matches registration. Take photos."
```

**Value**: $20 prevents thousands in fraud losses

### 4. Regulatory Compliance

**Scenario**: AI compliance agent conducting audit

```bash
human-rent dispatch "Conduct on-site safety inspection. Verify: licenses displayed, safety equipment present, compliance documentation. Document findings."
```

**Value**: $50 ensures regulatory compliance

## 🔧 Advanced Configuration

### Custom Requirements

```bash
# Require specific skills
human-rent dispatch "Inspect electrical panel" --requirements='{"requiredSkills":["electrical_inspection"],"minHumanRating":4.5}'

# Set location and timeout
human-rent dispatch "Take photo" --location="37.7749,-122.4194" --timeout="60min"

# Priority task
human-rent dispatch "Urgent verification" --priority=urgent --budget="$50"
```

### Programmatic Usage

```typescript
import MCPServer from 'openclaw-human-rent';

const server = new MCPServer();

// Dispatch task
const response = await server.dispatchHuman({
  task_type: 'photo_verification',
  location: '37.7749,-122.4194',
  instruction: 'Take photo of building',
  budget: '$15',
  timeout: '30min'
});

// Check status later (async)
const status = await server.checkTaskStatus(response.task_id);
console.log(status.result);
```

## 📊 Agent Behavior Guidelines

### When to Use

✅ **DO USE** when:
- Physical presence required
- Real-world verification needed
- High-stakes decisions need validation
- Digital APIs insufficient

❌ **DON'T USE** when:
- Task can be done digitally (APIs, web search)
- No physical component
- Illegal or dangerous
- Privacy concerns

### Auto-trigger Keywords

Agent should trigger Human-Rent when detecting:
- "verify address"
- "check in person"
- "take a photo"
- "inspect physically"
- "go to location"
- "confirm on-site"

### Response Pattern

```
User: "I need to verify this address exists"
Agent:
  1. Detect physical task need
  2. Dispatch human-rent task
  3. Return task ID to user
  4. Continue other work (non-blocking)
  5. Check status later
  6. Return verified results
```

## 🎯 Verification System

### Three Layers

1. **Automatic (AI)** - Fast, free
   - Photo quality check
   - GPS verification
   - Timestamp validation

2. **Cross-check (Multiple Humans)** - Slower, reliable
   - 3 humans verify same task
   - Majority decision
   - Agreement score

3. **Manual Review (Expert)** - Slowest, highest quality
   - Platform expert reviews
   - Final decision
   - Detailed notes

## 💰 Pricing

### Task Pricing

- **Quick photo**: $10-15 (5-10 min)
- **Address verify**: $15-25 (10-20 min)
- **Inspection**: $25-40 (20-30 min)
- **Expert task**: $40-100+ (30-60 min)

### Business Model

- Platform fee: 20%
- Human worker: 80%
- Only charged on completion

### Cost-Benefit Examples

| Scenario | Human-Rent | Traditional | Savings |
|----------|-----------|-------------|---------|
| Due diligence | $75 | $500-1000 | 85-93% |
| Warehouse audit | $140 | $1000-2000 | 86-93% |
| Address check | $20 | $100-200 | 80-90% |

## 🛠️ Troubleshooting

### Issue: No Humans Available

**Error**: "No suitable humans found for this task"

**Solutions**:
- Expand search radius (default: 5km)
- Increase budget to attract workers
- Try different time of day
- Reduce requirements (skills, rating)

### Issue: Task Timeout

**Error**: "Task timed out"

**Solutions**:
- Increase timeout (default: 30min)
- Verify location is accessible
- Simplify task instructions
- Check if task is reasonable

### Issue: Low Quality Results

**Solutions**:
- Require higher human rating (4.5+)
- Use cross-check verification
- Provide clearer instructions
- Require specific equipment

## 📚 Documentation

### Complete Guides

- **[README](https://github.com/ZhenRobotics/openclaw-human-rent/blob/main/README.md)** - Full project overview
- **[QUICKSTART](https://github.com/ZhenRobotics/openclaw-human-rent/blob/main/QUICKSTART.md)** - 5-minute guide
- **[Examples](https://github.com/ZhenRobotics/openclaw-human-rent/tree/main/examples)** - Code examples
- **[API](https://github.com/ZhenRobotics/openclaw-human-rent/blob/main/openclaw-skill/SKILL.md)** - Complete API docs

### Support

- **GitHub Issues**: https://github.com/ZhenRobotics/openclaw-human-rent/issues
- **Discussions**: https://github.com/ZhenRobotics/openclaw-human-rent/discussions
- **Email**: support@human-rent.com (coming soon)

## 🔄 Roadmap

### Phase 2: Automation (Next 3 months)
- Real human workers in SF, NYC, LA
- Stripe payment integration
- Mobile app for workers
- Webhook callbacks

### Phase 3: Scaling (6 months)
- 10+ cities globally
- Expert marketplace
- Blockchain verification
- Enterprise features

### Phase 4: Intelligence (12 months)
- AI-powered routing
- Natural language parsing
- Multi-human collaboration
- Industry leadership

Full roadmap: [ROADMAP.md](https://github.com/ZhenRobotics/openclaw-human-rent/blob/main/ROADMAP.md)

## ⚠️ Important Notes

### Current Status

- **MVP**: Using mock data (5 simulated workers in SF)
- **Beta**: Real human recruitment starts next month
- **Geography**: Currently SF only, expanding soon

### Legal & Ethics

- Workers are independent contractors
- Platform provides marketplace only
- Workers assume liability
- Currently US-only
- GDPR/CCPA compliant architecture

### Limitations

- **High latency**: Minutes to hours (not milliseconds)
- **Geographic**: Limited to worker availability
- **Cost**: Higher than API calls
- **Reliability**: Humans can cancel/fail

## 🤝 Contributing

We welcome contributions!

- **Code**: Submit PRs for features/fixes
- **Documentation**: Improve guides
- **Examples**: Share use cases
- **Workers**: Join as human worker (SF)
- **Feedback**: Report issues, suggest features

See [CONTRIBUTING.md](https://github.com/ZhenRobotics/openclaw-human-rent/blob/main/CONTRIBUTING.md)

## 📄 License

MIT License - See [LICENSE](https://github.com/ZhenRobotics/openclaw-human-rent/blob/main/LICENSE)

## 🌟 Why Human-Rent?

### Unique Value

- **First mover**: Only Human-as-a-Service for AI
- **Network effects**: More humans = more value
- **Technical moat**: MCP protocol integration
- **Clear economics**: Proven gig economy model
- **Physical access**: What AI agents need most

### Competitive Advantage

| Feature | AutoGPT | MetaGPT | Devin | **Human-Rent** |
|---------|---------|---------|-------|----------------|
| Code Gen | ✅ | ✅ | ✅ | N/A |
| Web Search | ✅ | ✅ | ✅ | ✅ |
| **Physical Tasks** | ❌ | ❌ | ❌ | **✅** |
| **Human Verify** | ❌ | ❌ | ❌ | **✅** |

## 🎊 Get Started

```bash
# Install
clawhub install human-rent

# Test
human-rent test

# Dispatch your first task
human-rent dispatch "Take a photo of the Golden Gate Bridge"
```

---

**Build hybrid intelligence. Give your AI hands.** 🤖🤝👨‍🔧

**Repository**: https://github.com/ZhenRobotics/openclaw-human-rent

**Version**: 0.1.0 | **License**: MIT | **Author**: @ZhenStaff
