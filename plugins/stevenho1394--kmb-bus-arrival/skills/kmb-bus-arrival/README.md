# 🚌 KMB Bus Arrival Skill v1.1.0

Real-time KMB bus arrival information for Hong Kong using the official government transport API.

---

## 📁 Package Structure

<pre>
kmb-bus-arrival/
    ├── kmb_bus.py          (main executable)
    ├── kmb_bus.sh          (shell wrapper)
    ├── SKILL.md            (OpenClaw skill definition)
    └── README.md           (documentation)
</pre>

## 🚀 Quick Start

1. Extract the ZIP file
2. Copy `kmb-bus-arrival/` to your OpenClaw `skills/` directory
3. Restart OpenClaw or reload skills
4. Use the skill with commands like:
   - `getRouteDirection 182`
   - `getNextArrivals 182 I ST871`

## 📊 Features

- ✅ Real-time ETA from HK Government API
- ✅ 5-minute caching
- ✅ Supports all KMB routes
- ✅ Chinese & English stop names
- ✅ Automatic retry on errors


Github link: https://github.com/StevenHo1394/kmb-bus-arrival

##  Version History

v1.1.0: Security Fixes
v1.0.0: Initial Release