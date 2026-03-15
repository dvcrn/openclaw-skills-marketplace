---
name: agent-proxy-guardian
description: "Autonomous RPC & VPN rotation for AI Agents. Ensures 99.9% uptime by bypassing geo-locks and rate limits on exchanges and Web3 protocols."
---

# Agent Proxy Guardian

The definitive tool for agents operating in restricted network environments. It automatically detects API timeouts and rotates through a pool of high-speed residential proxies and VPN nodes.

## Features
- **Smart Rotation**: Switches nodes only when a disruption is detected to minimize latency.
- **Protocol Support**: Works with HTTP, WebSocket (for OKX/Binance), and RPC (for Solana/Base).
- **Latency Benchmarking**: Always selects the fastest available route.

## Usage
```bash
npx openclaw skill run agent-proxy-guardian --target okx
```

## Architect's Note
Operational continuity is a prerequisite for autonomy.
