/**
 * PM2 Ecosystem Config for CodeDNA Runner
 * 
 * Usage:
 *   pm2 start ecosystem.config.cjs
 *   pm2 stop codedna-runner
 *   pm2 restart codedna-runner
 *   pm2 logs codedna-runner
 *   pm2 delete codedna-runner
 * 
 * Auto-restart on crash, memory limit 512MB, exponential backoff.
 */

const { readFileSync, existsSync } = require("fs");
const { join } = require("path");
const os = require("os");

const configDir = join(os.homedir(), ".codedna");
const configPath = join(configDir, "config.json");

// Read agent list from config
let agents = [];
if (existsSync(configPath)) {
  try {
    const cfg = JSON.parse(readFileSync(configPath, "utf-8"));
    agents = cfg.agents || (cfg.tokenId ? [cfg.tokenId] : []);
  } catch (e) {
    console.error("Failed to read config:", e.message);
  }
}

const tokenArg = agents.length > 0 ? agents.join(",") : "";

module.exports = {
  apps: [
    {
      name: "codedna-runner",
      script: "runner.mjs",
      args: tokenArg ? `--token ${tokenArg}` : "",
      cwd: __dirname,
      interpreter: "node",
      node_args: "",
      
      // Restart policy
      autorestart: true,
      max_restarts: 50,
      min_uptime: "30s",
      restart_delay: 10000,        // 10s between restarts
      exp_backoff_restart_delay: 5000,  // exponential backoff starting at 5s
      
      // Resource limits
      max_memory_restart: "512M",
      
      // Logs
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      error_file: join(configDir, "runner-error.log"),
      out_file: join(configDir, "runner-out.log"),
      merge_logs: true,
      log_type: "raw",
      
      // Environment
      env: {
        NODE_ENV: "production",
      },
      
      // Watch (disabled — runner handles its own state)
      watch: false,
    },
  ],
};
