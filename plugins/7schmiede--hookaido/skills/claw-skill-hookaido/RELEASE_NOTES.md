# Release Notes

## GitHub Release Summary

Recommended tag: `v2.0.0`

Public Hookaido skill refresh for upstream `v2.0.0`.
This update pins installer assets and checksums to the latest Hookaido release, switches the skill metadata to the public repository URL, and documents v2 features such as `queue postgres`, batch pull lease operations, gRPC pull workers, and release verification as additive guidance without changing the default workflow.

## v2.0.0 - 2026-03-09

This release updates the public Hookaido skill to upstream Hookaido `v2.0.0` and prepares the repository for distribution via its public GitHub URL.

### Highlights

- Pinned all binary installer actions to Hookaido `v2.0.0`.
- Updated the fallback installer script with the official `v2.0.0` SHA256 checksums for macOS, Linux, and Windows on `amd64` and `arm64`.
- Switched the skill homepage metadata to the public skill repository: `https://github.com/7schmiede/claw-skill-hookaido`.
- Documented source-based installation from the public upstream repo: `go install github.com/nuetzliches/hookaido/cmd/hookaido@v2.0.0`.

### Compatibility

This skill keeps the established inbound, outbound, and pull-based workflow as the default path.
Hookaido v2 capabilities are documented as additive options so existing skill usage does not receive breaking changes by default.

Additive v2 coverage includes:

- `queue postgres` as an optional backend alongside the existing defaults
- HTTP and gRPC pull-worker guidance
- Batch `ack` and batch `nack` pull operations
- `config validate --strict-secrets`
- `verify-release` for public release verification

### Documentation Updates

- Refreshed [SKILL.md](SKILL.md) to reflect Hookaido v2.0.0 terminology and workflow guidance.
- Expanded [references/operations.md](references/operations.md) with Postgres runtime examples, batch pull API calls, and release verification commands.
- Added [README.md](README.md) so the repo is ready to be consumed directly as a public skill repository.

### Notes

- Upstream modular architecture changes in Hookaido v2.0.0 are treated as opt-in guidance in this skill rather than mandatory workflow changes.
- The skill name now matches the repository folder name, which fixes skill validation in the current layout.