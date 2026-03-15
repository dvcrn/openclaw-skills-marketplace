---
name: mac-mini-server
description: "Set up OpenClaw on Mac Mini as always-on AI server — hardware recommendations, macOS config, Docker Desktop, launchd auto-start, Tailscale remote access, and cost comparison vs VPS. Use when deploying OpenClaw on Mac Mini for 24/7 personal AI."
homepage: https://www.agxntsix.ai
---

# 🖥️ Mac Mini Server

Complete guide to running OpenClaw on a Mac Mini as an always-on AI server. From hardware selection to monitoring.

---

## 1. Hardware Recommendations

### Mac Mini M4 (2024) — $499 base

| Spec | Base | Upgraded |
|------|------|---------|
| CPU | 10-core | 10-core |
| GPU | 10-core | 10-core |
| RAM | 16GB | 32GB (+$200) |
| Storage | 256GB | 512GB (+$200) |

**Best for:** Personal assistant, small team, cloud API-only usage.
**Recommendation:** Upgrade to 32GB RAM ($699 total) — worth it for Docker overhead + future local models.

### Mac Mini M4 Pro — $1,399 base

| Spec | Base | Upgraded |
|------|------|---------|
| CPU | 12-core | 14-core |
| GPU | 16-core | 20-core |
| RAM | 24GB | 48GB (+$200) / 64GB (+$400) |
| Storage | 512GB | 1TB (+$200) |

**Best for:** Local model inference (Ollama), multiple clients, heavy workloads.
**Recommendation:** 48GB RAM ($1,599) for running 7B-13B models locally alongside OpenClaw.

### Which One?

| Use Case | Pick | Why |
|----------|------|-----|
| Cloud APIs only (Claude, GPT) | M4 32GB | Plenty of power, great value |
| Local + cloud hybrid | M4 Pro 48GB | Run Ollama + OpenClaw together |
| Multi-client server | M4 Pro 64GB | Headroom for multiple agents |
| Budget-conscious | M4 16GB | Works fine for single user |

---

## 2. macOS Initial Setup

### Disable Sleep & Energy Settings

```bash
# Prevent sleep entirely
sudo pmset -a sleep 0
sudo pmset -a disksleep 0
sudo pmset -a displaysleep 0

# Restart after power failure
sudo pmset -a autorestart 1

# Disable hibernation
sudo pmset -a hibernatemode 0

# Verify settings
pmset -g
```

**System Settings UI path:** System Settings → Energy → set all to Never.

### Enable Auto-Login

1. System Settings → Users & Groups → Automatic Login → select your user
2. System Settings → Lock Screen → disable "Require password"

> ⚠️ Only do this on a physically secure machine. The Mac Mini should be in a locked location.

### Disable Automatic Updates Reboots

```bash
# Prevent auto-restart for updates
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticallyInstallMacOSUpdates -bool false
```

Update manually on your schedule instead.

### Enable Remote Access

```bash
# Enable SSH
sudo systemsetup -setremotelogin on

# Enable Screen Sharing (optional)
sudo defaults write /var/db/launchd.db/com.apple.launchd/overrides.plist com.apple.screensharing -dict Disabled -bool false
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist
```

---

## 3. Homebrew + Docker Desktop

### Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### Install Docker Desktop

```bash
brew install --cask docker

# Launch Docker Desktop
open -a Docker

# Wait for Docker to start, then verify
docker --version
docker compose version
```

**Docker Desktop Settings:**
- Resources → CPUs: leave 2 for macOS, give rest to Docker
- Resources → Memory: leave 4GB for macOS, give rest to Docker
- General → Start Docker Desktop when you sign in: ✅

### Install Essential Tools

```bash
brew install git node pnpm tailscale jq htop
```

---

## 4. OpenClaw Docker Compose Setup

### Clone and Build

```bash
cd ~
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# Install dependencies and build
pnpm install
pnpm build

# Build Docker image
docker build -t openclaw:latest .
```

### Configure

```bash
mkdir -p ~/.openclaw
cp openclaw.example.json ~/.openclaw/openclaw.json
nano ~/.openclaw/openclaw.json
```

### docker-compose.yml

