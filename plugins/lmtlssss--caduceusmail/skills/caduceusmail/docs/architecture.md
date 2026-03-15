# Architecture

☤CaduceusMail treats enterprise email as a coordinated state machine.

The identity plane lives in Entra and Microsoft Graph. The transport plane lives in Exchange Online. The DNS and authentication plane lives in Cloudflare. The repo stitches those planes together so lane creation and retirement are not manual ticket choreography.

## Core runtime pieces

`caduceusmail.sh`
: shell wrapper that loads credentials, writes a baseline env file, calls the PowerShell bootstrap, then runs stack audit and optimization.

`caduceusmail-bootstrap.ps1`
: PowerShell bootstrap for Graph delegated consent, Exchange connection, service principal registration, RBAC grants, and optional accepted domain tuning.

`email_alias_fabric_ops.py`
: the main operational engine for lane provisioning, retirement, verification, stack audit, and DNS mutations.

`entra-exchange.sh`
: command bridge for probe sends. Today it routes `send` to `send_mail_graph.py`.

`send_mail_graph.py`
: Graph app only helper that sends a probe through `/users/{mailbox}/sendMail` with the `from` field set to the lane alias.

`caduceusmail-doctor.py`
: local readiness detector for OpenClaw, CI, and operator workstations.

## Lifecycle

1. Bootstrap delegated auth once with device or browser auth.
2. Rotate or capture the client secret for headless steady state.
3. Run daily operations with `--skip-m365-bootstrap`.
4. Provision, verify, rotate, and retire alias lanes as needed.
5. Store JSON artifacts in `~/.caduceusmail/intel` for state visibility and resumability.
