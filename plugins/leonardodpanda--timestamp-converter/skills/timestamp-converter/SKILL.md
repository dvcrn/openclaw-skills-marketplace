---
name: timestamp-converter
description: "Convert between Unix timestamps, ISO 8601 dates, and human-readable formats. Use when working with timestamps from APIs, logs, or databases that need conversion to local time, timezone adjustments, or format standardization. Supports batch conversion, timezone handling, and date arithmetic for developers working with temporal data."
---

# Timestamp Converter

Convert between Unix timestamps, ISO dates, and human-readable formats.

## When to Use

- Converting API response timestamps to readable dates
- Working with log files containing Unix timestamps
- Converting between timezones for international users
- Calculating time differences between dates
- Batch converting timestamps in data processing
- Formatting dates for different locales

## Quick Start

### Convert Unix Timestamp

```python
from datetime import datetime, timezone

def unix_to_datetime(timestamp, tz=None):
    """
    Convert Unix timestamp to datetime
    
    Args:
        timestamp: Unix timestamp (seconds or milliseconds)
        tz: Target timezone (default: UTC)
    """
    # Auto-detect seconds vs milliseconds
    if timestamp > 1e10:
        timestamp = timestamp / 1000
    
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    
    if tz:
        dt = dt.astimezone(tz)
    
    return dt

# Usage
unix_to_datetime(1704067200)
# Result: 2024-01-01 00:00:00+00:00

unix_to_datetime(1704067200000)  # Milliseconds
# Result: 2024-01-01 00:00:00+00:00
```

### Format Conversion

```python
def format_timestamp(timestamp, fmt='%Y-%m-%d %H:%M:%S'):
    """Convert timestamp to custom format"""
    dt = unix_to_datetime(timestamp)
    return dt.strftime(fmt)

# Common formats
format_timestamp(1704067200, '%Y-%m-%d')           # 2024-01-01
format_timestamp(1704067200, '%d/%m/%Y')           # 01/01/2024
format_timestamp(1704067200, '%B %d, %Y')          # January 01, 2024
format_timestamp(1704067200, '%I:%M %p')           # 12:00 AM
```

### ISO 8601 Conversion

```python
from datetime import datetime

def parse_iso8601(iso_string):
    """Parse ISO 8601 string to datetime"""
    # Handle various ISO formats
    iso_string = iso_string.replace('Z', '+00:00')
    return datetime.fromisoformat(iso_string)

def to_iso8601(dt, include_ms=False):
    """Convert datetime to ISO 8601 string"""
    if include_ms:
        return dt.isoformat()
    return dt.strftime('%Y-%m-%dT%H:%M:%S%z')

# Usage
parse_iso8601('2024-01-01T00:00:00Z')
to_iso8601(datetime.now())
```

### Timezone Conversion

```python
from zoneinfo import ZoneInfo

def convert_timezone(timestamp, from_tz='UTC', to_tz='America/New_York'):
    """Convert timestamp between timezones"""
    dt = unix_to_datetime(timestamp)
    
    # Set source timezone
    if from_tz != 'UTC':
        dt = dt.replace(tzinfo=ZoneInfo(from_tz))
    
    # Convert to target timezone
    return dt.astimezone(ZoneInfo(to_tz))

# Usage
convert_timezone(1704067200, 'UTC', 'Asia/Shanghai')
# Result: 2024-01-01 08:00:00+08:00
```

### Date Arithmetic

```python
from datetime import timedelta

def add_time(timestamp, days=0, hours=0, minutes=0):
    """Add time to timestamp"""
    dt = unix_to_datetime(timestamp)
    delta = timedelta(days=days, hours=hours, minutes=minutes)
    return dt + delta

def time_diff(timestamp1, timestamp2):
    """Calculate difference between two timestamps"""
    dt1 = unix_to_datetime(timestamp1)
    dt2 = unix_to_datetime(timestamp2)
    diff = dt2 - dt1
    
    return {
        'days': diff.days,
        'seconds': diff.seconds,
        'total_seconds': diff.total_seconds(),
        'hours': diff.total_seconds() / 3600
    }

# Usage
add_time(1704067200, days=7)  # Add 1 week
time_diff(1704067200, 1704672000)  # Difference between timestamps
```

## Batch Conversion

```python
def batch_convert(timestamps, target_format='%Y-%m-%d %H:%M:%S'):
    """Convert multiple timestamps at once"""
    results = []
    for ts in timestamps:
        try:
            formatted = format_timestamp(ts, target_format)
            results.append({'timestamp': ts, 'formatted': formatted})
        except Exception as e:
            results.append({'timestamp': ts, 'error': str(e)})
    return results

# Usage
timestamps = [1704067200, 1704672000, 1705276800]
batch_convert(timestamps)
```

## Common Formats Reference

| Format | Example | Use Case |
|--------|---------|----------|
| Unix (seconds) | `1704067200` | APIs, databases |
| Unix (ms) | `1704067200000` | JavaScript |
| ISO 8601 | `2024-01-01T00:00:00Z` | APIs, logs |
| RFC 2822 | `Mon, 01 Jan 2024 00:00:00 GMT` | Email headers |
| SQL | `2024-01-01 00:00:00` | SQL databases |

## Dependencies

```bash
pip install pytz
```

Or use Python 3.9+ built-in `zoneinfo`:
```python
from zoneinfo import ZoneInfo
```
