# Publish Pattern

Use this pattern when turning a local wrapper setup into a ClawHub skill.

## Design Rules

- The skill must target a wrapper or remote CLI contract, not bundled OpenClaw internals.
- Do not claim Linux natively supports a macOS-only tool.
- Keep the wrapper path explicit in the skill instructions.
- Store credentials outside the skill folder.
- Put node ownership in the setup section, for example:
  - `imsg` lives on `M1`
  - `remindctl` lives on `MacBook Pro`

## Recommended Contract

1. Install the wrapper with `mac-node-bridge`.
2. Verify the wrapper path works from the gateway shell.
3. Make the published skill call the wrapper by absolute path.
4. Treat the wrapper as the dependency boundary.

## Good Example

- Skill: `mac-imessage-remote`
- Setup:
  - install `/home/node/.openclaw/bin/imsg`
  - verify `/home/node/.openclaw/bin/imsg chats --limit 1`
- Runtime:
  - all message operations call `/home/node/.openclaw/bin/imsg`

## Bad Example

- Patch OpenClaw core so Linux says the bundled macOS `imsg` skill is ready
- Store SSH keys or OAuth tokens in the skill directory
- Assume every node has the same privacy permissions or Homebrew packages
