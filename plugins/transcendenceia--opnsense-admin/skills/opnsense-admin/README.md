# OPNsense Admin Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OPNsense](https://img.shields.io/badge/OPNsense-26.1+-blue.svg)](https://opnsense.org/)

> ⚠️ **WARNING: This tool grants HIGH PRIVILEGE access to your firewall.**
> By using it, you declare you are a responsible adult. [See full disclaimer](SKILL.md)

Complete OPNsense firewall administration for AI agents. Automate backups, monitor security, manage services, and troubleshoot network issues via API and SSH.

## 🚀 Quick Start

```bash
# Clone the skill
gh repo clone Transcendenceia/opnsense-admin-skill

# Configure credentials
cat > ~/.opnsense/credentials << EOF
OPNSENSE_HOST=192.168.1.1
OPNSENSE_KEY=your_api_key
OPNSENSE_SECRET=your_api_secret
EOF

# Check status
./scripts/opnsense-api.sh status
```

## 📋 Features

- **🔥 Firewall Management** - Rules, NAT, aliases, diagnostics
- **🛡️ IDS/IPS (Suricata)** - Intrusion detection and prevention
- **🌐 DNS (Unbound)** - DNS resolver, blocklists, DNS over TLS
- **📊 Monitoring** - Service status, traffic analysis
- **💾 Automated Backups** - Scheduled backups with retention
- **🔧 Service Control** - Start/stop/restart via SSH

## 📖 Documentation

See [SKILL.md](SKILL.md) for complete documentation.

## 🔧 Requirements

- OPNsense 26.1 or later
- API access enabled
- SSH access (optional, for service management)
- `curl` and `jq` installed

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🤝 Contributing

Contributions welcome! Please open issues and pull requests.

## ⚠️ Disclaimer

This is an unofficial skill. Not affiliated with Deciso B.V. or the OPNsense project.
