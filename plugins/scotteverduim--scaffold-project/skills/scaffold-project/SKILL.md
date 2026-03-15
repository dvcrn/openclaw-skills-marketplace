---
name: scaffold-project
description: "Scaffold Project"
---

# scaffold-project

Create a new project structure inside the mission-control workspace.

## Allowed path
~/.openclaw-workspace/projects/mission-control

## What this skill does
- Creates folders
- Creates base files
- Initializes project structure

## Default structure
When called, create:

projects/mission-control/
 ├─ frontend/
 ├─ backend/
 ├─ database/
 ├─ integrations/
 ├─ marketing/
 └─ README.md

## Instructions
1. Check if the folder exists
2. If not, create the folder structure
3. Create README.md describing the project
4. Return a list of created files
