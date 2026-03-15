#!/usr/bin/env node
/**
 * wire-openclaw-bridge.mjs
 *
 * Wires VAIBot Guard enforcement into OpenClaw by:
 *  - installing/enabling the local vaibot-guard-bridge plugin (assumes plugin folder already present)
 *  - setting tool policy so the agent cannot use system.run directly
 *  - allowlisting the plugin tool `vaibot_exec`
 *
 * Safe-ish defaults:
 *  - merges allow/deny arrays (does not blindly overwrite with a single value)
 *  - will prompt before applying unless --yes is provided
 */

import { execSync } from "node:child_process";

function sh(cmd) {
  return execSync(cmd, { stdio: ["ignore", "pipe", "pipe"], encoding: "utf8" });
}

function getJson(cmd) {
  const out = sh(cmd).trim();
  if (!out) return undefined;
  try {
    return JSON.parse(out);
  } catch (e) {
    throw new Error(`Failed to parse JSON from: ${cmd}\nOutput: ${out.slice(0, 500)}`);
  }
}

function setJson(path, value) {
  const json = JSON.stringify(value);
  sh(`openclaw config set '${path}' '${json.replace(/'/g, "'\\''")}'`);
}

function getValue(path) {
  // openclaw config get returns JSON only with --json.
  return getJson(`openclaw config get '${path}' --json`);
}

function uniq(arr) {
  const out = [];
  const seen = new Set();
  for (const x of arr) {
    const k = String(x);
    if (seen.has(k)) continue;
    seen.add(k);
    out.push(x);
  }
  return out;
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--") {
      out._.push(...argv.slice(i + 1));
      break;
    }
    if (a.startsWith("--")) {
      const k = a.slice(2);
      const v = argv[i + 1];
      if (!v || v.startsWith("--")) out[k] = true;
      else {
        out[k] = v;
        i++;
      }
    } else out._.push(a);
  }
  return out;
}

function die(msg, code = 2) {
  console.error(msg);
  process.exit(code);
}

async function main() {
  const flags = parseArgs(process.argv.slice(2));
  if (flags.help || flags.h) {
    console.log(`Usage: node scripts/wire-openclaw-bridge.mjs [options]

Options:
  --token <VAIBOT_GUARD_TOKEN>   Guard bearer token (or set env VAIBOT_GUARD_TOKEN)
  --host <host>                  Default 127.0.0.1
  --port <port>                  Default 39111
  --agentId <id>                 Agent id to enforce (default: main)
  --yes                          Apply without prompting

Notes:
  - This script assumes the vaibot-guard-bridge plugin exists at:
      <workspace>/.openclaw/extensions/vaibot-guard-bridge/
  - It configures OpenClaw to deny system.run and allow vaibot_exec.
`);
    process.exit(0);
  }

  const token = String(flags.token || process.env.VAIBOT_GUARD_TOKEN || "").trim();
  if (!token) die("Missing VAIBOT_GUARD_TOKEN. Pass --token ... or set env VAIBOT_GUARD_TOKEN.");

  const host = String(flags.host || "127.0.0.1");
  const port = Number(flags.port || 39111);
  const agentId = String(flags.agentId || "main");

  // Resolve agent index
  const agents = getValue("agents.list") ?? [];
  const idx = agents.findIndex((a) => a && a.id === agentId);
  if (idx === -1) {
    die(`Could not find agent id '${agentId}' in agents.list. Found: ${agents.map((a) => a?.id).join(", ")}`);
  }

  const plan = [];

  // 1) plugins.allow add vaibot-guard-bridge (avoid auto-load warnings)
  const pluginsAllow = (getValue("plugins.allow") ?? []);
  const nextPluginsAllow = uniq(["vaibot-guard-bridge", ...pluginsAllow]);
  plan.push({ path: "plugins.allow", value: nextPluginsAllow });

  // 2) ensure plugin enabled
  plan.push({ path: "plugins.entries.vaibot-guard-bridge.enabled", value: true });

  // 3) configure plugin token/host/port
  plan.push({ path: "plugins.entries.vaibot-guard-bridge.config.token", value: token });
  plan.push({ path: "plugins.entries.vaibot-guard-bridge.config.host", value: host });
  plan.push({ path: "plugins.entries.vaibot-guard-bridge.config.port", value: port });

  // 4) deny system.run globally
  const toolsDeny = (getValue("tools.deny") ?? []);
  const nextToolsDeny = uniq(["system.run", ...toolsDeny]);
  plan.push({ path: "tools.deny", value: nextToolsDeny });

  // 5) allowlist vaibot_exec tool for the target agent
  const agentAllowPath = `agents.list[${idx}].tools.allow`;
  const agentAllow = (getValue(agentAllowPath) ?? []);
  const nextAgentAllow = uniq(["vaibot_exec", ...agentAllow]);
  plan.push({ path: agentAllowPath, value: nextAgentAllow });

  // Summary
  console.error("Will apply the following OpenClaw config changes:");
  for (const step of plan) {
    console.error(`- ${step.path} = ${JSON.stringify(step.value)}`);
  }
  console.error("\nAfter applying, restart the gateway: openclaw gateway restart");

  if (!flags.yes) {
    // Primitive prompt (TTY only)
    if (!process.stdin.isTTY) die("Refusing to apply without TTY. Re-run with --yes.");
    process.stderr.write("\nApply changes? [y/N]: ");
    const answer = await new Promise((resolve) => {
      process.stdin.once("data", (d) => resolve(String(d).trim().toLowerCase()));
    });
    if (answer !== "y" && answer !== "yes") {
      console.error("Aborted.");
      process.exit(1);
    }
  }

  for (const step of plan) {
    if (typeof step.value === "boolean") {
      sh(`openclaw config set '${step.path}' ${step.value ? "true" : "false"}`);
    } else if (typeof step.value === "number") {
      sh(`openclaw config set '${step.path}' ${step.value}`);
    } else {
      setJson(step.path, step.value);
    }
  }

  process.stdout.write(JSON.stringify({ ok: true, applied: plan.map((p) => p.path) }, null, 2) + "\n");
}

main().catch((e) => {
  console.error(e?.stack || e?.message || String(e));
  process.exit(1);
});
