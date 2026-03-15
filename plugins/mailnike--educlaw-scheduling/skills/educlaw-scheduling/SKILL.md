---
name: educlaw-scheduling
description: "Master scheduling, schedule patterns, conflict resolution, and room assignment for K-12 and higher-education institutions. Sub-vertical of EduClaw SIS."
---

# EduClaw Advanced Scheduling

Advanced scheduling for K-12 and higher-education. Named schedule patterns, master
schedule lifecycle, course request demand analysis, 11 conflict types, smart room
assignment, and instructor constraints.

## Quick Start

```bash
# 1. Define a schedule pattern
python3 db_query.py --action add-schedule-pattern \
  --name "Traditional 7-Period" --pattern-type traditional --cycle-days 1 --company-id <id>
python3 db_query.py --action add-day-type \
  --schedule-pattern-id <id> --code "MON-FRI" --name "Regular Day"
python3 db_query.py --action add-bell-period \
  --schedule-pattern-id <id> --period-number 1 --period-name "Period 1" \
  --start-time "08:00" --end-time "08:50" --duration-minutes 50
python3 db_query.py --action activate-schedule-pattern --pattern-id <id>

# 2. Build and publish master schedule
python3 db_query.py --action create-master-schedule \
  --academic-term-id <id> --schedule-pattern-id <id> --name "Fall 2026" --company-id <id>
python3 db_query.py --action add-section-meeting \
  --master-schedule-id <id> --section-id <id> --day-type-id <id> --bell-period-id <id>
python3 db_query.py --action generate-conflict-check --master-schedule-id <id>
python3 db_query.py --action submit-master-schedule --master-schedule-id <id>
```

---

## Tier 1 — Core Scheduling Workflow

### `add-schedule-pattern`
Create a named, reusable schedule structure.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--name` | ✓ | Pattern name (e.g., "Traditional 7-Period") |
| `--pattern-type` | ✓ | `traditional`, `block_4x4`, `block_ab`, `trimester`, `rotating_drop`, `semester`, `custom` |
| `--cycle-days` | ✓ | Number of unique days in one cycle |
| `--company-id` | ✓ | Company ID |
| `--description` | | Human-readable description |
| `--notes` | | Internal notes |
| `--total-periods-per-cycle` | | Pre-computed total periods (informational) |

### `add-day-type`
Add a named day type to a pattern (e.g., "Day A", "Day B").

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--schedule-pattern-id` | ✓ | Parent pattern ID |
| `--code` | ✓ | Short code (e.g., "A", "B", "MON") |
| `--name` | ✓ | Display name |
| `--sort-order` | | Display order (default: 0) |

### `add-bell-period`
Add a named time slot to a pattern.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--schedule-pattern-id` | ✓ | Parent pattern ID |
| `--period-number` | ✓ | Period identifier (e.g., "1", "Block A") |
| `--period-name` | ✓ | Display name |
| `--start-time` | ✓ | HH:MM |
| `--end-time` | ✓ | HH:MM |
| `--duration-minutes` | ✓ | Duration in minutes (> 0) |
| `--period-type` | | `class` (default), `break`, `lunch`, `homeroom`, `advisory`, `flex`, `passing` |
| `--sort-order` | | Display order |
| `--applies-to-day-types` | | JSON array of day_type IDs; empty = all |

### `activate-schedule-pattern`
Activate a pattern after defining its day types and bell periods.
**Required:** `--pattern-id`

### `create-master-schedule`
Create a master schedule container for an academic term.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--academic-term-id` | ✓ | Term (unique per term) |
| `--schedule-pattern-id` | ✓ | Pattern defining days and periods |
| `--name` | ✓ | Schedule name |
| `--company-id` | ✓ | Company ID |
| `--build-notes` | | Internal building notes |

