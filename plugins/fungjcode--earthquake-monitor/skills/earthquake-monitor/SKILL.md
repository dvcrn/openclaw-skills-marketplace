---
name: earthquake-monitor
description: "Real-time earthquake monitoring for China, Taiwan, and Japan. CENC/CWA/JMA WebSocket data with proactive alert support."
homepage: https://github.com/fungjcode/earthquake-monitor
---

# Earthquake Monitor

Real-time earthquake monitoring for China, Taiwan, and Japan.

## Data Sources

| Source | Region | Description |
|--------|--------|-------------|
| CENC | 🇨🇳 China | China Earthquake Networks Center |
| CWA | 🇹🇼 Taiwan | Central Weather Administration |
| JMA | 🇯🇵 Japan | Japan Meteorological Agency |

## Get Earthquakes

```javascript
// Get all earthquakes
getAll()

// Get by source
getCENC()
getJMA()
getCWA()
```

## Initialize & Start Monitoring

```javascript
// First time setup
init({ location: "大理" })

// Start proactive monitoring
start({ interval: 60000 })

// Stop monitoring
stop()
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| location | 大理 | Monitoring city |
| distanceThreshold | 300 | Alert distance (km) |
| minMagnitude | 3.0 | Minimum magnitude |
| interval | 60000 | Check interval (ms) |

## Supported Cities

大理、昆明、北京、上海、广州、深圳、成都、重庆、杭州、西安、南京、武汉、台北、东京、首尔等 40+ cities.

## Notes

- Data from official government agencies (CENC/CWA/JMA)
- No API key required
- WebSocket + HTTP fallback

## Author

- Author: fungjcode
- GitHub: https://github.com/fungjcode
