# claw-skill-hookaido

Public OpenClaw skill repository for Hookaido.

Repository link for skill distribution:

- `https://github.com/7schmiede/claw-skill-hookaido`

Upstream Hookaido project:

- `https://github.com/nuetzliches/hookaido`

This skill is pinned to Hookaido `v2.0.0` and keeps existing inbound/outbound/pull workflows as the default path.
New v2 capabilities such as `queue postgres`, gRPC pull workers, batch `ack`/`nack`, and release verification are documented as additive modules so existing usage does not receive breaking changes by default.

Main files:

- `SKILL.md` for skill metadata and operating guidance
- `references/operations.md` for install, runtime, and API command examples
- `scripts/install_hookaido.sh` for pinned release-binary installation with SHA256 verification
- `RELEASE_NOTES.md` for the current public skill release summary