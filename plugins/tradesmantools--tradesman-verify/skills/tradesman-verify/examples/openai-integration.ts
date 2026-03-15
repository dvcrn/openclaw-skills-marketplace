/**
 * tradesman-verify — OpenAI function calling integration example
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Full tool-call loop: model selects tool → skill executes → model summarizes.
 *
 * Prerequisites:
 *   npm install openai tradesman-verify
 *   export OPENAI_API_KEY=sk-...
 *   export OPENCORPORATES_API_KEY=...   # for verify_business_entity
 */

import OpenAI from 'openai';
import { createTradesmanVerifySkill } from 'tradesman-verify';

const openai = new OpenAI({ apiKey: process.env['OPENAI_API_KEY'] });

// Build the skill — no signer for verify-only mode
// Pass { signer } to also enable issue_credential, self_attest_credential, revoke_credential
const skill = createTradesmanVerifySkill();

// Convert to OpenAI function calling format
const tools = skill.toOpenAIFunctions().map((f) => ({
  type: 'function' as const,
  function: f,
}));

async function chat(userMessage: string): Promise<void> {
  console.log(`\nUser: ${userMessage}`);

  const messages: OpenAI.ChatCompletionMessageParam[] = [
    { role: 'user', content: userMessage },
  ];

  // First turn — model decides whether to call a tool
  const response = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages,
    tools,
    tool_choice: 'auto',
  });

  const assistantMessage = response.choices[0]!.message;
  messages.push(assistantMessage);

  // Execute each tool call and collect results
  if (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
    for (const toolCall of assistantMessage.tool_calls) {
      const toolName = toolCall.function.name;
      const toolInput = JSON.parse(toolCall.function.arguments) as Record<string, unknown>;

      console.log(`\n→ Calling tool: ${toolName}`);

      const toolResult = await skill.executeTool(toolName, toolInput);

      messages.push({
        role: 'tool',
        tool_call_id: toolCall.id,
        content: JSON.stringify(toolResult),
      });
    }

    // Second turn — model summarizes tool results in natural language
    const summary = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages,
    });

    console.log(`\nAssistant: ${summary.choices[0]!.message.content}`);
  } else {
    console.log(`\nAssistant: ${assistantMessage.content}`);
  }
}

// ── Example calls ─────────────────────────────────────────────────────────────

// Verify a business entity via OpenCorporates
await chat('Look up "ABC Roofing LLC" in Texas (jurisdiction: us_tx) and tell me if they are actively registered.');

// Verify an on-chain contractor ADI
await chat('Verify the contractor at acc://john-doe-electric.acme on the Accumulate blockchain.');

// Two-step: verify business entity, then anchor result on-chain
// (Requires a signer — see createTradesmanVerifySkill({ signer }))
await chat(
  'Look up "ABC Roofing LLC" in Texas, then issue a BusinessEntityCredential ' +
  'to acc://abc-roofing.acme anchoring the result on the Accumulate blockchain.'
);
