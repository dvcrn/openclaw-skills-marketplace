---
name: bazi-pillars-from-datetime
description: "Deterministic four-pillar (bazi) calculation from datetime."
---

# Scope
This skill defines a deterministic, reproducible calculation contract for
four pillars (year/month/day/hour) from a Gregorian datetime. It must not
generate user-facing prose or interpretations.

# Inputs (JSON)
{
  "datetime": "YYYY-MM-DDTHH:MM:SS",
  "timezone": "IANA/Timezone",
  "location": {
    "name": "City/Region",
    "longitude": 0.0,
    "latitude": 0.0,
    "lookup_mode": "auto|local|online",
    "lookup_provider": "nominatim|amap|tencent",
    "lookup_key": "optional-api-key",
    "lookup_path": "/path/to/cities.json",
    "cache_path": "/path/to/city_cache.json",
    "lookup_timeout": 6
  },
  "gender": "female|male|other",
  "rules": {
    "year_boundary": "lichun",
    "month_rule": "solar_terms",
    "day_boundary": "00:00",
    "time_correction": "mean_solar_time",
    "require_dayun": false
  },
  "flows": {
    "datetime": "YYYY-MM-DDTHH:MM:SS",
    "timezone": "IANA/Timezone"
  },
  "mode": "strict"
}

## Notes
- `datetime` has no offset; interpret it in `timezone`.
- `timezone` is required; if defaulted by the caller, record it in notes.
- `location` is required when `time_correction=mean_solar_time` or `true_solar_time`. Prefer longitude/latitude.
  If only `name` is provided, the skill will resolve it by:
  - local map (`lookup_path`) when `lookup_mode` is `local` or `auto`
  - online geocoding when `lookup_mode` is `online` or `auto`
- `lookup_provider` defaults to `nominatim`. For `amap`/`tencent`, provide `lookup_key`
  (or set env `BAZI_GEOCODE_KEY`).
- `lookup_path` defaults to `./cities.json` next to `main.py`.
- `cache_path` defaults to `./city_cache.json` next to `main.py`.
- You can override defaults via env:
  - `BAZI_CITY_MAP_PATH`, `BAZI_CITY_CACHE_PATH`
  - `BAZI_GEOCODE_PROVIDER`, `BAZI_GEOCODE_KEY`, `BAZI_GEOCODE_TIMEOUT`
- `gender` is required when requesting `dayun` (大运) calculation.
  If `require_dayun=true` and gender is missing, return `MISSING_GENDER`.
- `rules` is optional; defaults are fixed as above.
- `flows` is optional. When provided, the skill returns 流年/流月/流日
  based on the given datetime. If omitted, flow data is not returned.
- `mode` defaults to `strict`.
- Lunar calendar is not used.

# Outputs (success)
{
  "ok": true,
  "bazi": {
    "year": { "tg": "...", "dz": "..." },
    "month": { "tg": "...", "dz": "..." },
    "day": { "tg": "...", "dz": "..." },
    "hour": { "tg": "...", "dz": "..." }
  },
  "dayun": {
    "direction": "forward|backward",
    "start_age_years": 0.0,
    "start_age_months": 0.0,
    "start_datetime": "YYYY-MM-DDTHH:MM:SS",
    "cycles": [
      {
        "index": 1,
        "tg": "...",
        "dz": "...",
        "gz": "...",
        "start_age_years": 0.0,
        "start_datetime": "YYYY-MM-DDTHH:MM:SS",
        "end_datetime": "YYYY-MM-DDTHH:MM:SS"
      }
    ]
  },
  "flows": {
    "datetime": "YYYY-MM-DDTHH:MM:SS",
    "year": { "tg": "...", "dz": "...", "gz": "..." },
    "month": { "tg": "...", "dz": "...", "gz": "..." },
    "day": { "tg": "...", "dz": "...", "gz": "..." }
  },
  "solar_terms": {
    "prev": { "name": "...", "datetime": "..." },
    "next": { "name": "...", "datetime": "..." }
  },
  "meta": {
    "timezone": "IANA/Timezone",
    "rules_used": {
      "year_boundary": "lichun",
      "month_rule": "solar_terms",
      "day_boundary": "00:00"
    },
    "true_solar_time": {
      "method": "mean_solar_time|true_solar_time",
      "datetime": "...",
      "delta_minutes": 0.0,
      "equation_of_time_minutes": 0.0,
      "longitude_correction_minutes": 0.0
    },
    "confidence": "high|medium|low",
    "notes": []
  }
}

# Outputs (failure)
{
  "ok": false,
  "error": {
    "code": "INVALID_DATETIME|INVALID_TIMEZONE|INVALID_LOCATION|MISSING_DATE|MISSING_TIME|MISSING_LOCATION|MISSING_GENDER",
    "missing": ["date|time|timezone|location|gender"],
    "message": "Human-readable error for agent use"
  }
}

# Fixed rules
- Year boundary: `lichun`
- Month boundary: split by solar terms
- Day boundary: `00:00`
- Time correction:
  - `mean_solar_time` (default): longitude correction only
  - `true_solar_time`: longitude correction + equation of time
- `require_dayun`: false (set true only when user requests dayun)
- Day pillar base: 1984-02-02 is 丙寅日 (used as reference)

# Missing time handling
- `strict` mode: return `MISSING_TIME` if hour is missing or ambiguous.
- `lenient` mode (not default): return candidates and set `confidence=low`.

# Tests (minimum)
- Before/after lichun (year boundary)
- Around solar term boundaries (month boundary)
- Day boundary at 00:00
- Timezone shifts (same UTC, different local date)
- Missing time (strict error)

# Implementation
Entry point: `main.py` (reads JSON from stdin, prints JSON).
Example:
```
echo '{"datetime":"1998-08-12T15:30:00","timezone":"Asia/Shanghai","location":{"name":"广州"},"rules":{"time_correction":"true_solar_time"}}' | python3 main.py
```
