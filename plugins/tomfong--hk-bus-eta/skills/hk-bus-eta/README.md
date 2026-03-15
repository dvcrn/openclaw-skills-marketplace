# 🚌 Hong Kong Bus ETA

> **BETA** - This skill is under active development and may change.

Real-time Hong Kong bus arrival predictions for KMB, LWB, and Citybus (CTB).


## Installation

### From ClawHub

```bash
clawhub install hk-bus-eta
```

### From Source

```bash
clawhub install https://github.com/tomfong/hk-bus-eta-skill
```



## Quick Start

Ask your OpenClaw agent in natural language:

| Example Query                            | Result                                     |
| ---------------------------------------- | ------------------------------------------ |
| "When will bus 1A arrive at Star Ferry?" | ETA for route 1A at Star Ferry area        |
| "KMB 68X to Yuen Long"                   | Next buses for route 68X heading Yuen Long |
| "Next 98D at Hang Hau"                   | ETA at nearest Hang Hau stops              |
| "A29 at the airport"                     | LWB route A29 at airport terminals         |



## Features

| Feature                 | Description                                  |
| ----------------------- | -------------------------------------------- |
| 🚌 **Multi-Operator**    | KMB, Citybus (CTB), LWB, and joint routes    |
| 🔍 **Smart Location**    | Search by area name (e.g., "尚德", "寶琳站") |
| 📍 **Stop Clustering**   | Merges stops within 50m radius               |
| 🔄 **Destination Merge** | Handles joint-route destination variations   |
| 🚏 **Terminus Marking**  | Shows `[終點站]` for drop-off only stops     |
| ⚡ **Local Cache**       | SQLite database for fast queries             |
| 📅 **Auto Sync**         | Weekly database update recommended           |



## First Run

⏱️ **First-time initialization takes ~10-30 seconds** to download and build the bus stops database (~20MB).

Subsequent queries are instant.

You are recommended to run the following command once before first use:

```bash
python3 ~/.openclaw/workspace/skills/hk-bus-eta/scripts/sync_bus_stops.py
```



## Usage

### Natural Language

Just ask in Cantonese, English, or mixed:

- "下班 68X 幾時到？"
- "When is the next A29 from Tung Chung?"
- "城巴 11 去中環邊個站最近？"

### Direct Command

```bash
exec python3  ~/.openclaw/workspace/skills/hk-bus-eta/scripts/eta.py {ROUTE} {STOP_NAME} [USER_LAT] [USER_LON] [LANG]
```

**Examples:**

```bash
# Route A29 at Po Lam Station
exec python3  ~/.openclaw/workspace/skills/hk-bus-eta/scripts/eta.py A29 寶琳站

# Route 1A at Tsim Sha Tsui area
exec python3  ~/.openclaw/workspace/skills/hk-bus-eta/scripts/eta.py 1A 尖沙咀

# Route A41P at Airport
exec python3  ~/.openclaw/workspace/skills/hk-bus-eta/scripts/eta.py A41P 機場
```


## Output Format

```
🚌 路線 1A - 尖沙咀碼頭

📍 尖沙咀碼頭總站 [終點站]
   Google Maps: https://maps.google.com/...
   └─ 中秀茂坪
       14:32 (3 min) [KMB]
       14:45 (16 min) [KMB]
       15:02 (33 min) [KMB]
```

- Shows destination with terminus marking
- Up to 3 upcoming ETAs
- Google Maps link for each stop
- Operator badge (KMB/CTB/LWB)



## Data Sync

Run weekly to keep bus stop data fresh:

```bash
python3  ~/.openclaw/workspace/skills/hk-bus-eta/scripts/sync_bus_stops.py
```

**Recommended cron schedule:** Every Sunday at 03:30


## Requirements

| Requirement | Notes                |
| ----------- | -------------------- |
| Python 3.x  | Main script runtime  |
| `curl`      | API calls            |
| `sqlite3`   | Local cache database |


## Data Source

Bus ETA data from Hong Kong Transport Department open data APIs.

## Changelog

### v1.0.0 (2026-03-13)

First stable release.

- Smart location association
- Coordinate clustering (50m)
- Destination fuzzy merge
- Multi-name support
- Terminus marking
- KMB/CTB/LWB support
- Auto background sync (7-day cycle)
- Auto initialization on first run
- 30s timeout enforcement

## License

MIT License - See [LICENSE](LICENSE) for details.

## Author

**Tom FONG** - [GitHub](https://github.com/tomfong)

Built with Mr. Usagi (Tom's OpenClaw Agent)