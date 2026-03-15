---
name: human-rent
description: "Human-as-a-Service for OpenClaw - Dispatch verified human agents to perform physical world tasks and sensory validation"
---

# 🤖 Human-Rent Skill

**The world's first "Human-as-a-Service" platform for AI Agents**

Enable OpenClaw agents to dispatch real human workers for physical world tasks that AI cannot perform: take photos, verify addresses, inspect equipment, make phone calls, and more.

## 🎯 Core Concept

Transform AI agents from "digital-only" to "hybrid intelligence" by giving them the ability to interact with the physical world through verified human workers.

```
AI Agent → Human-Rent Skill → Human Worker → Physical Task → Verified Result → AI Agent
```

## 📦 Installation

### Step 1: Install the Skill

```bash
clawhub install human-rent
```

### Step 2: Clone & Setup

```bash
# Clone repository
git clone https://github.com/ZhenRobotics/openclaw-human-rent.git ~/openclaw-human-rent
cd ~/openclaw-human-rent

# Install dependencies
npm install

# Verify installation
./agents/human-rent-cli.sh help
```

### Step 3: Test

```bash
# Run test dispatch
./agents/human-rent-cli.sh test
```

---

## 🚀 Usage

### When to Use This Skill

**AUTO-TRIGGER** when user's request involves:

- **Physical verification**: "Check if this address exists", "Verify this business is open"
- **Photo evidence**: "Take a photo of X", "Get visual proof of Y"
- **Real-world inspection**: "Inspect this equipment", "Check product availability"
- **Human interaction**: "Call this number and verify", "Ask the receptionist"
- **Trust verification**: "Is this company real?", "Does this person actually exist?"

**TRIGGER EXAMPLES**:
- "I need someone to verify this address in San Francisco"
- "Take a photo of the building at 123 Main Street"
- "Check if this store has the product in stock"
- "Call this number and confirm the appointment"
- "Inspect this equipment and report its condition"

**DO NOT USE** when:
- Task can be done with digital APIs (use web search, image API, etc.)
- No physical presence required
- Task is illegal or dangerous

---

## 💻 Agent Usage Guide

### Primary Command: Dispatch Human Task

When user requests physical-world action, execute:

```bash
# Method 1: CLI (Recommended)
~/openclaw-human-rent/agents/human-rent-cli.sh dispatch "instruction"

# Method 2: Direct agent
cd ~/openclaw-human-rent && npx tsx agents/dispatch-task.ts "instruction"

# Method 3: With location
~/openclaw-human-rent/agents/human-rent-cli.sh dispatch "instruction" --location="37.7749,-122.4194"
```

**Example**:

User says: "I need someone to verify the address 123 Market St in SF exists"

Execute:
```bash
~/openclaw-human-rent/agents/human-rent-cli.sh dispatch "Go to 123 Market Street, San Francisco and take a photo of the building entrance to verify it exists" --location="37.7749,-122.4194"
```

### Check Task Status

```bash
# Check status by task ID
~/openclaw-human-rent/agents/human-rent-cli.sh status <task_id>
```

### List Available Humans

```bash
# See available human workers
~/openclaw-human-rent/agents/human-rent-cli.sh humans
```

---

## 🎨 Task Types

### Layer 1: Instant Human (MVP - Currently Available)

| Type | Description | Latency | Cost |
|------|-------------|---------|------|
| `photo_verification` | Take a photo of something | 5-15 min | $10-20 |
| `address_verification` | Verify physical address exists | 10-20 min | $15-25 |
| `document_scan` | Scan a physical document | 10-20 min | $15-25 |
| `visual_inspection` | Detailed visual inspection | 15-30 min | $20-40 |
| `voice_verification` | Make a phone call and verify | 5-10 min | $10-20 |
| `purchase_verification` | Check product availability | 15-30 min | $20-40 |

### Layer 2: Expert on Call (Planned)

- Legal document review
- Medical image analysis
- Code audit
- Professional consultation

### Layer 3: Embodied Agent (Planned)

- Attend meetings
- Equipment installation
- Long-term physical monitoring

---

## 📊 Technical Architecture

### Async Function Calling Pattern

```typescript
// Agent calls human-rent skill
const task = await openclaw.skills.human_rent.dispatch({
  task_type: "photo_verification",
  location: "37.7749,-122.4194",
  instruction: "Take photo of building entrance",
  budget: "$15",
  timeout: "30min"
});

// Returns immediately with task ID
console.log(task.task_id); // "abc-123-def"
console.log(task.status); // "assigned"

// Agent continues other work (non-blocking)
await openclaw.doOtherStuff();

// Later, check status
const result = await openclaw.skills.human_rent.checkStatus(task.task_id);
if (result.status === "completed") {
  // Process human's result
  console.log(result.result.photos); // ["https://..."]
  console.log(result.result.notes); // Human's observations
}
```

