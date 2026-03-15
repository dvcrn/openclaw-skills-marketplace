---
name: vext-scan
description: Scan installed OpenClaw skills for prompt injection, data exfiltration, persistence manipulation, and other AI-native security threats. Built by Vext Labs.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🛡️"
    requires:
      bins: ["python3"]
---

# VEXT Scan

Scan your installed OpenClaw skills for security threats that traditional antivirus cannot detect — prompt injection, data exfiltration, persistence manipulation, privilege escalation, supply chain attacks, and semantic worms.

## Usage

- "Scan my skills for security issues"
- "Run a security scan on all installed skills"
- "Check if my skills are safe"
- "Scan the weather-lookup skill"

## How It Works

1. Enumerates all installed skills (bundled, managed, workspace)
2. Reads each skill's SKILL.md and supporting files
3. Runs three layers of analysis:
   - **Pattern matching**: 200+ threat signatures for known attack patterns
   - **AST analysis**: Python code analysis for dangerous function calls
   - **Encoding detection**: Base64, ROT13, and unicode homoglyph tricks
4. Generates a security report with risk ratings per skill
5. Saves the report and provides a summary

## Running

Run the scanner with:

```bash
python3 scan.py --all                          # Scan all installed skills
python3 scan.py --skill-dir /path/to/skill     # Scan a specific skill
python3 scan.py --output /path/to/report.md    # Custom output path
```

## Rules

- Only perform read-only analysis — never modify scanned files
- Report all findings honestly without minimizing severity
- Do not execute any code from scanned skills
- Do not transmit scan results externally
- Always save the report locally before summarizing

## Safety

- This skill only reads files — it never writes to scanned skill directories
- No network requests are made during scanning
- No code from scanned skills is executed
- Reports are saved locally to ~/.openclaw/vext-shield/reports/
- All analysis is performed using static pattern matching and AST parsing