```yaml
version: "3.8"
services:
  openclaw-gateway:
    image: openclaw:latest
    container_name: openclaw-gateway
    restart: unless-stopped
    volumes:
      - ~/.openclaw:/home/node/.openclaw
      - ./:/host/openclaw:rw
      - /var/run/docker.sock:/var/run/docker.sock
      - ~/.ssh:/home/node/.ssh:ro
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - NODE_ENV=production
```

> ⚠️ **ALWAYS** use `127.0.0.1:` prefix on ports. Never expose to `0.0.0.0`.

### Launch

```bash
docker compose up -d
docker compose logs -f  # verify startup
```

---

## 5. Launchd Service (Auto-Start on Boot)

Create `~/Library/LaunchAgents/com.openclaw.gateway.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/docker</string>
        <string>compose</string>
        <string>-f</string>
        <string>/Users/YOUR_USER/openclaw/docker-compose.yml</string>
        <string>up</string>
        <string>-d</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>StandardOutPath</key>
    <string>/tmp/openclaw-launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw-launchd-err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

```bash
# Replace YOUR_USER with actual username
sed -i '' "s/YOUR_USER/$(whoami)/g" ~/Library/LaunchAgents/com.openclaw.gateway.plist

# Load the service
launchctl load ~/Library/LaunchAgents/com.openclaw.gateway.plist

# Verify
launchctl list | grep openclaw
```

---

## 6. Tailscale for Remote Access

```bash
# Install (already done via brew)
brew install --cask tailscale

# Or use CLI version
brew install tailscale

# Start and authenticate
sudo tailscale up

# Get your Tailscale IP
tailscale ip -4

# Enable Tailscale Serve for HTTPS
tailscale serve https / http://127.0.0.1:3000
```

### Access from Anywhere
- SSH: `ssh user@100.x.x.x`
- OpenClaw: `https://mac-mini.tail-xxxxx.ts.net`
- No port forwarding needed
- End-to-end encrypted

### Tailscale ACLs (recommended)
In the Tailscale admin console, restrict who can access the Mac Mini:
```json
{
  "acls": [
    {"action": "accept", "src": ["your-devices"], "dst": ["mac-mini:*"]}
  ]
}
```

---

## 7. Telegram Bot Configuration

```bash
# 1. Create bot via @BotFather on Telegram
# 2. Get your user ID via @userinfobot
# 3. Edit config
nano ~/.openclaw/openclaw.json
```

Add to config:
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "dmPolicy": "allowlist",
      "dmAllowlist": ["YOUR_USER_ID"]
    }
  }
}
```

```bash
# Restart to apply
docker compose restart
```

---

## 8. Port Forwarding Alternatives

If Tailscale isn't an option:

| Method | Pros | Cons |
|--------|------|------|
| **Tailscale** (recommended) | Zero config, encrypted, free | Requires client on each device |
| **Cloudflare Tunnel** | Free, no open ports | Slight latency, CF dependency |
| **ngrok** | Easy setup | Free tier limited, costs for production |
| **Router port forwarding** | Direct access | Security risk, dynamic IP issues |
| **WireGuard** | Fast, self-hosted | Manual setup, maintain yourself |

### Cloudflare Tunnel (alternative to Tailscale)

```bash
brew install cloudflared
cloudflared tunnel login
cloudflared tunnel create openclaw
cloudflared tunnel route dns openclaw agent.yourdomain.com

# Create config: ~/.cloudflared/config.yml
cat > ~/.cloudflared/config.yml << EOF
tunnel: YOUR_TUNNEL_ID
credentials-file: /Users/$USER/.cloudflared/YOUR_TUNNEL_ID.json
ingress:
  - hostname: agent.yourdomain.com
    service: http://localhost:3000
  - service: http_status:404
EOF