### `add-section-meeting`
Place a section into a specific day-type + period slot.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--master-schedule-id` | ✓ | Parent master schedule |
| `--section-id` | ✓ | Section from educlaw_section |
| `--day-type-id` | ✓ | Which day type |
| `--bell-period-id` | ✓ | Which period |
| `--room-id` | | Room assignment |
| `--instructor-id` | | Override section default |
| `--meeting-type` | | `regular` (default), `lab`, `exam`, `field_trip`, `make_up` |
| `--meeting-mode` | | `in_person` (default), `hybrid`, `online` |

### `generate-conflict-check`
Run all 11 conflict categories for a master schedule. **Required:** `--master-schedule-id`

Types: `instructor_double_booking` (CRITICAL), `room_double_booking` (CRITICAL),
`student_conflict` (HIGH), `instructor_overload` (HIGH), `instructor_contract_violation` (HIGH),
`capacity_exceeded` (HIGH), `singleton_overlap` (HIGH), `room_shortage` (HIGH),
`room_type_mismatch` (MEDIUM), `credential_mismatch` (MEDIUM), `contact_hours_deficit` (MEDIUM)

### `submit-master-schedule`
Publish the master schedule (blocks if open CRITICAL conflicts exist).
**Required:** `--master-schedule-id`. Opt: `--published-by`

---

## Tier 2 — Schedule Patterns & Master Schedule

`update-schedule-pattern` **Req:** `--pattern-id`. Opt: `--name`, `--description`, `--notes`
`get-schedule-pattern` **Req:** `--pattern-id`
`list-schedule-patterns` Opt: `--company-id`, `--pattern-type`, `--is-active`, `--search`, `--limit`
`get-day-type-calendar` **Req:** `--pattern-id`, `--date-range-start`, `--date-range-end`
`get-pattern-calendar` **Req:** `--pattern-id`
`get-contact-hours` **Req:** `--pattern-id`. Opt: `--section-id`, `--master-schedule-id`
`update-master-schedule` **Req:** `--master-schedule-id`. Opt: `--name`, `--build-notes`, `--schedule-status`
`get-master-schedule` Opt: `--master-schedule-id`, `--naming-series`
`list-master-schedules` Opt: `--company-id`, `--schedule-status`, `--academic-term-id`
`add-section-to-schedule` **Req:** `--master-schedule-id`, `--section-id`
`delete-section-meeting` **Req:** `--section-meeting-id`
`list-section-meetings` **Req:** `--master-schedule-id`. Opt: `--section-id`, `--day-type-id`, `--instructor-id`, `--room-id`
`get-schedule-matrix` **Req:** `--master-schedule-id`
`update-schedule-lock` **Req:** `--master-schedule-id`. Opt: `--locked-by`
`create-schedule-clone` **Req:** `--master-schedule-id`, `--target-academic-term-id`. Opt: `--name`, `--company-id`

## Tier 2 — Course Requests

`activate-course-requests` **Req:** `--academic-term-id`
`submit-course-request` **Req:** `--student-id`, `--academic-term-id`, `--course-id`. Opt: `--request-priority`, `--is-alternate`, `--alternate-for-course-id`, `--has-iep-flag`, `--prerequisite-override`, `--prerequisite-override-by`, `--prerequisite-override-note`, `--submitted-by`, `--company-id`
`approve-course-requests` **Req:** `--academic-term-id`, `--approved-by`. Opt: `--course-id`
`get-demand-report` **Req:** `--academic-term-id`
`get-singleton-analysis` **Req:** `--academic-term-id`. Opt: `--min-requests`
`get-course-demand-analysis` **Req:** `--academic-term-id`
`get-fulfillment-report` Opt: `--master-schedule-id`, `--academic-term-id`
`get-load-balance-report` **Req:** `--master-schedule-id`
`update-course-request` **Req:** `--course-request-id`. Opt: `--request-priority`, `--is-alternate`, `--has-iep-flag`
`get-course-request` **Req:** `--course-request-id`
`list-course-requests` Opt: `--student-id`, `--academic-term-id`, `--course-id`, `--request-status`
`complete-course-requests` **Req:** `--academic-term-id`

## Tier 2 — Conflict Resolution

`list-conflicts` **Req:** `--master-schedule-id`. Opt: `--conflict-type`, `--severity`, `--conflict-status`
`get-conflict` **Req:** `--conflict-id`
`complete-conflict` **Req:** `--conflict-id`, `--resolution-notes`. Opt: `--resolved-by`
`accept-conflict` **Req:** `--conflict-id` (not CRITICAL). Opt: `--resolution-notes`, `--resolved-by`
`get-conflict-summary` **Req:** `--master-schedule-id`
`get-singleton-conflict-map` **Req:** `--master-schedule-id`
`get-student-conflict-report` **Req:** `--master-schedule-id`

## Tier 2 — Room Assignment

`assign-room` **Req:** `--section-meeting-id`, `--room-id`. Opt: `--booking-type`, `--accessibility-required`, `--booked-by`
`propose-room` **Req:** `--section-meeting-id`. Opt: `--room-type`, `--accessibility-required`
`assign-rooms` **Req:** `--master-schedule-id`. Opt: `--room-type`
`delete-room-assignment` Opt: `--section-meeting-id`, `--booking-id`
`add-room-block` **Req:** `--room-id`, `--day-type-id`, `--bell-period-id`, `--booking-title`. Opt: `--booked-by`, `--booking-type`
`update-room-swap` **Req:** `--section-meeting-id` (A), `--section-meeting-id-b` (B)
`get-room-availability` **Req:** `--room-id`, `--master-schedule-id`
`get-room-utilization-report` **Req:** `--master-schedule-id`
`list-rooms-by-features` Opt: `--company-id`, `--room-type`, `--capacity`, `--building`, `--features` (JSON)
`assign-room-emergency` **Req:** `--room-id`, `--target-room-id`, `--master-schedule-id`

## Tier 3 — Instructor Constraints

`add-instructor-constraint` **Req:** `--instructor-id`, `--academic-term-id`, `--constraint-type` (`unavailable`, `preferred`, `max_periods_per_day`, `max_consecutive_periods`, `requires_prep_period`, `preferred_building`). Opt: `--day-type-id`, `--bell-period-id`, `--constraint-value`, `--constraint-notes`, `--priority` (`hard`, `soft`, `preference`)
`update-instructor-constraint` **Req:** `--constraint-id`. Opt: `--constraint-value`, `--constraint-notes`, `--priority`, `--is-active`
`list-instructor-constraints` Opt: `--instructor-id`, `--academic-term-id`, `--constraint-type`, `--is-active`
`delete-instructor-constraint` **Req:** `--constraint-id`

---

## Lifecycle Rules

**Master Schedule:** `draft → building → review → published → locked → archived`. Cannot publish with open CRITICAL conflicts. All sections → `scheduled` and term → `enrollment_open` on publish.
**Course Request:** `draft → submitted → approved → scheduled / alternate_used / unfulfilled`. Any → `withdrawn`.
**Conflict:** `open → resolving → resolved / accepted / superseded`.

## Workflows

1. **Pattern:** `add-schedule-pattern → add-day-type (×N) → add-bell-period (×N) → activate-schedule-pattern`
2. **Demand:** `activate-course-requests → submit-course-request (×N) → approve-course-requests → get-demand-report → complete-course-requests`
3. **Build:** `create-master-schedule → add-section-to-schedule (×N) → add-section-meeting (×N) → assign-room OR assign-rooms → update-master-schedule (status=review)`
4. **Publish:** `generate-conflict-check → get-conflict-summary → [complete-conflict|accept-conflict] (×N) → submit-master-schedule → update-schedule-lock`
5. **Emergency:** `get-room-availability → assign-room-emergency → generate-conflict-check`
