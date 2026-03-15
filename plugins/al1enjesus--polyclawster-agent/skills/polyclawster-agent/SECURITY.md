# Security Policy

## Architecture

This skill is **non-custodial**. The private signing key is generated locally and stored only on the user's machine at `~/.polyclawster/config.json`. It is never transmitted to any server.

## Key Storage

- Keys are generated using `ethers.Wallet.createRandom()` (cryptographically secure)
- Stored in a local JSON config file with filesystem permissions
- Never sent over the network — all signing happens locally

## Token Approvals

The skill approves USDC.e spending for Polymarket exchange contracts. This is standard DeFi behavior required for trading. Approvals can be revoked anytime via any Polygon wallet tool.

## Network Requests

All network requests go to:
- `polyclawster.com` — order relay (geo-bypass proxy to Polymarket CLOB)
- `polygon-bor-rpc.publicnode.com` — Polygon RPC (public, read-only for balance checks)
- `clob.polymarket.com` — Polymarket's Central Limit Order Book
- `gamma-api.polymarket.com` — Market metadata

## Reporting Vulnerabilities

Contact: security@polyclawster.com or open a GitHub issue.
