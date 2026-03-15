---
name: space-router
description: "Route HTTP traffic through Space Router residential IP proxy network."
---

# Space Router — Residential IP Proxy Routing

Route your HTTP requests through residential IP addresses via Space Router's forward proxy.

## Setup

The environment variable `SPACE_ROUTER_PROXY_URL` must contain your full proxy URL including API key credentials:

```
SPACE_ROUTER_PROXY_URL=http://sr_live_YOUR_API_KEY@proxy.spacerouter.io:8080
```

For local development the host is typically `localhost:8080`.

## When to Use This Skill

Use Space Router when a task requires any of the following:

- Accessing a website that blocks datacenter IPs or cloud provider IP ranges
- Web scraping where you need residential IP rotation
- The user explicitly asks you to route traffic through a residential proxy
- A previous HTTP request failed with a 403 or CAPTCHA challenge suggesting IP-based blocking
- The user says to use "Space Router", "residential proxy", or "residential IP"

Do NOT route through the proxy when:

- Accessing local services (localhost, 127.0.0.1, internal hostnames)
- Accessing APIs that authenticate by IP allowlist (the residential IP will not be allowlisted)
- The user explicitly says to make a direct request

## How to Route Traffic

### Environment variables (preferred)

Set `HTTP_PROXY` and `HTTPS_PROXY` so all HTTP clients in the shell session use the proxy automatically:

```bash
export HTTP_PROXY="$SPACE_ROUTER_PROXY_URL"
export HTTPS_PROXY="$SPACE_ROUTER_PROXY_URL"
```

Then run any command normally. Both curl and most HTTP libraries honor these variables.

### curl

```bash
curl -x "$SPACE_ROUTER_PROXY_URL" https://example.com
```

Or for explicit control over individual requests:

```bash
curl --proxy "$SPACE_ROUTER_PROXY_URL" https://httpbin.org/ip
```

### Python httpx

```python
import os, httpx

proxy_url = os.environ["SPACE_ROUTER_PROXY_URL"]

async with httpx.AsyncClient(proxy=proxy_url) as client:
    response = await client.get("https://example.com")
    print(response.status_code, response.text)
```

### Python requests

```python
import os, requests

proxy_url = os.environ["SPACE_ROUTER_PROXY_URL"]
proxies = {"http": proxy_url, "https": proxy_url}

response = requests.get("https://example.com", proxies=proxies)
```

### Node.js fetch (with undici ProxyAgent)

```javascript
import { ProxyAgent, fetch } from "undici";
const proxy = new ProxyAgent(process.env.SPACE_ROUTER_PROXY_URL);
const res = await fetch("https://example.com", { dispatcher: proxy });
```

## Verifying the Proxy Works

After configuring the proxy, confirm that traffic is routed through a residential IP:

```bash
curl -x "$SPACE_ROUTER_PROXY_URL" https://httpbin.org/ip
```

The returned IP should differ from your machine's public IP. You can also run the verification script:

```bash
bash {baseDir}/scripts/verify-proxy.sh
```

## Response Headers

Space Router adds these headers to proxied responses:

| Header | Meaning |
|---|---|
| `X-SpaceRouter-Node` | ID of the residential node that served the request |
| `X-SpaceRouter-Request-Id` | Unique request ID for debugging |

## Error Handling

| HTTP Status | Meaning | What to Do |
|---|---|---|
| 407 | API key missing or invalid | Check that `SPACE_ROUTER_PROXY_URL` contains a valid `sr_live_` key |
| 429 | Rate limit exceeded | Wait and retry. Check `Retry-After` header for delay |
| 502 | Upstream error — residential node could not reach target | Retry the request; the proxy will try a different node |
| 503 | No residential nodes available | Wait and retry; nodes may be temporarily offline |

If you get a 407, verify your proxy URL format is `http://sr_live_<key>@<host>:<port>`.

## Important Notes

- The proxy URL uses HTTP scheme even for HTTPS targets. The proxy establishes a CONNECT tunnel for TLS traffic — your end-to-end encryption is preserved.
- Do not put the proxy URL in `NO_PROXY` or bypass lists.
- API keys have the prefix `sr_live_` and are passed as the username in the proxy URL (password is empty).
- Rate limits are per API key, default 60 requests per minute.
