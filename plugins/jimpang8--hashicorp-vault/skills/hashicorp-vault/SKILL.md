---
name: hashicorp-vault
description: "Work with HashiCorp Vault using the `vault` CLI for authentication checks, KV secret reads and writes, listing paths, enabling and tuning secrets engines, policy inspection, token lookup, and operational troubleshooting. Use when tasks mention HashiCorp Vault, Vault KV, secret paths like `secret/` or `kv/`, `VAULT_ADDR`, `VAULT_TOKEN`, AppRole, policies, mounts, or the `vault` command."
---

# HashiCorp Vault CLI

Use the `vault` CLI for Vault work. Prefer read-only inspection first, then confirm before writing secrets, changing auth methods, enabling engines, or editing policies.

## Quick checks

```bash
vault version
vault status
vault auth list
vault secrets list
vault token lookup
```

If `VAULT_ADDR` is missing, set it first:

```bash
export VAULT_ADDR='https://vault.example.com'
```

For Jim's local Vault, use the tested local endpoint:

```bash
export VAULT_ADDR='http://192.168.1.106:8200'
vault status
curl -s "$VAULT_ADDR/v1/sys/health"
```

Notes for the local environment:
- `http://192.168.1.106:8200` responded successfully.
- `https://192.168.1.106:8200` returned a wrong-version TLS error, so this endpoint is HTTP, not HTTPS.
- `vault.jimcom2.local` did not resolve from this runtime, so prefer the IP unless local DNS/mDNS is fixed.

Verify auth before assuming a path is missing:

```bash
vault token lookup
vault kv get secret/my-app
```

## Read secrets

For KV v2 paths, use `vault kv` commands instead of raw API-style paths.

```bash
vault kv get secret/my-app
vault kv get -field=password secret/my-app
vault kv list secret/
```

If output is unclear, use JSON:

```bash
vault kv get -format=json secret/my-app
vault secrets list -format=json
```

## Write secrets

Confirm before overwriting or deleting anything.

```bash
vault kv put secret/my-app username=app password='s3cr3t'
vault kv patch secret/my-app password='rotated'
```

Prefer `patch` when updating a subset of keys on KV v2.

## Policies and mounts

Inspect first:

```bash
vault policy list
vault policy read my-policy
vault secrets list -detailed
```

Change only with explicit user intent:

```bash
vault policy write my-policy ./policy.hcl
vault secrets enable -path=secret kv-v2
vault secrets tune -max-versions=10 secret/
```

## Authentication helpers

Common login flows:

```bash
vault login
vault login -method=userpass username=<user>
vault write auth/approle/login role_id=<role_id> secret_id=<secret_id>
```

When troubleshooting auth, inspect enabled auth backends and token details first:

```bash
vault auth list -detailed
vault token lookup
```

## Troubleshooting workflow

1. Check `vault status` and `VAULT_ADDR`.
2. Check auth with `vault token lookup` or the intended login flow.
3. Confirm mount names with `vault secrets list`.
4. For KV access, verify whether the engine is KV v1 or KV v2 before choosing commands.
5. Prefer `-format=json` when output will be parsed or compared.
6. Read `references/kv-and-troubleshooting.md` for command patterns and common errors when the task is non-trivial.
