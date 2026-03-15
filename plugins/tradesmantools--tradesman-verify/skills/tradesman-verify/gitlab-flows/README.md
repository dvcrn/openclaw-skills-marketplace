# GitLab Duo Workflow Specs — tradesman-verify

Four canonical workflow templates for construction/trades operations teams using
`tradesman-verify` as their contractor credential backbone.

## Requirements

- GitLab Premium or Ultimate with Duo license
- TradesmanTools MCP server registered as a GitLab external agent (B-012 / B-013)
- Accumulate blockchain RPC access (`ACCUMULATE_RPC_URL`)

## Flows

| File | Trigger | Purpose |
|------|---------|---------|
| [`tradesman_job_intake.yml`](./tradesman_job_intake.yml) | Manual / issue webhook | Intake a job request, verify contractor, route to dispatch |
| [`crew_routing_and_dispatch.yml`](./crew_routing_and_dispatch.yml) | Downstream from intake | Match and dispatch a qualified crew member |
| [`compliance_attestation.yml`](./compliance_attestation.yml) | Manual / weekly cron / pre-job gate | Full compliance check with optional on-chain attestation |
| [`invoice_and_royalty_settlement.yml`](./invoice_and_royalty_settlement.yml) | Job completion event | Compute splits, generate invoice, record settlement |

## Tool References

All agent steps reference one of two MCP servers:

**`tradesman-verify`** — open-source blockchain tools (this library)
- `verify_contractor` — reads ADI credentials, returns verification level
- `verify_business_entity` — OpenCorporates business registry lookup
- `issue_credential` — writes a third-party W3C VC to the Accumulate chain
- `self_attest_credential` — writes a self-attested W3C VC to the chain
- `revoke_credential` — writes a revocation entry to the chain

**`tradesman-tools`** — TradesmanTools platform tools (proprietary, LV8R Labs)
- `create_job_record`, `assign_job`, `cancel_job_record`
- `generate_invoice`, `record_provider_revenue`, `mark_job_settled`
- `notify_contractor`, `hold_job_payment`, `compute_revenue_splits`

## Workflow Chain

```
tradesman_job_intake
        │
        ▼
crew_routing_and_dispatch
        │
        ▼
compliance_attestation  ◄── also runs on weekly cron
        │
        ▼
invoice_and_royalty_settlement
```

## Status

These flows are spec-ahead — they are ready to publish to the GitLab AI Catalog
once B-012 (GitLab Premium + Duo license) and B-013 (GitLab AI Catalog registration)
are complete.
