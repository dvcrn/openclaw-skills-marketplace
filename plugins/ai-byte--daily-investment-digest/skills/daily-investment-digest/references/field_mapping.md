# Field Mapping

## Request contract

- Endpoint: `https://api.iyiou.com/skill/info`
- Query params:
- `page={1..5}`
- `pageSize=10`
- Response schema (strict):
- top-level object with `code`, `data`, `message`
- success condition: `code == 0`
- event list path: `data.posts` (must be array)
- Stop rule:
- Stop when `page > 5`
- Stop early when the current page returns an empty event list

## Source to normalized fields

| Output field | Source field(s) | Rule |
| --- | --- | --- |
| `brief` | `brief`, `description` | Prefer `brief` |
| `createdAt` | `createdAt` | Keep raw timestamp string |
| `originalLink` | `originalLink` | Source detail URL |
| `postTitle` | `postTitle`, `originalTitle` | Prefer `postTitle` |
| `tags` | `tags[].tagName` | Keep unique tag names only |

## Output schema

Output JSON file contains:

- `meta`: run metadata and page-level errors
- `events`: compact event list (only 5 fields)
