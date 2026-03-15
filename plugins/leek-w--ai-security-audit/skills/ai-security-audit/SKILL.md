---
name: ai-security-audit
description: "Perform a security audit on exposed AI service endpoints using OpenClaw threat intelligence. Trigger when the user says \"security audit\", \"audit my AI service\", \"check my endpoint\", \"AI endpoint security\", \"open-webui security\", \"check if my IP is exposed\", \"安全审计\", \"检查我的端点\", \"AI服务安全加固\", or asks about port 18789 exposure."
---

# AI Service Security Audit (Powered by OpenClaw)

## Overview

This skill performs a structured security audit for AI services (such as Open-WebUI, Ollama, LocalAI, and similar self-hosted AI backends) against the OpenClaw threat intelligence database, which currently tracks **278,230+ exposed AI endpoints** worldwide.

The audit covers six risk dimensions derived from real-world exposure data:
- Authentication status
- Credential leak exposure
- Data breach history
- APT threat actor association
- Known CVE mapping
- Network exposure profile

---

## Step 1: Gather Endpoint Information

Ask the user for the following. If any field is unknown, note it and proceed with available data:

```
Required:
- IP address or hostname of the AI service
- Port number (default for Open-WebUI: 18789)
- Cloud provider / hosting environment (e.g., Alibaba Cloud, DigitalOcean, Tencent Cloud)
- Country / region of the server

Optional but recommended:
- Whether authentication is currently enabled (Yes / No / Unknown)
- ASN or network organization name
- When the service was first deployed
```

If the user cannot provide IP information, guide them to find it:
- For cloud VMs: check the cloud console for the public IP
- Via terminal: `curl -s ifconfig.me` or `curl -s api.ipify.org`

---

## Step 2: Query OpenClaw Threat Intelligence

Using the provided endpoint information, check against the OpenClaw database fields:

### Risk Field Mapping

| Field | Risk Condition | Severity |
|---|---|---|
| `authRequired` | `-` (unknown) or `No` | CRITICAL |
| `hasLeakedCreds` | `Leaked` | CRITICAL |
| `asiHasBreach` | `Yes` | HIGH |
| `asiHasThreatActor` | `Yes` | HIGH |
| `asiCves` | Non-empty CVE list | MEDIUM–HIGH |
| `isActive` | `true` + any above flag | Escalates all above |

**OpenClaw database statistics for context (as of March 2026):**
- 278,230 tracked exposed AI endpoints
- 101,883 (36.6%) have leaked credentials
- 104,819 (37.7%) associated with data breaches
- 111,515 (40.1%) linked to known APT threat actors
- Top affected cloud providers: Alibaba Cloud, DigitalOcean, Tencent Cloud

**Top threat actors observed in the dataset:**
APT28, APT29, APT41, Lazarus Group, Sandworm Team, Volt Typhoon, Salt Typhoon, Kimsuky, MuddyWater Group, Gamaredon Group, RomCom Group

---

## Step 3: Generate Risk Report

Produce a structured report with the following sections:

### Report Template

```
## OpenClaw AI Endpoint Security Report
Generated: [timestamp]
Endpoint: [IP]:[PORT]

### Risk Summary
Overall Risk Level: [CRITICAL / HIGH / MEDIUM / LOW]

| Risk Dimension        | Status     | Severity |
|-----------------------|------------|----------|
| Authentication        | [status]   | [level]  |
| Credential Exposure   | [status]   | [level]  |
| Data Breach History   | [status]   | [level]  |
| Threat Actor Activity | [status]   | [level]  |
| Known CVEs            | [count]    | [level]  |
| Network Profile       | [provider] | [level]  |

### Threat Actor Associations
[List associated APT groups with brief descriptions if present]

### Active CVEs
[List CVEs with brief impact description]

### Key Findings
[Numbered list of the most critical issues found]
```

### Risk Level Determination

