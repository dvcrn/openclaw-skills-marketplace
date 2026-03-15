---
name: runpodctl
description: "Manage RunPod GPU pods, serverless endpoints, templates, network volumes, and models using the runpodctl CLI. Use when the user wants to list/create/stop/delete pods, manage serverless endpoints, check GPU availability, or manage RunPod resources."
---

# RunPod CLI Skill

Manage GPU pods, serverless endpoints, templates, network volumes, and models on RunPod.

> **Binary location:** `~/.local/bin/runpodctl`
> **Spelling:** "Runpod" (capital R). Command is `runpodctl` (lowercase).

## Setup (first time)

If API key not yet configured:
```bash
~/.local/bin/runpodctl config set --apiKey YOUR_API_KEY
```
API key: https://runpod.io/console/user/settings

Check setup:
```bash
~/.local/bin/runpodctl user
```

## Pods

```bash
~/.local/bin/runpodctl pod list               # List running pods
~/.local/bin/runpodctl pod list --all         # All pods including stopped
~/.local/bin/runpodctl pod get <pod-id>       # Pod details + SSH info
~/.local/bin/runpodctl pod create --template-id runpod-torch-v21 --gpu-id "NVIDIA RTX 4090"
~/.local/bin/runpodctl pod start <pod-id>
~/.local/bin/runpodctl pod stop <pod-id>
~/.local/bin/runpodctl pod restart <pod-id>
~/.local/bin/runpodctl pod delete <pod-id>
```

## GPUs & Templates

```bash
~/.local/bin/runpodctl gpu list                          # Available GPUs + prices
~/.local/bin/runpodctl template list --type official     # Official templates
~/.local/bin/runpodctl template search pytorch           # Search templates
~/.local/bin/runpodctl template get <template-id>        # Template details
```

## Serverless Endpoints

```bash
~/.local/bin/runpodctl serverless list
~/.local/bin/runpodctl serverless get <endpoint-id>
~/.local/bin/runpodctl serverless create --name "x" --template-id "tpl_abc"
~/.local/bin/runpodctl serverless update <endpoint-id> --workers-max 5
~/.local/bin/runpodctl serverless delete <endpoint-id>
```

## Network Volumes

```bash
~/.local/bin/runpodctl network-volume list
~/.local/bin/runpodctl network-volume create --name "x" --size 100 --data-center-id "US-GA-1"
~/.local/bin/runpodctl network-volume delete <volume-id>
```

## Models

```bash
~/.local/bin/runpodctl model list
~/.local/bin/runpodctl model list --name "llama"
~/.local/bin/runpodctl model add --name "my-model" --model-path ./model
```

## Account

```bash
~/.local/bin/runpodctl user          # Account info + balance
```

## Accessing pods

Exposed ports via: `https://<pod-id>-<port>.proxy.runpod.net`

## Notes

- Always use `~/.local/bin/runpodctl` (full path) in exec commands — PATH may not be loaded in sandbox
- Pod create requires either `--template-id` or `--image`
- GPU IDs must match exactly (e.g., `"NVIDIA RTX 4090"`, `"NVIDIA A100 80GB PCIe"`)
