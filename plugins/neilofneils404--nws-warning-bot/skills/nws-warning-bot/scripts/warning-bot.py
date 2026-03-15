#!/usr/bin/env python3
"""
NWS Warning Polygon Bot
Checks if warning polygons intersect a specific address
"""

import json
import urllib.request
import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Configuration - set these via environment variables or config file
HOME_LAT = float(os.environ.get("WARNING_BOT_LAT", 0.0))
HOME_LON = float(os.environ.get("WARNING_BOT_LON", 0.0))
HOME_ADDRESS = os.environ.get("WARNING_BOT_ADDRESS", "Unknown Location")

# Validation
if HOME_LAT == 0.0 or HOME_LON == 0.0:
    print("Error: Set WARNING_BOT_LAT and WARNING_BOT_LON environment variables", file=sys.stderr)
    print("Example: export WARNING_BOT_LAT=40.758896 WARNING_BOT_LON=-73.985130", file=sys.stderr)
    print("         (Times Square, NYC - replace with YOUR coordinates)", file=sys.stderr)
    sys.exit(2)

# State code for NWS API (default to Ohio, override with WARNING_BOT_STATE)
STATE_CODE = os.environ.get("WARNING_BOT_STATE", "OH")
NWS_URL = f"https://api.weather.gov/alerts/active?area={STATE_CODE}"

# Warning types to monitor
WATCHED_TYPES = {
    "Tornado Warning": "🌪️ TORNADO WARNING",
    "Severe Thunderstorm Warning": "⚡ SEVERE TSTORM WARNING",
    "Tornado Watch": "👁️ TORNADO WATCH",
    "Severe Thunderstorm Watch": "👁️ SEVERE TSTORM WATCH",
}

# Database path - relative to script by default, or override with env var
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("WARNING_BOT_DATA_DIR", os.path.join(SCRIPT_DIR, "..", "data"))
DATA_DIR = os.path.abspath(DATA_DIR)  # Resolve ".."
DB_PATH = os.path.join(DATA_DIR, "warning-bot.db")
ALERT_FILE = os.path.join(DATA_DIR, "alert-pending.txt")

# Optional: contact email for User-Agent (helps NWS identify legitimate users)
CONTACT_EMAIL = os.environ.get("WARNING_BOT_CONTACT", "warning-bot@example.com")


def init_db():
    """Initialize SQLite database for alert tracking"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_alerts (
            alert_id TEXT PRIMARY KEY,
            alert_type TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def already_sent(alert_id: str) -> bool:
    """Check if alert was already sent"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sent_alerts WHERE alert_id = ?", (alert_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result


def mark_sent(alert_id: str, alert_type: str):
    """Mark alert as sent"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO sent_alerts (alert_id, alert_type, sent_at) VALUES (?, ?, ?)",
        (alert_id, alert_type, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def cleanup_old_alerts():
    """Remove alerts older than 24 hours"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    cursor.execute("DELETE FROM sent_alerts WHERE sent_at < ?", (cutoff,))
    conn.commit()
    conn.close()


def point_in_polygon(lat, lon, polygon):
    """Ray-casting algorithm for point-in-polygon test"""
    inside = False
    n = len(polygon)
    j = n - 1
    
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside


def fetch_alerts():
    """Fetch active alerts from NWS API"""
    try:
        req = urllib.request.Request(
            NWS_URL,
            headers={
                "User-Agent": "warning-bot/1.0 (your-email@example.com)",
                "Accept": "application/geo+json"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        return None


def check_warnings():
    """Check if home is inside any warning polygons"""
    cleanup_old_alerts()
    
    data = fetch_alerts()
    if not data or "features" not in data:
        return []
    
    alerts_for_home = []
    
    for feature in data["features"]:
        props = feature.get("properties", {})
        event_type = props.get("event", "")
        alert_id = feature.get("id", props.get("@id", ""))
        
        if event_type not in WATCHED_TYPES:
            continue
        
        if already_sent(alert_id):
            continue
        
        geometry = feature.get("geometry")
        if not geometry:
            continue
        
        # Handle both Polygon and MultiPolygon geometries
        rings = []
        if geometry.get("type") == "Polygon":
            coordinates = geometry.get("coordinates", [])
            if coordinates and len(coordinates[0]) >= 3:
                rings.append(coordinates[0])
        elif geometry.get("type") == "MultiPolygon":
            for polygon in geometry.get("coordinates", []):
                if polygon and len(polygon[0]) >= 3:
                    rings.append(polygon[0])
        
        inside = False
        for exterior_ring in rings:
            if point_in_polygon(HOME_LAT, HOME_LON, exterior_ring):
                inside = True
                break
        
        if inside:
            alert_info = {
                "id": alert_id,
                "type": event_type,
                "headline": props.get("headline", "No headline"),
                "description": props.get("description", "")[:200],
                "instruction": props.get("instruction", "")[:300],
                "effective": props.get("effective", ""),
                "expires": props.get("expires", ""),
                "areaDesc": props.get("areaDesc", ""),
                "severity": props.get("severity", "Unknown"),
                "certainty": props.get("certainty", "Unknown"),
                "urgency": props.get("urgency", "Unknown"),
            }
            alerts_for_home.append(alert_info)
            mark_sent(alert_id, event_type)
    
    return alerts_for_home


def format_message(alerts):
    """Format alerts for display"""
    if not alerts:
        return None
    
    messages = []
    messages.append("🚨 WEATHER ALERT FOR YOUR ADDRESS 🚨\n")
    messages.append(f"{HOME_ADDRESS}\n")
    messages.append(f"Checked: {datetime.now().strftime('%Y-%m-%d %H:%M %Z')}\n")
    messages.append("=" * 40)
    
    for alert in alerts:
        emoji = WATCHED_TYPES.get(alert["type"], "⚠️ WARNING")
        messages.append(f"\n{emoji}")
        messages.append(f"{alert['headline']}")
        messages.append(f"Area: {alert['areaDesc']}")
        messages.append(f"Expires: {alert['expires'][:16].replace('T', ' ') if alert['expires'] else 'Unknown'}")
        messages.append(f"Certainty: {alert['certainty']} | Urgency: {alert['urgency']}")
        
        if alert["instruction"]:
            messages.append(f"\n📋 INSTRUCTION:\n{alert['instruction']}")
        
        messages.append("\n" + "-" * 20)
    
    messages.append("\n" + "=" * 40)
    messages.append("Stay safe. Check weather.gov for updates.")
    
    return "\n".join(messages)


def main():
    """Main entry point"""
    alerts = check_warnings()
    
    if alerts:
        message = format_message(alerts)
        if message:
            # Save alert to file for notification systems
            with open(ALERT_FILE, 'w') as f:
                f.write(message)
            print(message)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
