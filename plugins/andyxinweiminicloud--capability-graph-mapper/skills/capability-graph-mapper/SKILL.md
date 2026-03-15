---
name: capability-graph-mapper
description: "Helps map the composite permission surface across AI agent skill dependency chains. Traces what each skill can do individually, then computes what they can do together — revealing emergent capabilities nobody explicitly approved."
---

# Your Agent Has 12 Skills — Do You Know What They Can Do Together?

> Helps map composite permission surfaces across skill dependency chains, revealing emergent capabilities that no single skill declares.

## Problem

Individual skill permissions look reasonable in isolation. A file-reader skill reads files. An HTTP client skill sends requests. A JSON parser skill transforms data. Each one passes a security review on its own.

But install all three in the same agent, and you've built a data exfiltration pipeline — read sensitive files, parse out credentials, send them to an external endpoint. Nobody approved that combination. Nobody even noticed it exists.

In traditional software, tools like `npm audit` map dependency trees and flag known vulnerabilities. In agent ecosystems, the risk isn't in individual dependencies — it's in the **composite capability surface** that emerges when skills combine. There is no `npm audit` for emergent agent capabilities.

## What This Maps

This mapper traces the permission graph across an agent's installed skills:

1. **Permission enumeration** — For each skill, extract declared capabilities: file access, network requests, shell execution, environment variable reads, credential access
2. **Pairwise composition** — For every pair of skills, check if their combined capabilities create a new emergent capability (e.g., read + send = exfiltrate)
3. **Transitive chains** — Trace three-hop and deeper composition paths where skill A feeds skill B feeds skill C, creating capabilities invisible at any single hop
4. **Privilege surface score** — Compute a single metric: how many distinct dangerous capability combinations exist in this agent's skill set?
5. **Delta analysis** — When a new skill is added, show what new composite capabilities it introduces to the existing set

## How to Use

**Input**: Provide one of:
- A list of skill names/slugs installed in an agent
- A skill manifest or configuration file
- A single skill to evaluate against a known agent profile

**Output**: A capability graph report containing:
- Permission matrix (skills × capabilities)
- Emergent capability combinations flagged as risky
- Privilege surface score (0-100)
- Recommendation: which skill combinations to review manually
- Delta report if evaluating a new addition

## Example

**Input**: Map capability surface for agent with skills: `log-analyzer`, `http-poster`, `env-reader`, `markdown-formatter`

```
🕸️ CAPABILITY GRAPH — 3 emergent risks detected

Permission matrix:
                    read_files  send_http  read_env  exec_shell  write_files
  log-analyzer         ✓
  http-poster                      ✓
  env-reader           ✓                     ✓
  markdown-formatter   ✓                                ✓

Emergent capability combinations:

  ⚠️ RISK 1: Data exfiltration path
     env-reader (read .env) → http-poster (send HTTP)
     Combined: Can read credentials and transmit them externally
     Severity: HIGH

  ⚠️ RISK 2: Sensitive file relay
     log-analyzer (read logs) → http-poster (send HTTP)
     Combined: Can read application logs and send contents externally
     Severity: MODERATE

  ⚠️ RISK 3: Three-hop chain
     env-reader (read secrets) → markdown-formatter (transform data)
     → http-poster (send HTTP)
     Combined: Read, obfuscate, and exfiltrate in one pipeline
     Severity: HIGH

Privilege surface score: 67/100 (elevated)

Recommendation:
  - Review whether http-poster needs to coexist with env-reader
  - Consider sandboxing env-reader's file access scope
  - The markdown-formatter → http-poster chain enables obfuscation;
    audit what markdown-formatter can output
```

## Related Tools

- **blast-radius-estimator** — estimates downstream impact when a skill turns malicious; capability-graph-mapper helps quantify *what* a compromised skill could do
- **permission-creep-scanner** — checks individual skills for over-permission; this mapper checks what happens when multiple over-permissioned skills combine
- **supply-chain-poison-detector** — detects poisoned individual skills; this mapper shows why a poisoned skill with network access is more dangerous in agents that also have file-read skills

## Limitations

Capability graph mapping depends on accurately extracting each skill's actual permissions, which may not always match declared permissions. Skills that dynamically request capabilities at runtime may not be fully captured through static analysis. The composition risk model uses known dangerous patterns (read+send, parse+execute) but novel attack chains may not be in the pattern library. This tool helps surface emergent risks for human review — it does not guarantee detection of all possible capability combinations. Privilege surface scores are relative, not absolute measures of risk.
