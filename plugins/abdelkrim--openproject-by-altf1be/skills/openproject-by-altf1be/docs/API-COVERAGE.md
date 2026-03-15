# OpenProject API v3 — Coverage & Limitations

This document lists all 55 API v3 resources, what this skill covers, and what's excluded with reasons.

## ✅ Covered (13 resources)

| Resource | Commands | Notes |
|----------|----------|-------|
| `work_packages` | wp-list, wp-create, wp-read, wp-update, wp-delete | Full CRUD with filters |
| `projects` | project-list, project-read, project-create | List, read, create |
| `activities` | comment-list, comment-add | Comments on work packages |
| `attachments` | attachment-list, attachment-add, attachment-delete | Upload/delete on work packages |
| `time_entries` | time-list, time-create, time-update, time-delete | Full CRUD |
| `statuses` | status-list | List all statuses; transitions via wp-update --status |
| `types` | type-list | List work package types |
| `priorities` | priority-list | List priorities |
| `memberships` | member-list | List project members |
| `versions` | version-list | List versions/milestones |
| `categories` | category-list | List work package categories |
| `principals` | (used internally) | User/group resolution |
| `roles` | (used internally) | Role resolution in member-list |

## ❌ Not Covered — With Reasons

### Meetings (`/api/v3/meetings`)
- **Reason:** Enterprise-only feature. Requires OpenProject Enterprise edition. Not available on Community edition instances.

### Notifications (`/api/v3/notifications`)
- **Reason:** Read-only, user-specific in-app notifications. Low value for CLI automation — better consumed via OpenProject UI or email.

### Relations (`/api/v3/relations`)
- **Reason:** Work package dependency links (blocks, follows, relates to, etc.). **Candidate for future version** — useful but complex bidirectional relationships.

### Queries (`/api/v3/queries`)
- **Reason:** Saved work package filters/views. Internal to OpenProject UI. CLI users can use `wp-list` filters directly instead.

### Wiki Pages (`/api/v3/wiki_pages`)
- **Reason:** Limited API — read-only in current API v3. No create/update via REST. Would only support listing/reading.

### News (`/api/v3/news`)
- **Reason:** Read-only in API v3. No create/update/delete endpoints. Project news announcements.

### Budgets (`/api/v3/budgets`)
- **Reason:** Enterprise-only feature. Financial/cost tracking tied to Enterprise edition.

### Documents (`/api/v3/documents`)
- **Reason:** Minimal API exposure. Document management is better handled via OpenProject UI or Nextcloud/SharePoint integrations.

### Revisions (`/api/v3/revisions`)
- **Reason:** Read-only. SCM/repository changesets linked to work packages. Requires server-side SCM integration (Git/SVN).

### Groups (`/api/v3/groups`)
- **Reason:** User group management. Admin-only operation. Low value for project management CLI.

### Users (`/api/v3/users`)
- **Reason:** Admin-only CRUD. Member-list covers project-level user visibility. Full user management is an admin task.

### File Links (`/api/v3/file_links`)
- **Reason:** External storage integration (Nextcloud, OneDrive, SharePoint). Requires storage integration to be configured server-side.

### Storages & Project Storages (`/api/v3/storages`, `/api/v3/project_storages`)
- **Reason:** External file storage configuration. Admin-level setup. Not a day-to-day project management action.

### Grids (`/api/v3/grids`)
- **Reason:** Dashboard/widget layout configuration. Internal to OpenProject UI rendering. No CLI use case.

### Views (`/api/v3/views`)
- **Reason:** Saved work package views (Gantt, board, etc.). Internal to OpenProject UI. No CLI equivalent.

### Custom Actions (`/api/v3/custom_actions`)
- **Reason:** Server-side workflow automation triggers. Read-only via API. Configured in admin settings.

### Custom Fields & Options (`/api/v3/custom_fields`, `/api/v3/custom_field_items`, `/api/v3/custom_options`)
- **Reason:** Schema configuration for custom fields. Admin-only setup. Custom field *values* are handled via wp-create/wp-update.

### Help Texts (`/api/v3/help_texts`)
- **Reason:** Attribute help text configuration. Admin-only. No project management use case.

### Placeholder Users (`/api/v3/placeholder_users`)
- **Reason:** Enterprise-only. Virtual users for resource planning before real users are assigned.

### Capabilities & Actions (`/api/v3/capabilities`, `/api/v3/actions`)
- **Reason:** Permission introspection. Internal framework resource. Used by OpenProject UI for dynamic permission checks.

### Configuration (`/api/v3/configuration`)
- **Reason:** Instance-level settings. Read-only. Admin information.

### OAuth (`/api/v3/oauth_applications`, `/api/v3/oauth_client_credentials`)
- **Reason:** OAuth app management. Admin setup task, not project management.

### My Preferences (`/api/v3/my_preferences`)
- **Reason:** Personal UI preferences. Not relevant for project management automation.

### Render (`/api/v3/render`)
- **Reason:** Textile/Markdown rendering utility endpoint. Used internally by OpenProject editor.

### Days (`/api/v3/days`)
- **Reason:** Working days/non-working days configuration. Calendar configuration, admin-level.

### Posts (`/api/v3/posts`)
- **Reason:** Forum posts. Limited API, legacy feature in OpenProject.

### Reminders (`/api/v3/reminders`)
- **Reason:** User-specific notification reminders. Personal notification settings.

### Portfolios & Programs (`/api/v3/portfolios`, `/api/v3/programs`)
- **Reason:** Enterprise-only. Portfolio/program management for multi-project oversight.

### Project Phases & Definitions (`/api/v3/project_phases`, `/api/v3/project_phase_definitions`)
- **Reason:** Enterprise-only. Project lifecycle phase tracking.

### Project Statuses (`/api/v3/project_statuses`)
- **Reason:** Project-level health statuses (on track, at risk, off track). Read-only reference data, low CLI value.

### Workspace & Workspaces (`/api/v3/workspace`, `/api/v3/workspaces`)
- **Reason:** Instance/workspace info. Read-only metadata.

### Values (`/api/v3/values`)
- **Reason:** Internal value resolution endpoint. Framework utility, not a user-facing resource.

### Example & Examples (`/api/v3/example`, `/api/v3/examples`)
- **Reason:** API documentation examples. Not real resources.

## 🔮 Candidates for Future Versions

| Resource | Priority | Why |
|----------|----------|-----|
| Relations | High | Dependency tracking (blocks, follows, etc.) is very useful for project management |
| Wiki Pages | Medium | If API adds write support in the future |
| Users | Medium | If user lookup/search is needed beyond member-list |
| Notifications | Low | Could be useful for monitoring, but mostly a UI concern |
| News | Low | If write API becomes available |

## Enterprise-Only Features (Not Available on Community Edition)

These require an OpenProject Enterprise license:
- Meetings
- Budgets
- Placeholder Users
- Portfolios & Programs
- Project Phases

---

*Based on OpenProject API v3 specification (55 resources, 193 endpoints)*
*Last updated: 2026-03-09*