cloudflared tunnel run openclaw
```

---

## 9. UPS Recommendations

A UPS prevents data corruption during power outages and gives time for graceful shutdown.

| Model | Capacity | Runtime | Price | Best For |
|-------|----------|---------|-------|----------|
| APC BE425M | 425VA | ~15min | $55 | Budget, Mac Mini only |
| CyberPower CP685AVRG | 685VA | ~20min | $80 | Mac Mini + router |
| APC BR700G | 700VA | ~25min | $120 | Mac Mini + monitor + router |
| CyberPower CP1500PFCLCD | 1500VA | ~45min | $220 | Full setup with margin |

**Recommendation:** CyberPower CP685AVRG — enough for Mac Mini + router, good price-to-runtime ratio.

### Auto-Shutdown on Power Loss

```bash
# macOS reads UPS status via USB automatically
# Configure in System Settings → Energy → UPS
# Set: "Shut down after using UPS battery for: 10 minutes"
```

---

## 10. Monitoring and Alerts

### Basic Health Check Script

Save as `~/{baseDir}/scripts/health_check.sh`:

```bash
#!/bin/bash
# Check if OpenClaw container is running
if ! docker ps | grep -q openclaw-gateway; then
    echo "$(date): OpenClaw container not running! Restarting..." >> /tmp/openclaw-monitor.log
    cd ~/openclaw && docker compose up -d
    # Send alert via Telegram (if bot is available on host)
    curl -s "https://api.telegram.org/botYOUR_TOKEN/sendMessage" \
      -d "chat_id=YOUR_ID&text=⚠️ OpenClaw was down. Auto-restarted."
fi
```

### Cron-Based Monitoring

```bash
crontab -e
# Check every 5 minutes
*/5 * * * * bash ~/{baseDir}/scripts/health_check.sh
```

### System Metrics

```bash
# Install monitoring tools
brew install htop btop

# Check resources
htop                          # Interactive process viewer
docker stats                  # Container resource usage
df -h                         # Disk space
```

### Uptime Monitoring (External)

Consider free external monitors:
- [UptimeRobot](https://uptimerobot.com) — ping your Tailscale Serve URL
- [Healthchecks.io](https://healthchecks.io) — cron job monitoring (ping on success)

---

## 11. Cost Comparison

### Mac Mini M4 32GB ($699 one-time)

| Item | Monthly Cost |
|------|-------------|
| Electricity (~15W average) | ~$2 |
| Internet (existing) | $0 |
| Tailscale | Free |
| AI APIs | $50-500 |
| **Total** | **$52-502/mo** |
| **Year 1 (with hardware)** | **$1,323-6,723** |
| **Year 2+** | **$624-6,024** |

### VPS (Hetzner CX32 — 4 vCPU, 8GB RAM)

| Item | Monthly Cost |
|------|-------------|
| Server | $15 |
| AI APIs | $50-500 |
| **Total** | **$65-515/mo** |
| **Year 1** | **$780-6,180** |

### Cloud (AWS t3.large)

| Item | Monthly Cost |
|------|-------------|
| EC2 | $60 |
| Storage | $10 |
| Bandwidth | $5-20 |
| AI APIs | $50-500 |
| **Total** | **$125-590/mo** |
| **Year 1** | **$1,500-7,080** |

### Verdict

| Factor | Mac Mini | VPS | Cloud |
|--------|----------|-----|-------|
| Upfront cost | $699 | $0 | $0 |
| Monthly cost | Lowest | Low | Highest |
| Performance | Best (M4 chip) | Good | Good |
| Latency | Depends on internet | Consistent | Consistent |
| Maintenance | You handle | Managed | Managed |
| Local models | ✅ Yes | ❌ No | ❌ Expensive |
| Break-even vs VPS | ~4 years | — | — |

**TL;DR:** Mac Mini wins if you want local model capability or plan to run 2+ years. VPS wins for simplicity and no upfront cost. Cloud is for enterprises with compliance needs.

---

## Quick Start Checklist

- [ ] Buy Mac Mini (M4 32GB recommended)
- [ ] macOS setup (disable sleep, auto-login, SSH)
- [ ] Install Homebrew, Docker, tools
- [ ] Clone and build OpenClaw
- [ ] Configure `openclaw.json`
- [ ] `docker compose up -d`
- [ ] Set up launchd auto-start
- [ ] Install and configure Tailscale
- [ ] Set up Telegram bot
- [ ] Connect UPS
- [ ] Configure health monitoring
- [ ] Test reboot recovery

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
