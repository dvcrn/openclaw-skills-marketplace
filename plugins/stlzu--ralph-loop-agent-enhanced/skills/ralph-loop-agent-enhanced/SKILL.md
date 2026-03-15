---
name: ralph-loop-agent-enhanced
description: "Ralph Loop Agent (Enhanced)"
---

---
name: ralph-loop-agent
description: Ralph Loop Agent for iterative task execution and automation loops in OpenClaw. Provides loop-based agent capabilities for repetitive tasks, data processing, and automated workflows.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["node", "npm"] },
        "install": []
      }
  }

# Ralph Loop Agent

An agent-based skill that provides loop functionality for iterative task execution, automation workflows, and repetitive data processing within OpenClaw.

## Features

- **Loop Execution**: Run tasks in controlled loops with configurable iterations
- **Conditional Loops**: Execute until conditions are met
- **Data Processing**: Process arrays, lists, and datasets iteratively
- **Workflow Automation**: Create automated sequences of tasks
- **Error Handling**: Robust error handling and recovery mechanisms

## Usage Examples

### Basic Loop
```
Loop 5 times:
- Task 1
- Task 2
- Task 3
```

### Conditional Loop
```
While condition is true:
- Check status
- Process data
- Update records
```

### Data Processing Loop
```
For each item in dataset:
- Validate item
- Transform data
- Save results
```

## Configuration

The skill integrates directly with OpenClaw's agent system and doesn't require additional configuration beyond installation.

## Integration

Once installed, you can use Ralph Loop commands in your conversations:

- "Create a loop that processes my email inbox"
- "Set up an automated workflow for data cleaning"
- "Run this task 10 times with different parameters"