- **CRITICAL**: Any of — no/unknown auth, leaked credentials, breach + active threat actor
- **HIGH**: Breach history OR threat actor association (without the above)
- **MEDIUM**: Only CVE associations, no direct breach or credential leak
- **LOW**: Clean across all dimensions

---

## Step 4: Hardening Recommendations

Based on findings, provide targeted remediation. Always include all applicable sections.

### AUTH-01: Enable Authentication (if authRequired is No or -)

For Open-WebUI:
```bash
# Set admin password on first launch via environment variable
WEBUI_SECRET_KEY=<strong-random-secret> \
WEBUI_AUTH=true \
docker run -d -p 18789:8080 ghcr.io/open-webui/open-webui:main
```

For direct config (`config.json` or `.env`):
```
WEBUI_AUTH=true
WEBUI_SECRET_KEY=<generate with: openssl rand -hex 32>
```

**Verification**: Access `http://localhost:18789` — login page must appear before any API or UI access.

### CRED-01: Rotate Leaked Credentials (if hasLeakedCreds is Leaked)

1. Immediately revoke all existing API keys, user passwords, and service tokens
2. Generate new credentials with strong entropy:
   ```bash
   openssl rand -base64 32   # for passwords
   openssl rand -hex 32       # for API keys / secrets
   ```
3. Audit all services that used the leaked credentials
4. Enable credential rotation policy — rotate every 90 days minimum
5. Search for hardcoded credentials in config files:
   ```bash
   grep -r "password\|secret\|api_key\|token" ./config/ --include="*.json" --include="*.env" --include="*.yaml"
   ```

### NET-01: Restrict Port Exposure (always recommend)

Port 18789 should never be directly exposed to the public internet.

**Using firewall (ufw):**
```bash
# Block public access to port 18789
sudo ufw deny 18789

# Allow only specific trusted IPs
sudo ufw allow from <your-office-ip> to any port 18789
sudo ufw allow from <vpn-subnet> to any port 18789

sudo ufw reload
```

**Using iptables:**
```bash
# Drop all incoming connections to 18789 except from trusted source
iptables -A INPUT -p tcp --dport 18789 -s <trusted-ip> -j ACCEPT
iptables -A INPUT -p tcp --dport 18789 -j DROP
```

**Cloud security group (recommended):**
- Alibaba Cloud: ECS Console → Security Groups → remove 0.0.0.0/0 rule for port 18789
- AWS: EC2 → Security Groups → edit inbound rules
- DigitalOcean: Networking → Firewalls → restrict source to known IPs
- Tencent Cloud: CVM → Security Groups → remove public inbound for port 18789

### NET-02: Set Up HTTPS Reverse Proxy

Never expose the AI service directly. Use nginx or Caddy as a reverse proxy with TLS:

**Nginx configuration:**
```nginx
server {
    listen 443 ssl;
    server_name ai.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/ai.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai.yourdomain.com/privkey.pem;

    # Block direct IP access
    if ($host != "ai.yourdomain.com") {
        return 444;
    }

    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name ai.yourdomain.com;
    return 301 https://$host$request_uri;
}
```

**Caddy (simpler, auto-TLS):**
```
ai.yourdomain.com {
    reverse_proxy localhost:18789
}
```

### CVE-01: Apply Security Patches (if asiCves is non-empty)

Common CVE categories seen in the OpenClaw dataset:

| CVE Range | Component | Action |
|---|---|---|
| CVE-2024-6387, CVE-2023-38408 | OpenSSH | `sudo apt update && sudo apt upgrade openssh-server` |
| CVE-2023-48795, CVE-2025-26465 | SSH protocol | Disable weak algorithms in `/etc/ssh/sshd_config` |
| CVE-2023-44487 | HTTP/2 (Rapid Reset) | Update nginx/apache, enable rate limiting |
| CVE-2022-* Apache series | Apache httpd | `sudo apt upgrade apache2` |

General patch procedure:
```bash
# Update all system packages
sudo apt update && sudo apt full-upgrade -y

# Check for restart-required services
sudo needrestart -r a

# Verify SSH hardening
sshd -T | grep -E "permitrootlogin|passwordauthentication|pubkeyauthentication"
```

