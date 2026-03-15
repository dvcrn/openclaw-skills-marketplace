---
name: docker-container-manager
description: "Docker Container Manager"
---

# Docker Container Manager

Manage Docker containers - start, stop, restart, pause, and inspect containers.

## Features

- **Start/Stop**: Control container lifecycle
- **Restart**: Restart running containers
- **Pause/Unpause**: Pause container processes
- **Inspect**: Get detailed container info
- **Logs**: View container logs

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- DevOps automation
- Container orchestration
- CI/CD pipelines
- Server management

## Example Input

```json
{
  "action": "stop",
  "container": "nginx-web"
}
```

## Example Output

```json
{
  "success": true,
  "action": "stop",
  "container": "nginx-web",
  "message": "Container nginx-web stopped successfully"
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
