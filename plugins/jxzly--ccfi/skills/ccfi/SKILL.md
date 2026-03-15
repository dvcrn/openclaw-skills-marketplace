---
name: ccfi
description: "CCFI"
---

# CCFI Data Skill

China Export Container Freight Index (CCFI) data lookup.

## Features

- Query CCFI historical data
- Get latest CCFI index
- View statistics (high/low/average)

## Usage

### Query latest data
```
CCFI latest
```

### Query historical data
```
CCFI 2025
CCFI January 2024
```

### Query statistics
```
CCFI stats
```

### Query date range
```
CCFI 2025-01-01 to 2025-12-31
```

## Data Source

- Ministry of Transport of China
- Tencent Cloud Database

## API Endpoints

- `http://106.54.203.43/ccfi` - Historical data
- `http://106.54.203.43/ccfi/latest` - Latest data
- `http://106.54.203.43/ccfi/stats` - Statistics
