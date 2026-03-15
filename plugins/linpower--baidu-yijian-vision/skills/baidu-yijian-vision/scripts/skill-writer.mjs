#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { hasVisualization, isInputVisualizableType, isBasicType, getSkillMdHints } from './types.mjs';

const SKILL_JSON = 'skill/skill.json';
const SKILL_MD = 'skill/SKILL.md';
const OLD_REGISTRY = '.claude/yijian-skills.local.md';

// ---------------------------------------------------------------------------
// skill.json read / write
// ---------------------------------------------------------------------------

export function readSkillJson(pluginRoot) {
  const filePath = path.join(pluginRoot, SKILL_JSON);
  if (!fs.existsSync(filePath)) {
    return { name: 'yijian-register', version: '0.5.0', tools: [] };
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

export function writeSkillJson(pluginRoot, data) {
  const filePath = path.join(pluginRoot, SKILL_JSON);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf-8');
}

// ---------------------------------------------------------------------------
// Auto-migrate old registry → skill.json (lazy, on first use)
// ---------------------------------------------------------------------------

/**
 * If skill.json has no tools but the old .claude/yijian-skills.local.md exists
 * in the current working directory, migrate automatically and return the
 * updated skillJson. Otherwise return the original skillJson unchanged.
 */
export function tryAutoMigrate(pluginRoot, skillJson) {
  if (skillJson.tools.length > 0) return skillJson;

  const oldFile = path.join(process.cwd(), OLD_REGISTRY);
  if (!fs.existsSync(oldFile)) return skillJson;

  // Dynamically import readRegistry from utils.mjs would create a circular
  // concern, so just inline the minimal parsing logic here.
  const content = fs.readFileSync(oldFile, 'utf-8');
  const jsonMatch = content.match(/```json\s*\n([\s\S]*?)\n```/);
  if (!jsonMatch) return skillJson;

  let registry;
  try { registry = JSON.parse(jsonMatch[1]); } catch { return skillJson; }

  const skills = registry.skills || {};
  const epIds = Object.keys(skills);
  if (epIds.length === 0) return skillJson;

  for (const epId of epIds) {
    const old = skills[epId];
    const inputs = [];
    for (const inp of old.inputs || []) {
      for (const field of inp.schema || []) {
        inputs.push({
          name: field.name,
          type: field.type,
          description: field.description || field.displayName || field.name,
          required: !field.optional,
        });
      }
    }
    const outputs = [];
    for (const out of old.outputs || []) {
      for (const field of out.schema || []) {
        outputs.push({
          name: field.name,
          type: field.type,
          description: field.description || field.displayName || field.name,
        });
      }
    }
    skillJson.tools.push({
      epId,
      name: old.displayName || old.name || epId,
      description: old.description || '',
      scope: '',
      version: old.version || '1.0',
      runUrl: old.runUrl,
      inputs,
      outputs,
      rawInputs: old.inputs || [],
      rawOutputs: old.outputs || [],
      registeredAt: old.registeredAt || new Date().toISOString(),
    });
  }

  writeSkillJson(pluginRoot, skillJson);

  // Rename old file to .bak
  fs.renameSync(oldFile, oldFile + '.bak');
  console.error(`[auto-migrate] Migrated ${epIds.length} tool(s) from old registry. Old file renamed to ${OLD_REGISTRY}.bak`);

  return skillJson;
}

// ---------------------------------------------------------------------------
// Build a tool entry from API metadata
// ---------------------------------------------------------------------------

/**
 * Build a simplified + raw tool entry from the metadata returned by the
 * Yijian `/metadata` API.
 *
 * @param {string} epId
 * @param {object} metadata  - parsed `result` from the metadata response
 * @param {string} mRunUrl   - the run URL for the skill
 * @param {object} [opts]    - optional overrides
 * @param {string} [opts.scope] - human-readable scope description (e.g. "用于人体检测")
 * @returns {object} tool entry for skill.json
 */
export function buildToolEntry(epId, metadata, mRunUrl, opts = {}) {
  // Simplified inputs — one entry per schema field inside each DataSet input
  const inputs = [];
  for (const inp of metadata.inputs || []) {
    for (const field of inp.schema || []) {
      inputs.push({
        name: field.name,
        type: field.type,
        description: field.description || field.displayName || field.name,
        required: !field.optional,
      });
    }
  }

  // Simplified outputs
  const outputs = [];
  for (const out of metadata.outputs || []) {
    for (const field of out.schema || []) {
      outputs.push({
        name: field.name,
        type: field.type,
        description: field.description || field.displayName || field.name,
      });
    }
  }

  return {
    epId,
    name: metadata.displayName || metadata.name || epId,
    description: metadata.description || '',
    scope: opts.scope || '',
    version: metadata.version || '1.0',
    runUrl: mRunUrl,
    inputs,
    outputs,
    rawInputs: metadata.inputs || [],
    rawOutputs: metadata.outputs || [],
    registeredAt: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// SKILL.md generation
// ---------------------------------------------------------------------------

const STATIC_HEADER = `\
---
name: yijian-register
description: "Manage Yijian (一见) platform skill registration: register, list, invoke, and delete skills from yijian-next.cloud.baidu.com. Use this skill when the user mentions 一见, yijian, yijian skill, skill registration, or yijian-next.cloud.baidu.com."
allowed-tools: Bash, Read, Write, Edit
---

# Yijian Skill Registration Manager

This skill manages Yijian platform skills — register, invoke, and delete.

## Prerequisites

The environment variable \`YIJIAN_API_KEY\` must be set. If it is not available, inform the user:

> Please set \`YIJIAN_API_KEY\` in your \`~/.claude/settings.json\` under \`"env"\`:
> \`\`\`json
> { "env": { "YIJIAN_API_KEY": "your-api-key-here" } }
> \`\`\`

## Operations

### Register a Skill

**When to use**: User wants to register/add a Yijian skill, provides a URL like \`https://yijian-next.cloud.baidu.com/api/skills/v1/<ep-id>/...\` or an \`ep-id\`.

**Steps**:
1. Extract the \`ep-id\` from the URL or user input. The ep-id format is typically \`ep-XXXX-YYYY\`.
2. Run the register script:
   \`\`\`bash
   YIJIAN_API_KEY=\${YIJIAN_API_KEY} node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/register.mjs <ep-id> \${CLAUDE_PLUGIN_ROOT}
   \`\`\`
3. Show the user the registered skill's name, description, and ep-id.

### Delete a Skill

**When to use**: User wants to remove/delete/unregister a Yijian skill.

\`\`\`bash
node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/delete.mjs <ep-id> \${CLAUDE_PLUGIN_ROOT}
\`\`\`

### Migrate Old Data

**When to use**: User has skills registered in the old \`.claude/yijian-skills.local.md\` format and wants to migrate to the new dual-layer architecture.

\`\`\`bash
node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/migrate.mjs <project-dir> \${CLAUDE_PLUGIN_ROOT}
\`\`\`

### Update a Skill

**When to use**: User wants to update properties of an already-registered skill (e.g. its scope / usage description).

\`\`\`bash
node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/update.mjs <ep-id> \${CLAUDE_PLUGIN_ROOT} --scope "用于人体检测、行人计数"
\`\`\`
`;

const STATIC_FOOTER = `\

## show-grid Usage

**When to use**: Before invoking a skill that requires ROI (polygon region) or Tripwire (polyline) input. Generates a grid reference image so the user can specify coordinates visually.

**Usage**:
\`\`\`bash
node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/show-grid.mjs <input-image> [output-path] [--cols N] [--rows N]
\`\`\`

- \`<input-image>\`: path to the original image
- \`[output-path]\`: optional, defaults to \`<input>_grid.<ext>\`
- \`--cols\`: number of column segments (default: auto based on aspect ratio)
- \`--rows\`: number of row segments (default: auto based on aspect ratio)

Outputs a JSON object to stdout:
\`\`\`json
{
  "path": "/path/to/photo_grid.png",
  "cols": 7, "rows": 4,
  "colLabels": ["A","B","C","D","E","F","G","H"],
  "rowLabels": ["0","1","2","3","4"],
  "gridWidth": 274.29, "gridHeight": 270,
  "marginLeft": 25, "marginTop": 25,
  "imageWidth": 1920, "imageHeight": 1080
}
\`\`\`

## ROI / Tripwire Input Guide

**When to use**: When a tool input requires ROI (Array<ROI>) or Tripwire (Array<Tripwire>).

Follow this interactive flow:

1. **Generate grid reference image** for the user:
   \`\`\`bash
   node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/show-grid.mjs <image>
   \`\`\`
   Show the generated grid image to the user. If the grid is too coarse, re-run with \`--cols\` / \`--rows\` to increase density.

2. **Ask user to specify vertices** using grid coordinates:
   - ROI (polygon): e.g. \`"B1, E1, E3, B3"\` — list polygon vertices in order
   - Tripwire (polyline): e.g. \`"A2, G2"\` — list polyline points, and ask for direction: "left to right" (Forward), "right to left" (Backward), or "both ways" (TwoWay)

3. **Convert grid coordinates to pixel coordinates** using the metadata from step 1:
   - Column index: A=0, B=1, C=2, ...
   - Row index: 0=0, 1=1, 2=2, ...
   - \`x = colIndex * gridWidth\`, \`y = rowIndex * gridHeight\`

4. **Visualize for confirmation** before invoking:
   \`\`\`bash
   node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/visualize.mjs <image> '[]' --overlays '<overlays-json>'
   \`\`\`
   Show the visualization to the user. If adjustments are needed (e.g. "move right one grid"), update coordinates and re-visualize.

5. **Proceed with invoke** after user confirms.

**Overlay JSON examples**:
\`\`\`json
[{"kind": "ROI", "points": [274,270,960,270,960,810,274,810], "name": "检测区域"}]
[{"kind": "TripWire", "points": [0,540,1920,540], "name": "绊线1", "direction": "Forward"}]
\`\`\`

## visualize Usage

**When to use**: After invoking a skill that returns \`Array<Detection>\` outputs, or when input parameters include ROI/Tripwire that should be visualized on the image. Also use when output is a basic type (e.g., count) but input has visual overlays — display the overlays with text results.

**Prerequisites**: \`sharp\` npm package must be installed. If not installed yet:
\`\`\`bash
cd \${CLAUDE_PLUGIN_ROOT} && npm install
\`\`\`

**Usage**:
\`\`\`bash
node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/visualize.mjs <input-image> '<detections-json>' [output-path] [--overlays '<overlays-json>'] [--text '<text-lines-json>']
\`\`\`

- \`<input-image>\`: path to the original image
- \`<detections-json>\`: JSON array of detections (\`parsedValue\` format), or \`-\` to read from stdin. Use \`[]\` if no detections.
- \`[output-path]\`: optional, defaults to \`<input>_detection.<ext>\`
- \`--overlays\`: JSON array of ROI/Tripwire overlay objects to draw on the image (blue polygons for ROI, orange dashed lines for Tripwire)
- \`--text\`: JSON array of text strings to display as a footer below the image

**Detection JSON format** (parsedValue):
\`\`\`json
[
  {
    "bbox": [x, y, width, height],
    "confidence": 0.94,
    "category": { "id": "person", "name": "人体" },
    "track_id": 1
  }
]
\`\`\`

**Overlays JSON format**:
\`\`\`json
[
  { "kind": "ROI", "points": [x1,y1,x2,y2,...], "name": "区域1" },
  { "kind": "TripWire", "points": [x1,y1,x2,y2,...], "name": "绊线1", "direction": "Forward" }
]
\`\`\`

**Text JSON format**:
\`\`\`json
["进入人数: 5", "离开人数: 3"]
\`\`\`

## Video Frame Extraction Guide

**When to use**: When the user provides a video file and wants to run detection/tracking skills on its frames.

**Steps**:

1. **Extract frames** using ffmpeg:
   \`\`\`bash
   mkdir -p /tmp/frames
   ffmpeg -i <video> -vf "fps=<N>" /tmp/frames/frame_%04d.jpg
   \`\`\`
   Choose \`fps\` based on the task: 1–5 for slow scenes, 10–25 for fast motion or tracking.

2. **Generate a sourceId** for the video (all frames share this):
   \`\`\`bash
   SOURCE_ID=$(head -c 65536 <video> | md5sum | cut -c1-16)
   \`\`\`

3. **Invoke the skill** for each frame in order, using the object form for the Image input:
   \`\`\`json
   { "file": "/tmp/frames/frame_0001.jpg", "sourceId": "<SOURCE_ID>", "timestamp": 0 }
   \`\`\`
   - \`sourceId\`: the hash from step 2 (same for all frames of this video)
   - \`imageId\`: omit to auto-generate from each frame file's content hash
   - \`timestamp\`: milliseconds relative to the first frame: \`(frameIndex - 1) * (1000 / fps)\`

   For example, at fps=5: frame_0001 → 0 ms, frame_0002 → 200 ms, frame_0003 → 400 ms, etc.

## Important Notes

- Always validate URL format: Yijian skill URLs follow the pattern \`https://yijian-next.cloud.baidu.com/api/skills/v1/<ep-id>/...\`
- The \`ep-id\` can be extracted from metadata URLs (\`/metadata\`) or run URLs (\`/run\`).
- When registering or invoking, always use the scripts (they make HTTP calls).
- All scripts output JSON to stdout on success and error messages to stderr on failure.
`;

/**
 * Generate the dynamic "Registered Tools" section for SKILL.md.
 */
function generateToolsSections(tools) {
  if (tools.length === 0) {
    return '## Registered Yijian Tools\n\n> No tools registered yet. Use the register operation to add tools.\n';
  }

  const lines = [
    '## Registered Yijian Tools',
    '',
    '> Technical declarations are in `skill.json`. Below is the usage guide for each tool.',
    '',
  ];

  for (const tool of tools) {
    lines.push(`### ${tool.epId}: ${tool.name}`);
    lines.push('');

    const outputTypes = tool.outputs.map(o => o.type);

    // Trigger condition — use scope if provided, otherwise infer from name + outputs
    if (tool.scope) {
      lines.push(`**Trigger**: ${tool.scope}`);
    } else {
      const triggerHints = [tool.name];
      if (tool.description) triggerHints.push(tool.description);
      if (outputTypes.some(t => hasVisualization(t))) {
        triggerHints.push('object detection', 'bounding box visualization');
      }
      lines.push(`**Trigger**: When user requests: ${triggerHints.join(', ')}.`);
    }
    lines.push('');

    // Inputs
    if (tool.inputs.length > 0) {
      lines.push('**Inputs**:');
      for (const inp of tool.inputs) {
        const req = inp.required ? '(required)' : '(optional)';
        lines.push(`- \`${inp.name}\` — ${inp.type} ${req}: ${inp.description}`);
      }
      lines.push('');
    }

    // Invoke command
    lines.push('**Invoke**:');
    lines.push('```bash');
    lines.push(`echo '{"input0":{${tool.inputs.map(i => `"${i.name}":"<value>"`).join(',')}}}' | node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/invoke.mjs ${tool.epId} \${CLAUDE_PLUGIN_ROOT} -`);
    lines.push('```');
    lines.push('');

    // Input notes
    for (const inp of tool.inputs) {
      const hints = getSkillMdHints(inp.type);
      if (hints.inputNote) {
        lines.push(`> For \`${inp.name}\`: ${hints.inputNote}`);
      }
    }
    lines.push('');

    // Result handling
    lines.push('**Result handling**:');
    for (const out of tool.outputs) {
      const outHints = getSkillMdHints(out.type);
      if (outHints.hasVisualization && outHints.visualizationCmd) {
        lines.push(`- \`${out.name}\` (${out.type}): ${out.description}. Can be visualized with ${outHints.visualizationCmd.replace('.mjs', '')}.`);
      } else if (outHints.hasVisualization) {
        lines.push(`- \`${out.name}\` (${out.type}): ${out.description}. Supports visualization.`);
      } else {
        lines.push(`- \`${out.name}\` (${out.type}): ${out.description}`);
      }
    }
    lines.push('');

    // Visualization hint — show for visualizable outputs OR visualizable inputs
    const vizOutput = tool.outputs.find(o => {
      const h = getSkillMdHints(o.type);
      return h.hasVisualization && h.visualizationCmd;
    });
    const hasVizInput = tool.inputs.some(i => isInputVisualizableType(i.type));
    const hasVizOutput = !!vizOutput;
    const hasBasicOutput = tool.outputs.some(o => isBasicType(o.type));

    if (hasVizOutput || hasVizInput) {
      lines.push('**Visualization**:');
      lines.push('```bash');

      // Build the command parts
      const cmdParts = [`node \${CLAUDE_PLUGIN_ROOT}/skill/scripts/visualize.mjs <image>`];

      if (hasVizOutput) {
        cmdParts.push(`'<parsedValue-json>'`);
      } else {
        cmdParts.push(`'[]'`);
      }

      if (hasVizInput) {
        cmdParts.push(`--overlays '<overlays-json>'`);
      }
      if (!hasVizOutput && hasBasicOutput) {
        cmdParts.push(`--text '<text-lines-json>'`);
      }

      lines.push(cmdParts.join(' '));
      lines.push('```');
      lines.push('');
    }

    lines.push('---');
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Generate the complete SKILL.md from the skill.json data and write it.
 */
export function generateSkillMd(pluginRoot, skillJson) {
  const toolsSection = generateToolsSections(skillJson.tools || []);
  const content = STATIC_HEADER + toolsSection + '\n' + STATIC_FOOTER;
  const filePath = path.join(pluginRoot, SKILL_MD);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content, 'utf-8');
}
