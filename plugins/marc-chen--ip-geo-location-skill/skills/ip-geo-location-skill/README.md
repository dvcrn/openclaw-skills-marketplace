# ip-geo-location-skill

## English

A production-ready MCP skill for IP geolocation lookup.

- Endpoint: `http://ip.api4claw.com/mcp`
- Tool: `get_ip_geolocation`
- Supports: IPv4, IPv6, batch lookup, and domain-to-IP resolution
- Session handling: auto `initialize`, and auto re-initialize + retry when `Mcp-Session-Id` expires

### Install

```bash
npx skills add marc-chen/ip-geo-location-skill
```

### Verify

Try prompts like:

- `Where is 8.8.8.8?`
- `Lookup geolocation for 8.8.8.8 and 1.1.1.1`
- `Where is example.com?`

## 中文说明 | Chinese

一个用于 IP 地理位置查询的 MCP Skill，适用于中文用户场景。

- MCP 接口地址: `http://ip.api4claw.com/mcp`
- 调用工具: `get_ip_geolocation`
- 支持能力: IPv4、IPv6、批量查询、域名转 IP 后查询
- 会话机制: 自动 `initialize` 获取会话 ID；当 `Mcp-Session-Id` 过期/失效时自动重新初始化并重试

### 安装 | Install

#### 方式一：skills.sh

```bash
npx skills add marc-chen/ip-geo-location-skill
```

#### 方式二：手动安装

克隆本仓库后，将该 Skill 目录放到你的 Agent skills 目录中。

### 入口文件 | Skill Entry

- `SKILL.md`

### 脚本说明 | Scripts

- `scripts/invoke-geoip-mcp.js`: MCP 调用封装（含会话初始化与会话过期自动重试）
- `scripts/resolve-domain.js`: 域名解析为 A/AAAA 记录

### 使用示例 | Examples

- `8.8.8.8 在哪里？`
- `查询 8.8.8.8 和 1.1.1.1 的地理位置`
- `example.com 在哪里`

## License

MIT. See `LICENSE`.
