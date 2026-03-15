# ConvoAI Sample Repos

Use this registry when the user needs a sample app, a reference project structure, or a known
repository for ConvoAI integration work.

Default rule:
- `sample-aligned` is the default implementation mode when a listed repo matches the user's stack or requested structure.
- `minimal-custom` may only be used if the user explicitly asks for a minimal demo or says not to follow the sample repo.
- Fall back to Shengwang doc fetching only when the repo does not cover the needed API detail or is not useful for the user's question.

Alignment rules:
- Preserve sample env var names from the cloned repo's env template files unless the user explicitly asks to rename or normalize them.
- Preserve the sample repo's folder structure, dependency choices, and API shape by default.
- If the sample repo already uses official SDKs or agent libraries for the needed flow, keep that path instead of replacing it with handwritten REST calls.
- Apply a tight diff budget: change only what is required for the user's confirmed provider choices and requested functionality.
- Before editing code, state which sample repo is being followed, which env template files were inspected, and list the exact planned differences.

Maintenance rules:
- Keep repo URLs here only. Other ConvoAI docs should link to this file instead of repeating URLs.
- Store repo root URLs only.
- Keep descriptions short and stable. Store only the structural fields that must be preserved during implementation.

Usage workflow:
1. Pick the row that matches the user's platform or implementation goal.
2. Clone the repo on demand with `git clone --depth 1 <repo-url>`.
3. Inspect the repo to confirm its current stack, folder map, entrypoints, env template files, and API surface.
4. Use the cloned repo's actual env template files as the source of truth for env naming.
5. Prefer the official SDKs, agent libraries, and dependency patterns already present in the sample repo over handwritten REST calls.
6. If the repo does not answer the question, fetch Shengwang docs for the missing API or product details.
7. Keep the implementation structurally close to the sample unless the user explicitly requests `minimal-custom`.

| Sample | Repo URL | Default Stack | Backend Entrypoint | Frontend Entrypoint | Use When |
|--------|----------|---------------|--------------------|---------------------|----------|
| ConvoAI web quickstart | https://gitee.com/agoraio-community/conversational-ai-quickstart | Monorepo with Bun scripts, `web-client` on Next.js 16 + React 19 + TypeScript, and `server-python` on FastAPI/Python | `server-python/src/server.py` | `web-client/app/page.tsx` | The user wants a ConvoAI web app structure reference, starter layout, or frontend/backend shape that stays close to the official quickstart |
