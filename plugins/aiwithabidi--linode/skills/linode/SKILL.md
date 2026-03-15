---
name: linode
description: "Linode (Akamai) — compute instances, volumes, networking, NodeBalancers, domains, and Kubernetes."
homepage: https://www.agxntsix.ai
---

# ☁️ Linode/Akamai

Linode (Akamai) — compute instances, volumes, networking, NodeBalancers, domains, and Kubernetes.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `LINODE_TOKEN` | ✅ | Linode/Akamai API token |


## Quick Start

```bash
# List Linode instances
python3 {{baseDir}}/scripts/linode.py list-instances --page "1"

# Get instance details
python3 {{baseDir}}/scripts/linode.py get-instance <id>

# Create instance
python3 {{baseDir}}/scripts/linode.py create-instance --type "g6-nanode-1" --region "us-east" --image "linode/ubuntu24.04" --label <value> --root-pass <value>

# Delete instance
python3 {{baseDir}}/scripts/linode.py delete-instance <id>

# Boot instance
python3 {{baseDir}}/scripts/linode.py boot-instance <id>

# Reboot instance
python3 {{baseDir}}/scripts/linode.py reboot-instance <id>

# Shut down instance
python3 {{baseDir}}/scripts/linode.py shutdown-instance <id>

# List volumes
python3 {{baseDir}}/scripts/linode.py list-volumes

# Create volume
python3 {{baseDir}}/scripts/linode.py create-volume --label <value> --size "20" --region "us-east"

# List NodeBalancers
python3 {{baseDir}}/scripts/linode.py list-nodebalancers

# List domains
python3 {{baseDir}}/scripts/linode.py list-domains

# List domain records
python3 {{baseDir}}/scripts/linode.py list-domain-records <id>

# List firewalls
python3 {{baseDir}}/scripts/linode.py list-firewalls

# List LKE clusters
python3 {{baseDir}}/scripts/linode.py list-kubernetes

# List instance types/plans
python3 {{baseDir}}/scripts/linode.py list-types

# List regions
python3 {{baseDir}}/scripts/linode.py list-regions

# List images
python3 {{baseDir}}/scripts/linode.py list-images

# Get account info
python3 {{baseDir}}/scripts/linode.py get-account
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/linode.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
