---
name: workspace-organizer
description: "Flexible workspace and task file organization system. Use when managing project files, organizing task inputs/outputs, structuring workspace directories, or when you need a systematic way to organize files for any type of task. This skill provides a methodology for creating timestamped task structures with workflow-based step decomposition, adaptable to any task type without preset constraints."
---

# Workspace Organizer

A flexible, extensible system for organizing workspace files based on task workflows, not fixed categories. Each task gets a unique structure derived from its actual requirements.

## Core Principles

1. **Task-first, not category-first**: No preset task types (document analysis, template extraction, etc.). Each task structure is unique.
2. **Timestamp + description naming**: `YYYY-MM-DD_TaskDescription` for clear chronological tracking.
3. **Workflow decomposition**: Analyze task requirements, break into logical steps, create corresponding subdirectories.
4. **Input/Output separation**: Clear distinction between source materials (`input/`) and generated artifacts (`output/`).
5. **Progressive refinement**: Structure evolves with task understanding; folders reflect actual work stages.

## Methodology

### 1. Task Analysis & Step Decomposition

Before creating directories:
- **Understand the task**: What's the end goal? What are the deliverables?
- **Identify natural phases**: What are the logical stages of work? (e.g., data collection → analysis → visualization → reporting)
- **Consider dependencies**: Which steps depend on others? What's the workflow sequence?
- **Keep it flexible**: Steps can be added, merged, or removed as task understanding deepens.

### 2. Directory Structure Design

```
workspace/
├── input/                            # Source materials
│   └── YYYY-MM-DD_TaskDescription/   # Task-specific inputs
├── output/                           # Generated artifacts
│   └── YYYY-MM-DD_TaskDescription/   # Task-specific outputs
│       ├── 01_StepOneDescription/    # Workflow step 1
│       ├── 02_StepTwoDescription/    # Workflow step 2
│       ├── 03_StepThreeDescription/  # Workflow step 3
│       └── (additional steps)        # As needed
└── (root config files)               # AGENTS.md, SOUL.md, etc.
```

### 3. Step Naming Convention

- **Numbered for sequence**: `01_`, `02_`, `03_` prefixes ensure chronological order
- **Descriptive, not generic**: "DataCollection" not "Step1"; "Analysis" not "Processing"
- **Verb-focused**: Use action-oriented names (Extract, Analyze, Transform, Visualize)
- **Consistent length**: Avoid mixing "Data_Cleaning" and "DataPreprocessingAndFeatureEngineering"

### 4. File Organization Logic

- **Input files**: Go to corresponding task folder in `input/`
- **Processing scripts**: Go to the step where they're primarily used
- **Intermediate results**: Go to the step that produced them
- **Final deliverables**: Go to the final step or a dedicated `Deliverables` folder
- **Cross-step utilities**: Consider a `shared/` or `utils/` folder at task level

## Implementation Process

### When Starting a New Task

1. **Create task folders**:
   ```bash
   mkdir -p input/YYYY-MM-DD_TaskDescription
   mkdir -p output/YYYY-MM-DD_TaskDescription
   ```

2. **Analyze and define steps**:
   - List required work phases
   - Assign descriptive names
   - Number sequentially

3. **Create step directories**:
   ```bash
   mkdir -p output/YYYY-MM-DD_TaskDescription/01_StepOne
   mkdir -p output/YYYY-MM-DD_TaskDescription/02_StepTwo
   # etc.
   ```

4. **Organize existing files**:
   - Move source materials to `input/`
   - Place scripts in relevant step folders
   - Structure reflects actual workflow

### When Task Evolves

- **Add steps**: Insert new numbered directories (e.g., `02b_` or renumber)
- **Merge steps**: Combine directories if separation proves unnecessary
- **Rename steps**: Update if better descriptions emerge
- **Restructure**: If workflow understanding fundamentally changes

## Examples (Not Prescriptive Templates)

See `references/examples.md` for illustrative case studies. These are **examples**, not templates—each real task should have its own unique structure.

## Best Practices

1. **Start simple**: Begin with 2-3 core steps, expand as needed
2. **Review periodically**: Is the structure still reflecting the actual workflow?
3. **Document decisions**: Note why certain structures were chosen in `MEMORY.md`
4. **Keep root clean**: Only system config files at workspace root
5. **Handle locked files**: Note which files couldn't be moved due to locks, retry later

## Extension & Iteration

This system is designed for evolution:
- New task types will create new structures
- Experience will refine the methodology
- User feedback will shape best practices
- The skill itself will be updated as patterns emerge

**Key insight**: The folder structure is a *result* of workflow analysis, not a *template* applied to tasks.