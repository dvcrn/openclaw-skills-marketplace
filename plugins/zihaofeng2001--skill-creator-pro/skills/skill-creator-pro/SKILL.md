---
name: skill-creator-pro
description: "Create new skills, modify and improve existing skills, and measure skill performance with eval-driven iteration. Use when users want to create a skill from scratch, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy. Also use when someone says 'turn this into a skill', 'make a skill for X', 'improve this skill', 'test this skill', 'run evals on this skill', or mentions skill descriptions, skill triggering, or skill quality."
---

# Skill Creator Pro

> Inspired by and adapted from Anthropic's Claude Code skill-creator
> (https://github.com/anthropics/skills/tree/main/skills/skill-creator).
> Licensed under Apache 2.0.

A skill for creating new OpenClaw skills and iteratively improving them through eval-driven development.

## High-Level Process

- Decide what the skill should do and roughly how it should work
- Write a draft of the skill
- Create test prompts and run the agent-with-skill on them (via sub-agents)
- Evaluate results both qualitatively and quantitatively
  - While runs happen in background, draft quantitative evals if there are none
  - Use `eval-viewer/generate_review.py` to show results to the user
- Rewrite the skill based on feedback
- Repeat until satisfied
- Expand the test set and try again at larger scale

Your job is to figure out where the user is in this process and help them progress. Maybe they want to create a new skill from scratch, or maybe they already have a draft and want to iterate. Be flexible — if the user says "just vibe with me", skip the formal eval loop.

After the skill is done, you can also run the description optimizer to improve triggering accuracy.

## Communicating with the User

Adjust your communication style based on the user's technical level. Watch for context cues:

- "evaluation" and "benchmark" are fine for most users
- For "JSON" and "assertion", make sure the user seems comfortable with those terms before using them freely
- Briefly explain terms if in doubt

---

## Creating a Skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow to capture (e.g., "turn this into a skill"). If so, extract answers from conversation history first — tools used, sequence of steps, corrections made, input/output formats. The user may need to fill gaps and should confirm before proceeding.

1. What should this skill enable the agent to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Skills with objectively verifiable outputs benefit from tests. Skills with subjective outputs (writing style, art) often don't. Suggest the appropriate default but let the user decide.

### Interview and Research

Proactively ask about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until this is ironed out.

### Write the SKILL.md

Based on the interview, fill in:

- **name**: Skill identifier (kebab-case)
- **description**: When to trigger, what it does. This is the primary triggering mechanism. Make it "pushy" — include both what the skill does AND specific contexts. Instead of "Dashboard builder", write "Build dashboards. Use whenever the user mentions dashboards, data visualization, metrics display, or wants to show any data visually, even if they don't say 'dashboard'."
- **the rest of the skill instructions**

### Skill Writing Guide

See `references/schemas.md` for detailed JSON schemas used throughout the eval system.

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context when skill triggers (<500 lines ideal)
3. **Bundled resources** - Loaded as needed (unlimited)

Keep SKILL.md under 500 lines; use references/ for overflow with clear pointers.

#### Writing Patterns

Use imperative form in instructions. Explain **why** things matter — today's LLMs are smart and respond better to reasoning than rigid MUSTs. Include examples where helpful. Make skills general, not narrow to specific examples.

### Test Cases

After writing the skill draft, create 2-3 realistic test prompts. Share with user for review. Save to `evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

## Running and Evaluating Test Cases

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Organize by iteration (`iteration-1/`, `iteration-2/`, etc.) with each test case in `eval-0/`, `eval-1/`, etc.

### Step 1: Spawn All Runs

For each test case, spawn two sub-agents — one with the skill, one without (baseline). Launch everything at once so it finishes around the same time.

**With-skill run** — spawn a sub-agent with instructions like:
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any>
- Save outputs to: <workspace>/iteration-N/eval-ID/with_skill/outputs/
```

**Baseline run** — same prompt without the skill, saving to `without_skill/outputs/`.

Write an `eval_metadata.json` for each test case:
```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: Draft Assertions While Runs Are in Progress

Draft quantitative assertions for each test case. Good assertions are objectively verifiable and have descriptive names. Update `eval_metadata.json` and `evals/evals.json` with assertions.

### Step 3: Capture Timing Data

When each sub-agent completes, save timing data to `timing.json`:
```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

### Step 4: Grade, Aggregate, and Launch Viewer

Once all runs complete:

1. **Grade each run** — read `agents/grader.md` and evaluate assertions against outputs. Save to `grading.json`. The grading.json expectations array must use fields `text`, `passed`, and `evidence`. For programmatically checkable assertions, write and run a script.

2. **Aggregate into benchmark** — run from this skill's directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

3. **Analyst pass** — read `agents/analyzer.md` and surface patterns the aggregate stats might hide.

4. **Launch the viewer** — always use `--static` mode in OpenClaw:
   ```bash
   python <skill-creator-pro-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     --static <workspace>/iteration-N/review.html
   ```
   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   Then send the HTML file to the user:
   ```
   message(action=send, filePath="<workspace>/iteration-N/review.html")
   ```
   Or present it via the Canvas tool if available.

   GENERATE THE EVAL VIEWER *BEFORE* evaluating results yourself. Get them in front of the user ASAP!

5. **Tell the user**: "I've generated the results viewer. The 'Outputs' tab lets you review each test case and leave feedback. The 'Benchmark' tab shows quantitative comparison. When done, come back and let me know."

### Step 5: Read the Feedback

The viewer's "Submit All Reviews" button downloads `feedback.json`. Read it when the user provides it:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus improvements on test cases with specific complaints.

---

## Improving the Skill

### How to Think About Improvements

1. **Generalize from feedback.** Don't overfit to specific examples. The skill will be used many times across different prompts. Rather than fiddly changes or oppressive MUSTs, try different metaphors or patterns.

2. **Keep the prompt lean.** Remove things not pulling their weight. Read transcripts — if the skill causes unproductive work, trim those parts.

3. **Explain the why.** LLMs respond better to reasoning than rigid rules. If you find yourself writing ALWAYS or NEVER in caps, reframe with explanation.

4. **Look for repeated work.** If all test cases independently wrote similar helper scripts, bundle that script in `scripts/` to save future invocations from reinventing the wheel.

### The Iteration Loop

1. Apply improvements to the skill
2. Rerun all test cases into `iteration-<N+1>/`, including baselines
3. Launch the viewer with `--previous-workspace` pointing at the previous iteration
4. Wait for user review
5. Read feedback, improve again, repeat

Keep going until the user is happy, feedback is all empty, or you're not making meaningful progress.

---

## Advanced: Blind Comparison

For rigorous comparison between two skill versions, read `agents/comparator.md` and `agents/analyzer.md`. Give two outputs to an independent sub-agent without revealing which is which. This is optional — human review is usually sufficient.

---

## Description Optimization

The description field is the primary trigger mechanism. After creating or improving a skill, offer to optimize it.

### Step 1: Generate Trigger Eval Queries

Create 20 eval queries — mix of should-trigger and should-not-trigger. Save as JSON:
```json
[
  {"query": "realistic user prompt", "should_trigger": true},
  {"query": "near-miss prompt", "should_trigger": false}
]
```

Queries must be realistic — include file paths, personal context, column names, casual speech, typos. Focus on edge cases, not clear-cut ones. Should-not-trigger queries should be near-misses, not obviously irrelevant.

### Step 2: Review with User

Present the eval set using the HTML template from `assets/eval_review.html`. Replace placeholders:
- `__EVAL_DATA_PLACEHOLDER__` → JSON array
- `__SKILL_NAME_PLACEHOLDER__` → skill name
- `__SKILL_DESCRIPTION_PLACEHOLDER__` → current description

Write to a temp file and send via `message(action=send, filePath=...)` or present via Canvas.

### Step 3: Run the Optimization Loop

The description optimization loop requires CLI access to run eval queries. In OpenClaw, use the adapted scripts:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id> \
  --max-iterations 5 \
  --verbose
```

Note: The `run_eval.py` and `run_loop.py` scripts use `claude -p` for triggering tests. In OpenClaw environments without the `claude` CLI, you can run description optimization manually: evaluate each query by spawning a sub-agent, check if it would trigger the skill, then use `improve_description.py`'s logic to generate better descriptions.

### Step 4: Apply the Result

Take `best_description` from the output and update the skill's SKILL.md frontmatter. Show before/after and report scores.

---

## Packaging

Package the skill for distribution:
```bash
python -m scripts.package_skill <path/to/skill-folder>
```

Then send the `.skill` file to the user via `message(action=send, filePath=...)`.

---

## OpenClaw-Specific Workflow

### Sub-Agent Based Testing

OpenClaw uses sub-agents for parallel test execution. When spawning test runs:
- Sub-agents can read the skill's SKILL.md and follow its instructions
- Results are saved to workspace files
- Timing data comes from sub-agent completion notifications

### Presenting Results

Since OpenClaw may not have a browser display:
- Always use `--static` mode with `generate_review.py` to create standalone HTML
- Send the HTML file via `message(action=send, filePath=...)`
- Or present via the Canvas tool: `canvas(action=present, url="file://...")`

### Feedback Collection

In static mode, the viewer's "Submit All Reviews" downloads `feedback.json`. The user can then provide this file back to you.

---

## Reference Files

- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison
- `agents/analyzer.md` — How to analyze benchmark results
- `references/schemas.md` — JSON schemas for evals.json, grading.json, benchmark.json, etc.

---

## Core Loop Summary

1. Figure out what the skill is about
2. Draft or edit the skill
3. Run agent-with-skill on test prompts (via sub-agents)
4. Evaluate outputs with the user:
   - Create benchmark.json and run `eval-viewer/generate_review.py`
   - Run quantitative evals
5. Repeat until satisfied
6. Package the final skill
