# @usedada/plugin

OpenClaw skill for dada — hosted backend infra for openclaw agents.

## Publishing

Publishing is a two-step process: npm (where OpenClaw pulls the package from) then ClawHub (the skill directory).

### Prerequisites

- npm granular access token with "bypass 2fa" stored in `.env` as `NPM_TOKEN`
- `clawhub` CLI authenticated

### Steps

1. Bump the version in `package.json`
2. Publish to npm:
   ```bash
   cd plugin
   echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc
   npm publish --access public
   rm .npmrc
   ```
3. Publish to ClawHub:
   ```bash
   clawhub publish plugin/ --slug usedada --name "dada" --version <version> --changelog "Description of changes"
   ```
