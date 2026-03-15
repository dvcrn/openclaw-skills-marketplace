---
name: workshop-agenda-designer
description: "Design workshops, trainings, and strategy sessions with timing, facilitation"
---

# Workshop Agenda Designer

## Purpose

Design workshops, trainings, and strategy sessions with timing, facilitation notes, activities, and follow-up artifacts.

## Trigger phrases

- 设计议程
- build a workshop agenda
- 培训大纲
- facilitation plan
- 会议流程设计

## Ask for these inputs

- session goal
- participants
- duration
- format online/offline
- decision needed
- constraints

## Workflow

1. Clarify the outcome and participant profile.
2. Break the session into opening, framing, working blocks, decision points, and close.
3. Add facilitation prompts, timeboxes, and materials checklists.
4. Generate a participant version and a facilitator-only version.
5. Include a follow-up recap and action capture template.

## Output contract

- agenda
- facilitator run-sheet
- materials checklist
- follow-up template

## Files in this skill

- Script: `{baseDir}/scripts/agenda_builder.py`
- Resource: `{baseDir}/resources/agenda_template.md`

## Operating rules

- Be concrete and action-oriented.
- Prefer preview / draft / simulation mode before destructive changes.
- If information is missing, ask only for the minimum needed to proceed.
- Never fabricate metrics, legal certainty, receipts, credentials, or evidence.
- Keep assumptions explicit.

## Suggested prompts

- 设计议程
- build a workshop agenda
- 培训大纲

## Use of script and resources

Use the bundled script when it helps the user produce a structured file, manifest, CSV, or first-pass draft.
Use the resource file as the default schema, checklist, or preset when the user does not provide one.

## Boundaries

- This skill supports planning, structuring, and first-pass artifacts.
- It should not claim that files were modified, messages were sent, or legal/financial decisions were finalized unless the user actually performed those actions.


## Compatibility notes

- Directory-based AgentSkills/OpenClaw skill.
- Runtime dependency declared through `metadata.openclaw.requires`.
- Helper script is local and auditable: `scripts/agenda_builder.py`.
- Bundled resource is local and referenced by the instructions: `resources/agenda_template.md`.
