# Reproduction Notes

## Suspected Bug

`selectDefaultFilePath` in `src/lib/diffing.ts` only checks for `skill.md`, not `skills.md`.
Every other part of the codebase checks for both filenames, but this function was missed.

## Reproduction Steps

1. Publish v1 of this skill with `SKILL.md` (current version)
2. Rename `SKILL.md` → `SKILLS.md` and publish v2
3. View the diff between v1 and v2 on ClawHub

## Expected Behaviour

The diff view defaults to showing `SKILLS.md`.

## Actual Behaviour (suspected)

The diff view defaults to `notes.md` (or another file) instead of `SKILLS.md`,
because `selectDefaultFilePath` doesn't recognise the plural filename.
