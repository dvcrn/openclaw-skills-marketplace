# API Reference

Base URL for this skill:

- `http://localhost:4000`

## Authentication

### Preferred: OpenClaw access key

Use this header on protected business endpoints:

```http
X-OpenClaw-Key: <access key>
```

The key is configured in ScrapeTab Settings as `openclaw_access_key`.
Do not use `OPENCLAW_SCRAPEFUN_API_KEY`. Only use `OPENCLAW_ACCESS_KEY`.
Do not use `X-OpenClaw-Api-Key`; correct header is `X-OpenClaw-Key`.

### Fallback: Admin login

- `POST /api/auth/login`

Body:

```json
{
  "username": "Admin",
  "password": "..."
}
```

Returns:

- `token`
- `expiresAt`
- `user`

Use the returned token on later protected requests:

```http
Authorization: Bearer <token>
```

## Endpoints

### Libraries

- `GET /api/libraries`

Returns list entries with fields such as:

- `id`
- `name`
- `type` (`movie` / `tv`)
- `sourceMode` (`filesystem` / `virtual_scraper`)
- `path`

### Metadata stats

- `GET /api/metadata/stats`

Response shape:

```json
{
  "total": 1234,
  "directories": {
    "Movie": 500,
    "Anime": 734
  }
}
```

Optional query:

- `paths` JSON string for explicit directory scope

### Metadata total count

- `GET /api/metadata/count`

Response shape:

```json
{
  "count": 1234
}
```

### Search

- `GET /api/scrape/search`

Common query params:

- `q`
- `scraper` (optional)
- `path` (optional)

### Match folder

- `POST /api/scrape/match-folder`

Used to match a folder path to metadata and update library records.

### Match single target

- `POST /api/scrape/match`

Used to match a single file/url to metadata.

### WebDAV scan/update

- `POST /api/scrape/webdav/scan`
- `POST /api/scrape/webdav/update`

### OpenClaw library scan (exposed operation)

- `POST /api/openclaw/libraries/scan`

Preferred payload:

```json
{
  "libraryName": "Movie"
}
```

Optional explicit payload:

```json
{
  "path": "/xunlei/迅雷云盘/媒体库/电影/",
  "scraper": "TMDB",
  "type": "movie"
}
```

### WebDAV file operations

- `POST /api/settings/webdav/move`
- `POST /api/settings/webdav/move_thunder_batch`
- `POST /api/settings/webdav/rename`

### Offline download

- `POST /api/settings/webdav/add_offline_download`

Used to submit URLs (including magnet links) through AList offline tools.

## Movie count recipe

For "how many movies":

1. Call `GET /api/libraries`.
2. Keep libraries where `type === "movie"`.
3. Call `GET /api/metadata/stats`.
4. Read `directories[library.name]` and sum values.

## Prohibited in this skill

Do not use OpenClaw-special endpoints in this skill:

- `/api/openclaw/bootstrap/status`
- `/api/openclaw/connect/context`
- `/api/openclaw/tasks/*`
- `/api/openclaw/workflows/*`
- `/api/openclaw/jobs/*`

Only exception: `POST /api/openclaw/libraries/scan`.
