/**
 * tradesman-verify — OpenClaw skill manifest
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * A skill is a named collection of tools that an AI agent can load.
 * This manifest is compatible with:
 *
 *   - OpenClaw  (https://openclaw.ai)
 *   - Claude tool_use  (Anthropic)
 *   - OpenAI function calling
 *   - MCP tool format  (Model Context Protocol)
 *
 * Usage with OpenClaw:
 *   const skill = createTradesmanVerifySkill({ signer });
 *   agent.loadSkill(skill);
 *
 * Usage with Claude tool_use:
 *   const skill = createTradesmanVerifySkill({ signer });
 *   const tools = skill.toClaudeTools();
 *   // Pass tools to Anthropic SDK messages.create({ tools, ... })
 *
 * Usage without signing (verify-only, no issuance):
 *   const skill = createTradesmanVerifySkill();
 *   // Only verify_contractor tool is available
 */

import {
  verifyContractorTool,
  verifyBusinessEntityTool,
  makeSelfAttestTool,
  makeIssueCredentialTool,
  makeRevokeCredentialTool,
} from './tools.js';
import type { Skill, SkillTool, Signer } from '../types.js';

export const SKILL_NAME = 'tradesman-verify';
export const SKILL_VERSION = '0.1.0';

export interface SkillOptions {
  /**
   * Signer for write operations (self-attest, issue, revoke).
   * If not provided, only verify_contractor is available.
   */
  signer?: Signer;
}

export interface TradesmanVerifySkill extends Skill {
  /**
   * Convert tools to Claude tool_use format.
   * Pass the returned array directly to Anthropic SDK's `tools` parameter.
   */
  toClaudeTools(): Array<{
    name: string;
    description: string;
    input_schema: SkillTool['inputSchema'];
  }>;

  /**
   * Convert tools to OpenAI function calling format.
   */
  toOpenAIFunctions(): Array<{
    name: string;
    description: string;
    parameters: SkillTool['inputSchema'];
  }>;

  /**
   * Convert tools to MCP tool format.
   */
  toMCPTools(): Array<{
    name: string;
    description: string;
    inputSchema: SkillTool['inputSchema'];
  }>;

  /**
   * Execute a tool by name with the given input.
   * Used by agent runtimes that dispatch tool calls by name.
   */
  executeTool(name: string, input: Record<string, unknown>): Promise<unknown>;
}

/**
 * Create a tradesman-verify skill instance.
 *
 * @param options.signer - Required for write operations (issue, revoke, self-attest).
 *                         Omit for verify-only deployments.
 */
export function createTradesmanVerifySkill(options: SkillOptions = {}): TradesmanVerifySkill {
  const { signer } = options;

  const tools: SkillTool[] = [verifyContractorTool, verifyBusinessEntityTool];

  if (signer) {
    tools.push(makeSelfAttestTool(signer));
    tools.push(makeIssueCredentialTool(signer));
    tools.push(makeRevokeCredentialTool(signer));
  }

  const toolMap = new Map(tools.map((t) => [t.name, t]));

  return {
    name: SKILL_NAME,
    version: SKILL_VERSION,
    description:
      'Issue and verify contractor credentials on the Accumulate blockchain. ' +
      'Reads and writes W3C Verifiable Credentials to Accumulate Digital Identifiers (ADIs). ' +
      'Reference implementation for the ACME Foundation credential standard.',
    tools,

    toClaudeTools() {
      return tools.map((t) => ({
        name: t.name,
        description: t.description,
        input_schema: t.inputSchema,
      }));
    },

    toOpenAIFunctions() {
      return tools.map((t) => ({
        name: t.name,
        description: t.description,
        parameters: t.inputSchema,
      }));
    },

    toMCPTools() {
      return tools.map((t) => ({
        name: t.name,
        description: t.description,
        inputSchema: t.inputSchema,
      }));
    },

    async executeTool(name: string, input: Record<string, unknown>): Promise<unknown> {
      const tool = toolMap.get(name);
      if (!tool) {
        throw new Error(`Unknown tool: ${name}. Available: ${[...toolMap.keys()].join(', ')}`);
      }
      return tool.execute(input);
    },
  };
}