### MCP Protocol Integration

This skill implements Model Context Protocol (MCP) extensions:

```json
{
  "name": "human-rent",
  "type": "physical_resource",
  "latency": "high",
  "cost_model": "per_task",
  "capabilities": [
    "visual_verification",
    "physical_manipulation",
    "social_interaction"
  ]
}
```

---

## 🎯 Strategic Value for OpenClaw

### 1. Capability Differentiation

**Problem**: All AI agents are limited to digital information
**Solution**: OpenClaw can verify physical reality

**Example Use Cases**:
- **Due Diligence**: Investor agent verifies company office exists before investment
- **E-commerce**: Purchasing agent inspects warehouse before bulk order
- **Security**: Safety agent verifies suspicious package before opening

### 2. Hybrid Intelligence Workflows

Enable "Human-in-the-Loop" automation:

```
Step 1: AI analysis (confidence: 85%)
Step 2: Human verification (if confidence < 90%)
Step 3: AI decision (based on verified data)
```

This makes OpenClaw agents **auditable** and **trustworthy** for regulated industries (finance, healthcare, legal).

### 3. New Revenue Model

- **Per-task fee**: $15-50/task
- **Platform fee**: 20% commission
- **Subscription**: $99/month for unlimited tasks

**Potential**: If 10K agents use 1 task/day at $15 → **$1M daily revenue** (20% = $200K to platform)

---

## 💰 Cost Estimation

| Task Type | Human Time | Human Cost | Platform Fee (20%) | Total Cost |
|-----------|-----------|-----------|-------------------|-----------|
| Quick photo | 10 min | $10 | $2 | $12 |
| Address verify | 20 min | $20 | $4 | $24 |
| Detailed inspect | 30 min | $30 | $6 | $36 |
| Expert consult | 60 min | $100 | $20 | $120 |

---

## 🔧 Configuration Options

### Task Requirements

```typescript
requirements: {
  minHumanRating: 4.5,  // Require highly rated workers
  requiredSkills: ['photography', 'legal_reading'],
  requiredEquipment: ['smartphone', 'tape_measure'],
  languageRequired: ['en', 'zh'],
  certificationRequired: ['driver_license']
}
```

### Verification Methods

- `automatic`: AI-based verification (fast, cheap)
- `cross_check`: Multiple humans verify same task (slower, more reliable)
- `manual_review`: Platform expert reviews (slowest, highest quality)
- `none`: Trust human worker (fastest, lowest cost)

---

## 📝 Usage Examples

### Example 1: Real Estate Investment

**Scenario**: AI agent analyzing potential property investment

```typescript
// Agent is uncertain about property condition
const task = await dispatch({
  task_type: "visual_inspection",
  location: "37.7749,-122.4194",
  instruction: "Inspect the property at 123 Main St. Check for: roof condition, foundation cracks, water damage, neighborhood safety. Take 10+ photos.",
  budget: "$50",
  timeout: "60min",
  requirements: {
    requiredSkills: ['property_inspection'],
    minHumanRating: 4.5
  }
});

// Agent continues analysis while waiting
await analyzeFinancials();
await checkLegalRecords();

// Retrieve human's findings
const result = await checkStatus(task.task_id);
// Use real-world data for final decision
```

### Example 2: Vendor Verification

**Scenario**: Procurement agent vetting new supplier

```bash
human-rent dispatch "Visit supplier's warehouse at 456 Industrial Rd. Verify: business license displayed, clean facilities, proper safety equipment, actual inventory matches claim. Interview manager if possible."
```

### Example 3: Emergency Response

**Scenario**: Security agent receives suspicious package alert

```bash
human-rent dispatch "URGENT: Suspicious package at office entrance. DO NOT TOUCH. Call building security (415-555-0123), evacuate area, wait for authorities. Take photos from safe distance." --priority=urgent --budget="$100"
```

---

## 🛠️ Troubleshooting

### Issue 1: No Humans Available

**Error**: "No suitable humans found for this task"

**Solutions**:
- Expand search radius (default: 5km)
- Increase budget to attract workers
- Reduce requirements (skills, rating, etc.)
- Try different time of day

### Issue 2: Task Timeout

**Error**: "Task timed out"

**Solutions**:
- Increase timeout (default: 30min)
- Check if location is accessible
- Verify task is clear and reasonable
- Increase budget for complex tasks

### Issue 3: Low Quality Results

**Solutions**:
- Require higher human rating (4.5+)
- Use cross-check verification
- Provide detailed instructions
- Require specific equipment

---

## 🌟 MVP Features (v0.1.0)

