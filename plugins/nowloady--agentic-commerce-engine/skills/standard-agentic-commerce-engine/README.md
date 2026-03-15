# Standard Agentic Commerce Engine

A production-ready universal engine for Agentic Commerce. This tool enables autonomous agents to interact with any compatible headless e-commerce backend through a standardized protocol. It provides out-of-the-box support for discovery, cart operations, and secure user management.

Clawdhub: https://clawdhub.com/NowLoadY/agent-commerce-engine
GitHub: https://github.com/NowLoadY/agent-commerce-engine

## Why?

As the "Agentic Web" matures, the need for standardized commerce interfaces is paramount. This project provides a production-ready implementation that is:

- **Universal & Multi-Merchant**: Connect to any store via `--store <url>`. Credentials are automatically isolated per domain.
- **Protocol-First**: Implements a standard toolset (search, cart, profile, orders) precisely optimized for Large Language Models and autonomous agents.
- **Production-Ready**: Built on a modular, robust client engine that handles identity, sessions, and error states gracefully.

## Significance for the Ecosystem

The **Standard Agentic Commerce Engine** eliminates the friction of building custom integrations for every brand. It serves as a reliable connector that allows agents to navigate catalogs and execute transactions with 100% data integrity across the entire agentic web.

## Quick Start

1.  **Install dependency**:
    ```bash
    pip install requests
    ```

2.  **Run with Agent/CLI**:
    ```bash
    # Target any compliant store via --store
    python3 scripts/commerce.py --store https://api.yourstore.com/v1 list

    # Login to a store
    python3 scripts/commerce.py --store https://api.yourstore.com/v1 login --account user@example.com --password secret

    # View all locally registered stores
    python3 scripts/commerce.py stores
    ```

## Structure

- `SKILL.md`: Metadata and instructions for Agent discovery.
- `SERVER_SPEC.md`: Standard API response and behavior specification for backends.
- `scripts/commerce.py`: The universal CLI entry point.
- `scripts/lib/commerce_client.py`: The reusable `BaseCommerceClient` library.

## Security & Privacy

This engine handles user credentials following these standards:

- **Token-Only Storage**: Only API tokens are persisted locally. Passwords are never stored — they are exchanged once for a token via `/auth/token`, then discarded.
- **Per-Domain Isolation**: Each merchant's credentials are stored in a separate subfolder: `~/.openclaw/credentials/agent-commerce-engine/<domain>/`.
- **Access Control**: Stored credential files are restricted to `0600` permissions (owner read/write only).
- **HTTPS Enforced**: The client library rejects non-HTTPS URLs for production endpoints.
- **Stateless Identity**: Uses non-cookie header-based authentication to minimize tracking footprint.

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `python3`  | Runtime |
| `requests` | HTTP client (installable via `pip install requests`) |

No other system dependencies, environment variables, or external services are required.

## License

MIT License - Supporting the open acceleration of Agentic Commerce standards.

---

# 标准 Agentic 商业交互引擎

面向 Agentic Commerce 的通用核心引擎。本工具提供了一套标准、高精度的协议，用于将自主 Agent 与任何无头 (Headless) 电商后端完美连接。

Clawdhub: https://clawdhub.com/NowLoadY/agent-commerce-engine
GitHub: https://github.com/NowLoadY/agent-commerce-engine

## 快速开始

```bash
pip install requests

# 通过 --store 指向任何合规商家
python3 scripts/commerce.py --store https://api.yourstore.com/v1 list

# 查看本地已登录的所有商家
python3 scripts/commerce.py stores
```

## 安全与隐私

- **仅存 Token**：密码仅用于一次性换取 Token，绝不持久化。
- **按域名隔离**：每个商家的凭据存储在独立子文件夹中。
- **权限控制**：凭据文件权限为 `0600`（仅所有者可读写）。
- **强制 HTTPS**：客户端库拒绝生产环境的非 HTTPS 地址。

## 许可协议

MIT License - 一起探讨 Agent 商业标准的开放进程。