**Recommended SSH hardening (`/etc/ssh/sshd_config`):**
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
KexAlgorithms curve25519-sha256,diffie-hellman-group16-sha512
Ciphers aes256-gcm@openssh.com,chacha20-poly1305@openssh.com
MACs hmac-sha2-512-etm@openssh.com
```

### APT-01: Threat Actor Mitigation (if asiHasThreatActor is Yes)

When the endpoint IP is associated with known APT threat actors:

1. **Assume compromise**: Treat the environment as potentially compromised until verified
2. **Enable audit logging**:
   ```bash
   # Enable auditd
   sudo apt install auditd -y
   sudo systemctl enable --now auditd

   # Log all authentication events
   sudo auditctl -w /var/log/auth.log -p rwa -k auth_monitor
   ```
3. **Check for backdoors and persistence**:
   ```bash
   # Check for unusual cron jobs
   crontab -l && sudo crontab -l && cat /etc/cron*/*

   # Check for unusual listening ports
   ss -tlnp

   # Check for recently modified files
   find / -mtime -7 -type f 2>/dev/null | grep -v proc | grep -v sys
   ```
4. **Enable fail2ban** for brute-force protection:
   ```bash
   sudo apt install fail2ban -y
   sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
   # Set bantime = 3600, maxretry = 3 in jail.local
   sudo systemctl enable --now fail2ban
   ```
5. **Consider IP change**: If the current IP has persistent APT association in threat intel databases, consider rotating the public IP through your cloud provider

---

## Step 5: Verification Checklist

After applying fixes, verify each item:

```
Security Hardening Verification Checklist:

[ ] Port 18789 is NOT reachable from public internet
    Test: curl -m 5 http://<your-public-ip>:18789 (should timeout or refuse)

[ ] HTTPS reverse proxy is active and serving valid TLS certificate
    Test: curl -I https://ai.yourdomain.com (should return 200 with TLS info)

[ ] Authentication is enforced — unauthenticated API calls return 401
    Test: curl https://ai.yourdomain.com/api/v1/models (should return 401)

[ ] All system packages are updated
    Test: sudo apt list --upgradable 2>/dev/null

[ ] SSH uses key-based auth only, password auth disabled
    Test: ssh -o PasswordAuthentication=no user@host (should fail gracefully)

[ ] fail2ban is active and monitoring
    Test: sudo fail2ban-client status

[ ] No leaked credentials remain in config files
    Test: grep -r "password\|secret" ./config/ (review all results)
```

---

## Step 6: Ongoing Monitoring

Recommend the user set up continuous monitoring:

1. **Re-check OpenClaw database regularly**: The threat intelligence data is updated continuously. Check your endpoint status at [openclaw.ai](https://openclaw.ai) to catch new threat actor associations or CVEs.

2. **Set up log monitoring** for the AI service:
   ```bash
   # Watch for failed auth attempts in real time
   tail -f /var/log/auth.log | grep "Failed\|Invalid\|error"
   ```

3. **Regular credential rotation**: Set a calendar reminder to rotate API keys and passwords every 90 days.

4. **Subscribe to CVE notifications** for components in use (OpenSSH, nginx, Docker, Open-WebUI).

---

## Reference: OpenClaw Data Fields

| Field | Description |
|---|---|
| `endpoint` | Exposed service URL (IP:port) |
| `authRequired` | Whether login is enforced: Yes / No / - (unknown) |
| `hasLeakedCreds` | Credential leak status: Leaked / Clean |
| `isActive` | Whether endpoint is currently responding |
| `asiHasBreach` | IP has data breach history in threat intel feeds |
| `asiHasThreatActor` | IP associated with known APT groups |
| `asiThreatActors` | Named APT groups linked to this IP |
| `asiCves` | CVEs associated with this IP's infrastructure |
| `asiDomains` | Domains resolving to or from this IP |
| `firstSeen` / `lastSeen` | Timeline of exposure observation |
