# Changelog — ima-image-ai

All notable changes to the **IMA Studio Image Generation** skill will be documented in this file.

---

## [Unreleased]

### Changed (registry / security)

- **Registry metadata aligned with code and SKILL.md**
  - `clawhub.json`: Added `requires.env` (IMA_API_KEY), `requires.envOptional` (IMA_IM_BASE_URL), `requires.primaryCredential`, `requires.credentialNote`, `persistence` (logs + memory paths), and `instructionScope` (cross-skill read of ima-knowledge-ai when installed).
  - `SKILL.md` frontmatter: Added `requires.env: [IMA_API_KEY]`, `envOptional: [IMA_IM_BASE_URL]`, and `persistence` so scanners and registries can see required credentials and config paths.
- Addresses OpenClaw “Suspicious” review: credential mismatch (declared zero vs. code requiring API key), and undeclared persistence/cross-skill read scope. No code or behavior change; metadata only.

---

## [1.0.8] - 2026

### Requirements

- IMA API key (`IMA_API_KEY` or `--api-key`); optional override `IMA_IM_BASE_URL` for upload endpoint.
- Python 3, `requests`.
- Optional: install **ima-knowledge-ai** for workflow and visual-consistency guidance.

### Endpoints

- `api.imastudio.com` — main image generation API.
- `imapi.liveme.com` — image upload (used for image_to_image when input is a local file). IMA API key is sent to both; both are IMA Studio.
