#!/usr/bin/env node

import { httpsRequest, getApiKey } from './utils.mjs';
import { readSkillJson, tryAutoMigrate } from './skill-writer.mjs';
import { buildValue, parseOutputs } from './types.mjs';
import fs from 'fs';
import path from 'path';

/**
 * Read all stdin as a string (for piped input).
 */
function readStdin() {
  return new Promise((resolve, reject) => {
    const chunks = [];
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => chunks.push(chunk));
    process.stdin.on('end', () => resolve(chunks.join('')));
    process.stdin.on('error', reject);
  });
}

/**
 * Build the value string for a schema field based on its type.
 */
function buildFieldValue(fieldSchema, userValue) {
  if (userValue === undefined || userValue === null) {
    return fieldSchema.defaultValue || '';
  }
  return buildValue(fieldSchema.type, userValue);
}

/**
 * Build the `inputs` array for the run request body.
 *
 * Uses the metadata schema as template, fills in user-provided values.
 *
 * User input format:
 * {
 *   "input0": {
 *     "image": "/path/to/image.jpg",
 *     "imageTemplate": "/path/to/template.jpg"
 *   }
 * }
 */
function buildRunInputs(skillInputs, userInputs) {
  return skillInputs.map((input) => {
    const userDataForInput = userInputs[input.name] || {};

    // Clone each schema field from metadata, only fill in value
    const schema = (input.schema || []).map((field) => {
      const userValue = userDataForInput[field.name];
      const cloned = { ...field };
      // Remove null schema to match working request format
      if (cloned.schema === null) delete cloned.schema;
      // Remove constraint if null
      if (cloned.constraint === null) delete cloned.constraint;
      // Fill in value
      cloned.value = buildFieldValue(field, userValue);
      return cloned;
    });

    // Clone top-level input, preserving all fields (optional, readonly, visuals, etc.)
    const cloned = { ...input };
    if (cloned.schema === null) delete cloned.schema;
    if (cloned.constraint === null) delete cloned.constraint;
    cloned.schema = schema;
    return cloned;
  });
}

async function main() {
  const epId = process.argv[2];
  const pluginRoot = process.argv[3];
  let inputArg = process.argv[4];

  if (!epId || !pluginRoot) {
    console.error('Usage: node invoke.mjs <ep-id> <plugin-root> \'<input-json>\' | -');
    console.error('Use - as input arg to read from stdin');
    console.error('');
    console.error('Input JSON format:');
    console.error('  { "input0": { "image": "/path/to/image.jpg" } }');
    console.error('  { "input0": { "text": "hello world" } }');
    process.exit(1);
  }

  let apiKey;
  try {
    apiKey = getApiKey();
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }

  // Read skill.json to get tool info (auto-migrate old registry if needed)
  const skillJson = tryAutoMigrate(pluginRoot, readSkillJson(pluginRoot));
  let tool = skillJson.tools.find(t => t.epId === epId);

  // If not found in registered, check presets
  if (!tool) {
    const presetPath = path.join(pluginRoot, 'skill/preset-skills.json');
    if (fs.existsSync(presetPath)) {
      try {
        const presetData = JSON.parse(fs.readFileSync(presetPath, 'utf-8'));
        const preset = (presetData.presetSkills || []).find(s => s.epId === epId);
        if (preset) {
          tool = preset;
        }
      } catch (err) {
        // Ignore preset read errors, skill not found message will be shown
      }
    }
  }

  if (!tool) {
    console.error(`Skill "${epId}" is not found in registered or preset skills.`);
    process.exit(1);
  }

  // Parse user input JSON
  let userInputs;
  if (inputArg === '-') {
    inputArg = await readStdin();
  }
  if (!inputArg) {
    userInputs = {};
  } else {
    try {
      userInputs = JSON.parse(inputArg);
    } catch (err) {
      console.error(`Failed to parse input JSON: ${err.message}`);
      process.exit(1);
    }
  }

  // Build the run request body using rawInputs schema as template
  const inputs = buildRunInputs(tool.rawInputs || [], userInputs);
  const requestBody = JSON.stringify({ inputs });

  // Call the skill
  let response;
  try {
    response = await httpsRequest(tool.runUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: requestBody,
    });
  } catch (err) {
    console.error(`Failed to invoke skill: ${err.message}`);
    process.exit(1);
  }

  if (response.statusCode !== 200) {
    // Check for "conditional branch did not hit" error
    let errorBody = response.body;
    try {
      const parsed = JSON.parse(errorBody);
      if (parsed.message?.global?.detail?.includes('conditional branch did not hit the expected path')) {
        // This means the skill didn't detect anything in the input
        console.log(JSON.stringify({
          success: false,
          epId,
          status: response.statusCode,
          message: '未检出',
          detail: '输入内容中未检出到相关目标，可能原因：输入图片不符合技能要求，或输入参数（如ROI、Tripwire）配置不正确',
          rawError: parsed.message.global.detail,
        }, null, 2));
        process.exit(0);
      }
    } catch {
      // Continue with regular error handling if parsing fails
    }

    console.error(`Skill invocation failed with status ${response.statusCode}: ${response.body}`);
    process.exit(1);
  }

  let result;
  try {
    result = JSON.parse(response.body);
  } catch {
    result = { rawResponse: response.body };
  }

  // Post-process: parse complex-type outputs
  if (result.result && result.result.outputs) {
    parseOutputs(result.result.outputs);
  }

  console.log(JSON.stringify({
    success: true,
    epId,
    result,
  }, null, 2));
}

main();
