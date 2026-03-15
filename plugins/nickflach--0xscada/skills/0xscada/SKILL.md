---
name: 0xscada
description: "Decentralized Industrial Control Fabric. Bridges SCADA systems with blockchain-backed audit trails and Kannaka memory integration. Provides a unified API for telemetry, geometry classification, and verifiable industrial state."
---

# 0xSCADA Skill

Decentralized Industrial Control Fabric mapping atoms to bits. Integrates natively with the Kannaka memory ecosystem (84-class SGA Fano geometry).

**Architecture Note:** This skill acts as a Clawhub wrapper/controller for a full local 0xSCADA node. It relies on executing the 0xSCADA project repository located relative to this skill or configured via `SCADA_DIR`.

## Prerequisites

- **Node.js 18+** on PATH
- **npm** on PATH
- **curl** on PATH (for health checks)
- **PostgreSQL** (optional, uses SQLite by default if not set up)

## Setup

```bash
cd ~/workspace/skills/0xscada
npm install
```

## Configuration

This skill supports extensive blockchain and integration features by communicating with the underlying 0xSCADA server. To enable these, configure the following environment variables:

- `SCADA_DIR`: Explicitly set the 0xSCADA repository path (defaults to relative parent dir)
- `WEB3_RPC_URL` & `PRIVATE_KEY`: Enable blockchain audit anchoring
- `FLUX_URL` & `FLUX_AUTH_TOKEN`: Enable Kannaka Flux integration

*Note: For security, the startup script validates that `SCADA_DIR` points to a legitimate 0xSCADA project containing `server/index.ts` before execution.*

## Quick Start

```bash
# Start 0xSCADA
./scripts/0xscada.sh start

# Check status
./scripts/0xscada.sh status
```

