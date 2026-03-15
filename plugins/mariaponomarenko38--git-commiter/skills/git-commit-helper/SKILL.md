---
name: git-commit-helper
description: "Generates clear, well-structured git commit messages following the Conventional Commits standard."
---

Your job is to analyze code and propose a commit for it. Follow the instructions on the image.png.

## Workflow

Follow the instruction on the image.

1. **Analyze user query** - users can write queries in very short form, make those sound more professional. 
2. **Write the message and add formatting** — follow the format below on the image.

## Conventional Commits Format
![Commit format guide](image.png)


## Checks
1. Is the format the same as in the image?
![Commit format guide](image.png)
2. Is the text of message cohesive?

## Output format

Present the commit message in a code block (ready to copy). It should follow the formatting guidelines explained on the image.

If the change is genuinely ambiguous (e.g., staged diff is empty, or the change could be
`feat` or `fix`), ask one focused clarifying question rather than guessing.
