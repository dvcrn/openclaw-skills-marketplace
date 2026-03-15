/**
 * Agent Team Plugin for OpenClaw
 *
 * Injects team member information into the system context before prompt build.
 * This ensures AI agents always have access to team information without needing
 * to explicitly invoke tools.
 */

import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";

interface TeamMember {
  agent_id: string;
  name: string;
  role: string;
  enabled: boolean;
  tags: string[];
  expertise: string[];
  not_good_at: string[];
}

interface TeamData {
  team: Record<string, TeamMember>;
}

interface PluginConfig {
  dataFile?: string;
  enabled?: boolean;
}

interface BeforePromptBuildContext {
  messages?: unknown[];
}

interface BeforePromptBuildResult {
  prependContext?: string;
  systemPrompt?: string;
  prependSystemContext?: string;
  appendSystemContext?: string;
}

interface PluginApi {
  config: PluginConfig;
  on: (
    event: "before_prompt_build",
    handler: (event: string, ctx: BeforePromptBuildContext) => BeforePromptBuildResult,
    options?: { priority?: number }
  ) => void;
}

// Default data file path
const DEFAULT_DATA_FILE = join(homedir(), ".agent-team", "team.json");

/**
 * Load team data from JSON file
 */
function loadTeamData(dataFilePath: string): TeamData | null {
  try {
    if (!existsSync(dataFilePath)) {
      return null;
    }
    const content = readFileSync(dataFilePath, "utf-8");
    const data = JSON.parse(content) as TeamData;
    if (!data || typeof data !== "object" || !data.team) {
      return null;
    }
    return data;
  } catch (error) {
    console.error(`[agent-team] Error loading team data: ${error}`);
    return null;
  }
}

/**
 * Format team data as markdown for system context
 */
function formatTeamContext(teamData: TeamData): string {
  const members = Object.values(teamData.team).filter((m) => m.enabled !== false);

  if (members.length === 0) {
    return "";
  }

  const lines: string[] = [
    "",
    "## 团队成员 (Team Members)",
    "",
    "以下是当前可用的团队成员。接到任务时，应根据成员专长分配任务：",
    "",
  ];

  for (const member of members) {
    lines.push(`### ${member.name} (${member.agent_id})`);
    lines.push(`- **角色**: ${member.role}`);
    if (member.tags.length > 0) {
      lines.push(`- **标签**: ${member.tags.join(", ")}`);
    }
    if (member.expertise.length > 0) {
      lines.push(`- **擅长**: ${member.expertise.join(", ")}`);
    }
    if (member.not_good_at.length > 0) {
      lines.push(`- **不擅长**: ${member.not_good_at.join(", ")}`);
    }
    lines.push("");
  }

  lines.push("> 提示：任务应交给最擅长的成员执行。使用 Agent 工具转交任务。");

  return lines.join("\n");
}

/**
 * Plugin register function
 */
export default function register(api: PluginApi): void {
  const config = api.config || {};

  // Skip if disabled
  if (config.enabled === false) {
    console.log("[agent-team] Plugin is disabled");
    return;
  }

  // Register before_prompt_build hook
  api.on(
    "before_prompt_build",
    (_event: string, _ctx: BeforePromptBuildContext) => {
      const dataFile = config.dataFile || DEFAULT_DATA_FILE;
      const teamData = loadTeamData(dataFile);

      if (!teamData) {
        console.log(`[agent-team] No team data found at ${dataFile}`);
        return {};
      }

      const context = formatTeamContext(teamData);
      if (!context) {
        console.log("[agent-team] No enabled team members");
        return {};
      }

      console.log(`[agent-team] Injecting team context (${Object.keys(teamData.team).length} members)`);

      return {
        appendSystemContext: context,
      };
    },
    { priority: 10 }
  );
}