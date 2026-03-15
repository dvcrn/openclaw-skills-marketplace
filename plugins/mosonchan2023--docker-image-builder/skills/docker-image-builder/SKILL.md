---
name: docker-image-builder
description: "Docker Image Builder"
---

# Docker Image Builder

Build Docker images from Dockerfile. Support for build args, tags, and multi-stage builds.

## Features

- **Build Images**: Build from Dockerfile
- **Tag Images**: Add custom tags
- **Build Args**: Support for build arguments
- **Multi-stage**: Handle multi-stage builds
- **Cache**: Efficient layer caching

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- CI/CD image builds
- Custom image creation
- Dev environment setup
- Microservice packaging

## Example Input

```json
{
  "dockerfile": "./Dockerfile",
  "tag": "myapp:latest",
  "context": "."
}
```

## Example Output

```json
{
  "success": true,
  "image": "myapp:latest",
  "tag": "myapp:latest",
  "message": "Docker image built successfully",
  "note": "Connect to Docker daemon for actual build"
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
