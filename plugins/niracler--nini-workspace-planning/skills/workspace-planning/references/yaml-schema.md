# Schedule YAML Schema Reference

## Complete Example

```yaml
project: my-project
title: My Project 显示名称

timeline:
  start: 2026-03-09
  end: 2026-06-01

capacity:                       # optional
  backend:
    days_per_week: 3
    notes: "周一/二/四"
  frontend:
    days_per_week: 5

milestones:
  - id: demo                    # kebab-case
    title: 进度同步
    date: 2026-04-03            # ISO date
    type: demo                  # demo | usable | release
    deliverable: "登录注册 + 项目管理 UI 原型"

phases:                         # optional
  - id: month-1
    title: 基础框架
    start: 2026-03-09
    end: 2026-04-03
    weeks: [W1, W2, W3, W4]

modules:
  # Infrastructure module (backend-only, no UI frames)
  - id: core-extraction
    title: srhome-core 代码提取
    type: infrastructure
    phase: month-1
    weeks: [W1, W2, W3, W4]
    status: planned             # planned | in_progress | done | deferred
    description: "从 sunlite-backend 提取共享代码到 srhome-core"
    yunxiao_id: null             # optional, populated by sync-yunxiao
    changes: []                 # optional, populated by planning link

  # Feature module (has UI frames, frontend/backend dependencies)
  - id: auth
    title: 登录与注册
    type: feature
    phase: month-1
    weeks: [W2, W3]
    status: in_progress
    priority: P1                # P1 | P2 | P3
    frames: 14
    design: OK                  # OK | partial | pending
    figma: "https://www.figma.com/design/..."
    backend:
      ready_week: W3
      apis: "Auth API（JWT, 注册, 邮箱验证）"
    frontend:
      mock_from: W1
      notes: "optional notes"
    yunxiao_id: "WI-12345"
    changes: ["add-auth-api"]
```

## Field Reference

### Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `project` | string | kebab-case identifier |
| `title` | string | Display name |
| `timeline.start` | date | Project start date (ISO) |
| `timeline.end` | date | Project end date (ISO) |
| `milestones` | list | Milestone definitions |
| `modules` | list | Module definitions |

### Optional Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `capacity` | object | Team capacity config |
| `phases` | list | Phase definitions |

### Module Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | kebab-case unique identifier |
| `title` | string | Display name |
| `type` | enum | `feature` or `infrastructure` |
| `phase` | string | Reference to phase id |
| `weeks` | list | Weeks this module spans (e.g. [W1, W2]) |
| `status` | enum | `planned`, `in_progress`, `done`, `deferred` |

### Feature-Only Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `priority` | enum | `P1`, `P2`, `P3` |
| `frames` | int | Number of Figma frames |
| `design` | enum | `OK`, `partial`, `pending` |
| `figma` | string | Figma URL |
| `backend.ready_week` | string | Week when backend API is ready |
| `backend.apis` | string | Backend API description |
| `frontend.mock_from` | string | Week when frontend can start with mocks |
| `frontend.notes` | string | Frontend notes |

### Shared Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Module description (useful for infrastructure) |
| `yunxiao_id` | string | Yunxiao work item ID |
| `changes` | list | Associated OpenSpec change names |

## Status Transitions

```text
planned ──▶ in_progress ──▶ done
   │
   └──▶ deferred ──▶ planned / in_progress
```

`done` is terminal — no transitions out of `done`.
