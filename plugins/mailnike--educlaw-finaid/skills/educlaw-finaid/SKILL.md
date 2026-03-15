---
name: educlaw-finaid
description: "Federal, state, and institutional financial aid management with Title IV compliance. ISIR processing, SAP evaluation, R2T4 calculations, award packaging, disbursements, COD origination, scholarships, work-study, and loan tracking."
---

# EduClaw Financial Aid

Federal, state, and institutional financial aid management. Full Title IV lifecycle
from ISIR import through disbursement, SAP evaluation, R2T4 return calculations,
professional judgment, COD origination, scholarships, work-study, and loan tracking.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **Fully offline**: No external API calls, no telemetry, no cloud dependencies
- **No credentials required**: Uses erpclaw_lib shared library (installed by erpclaw)
- **SQL injection safe**: All queries use parameterized statements
- **FERPA compliant**: Student financial data access is logged
- **Title IV compliance**: ISIR, SAP, R2T4, and COD records follow federal regulations. COD origination records are generated locally for export.

## Quick Start

```bash
# 1. Set up aid year
python3 db_query.py --action add-aid-year \
  --aid-year-code "2025-2026" --start-date 2025-07-01 --end-date 2026-06-30 \
  --pell-max-award 7395 --company-id <id>
python3 db_query.py --action import-pell-schedule --aid-year-id <id> --rows '<json>'

# 2. Import ISIR and create award package
python3 db_query.py --action import-isir --student-id <id> --aid-year-id <id> \
  --transaction-number 1 --receipt-date 2025-02-15 --sai -1500
python3 db_query.py --action create-award-package --student-id <id> \
  --aid-year-id <id> --isir-id <id> --cost-of-attendance-id <id>

# 3. Add awards and disburse
python3 db_query.py --action add-award --award-package-id <id> \
  --aid-type grant --aid-source federal --offered-amount 7395
python3 db_query.py --action submit-award-offer --id <id>
python3 db_query.py --action record-award-disbursement --award-id <id> --amount 3697.50
```

## Tier 1 — Daily Operations

### Aid Year & Fund Setup
| Action | Description |
|--------|-------------|
| `add-aid-year` | Create an aid year with Pell max award |
| `update-aid-year` | Update aid year dates and parameters |
| `activate-aid-year` | Activate aid year for packaging |
| `get-aid-year` | Get aid year details |
| `list-aid-years` | List all aid years |
| `import-pell-schedule` | Import Pell disbursement schedule |
| `list-pell-schedule` | List Pell schedule rows |
| `add-fund-allocation` | Create fund allocation (Pell, SEOG, etc.) |
| `update-fund-allocation` | Update allocation amounts |
| `get-fund-allocation` | Get fund details |
| `list-fund-allocations` | List fund allocations for aid year |

### Cost of Attendance
| Action | Description |
|--------|-------------|
| `add-cost-of-attendance` | Define COA by enrollment/living status |
| `update-cost-of-attendance` | Update COA components |
| `delete-cost-of-attendance` | Remove COA record |
| `get-cost-of-attendance` | Get COA details |
| `list-cost-of-attendance` | List COA records for aid year |

### ISIR Processing
| Action | Description |
|--------|-------------|
| `import-isir` | Import ISIR with SAI, dependency, C-flags |
| `complete-isir-review` | Mark ISIR as reviewed |
| `update-isir` | Update ISIR fields after correction |
| `get-isir` | Get ISIR details |
| `list-isirs` | List ISIRs for student/aid year |
| `add-isir-cflag` | Add C-flag comment code |
| `complete-isir-cflag` | Resolve a C-flag |
| `list-isir-cflags` | List C-flags for an ISIR |

## Tier 2 — Award Packaging & Verification

### Verification
| Action | Description |
|--------|-------------|
| `create-verification-request` | Create verification with required docs |
| `add-verification-document` | Add document to verification request |
| `update-verification-document` | Update document submission status |
| `update-verification-request` | Update verification request |
| `complete-verification` | Mark verification complete |
| `get-verification-request` | Get verification details |
| `list-verification-requests` | List verification requests |
| `list-verification-documents` | List documents for request |

### Award Packaging
| Action | Description |
|--------|-------------|
| `create-award-package` | Create award package for student |
| `update-award-package` | Update package details |
| `submit-award-offer` | Offer package to student |
| `cancel-award-package` | Cancel an award package |
| `get-award-package` | Get package details with awards |
| `list-award-packages` | List packages for student/aid year |
| `add-award` | Add individual award to package |
| `update-award` | Update award amounts |
| `accept-award` | Student accepts an award |
| `deny-award` | Student declines an award |
| `delete-award` | Remove unapproved award |
| `get-award` | Get award details |
| `list-awards` | List awards in package |