- ✅ Async task dispatch system
- ✅ Geographic matching (5 mock humans in SF)
- ✅ 6 task types supported
- ✅ Task status tracking
- ✅ Simulated human completion (for testing)
- ✅ MCP protocol interface
- ✅ CLI tools
- ✅ TypeScript type safety

---

## 🔮 Roadmap

### Phase 2: Automation (Next 3 months)
- [ ] Real geographic matching algorithm
- [ ] Stripe payment integration
- [ ] Webhook callbacks for async updates
- [ ] Cross-check verification
- [ ] Human mobile app (for workers)

### Phase 3: Scaling (6 months)
- [ ] Multi-city support (NY, LA, Beijing, London)
- [ ] Expert-on-call marketplace
- [ ] Blockchain result verification
- [ ] AR glasses for workers
- [ ] Integration with Uber/TaskRabbit APIs

### Phase 4: Intelligence (12 months)
- [ ] AI task routing optimization
- [ ] Predictive human availability
- [ ] Automated quality scoring
- [ ] Natural language task parsing
- [ ] Multi-human collaboration

---

## ⚠️ Important Notes

### Legal & Ethical

1. **Liability**: Human workers assume responsibility for their actions (contractor model)
2. **Privacy**: No PII collection without consent
3. **Safety**: Dangerous tasks are rejected automatically
4. **Labor Law**: Compliant with gig economy regulations
5. **Geographic**: Initially US-only (expand after legal review)

### Technical

1. **Latency**: This is a HIGH-LATENCY tool (minutes to hours)
2. **Cost**: Much more expensive than API calls
3. **Availability**: Geographic and time-dependent
4. **Reliability**: Human workers can fail/cancel tasks
5. **MVP Mode**: Currently using mock data for testing

---

## 🎯 Agent Behavior Guidelines

When using this skill, agents should:

**DO**:
- ✅ Use for tasks that REQUIRE physical presence
- ✅ Provide clear, specific instructions
- ✅ Set appropriate budgets (humans value their time)
- ✅ Handle async results (don't block waiting)
- ✅ Verify results before making decisions
- ✅ Respect human workers (polite instructions)

**DON'T**:
- ❌ Use for tasks that can be done digitally
- ❌ Request illegal or dangerous actions
- ❌ Expect instant results
- ❌ Underpay workers
- ❌ Share sensitive/private information unnecessarily
- ❌ Abuse the service with spam tasks

---

## 📚 API Reference

### `dispatchHuman(request)`

Dispatch a task to a human worker.

**Parameters**:
```typescript
{
  task_type: string,        // Type of task
  instruction: string,      // Clear instructions for human
  location?: string,        // "lat,lng" format
  budget?: string,          // "$15" format
  timeout?: string,         // "30min" format
  priority?: string,        // low|normal|high|urgent
  requirements?: object     // Skills, rating, equipment
}
```

**Returns**:
```typescript
{
  task_id: string,
  status: "assigned" | "failed",
  estimated_completion?: string,
  message: string
}
```

### `checkTaskStatus(taskId)`

Check status of a dispatched task.

**Returns**:
```typescript
{
  task_id: string,
  status: TaskStatus,
  result?: TaskResult,
  verification?: Verification,
  message: string
}
```

### `listAvailableHumans(location?, skills?)`

Get available human workers.

**Returns**:
```typescript
{
  statistics: { total, available, averageRating },
  available_humans: Human[]
}
```

---

## 📊 Tech Stack

- **TypeScript**: Type-safe development
- **Node.js**: Runtime environment
- **MCP**: Model Context Protocol
- **Express**: API server (planned)
- **Stripe**: Payment processing (planned)
- **Blockchain**: Result verification (planned)

---

## 🆕 Version History

### v0.1.0 - MVP Release (2026-03-07)
- ✨ Initial release with core functionality
- 🤖 Async task dispatch system
- 👥 Mock human pool (5 workers in SF)
- 📊 6 task types supported
- 🔧 CLI tools
- 📡 MCP protocol interface
- 🧪 Full testing simulation

---

**Project Status**: 🧪 MVP - Testing Phase

**License**: MIT

**Author**: @ZhenStaff

**Support**: https://github.com/ZhenRobotics/openclaw-human-rent/issues

**ClawHub**: https://clawhub.ai/ZhenStaff/human-rent

---

## 🚀 Quick Start Example

```bash
# 1. Install
git clone https://github.com/ZhenRobotics/openclaw-human-rent.git ~/openclaw-human-rent
cd ~/openclaw-human-rent && npm install

# 2. Test
./agents/human-rent-cli.sh test

# 3. Dispatch real task
./agents/human-rent-cli.sh dispatch "Take a photo of the Golden Gate Bridge"

# 4. Check status
./agents/human-rent-cli.sh status <task_id>

# 5. List humans
./agents/human-rent-cli.sh humans
```

---

**Make AI agents that can touch the physical world.** 🌍🤖✨
