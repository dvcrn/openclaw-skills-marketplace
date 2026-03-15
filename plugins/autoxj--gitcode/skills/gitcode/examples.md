# GitCode API 示例

`YOUR_TOKEN` 即环境变量 `GITCODE_TOKEN`。

## Example 1: List current user's repositories (authenticated)

```bash
curl --location 'https://api.gitcode.com/api/v5/user/repos' \
  --header 'PRIVATE-TOKEN: YOUR_TOKEN'
```

- **200**: Returns JSON array of repositories.
- **401**: Invalid or missing token; check `PRIVATE-TOKEN` or use `Authorization: Bearer YOUR_TOKEN` instead.

---

## Example 2: List issues for a repository

```bash
curl "https://api.gitcode.com/api/v5/repos/OWNER/REPO/issues?per_page=20&page=1" \
  --header 'Authorization: Bearer YOUR_TOKEN'
```

Replace `OWNER` and `REPO` with the namespace and repository name (e.g. `myorg/my-project`). Optional: `state=open|closed|all`, `labels`, etc.

- **200**: Returns list of issues.
- **401**: Authentication required for private repos.
- **404**: Repository not found or no access.

---

## Example 3: Get issue-related branches and pull requests

```bash
# Related branches for issue #42
curl "https://api.gitcode.com/api/v5/repos/OWNER/REPO/issues/42/related_branches" \
  --header 'PRIVATE-TOKEN: YOUR_TOKEN'

# Related pull requests for issue #42
curl "https://api.gitcode.com/api/v5/repos/OWNER/REPO/issues/42/pull_requests" \
  --header 'PRIVATE-TOKEN: YOUR_TOKEN'
```

Use when the user asks for branches or PRs linked to a specific issue.
