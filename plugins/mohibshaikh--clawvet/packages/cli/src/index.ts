import { Command } from "commander";
import { scanCommand } from "./commands/scan.js";
import { auditCommand } from "./commands/audit.js";
import { watchCommand } from "./commands/watch.js";

const program = new Command();

program
  .name("clawvet")
  .description("Skill vetting & supply chain security for OpenClaw")
  .version("0.2.3");

program
  .command("scan")
  .description("Scan a skill for security threats")
  .argument("<target>", "Path to skill folder or SKILL.md file")
  .option("--format <format>", "Output format: terminal or json", "terminal")
  .option("--fail-on <severity>", "Exit 1 if findings at this severity or above")
  .option("--semantic", "Enable AI semantic analysis (requires ANTHROPIC_API_KEY)")
  .option("--remote", "Fetch skill from ClawHub by name instead of local path")
  .action(async (target, opts) => {
    await scanCommand(target, {
      format: opts.format,
      failOn: opts.failOn,
      semantic: opts.semantic,
      remote: opts.remote,
    });
  });

program
  .command("audit")
  .description("Scan all installed OpenClaw skills")
  .option("--dir <path>", "Custom skills directory to scan")
  .action(async (opts) => {
    await auditCommand({ dir: opts.dir });
  });

program
  .command("watch")
  .description("Pre-install hook — blocks risky skill installs")
  .option("--threshold <score>", "Risk score threshold (default 50)", "50")
  .option("--dir <path>", "Custom skills directory to watch")
  .action(async (opts) => {
    await watchCommand({ threshold: parseInt(opts.threshold), dir: opts.dir });
  });

program.parse();
