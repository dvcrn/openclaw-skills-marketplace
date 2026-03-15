---
name: educlaw-statereport
description: "EduClaw State Reporting — State reporting, Ed-Fi integration, data validation, and submission tracking for K-12 LEAs. Transforms operational EduClaw data into compliant state/federal reporting submissions (Ed-Fi ODS/API, EDFacts, CRDC, IDEA 618)."
---

# EduClaw State Reporting

State reporting, Ed-Fi API integration, data validation, and submission tracking
for K-12 Local Education Agencies (LEAs).

## Security Model

- **Local-only data**: All records stored in `~/.openclaw/erpclaw/data.sqlite`
- **Fully offline by default**: No network activity during data entry, validation, snapshot, or submission tracking
- **No credentials required for core operations**: Uses erpclaw_lib shared library (installed by erpclaw)
- **SQL injection safe**: All queries use parameterized statements
- **Ed-Fi sync is opt-in**: The `submit-*-to-edfi` and `get-edfi-connection-test` actions make outbound HTTPS calls to a configured ODS endpoint only when explicitly invoked. These are the sole source of external network activity.
- **Credential protection**: OAuth client secrets are encrypted before database insertion. Decrypted values are never returned in action output, logs, or error messages.

## Quick Reference

### Tier 1 — Daily Operations

| Action | Description |
|--------|-------------|
| `add-student-supplement` | Create state reporting supplement (race, SSID, EL/SPED flags) for a student |
| `assign-ssid` | Record state-assigned SSID; sets ssid_status='assigned' |
| `update-student-race` | Set race/ethnicity; auto-computes federal rollup per OMB rules |
| `update-el-status` | Update EL flags (is_el, el_entry_date, home_language_code) |
| `update-sped-status` | Update SPED flags (is_sped, is_504, sped_entry_date) |
| `add-discipline-incident` | Create discipline incident (INC-YYYY-NNNNN naming series) |
| `add-discipline-student` | Add student to incident; auto-populates IDEA/504 flags |
| `add-discipline-action` | Add disciplinary action; auto-sets mdr_required for IDEA students |
| `apply-validation` | Execute all active rules for a collection window |
| `list-submission-errors` | List open errors by window, severity, category |
| `update-error-resolution` | Mark error resolved/deferred with method and notes |

### Tier 2 — Collection Window Management

| Action | Description |
|--------|-------------|
| `add-collection-window` | Define a new state reporting collection window |
| `apply-window-status` | Move window through lifecycle (upcoming→open→…→certified) |
| `create-snapshot` | Freeze data: creates sr_snapshot + sr_snapshot_record rows |
| `add-submission` | Record a submission attempt (initial/amendment) |
| `approve-submission` | Certify accuracy; atomically updates submission+snapshot+window |
| `create-amendment` | Create amendment linked to original; re-opens window |
| `get-error-dashboard` | Error counts by severity × category × resolution_status |
| `assign-errors` | Assign multiple errors to staff in one operation |
| `generate-ada` | Calculate ADA/ADM for a period |
| `get-ada-dashboard` | ADA with funding impact calculation |
| `list-chronic-absenteeism` | Flag students with ≥10% absent days |

### Tier 3 — Ed-Fi Integration & Reports

| Action | Description |
|--------|-------------|
| `add-edfi-config` | Create Ed-Fi ODS connection profile; encrypts OAuth secret |
| `get-edfi-connection-test` | Test OAuth + ODS connectivity; records last_tested_at |
| `add-org-mapping` | Map LEA/school to NCES and Ed-Fi identifiers |
| `import-descriptor-mappings` | Upsert multiple code→URI descriptor mappings |
| `submit-student-to-edfi` | Push Student + SEOrgAssociation payload |
| `submit-enrollment-to-edfi` | Push StudentSchoolAssociation records |
| `submit-attendance-to-edfi` | Push StudentSchoolAttendanceEvent records |
| `submit-sped-to-edfi` | Push StudentSpecialEducationProgramAssociation |
| `submit-el-to-edfi` | Push StudentLanguageInstructionProgramAssociation |
| `submit-discipline-to-edfi` | Push DisciplineIncident records |
| `submit-staff-to-edfi` | Push Staff + StaffSchoolAssociation records |
| `submit-failed-syncs` | Re-queue all error/retry sync entries for a window |
| `import-validation-rules` | Load 57 built-in federal validation rules |
| `generate-enrollment-report` | Enrollment by race/grade/subgroup with suppression |
| `generate-crdc-report` | CRDC-formatted counts by race/sex/disability |
| `get-data-readiness-report` | Data completeness score per category (0-100) |
| `generate-submission-package` | Full snapshot+records JSON for audit defense |

