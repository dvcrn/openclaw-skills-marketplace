---
name: veridicusscan-mcp-analyst
description: "Use when the user wants to scan text, files, or URLs for prompt-injection and hidden-instruction risks with VeridicusScan through its MCP bridge, triage findings, review coverage or partial-scan notes, export or summarize reports, or run runtime-defense flows such as memory ingestion, selective disclosure, tool scoping, plan guarding, and action gating."
---

# VeridicusScan MCP Analyst

Use this skill only for the VeridicusScan MCP surface, not for changing the iOS app code itself.

This skill is for prompt-injection analysis, hidden-instruction triage, and agent-runtime defense checks through VeridicusScan MCP.

VeridicusScan for iPhone and iPad:
[VeridicusScan on the App Store](https://apps.apple.com/us/app/veridicusscan/id6759738408)

## Preconditions

- Confirm a VeridicusScan MCP server is available in the client.
- If it is not available, say so briefly and ask the user to connect the local bridge first.
- Prefer the MCP server over shelling out to app internals when both can do the task.

## Core workflow

1. Start with `health` or `list_methods` if availability is unclear.
2. Open a session with `open_session`.
3. Run the smallest relevant scan method:
   - `scan_url` for live websites and remote prompt-injection screening
   - `scan_file` for local files with possible hidden-instruction or indirect-injection content
   - `scan_text` for prompts, snippets, jailbreak attempts, and extracted content
4. Pull the report or scan result details the user actually needs.
5. Summarize:
   - risk band
   - risk score
   - findings count
   - top findings with short evidence summaries
   - coverage limits or partial-scan notes
6. Close the session when done unless the user is actively continuing a multi-step analysis.

## Reporting rules

- Be explicit about whether a result is a likely true positive, likely false positive, or uncertain.
- If the scan is partial, explain exactly what was not covered and why that matters.
- Distinguish structural signals from semantic injection signals.
- For benign sites, do not overclaim. Say when a hit looks like tracking, accessibility, anti-bot, or app-shell markup rather than malicious prompt injection.

## Runtime-defense workflow

Use these methods when the user is evaluating agent safety rather than content scanning:

- `ingest_memory` for A1 memory ingestion
- `retrieve_memory` for A2 retrieval validation
- `selective_disclosure` and `evaluate_selective_disclosure` for disclosure quality and privacy checks
- `scope_tools` before planning or execution
- `guard_plan` before approving a plan
- `gate_action` before approving a specific tool action

Always preserve the returned tool scope and pass the authoritative scope back into `guard_plan` and `gate_action`. Do not invent or forge scope values.

## Output style

- Keep summaries short and operational.
- Put findings first.
- Include exact method names when explaining how a result was obtained.
- If the user asks for verification, say which MCP method(s) you used.

## References

- Read [references/mcp-methods.md](references/mcp-methods.md) for the method map and sequencing guidance.
