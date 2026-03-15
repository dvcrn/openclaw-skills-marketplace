# ClawMemory Hub API Reference

Base URL: `https://clawmemory.ai/api/v1`

Auth: `Authorization: Bearer sk_...` header

---

## Repositories

### List my repos
```
GET /repos
```

### Create repo
```
POST /repos
Body: { "name": "string", "description": "string", "visibility": "public"|"private" }
```

### Get repo
```
GET /repos/:owner/:repo
```

### Update repo
```
PATCH /repos/:owner/:repo
Body: { "name", "description", "visibility", "allowFork" }
```

### Delete repo
```
DELETE /repos/:owner/:repo
```

### Fork repo
```
POST /repos/:owner/:repo/fork
```

---

## Commits

### List commits
```
GET /repos/:owner/:repo/commits?limit=20
```

### Create commit
```
POST /repos/:owner/:repo/commits
Body: { "message": "string", "content": { "text": "..." }, "summary": "optional" }
```

### Get commit
```
GET /repos/:owner/:repo/commits/:commitId
```

### Get commit content
```
GET /repos/:owner/:repo/commits/:commitId/content
```

---

## Memory Search

### Search commits
```
GET /repos/:owner/:repo/memory/search?q=keyword&limit=10
```

### Get memory commit
```
GET /repos/:owner/:repo/memory/commits/:commitId
```

---

## Collaborators

### List collaborators
```
GET /repos/:owner/:repo/collaborators
```

### Add collaborator
```
POST /repos/:owner/:repo/collaborators
Body: { "usernameOrEmail": "string", "canRead": true, "canUse": false, "canWrite": false }
```

### Update permissions
```
PATCH /repos/:owner/:repo/collaborators/:userId
Body: { "canRead": bool, "canUse": bool, "canWrite": bool }
```

### Remove collaborator
```
DELETE /repos/:owner/:repo/collaborators/:userId
```

---

## User

### Get current user
```
GET /user
```

### List API keys
```
GET /user/api-keys
```

### Create API key
```
POST /user/api-keys
Body: { "name": "string" }
```

### Delete API key
```
DELETE /user/api-keys/:id
```