### Disbursements
| Action | Description |
|--------|-------------|
| `record-award-disbursement` | Disburse funds for an award |
| `cancel-disbursement` | Reverse a disbursement |
| `record-credit-balance-return` | Mark credit balance returned to student |
| `get-disbursement` | Get disbursement details |
| `list-disbursements` | List disbursements for package/award |

## Tier 3 — SAP, R2T4, COD & Professional Judgment

### SAP (Satisfactory Academic Progress)
| Action | Description |
|--------|-------------|
| `generate-sap-evaluation` | Evaluate SAP for a student |
| `generate-sap-batch` | Batch SAP evaluation |
| `apply-sap-override` | Override SAP status |
| `get-sap-evaluation` | Get SAP evaluation details |
| `list-sap-evaluations` | List SAP evaluations |
| `submit-sap-appeal` | Submit SAP appeal with academic plan |
| `complete-sap-appeal` | Approve or deny SAP appeal |
| `update-sap-appeal` | Update appeal details |
| `get-sap-appeal` | Get appeal details |
| `list-sap-appeals` | List SAP appeals |

### R2T4 (Return of Title IV)
| Action | Description |
|--------|-------------|
| `create-r2t4` | Create R2T4 calculation for withdrawn student |
| `generate-r2t4-calculation` | Execute R2T4 calculation |
| `approve-r2t4` | Approve R2T4 result |
| `record-r2t4-return` | Record institutional return |
| `record-r2t4-return-disbursement` | Record return disbursement |
| `get-r2t4` | Get R2T4 calculation details |
| `list-r2t4s` | List R2T4 calculations |

### COD (Common Origination & Disbursement)
| Action | Description |
|--------|-------------|
| `generate-cod-origination` | Generate COD origination record |
| `update-cod-origination-status` | Update origination status |
| `generate-cod-export` | Generate COD export batch |
| `update-cod-status` | Update COD response status |

### Professional Judgment
| Action | Description |
|--------|-------------|
| `add-professional-judgment` | Create PJ request with documentation |
| `approve-professional-judgment` | Approve PJ with supervisor review |
| `get-professional-judgment` | Get PJ details |
| `list-professional-judgments` | List PJ requests |

### Scholarships
| Action | Description |
|--------|-------------|
| `add-scholarship-program` | Create scholarship program |
| `update-scholarship-program` | Update program criteria |
| `terminate-scholarship-program` | Deactivate program |
| `get-scholarship-program` | Get program details |
| `list-scholarship-programs` | List scholarship programs |
| `submit-scholarship-application` | Submit student application |
| `complete-scholarship-review` | Review application |
| `approve-scholarship-application` | Award scholarship to applicant |
| `deny-scholarship-application` | Deny application |
| `update-scholarship-application` | Update application |
| `get-scholarship-application` | Get application details |
| `list-scholarship-applications` | List applications |
| `generate-scholarship-renewal` | Evaluate renewal eligibility |
| `list-scholarship-renewals` | List renewal evaluations |
| `generate-scholarship-matches` | Auto-match students to programs |

### Work-Study
| Action | Description |
|--------|-------------|
| `add-work-study-job` | Create work-study position |
| `update-work-study-job` | Update job details |
| `terminate-work-study-job` | Close position |
| `get-work-study-job` | Get job details |
| `list-work-study-jobs` | List work-study positions |
| `assign-student-to-job` | Assign student to position |
| `update-work-study-assignment` | Update assignment |
| `terminate-work-study-assignment` | End assignment |
| `get-work-study-assignment` | Get assignment details |
| `list-work-study-assignments` | List assignments |
| `submit-work-study-timesheet` | Submit timesheet |
| `approve-work-study-timesheet` | Approve timesheet |
| `deny-work-study-timesheet` | Reject timesheet |
| `update-work-study-timesheet` | Update timesheet |
| `get-work-study-timesheet` | Get timesheet details |
| `list-work-study-timesheets` | List timesheets |
| `get-work-study-earnings-summary` | Get earnings summary |
| `generate-payroll-export` | Export payroll data |

### Loan Tracking
| Action | Description |
|--------|-------------|
| `add-loan` | Track a student loan |
| `update-loan` | Update loan details |
| `get-loan` | Get loan details |
| `list-loans` | List student loans |
| `get-loan-limits-status` | Check aggregate loan limits |
| `update-mpn-status` | Update MPN status |
| `update-entrance-counseling` | Update entrance counseling status |
| `update-exit-counseling` | Update exit counseling status |
| `generate-cod-origination` | Generate COD loan origination |
| `update-cod-origination-status` | Update COD origination response |

## Compliance

- **Title IV**: Full ISIR→packaging→disbursement→R2T4 lifecycle
- **FAFSA**: SAI-based Pell calculation, C-flag resolution, verification
- **SAP**: Quantitative + qualitative + pace evaluation with appeal workflow
- **R2T4**: 34 CFR 668.22 compliant percentage-based calculations
- **COD**: Origination and disbursement record generation
- **FERPA**: Student financial data access logging