---

## All Actions Index

Complete index of all 98 actions across 6 domains. All names use standard kebab-case
prefixes per ClawHub naming convention.

| Action | Domain | Description |
|--------|--------|-------------|
| `add-student-supplement` | demographics | Create state reporting supplement for a student |
| `update-student-supplement` | demographics | Update supplement fields; recomputes race_federal_rollup |
| `get-student-supplement` | demographics | Get supplement by student_id or supplement_id |
| `list-student-supplements` | demographics | List supplements with filters |
| `assign-ssid` | demographics | Record state-assigned SSID |
| `update-student-race` | demographics | Set race/ethnicity; auto-computes federal rollup |
| `update-el-status` | demographics | Update EL flags |
| `update-sped-status` | demographics | Update SPED flags |
| `update-economic-status` | demographics | Update economic disadvantage flag |
| `add-sped-placement` | demographics | Add SPED placement record |
| `update-sped-placement` | demographics | Update SPED placement fields |
| `get-sped-placement` | demographics | Get SPED placement by student_id + school_year |
| `list-sped-placements` | demographics | List SPED placements with filters |
| `add-sped-service` | demographics | Add related service to a SPED placement |
| `update-sped-service` | demographics | Update service fields |
| `list-sped-services` | demographics | List SPED services |
| `delete-sped-service` | demographics | Delete a service record |
| `add-el-program` | demographics | Record EL program enrollment |
| `update-el-program` | demographics | Update EL program fields |
| `get-el-program` | demographics | Get EL program record |
| `list-el-programs` | demographics | List EL programs with filters |
| `add-discipline-incident` | discipline | Create discipline incident |
| `update-discipline-incident` | discipline | Update incident fields |
| `get-discipline-incident` | discipline | Get incident with students and actions |
| `list-discipline-incidents` | discipline | List incidents with filters |
| `delete-discipline-incident` | discipline | Delete incident (only if no students attached) |
| `add-discipline-student` | discipline | Add student to incident |
| `update-discipline-student` | discipline | Update student role or IDEA/504 flags |
| `delete-discipline-student` | discipline | Remove student from incident |
| `list-discipline-students` | discipline | List all students for an incident |
| `add-discipline-action` | discipline | Add disciplinary action |
| `update-discipline-action` | discipline | Update action fields including MDR outcome |
| `record-mdr-outcome` | discipline | Record MDR outcome |
| `get-discipline-action` | discipline | Get a specific disciplinary action |
| `list-discipline-actions` | discipline | List actions with filters |
| `get-discipline-summary` | discipline | CRDC-formatted discipline summary |
| `add-edfi-config` | ed_fi | Create Ed-Fi ODS connection profile |
| `update-edfi-config` | ed_fi | Update ODS URL, OAuth credentials |
| `get-edfi-config` | ed_fi | Get Ed-Fi config (no decrypted secret) |
| `list-edfi-configs` | ed_fi | List configs with filters |
| `get-edfi-connection-test` | ed_fi | Test OAuth token fetch; records last_tested_at |
| `add-org-mapping` | ed_fi | Map LEA/school to NCES and Ed-Fi identifiers |
| `update-org-mapping` | ed_fi | Update NCES/Ed-Fi identifiers |
| `get-org-mapping` | ed_fi | Get org mapping |
| `list-org-mappings` | ed_fi | List org mappings for a company |
| `add-descriptor-mapping` | ed_fi | Add a code → Ed-Fi descriptor URI mapping |
| `update-descriptor-mapping` | ed_fi | Update descriptor URI |
| `import-descriptor-mappings` | ed_fi | Upsert multiple descriptor mappings from JSON array |
| `list-descriptor-mappings` | ed_fi | List descriptor mappings for a config |
| `delete-descriptor-mapping` | ed_fi | Delete a descriptor mapping |
| `submit-student-to-edfi` | ed_fi | Push Student + SEOrgAssociation payload |
| `submit-enrollment-to-edfi` | ed_fi | Push StudentSchoolAssociation records |
| `submit-attendance-to-edfi` | ed_fi | Push StudentSchoolAttendanceEvent records |
| `submit-sped-to-edfi` | ed_fi | Push StudentSpecialEducationProgramAssociation |
| `submit-el-to-edfi` | ed_fi | Push StudentLanguageInstructionProgramAssociation |
| `submit-discipline-to-edfi` | ed_fi | Push DisciplineIncident records |
| `submit-staff-to-edfi` | ed_fi | Push Staff + StaffSchoolAssociation records |
| `get-edfi-sync-log` | ed_fi | Get sync log entries |
| `list-edfi-sync-errors` | ed_fi | List failed/pending sync entries |
| `submit-failed-syncs` | ed_fi | Re-attempt all error/retry sync entries |
| `add-collection-window` | state_reporting | Define a new reporting collection window |
| `update-collection-window` | state_reporting | Update window dates/config |
| `get-collection-window` | state_reporting | Get window with error counts and snapshot summary |
| `list-collection-windows` | state_reporting | List windows with filters |
| `apply-window-status` | state_reporting | Move window through lifecycle |
| `create-snapshot` | state_reporting | Freeze data into snapshot |
| `get-snapshot` | state_reporting | Get snapshot summary |
| `list-snapshot-records` | state_reporting | Get student-level snapshot records |
| `generate-ada` | state_reporting | Calculate ADA/ADM |
| `get-ada-dashboard` | state_reporting | ADA with trend and funding impact |
| `list-chronic-absenteeism` | state_reporting | Flag students with ≥10% absent days |
| `get-data-readiness-report` | state_reporting | Data completeness score per category (0-100) |
| `generate-enrollment-report` | state_reporting | Enrollment by race/grade/subgroup |
| `generate-crdc-report` | state_reporting | CRDC-formatted counts by race/sex/disability |
| `add-validation-rule` | data_validation | Add a validation rule to the library |
| `update-validation-rule` | data_validation | Update rule SQL, message template, or metadata |
| `get-validation-rule` | data_validation | Get rule by ID or code |
| `list-validation-rules` | data_validation | List rules with filters |
| `update-validation-rule-status` | data_validation | Activate or deactivate a rule |
| `import-validation-rules` | data_validation | Load 57 built-in federal validation rules |
| `apply-validation` | data_validation | Execute all active rules for a collection window |
| `apply-student-validation` | data_validation | Run all rules for a single student |
| `get-validation-results` | data_validation | Get validation results with summary counts |
| `assign-submission-error` | data_validation | Assign error to a staff member |
| `update-error-resolution` | data_validation | Mark error resolved/deferred |
| `list-submission-errors` | data_validation | List errors for a window |
| `get-error-dashboard` | data_validation | Error counts by severity × category × resolution_status |
| `assign-errors` | data_validation | Assign multiple errors to a staff member |
| `submit-error-escalation` | data_validation | Escalate to state help desk with ticket ID |
| `add-submission` | submission_tracking | Record a new submission attempt |
| `update-submission-status` | submission_tracking | Update submission status |
| `get-submission` | submission_tracking | Get submission with snapshot and error counts |
| `list-submissions` | submission_tracking | List submissions for a company |
| `approve-submission` | submission_tracking | Certify accuracy; atomically updates submission + snapshot |
| `create-amendment` | submission_tracking | Create amendment linked to original |
| `get-submission-history` | submission_tracking | Full chronological submission history |
| `generate-submission-package` | submission_tracking | Full snapshot+records JSON for audit defense |
| `get-submission-audit-trail` | submission_tracking | Complete audit trail |

---

## Invariants

| Domain | Invariant |
|--------|-----------|
| Demographics | One `sr_student_supplement` per `educlaw_student` (UNIQUE) |
| Demographics | `race_federal_rollup` computed from is_hispanic_latino + race_codes |
| Demographics | One `sr_sped_placement` per student per school_year |
| Discipline | `mdr_required=1` auto-set for IDEA student + days_removed > 10 |
| Ed-Fi | `oauth_client_secret_encrypted` never stored in plaintext |
| State Reporting | Cannot advance to snapshot if critical open errors exist |
| State Reporting | `sr_snapshot_record` is INSERT-only (no UPDATE/DELETE) |
| Submission | `approve-submission` atomically updates submission + snapshot + window |
| Validation | `rule_code` is globally UNIQUE |
| All | `company_id` is never NULL |

