import { readFileSync, existsSync, statSync } from "node:fs";
import { resolve, join } from "node:path";
import { scanSkill } from "@clawvet/shared";
import { printScanResult } from "../output/terminal.js";
import { printJsonResult } from "../output/json.js";

export interface ScanOptions {
  format?: "terminal" | "json";
  failOn?: "critical" | "high" | "medium" | "low";
  semantic?: boolean;
  remote?: boolean;
}

async function fetchRemoteSkill(slug: string): Promise<string> {
  const urls = [
    `https://raw.githubusercontent.com/openclaw/skills/main/${slug}/SKILL.md`,
    `https://clawhub.ai/api/v1/skills/${slug}/raw`,
  ];

  for (const url of urls) {
    try {
      const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
      if (res.ok) {
        return await res.text();
      }
    } catch {
      // try next
    }
  }

  throw new Error(
    `Could not fetch skill "${slug}" from ClawHub. Check the skill name and try again.`
  );
}

export async function scanCommand(
  target: string,
  options: ScanOptions
): Promise<void> {
  let content: string;

  if (options.remote) {
    try {
      process.stderr.write(`Fetching "${target}" from ClawHub...\n`);
      content = await fetchRemoteSkill(target);
    } catch (err) {
      console.error(
        err instanceof Error ? err.message : "Failed to fetch remote skill"
      );
      process.exit(1);
    }
  } else {
    const skillPath = resolve(target);
    let skillFile = skillPath;

    if (
      existsSync(skillPath) &&
      !skillPath.endsWith(".md") &&
      existsSync(join(skillPath, "SKILL.md"))
    ) {
      skillFile = join(skillPath, "SKILL.md");
    }

    if (!existsSync(skillFile) || statSync(skillFile).isDirectory()) {
      console.error(`Error: Cannot find SKILL.md at ${skillFile}`);
      console.error(`Hint: If this is a directory of skills, use 'clawvet audit --dir ${target}' instead.`);
      process.exit(1);
    }

    content = readFileSync(skillFile, "utf-8");
  }

  const result = await scanSkill(content, {
    semantic: options.semantic ?? false,
  });

  if (options.format === "json") {
    printJsonResult(result);
  } else {
    printScanResult(result);
  }

  if (options.failOn) {
    const severityOrder = ["low", "medium", "high", "critical"];
    const threshold = severityOrder.indexOf(options.failOn);
    const hasFailure = result.findings.some(
      (f) => severityOrder.indexOf(f.severity) >= threshold
    );
    if (hasFailure) {
      process.exit(1);
    }
  }
}
