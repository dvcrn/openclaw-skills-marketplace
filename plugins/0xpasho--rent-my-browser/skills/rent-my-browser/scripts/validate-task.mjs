#!/usr/bin/env node
// Validates a task goal + context before the agent sees it.
// Rejects goals that attempt to exfiltrate secrets, access local files,
// or inject prompt-override instructions.
//
// Usage: node validate-task.mjs <path-to-task.json>
// Exit 0 = safe, Exit 1 = rejected (reason printed to stdout)

import { readFileSync } from "node:fs";

const taskPath = process.argv[2];
if (!taskPath) {
  console.error("Usage: node validate-task.mjs <task.json>");
  process.exit(2);
}

let task;
try {
  task = JSON.parse(readFileSync(taskPath, "utf-8"));
} catch {
  console.error("Failed to parse task JSON");
  process.exit(2);
}

const goal = (task.goal ?? "").toLowerCase();
const contextStr = JSON.stringify(task.context ?? {}).toLowerCase();
const combined = `${goal}\n${contextStr}`;

// --- Pattern categories ---

const SENSITIVE_FILE_PATTERNS = [
  /wallet\.json/i,
  /credentials\.json/i,
  /private.?key/i,
  /\bapi.?key\b/i,
  /\.env\b/i,
  /\bclient.?secret\b/i,
  /\bsecret.?key\b/i,
  /\bjwt.?secret\b/i,
  /seed.?phrase/i,
  /mnemonic/i,
  /keystore/i,
  /\.pem\b/i,
  /\.key\b/i,
  /id_rsa/i,
  /id_ed25519/i,
];

const FILE_ACCESS_PATTERNS = [
  /\bcat\s+.*state\//i,
  /\bread\s+.*state\//i,
  /\bopen\s+.*state\//i,
  /\/etc\/passwd/i,
  /\/etc\/shadow/i,
  /~\/\.\w+/i,              // dotfiles like ~/.ssh, ~/.bashrc
  /\$HOME\/\.\w+/i,
  /\.ssh\//i,
];

const EXFILTRATION_PATTERNS = [
  /send.*(key|secret|token|credential|password|wallet|private)/i,
  /upload.*(key|secret|token|credential|password|wallet|private)/i,
  /post.*(key|secret|token|credential|password|wallet|private)/i,
  /share.*(key|secret|token|credential|password|wallet|private)/i,
  /include.*(key|secret|token|credential|password|wallet|private).*(result|response|output|data)/i,
  /extract.*(key|secret|token|credential|password|wallet|private)/i,
  /\bcurl\b.*\b(key|secret|token|wallet|private)/i,
  /webhook.*\b(key|secret|token|wallet|private)/i,
];

const PROMPT_INJECTION_PATTERNS = [
  /ignore\s+(previous|prior|above|all)\s+(instructions|rules|constraints)/i,
  /disregard\s+(previous|prior|above|all)\s+(instructions|rules|constraints)/i,
  /forget\s+(previous|prior|above|all|your)\s+(instructions|rules|constraints)/i,
  /you\s+are\s+now\s+/i,
  /new\s+system\s+prompt/i,
  /override\s+(safety|security|instructions)/i,
  /act\s+as\s+(if|though)\s+you\s+(have\s+no|don.t\s+have)/i,
  /pretend\s+(there\s+are|you\s+have)\s+no\s+(restrictions|rules|constraints|safety)/i,
  /jailbreak/i,
  /do\s+not\s+follow\s+(the|your)\s+(safety|security|instructions)/i,
];

const SYSTEM_ACCESS_PATTERNS = [
  /\brm\s+-rf\b/i,
  /\bchmod\b.*state\//i,
  /\bmodify\b.*script/i,
  /\bedit\b.*\.sh\b/i,
  /\boverwrite\b.*config/i,
  /\bkill\b.*poll/i,
  /\bpkill\b/i,
  /process\.env/i,
  /\benv\b.*variable/i,
  /environment\s+variable/i,
];

// --- Check all patterns ---

function checkPatterns(text, patterns, category) {
  for (const pattern of patterns) {
    if (pattern.test(text)) {
      return `${category}: matched pattern ${pattern}`;
    }
  }
  return null;
}

const checks = [
  checkPatterns(combined, SENSITIVE_FILE_PATTERNS, "SENSITIVE_FILE_ACCESS"),
  checkPatterns(combined, FILE_ACCESS_PATTERNS, "LOCAL_FILE_ACCESS"),
  checkPatterns(combined, EXFILTRATION_PATTERNS, "DATA_EXFILTRATION"),
  checkPatterns(combined, PROMPT_INJECTION_PATTERNS, "PROMPT_INJECTION"),
  checkPatterns(combined, SYSTEM_ACCESS_PATTERNS, "SYSTEM_TAMPERING"),
];

const rejection = checks.find(Boolean);
if (rejection) {
  console.log(rejection);
  process.exit(1);
}

// All clear
process.exit(0);
