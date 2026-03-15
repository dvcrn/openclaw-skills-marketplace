# Changelog

## v1.7.0 (2026-03-12)
- External Agent Protocol (EAP): trade directly on Polymarket CLOB, sync history without relay
- `record_external` and `close_external` API endpoints live
- Contributors section added to README
- `scripts/record-external.js` — sync on-chain trade history
- `scripts/strategy-card.js` — publish strategy for copy-traders

## v1.6.2 (2026-03-11)
- Security fix: VT scan clean, unblocked on ClawHub

## v1.5.2 (2026-03-10)
- Auto-swap POL → USDC.e before trades
- Relay fee 1% collected after successful order
- Fixed NEG_RISK approvals (USDC.e + CTF setApprovalForAll)
