/**
 * Threat Model Layer
 * Generates a threat model by identifying capabilities (network, exec, fs, etc.)
 * within a given context/codebase to contextualize heuristic pattern findings.
 */

const CAPABILITY_PATTERNS = {
  network: /(?:fetch|axios|http\.get|https\.request|XMLHttpRequest|WebSocket)/i,
  exec: /(?:exec|spawn|child_process|eval|Function|system)/i,
  fs_read: /(?:readFileSync|readFile|createReadStream)/i,
  fs_write: /(?:writeFileSync|writeFile|createWriteStream|appendFile)/i,
  env_access: /(?:process\.env)/i
};

function generateModel(codeContent) {
  const capabilities = {
    network: false,
    exec: false,
    fs_read: false,
    fs_write: false,
    env_access: false
  };

  let riskScore = 0;

  for (const [cap, regex] of Object.entries(CAPABILITY_PATTERNS)) {
    if (regex.test(codeContent)) {
      capabilities[cap] = true;
      riskScore += 10; // Base score for having a risky capability
    }
  }

  // Capability compounding (e.g. read + network = exfil risk)
  if (capabilities.fs_read && capabilities.network) {
    riskScore += 20;
  }
  if (capabilities.env_access && capabilities.network) {
    riskScore += 30; // High risk of credential exfiltration
  }

  return {
    capabilities,
    riskScore,
    summary: `Capabilities detected: ${Object.keys(capabilities).filter(k => capabilities[k]).join(', ')}`
  };
}

module.exports = {
  generateModel
};
