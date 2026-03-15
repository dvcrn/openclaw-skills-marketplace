#!/usr/bin/env python3
"""
Secure KMB Bus Arrival Skill (fixed)
- Removed bash wrapper (vulnerable to command injection)
- Input validation
- SSL verification enabled
- Respects proxy environment
"""

import json, sys, time, os, subprocess, re
from datetime import datetime

BASE = "https://data.etabus.gov.hk/v1/transport/kmb"
CACHE_DIR = "/tmp/kmb_bus_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Validation patterns
ROUTE_PATTERN = re.compile(r'^[A-Za-z0-9]+$')
DIRECTION_PATTERN = re.compile(r'^(O|I|outbound|inbound)$', re.IGNORECASE)
STOP_ID_PATTERN = re.compile(r'^[A-Za-z0-9]+$')

def validate_route(route: str):
    if not isinstance(route, str) or not ROUTE_PATTERN.match(route):
        raise ValueError(f"Invalid route format: '{route}'")

def validate_direction(direction: str) -> str:
    if not isinstance(direction, str) or not DIRECTION_PATTERN.match(direction):
        raise ValueError(f"Invalid direction: '{direction}'. Use 'O' or 'outbound', 'I' or 'inbound'")
    # Normalize to API codes
    d = direction.upper()
    if d == 'OUTBOUND': return 'O'
    if d == 'INBOUND': return 'I'
    return d

def validate_stop_id(stop_id: str):
    if not isinstance(stop_id, str) or not STOP_ID_PATTERN.match(stop_id):
        raise ValueError(f"Invalid stop ID format: '{stop_id}'")

def validate_name(name: str):
    if not isinstance(name, str) or not (1 <= len(name) <= 100):
        raise ValueError("Stop name must be 1-100 characters")

def cache_path(key):
    return os.path.join(CACHE_DIR, f"{key}.json")

def load_cache(key, ttl_seconds=60):
    path = cache_path(key)
    if os.path.exists(path):
        if time.time() - os.path.getmtime(path) < ttl_seconds:
            try:
                return json.load(open(path))
            except:
                pass
    return None

def save_cache(key, data):
    with open(cache_path(key), 'w') as f:
        json.dump(data, f, ensure_ascii=False)

def curl_fetch(url, retries=3, delay=2):
    """Fetch JSON with SSL verification and respecting proxy env."""
    for attempt in range(1, retries+1):
        try:
            cmd = ["curl", "-s", "-S", "--http1.1", "-4",
                   "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                   "-H", "Accept: application/json", url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode != 0:
                raise RuntimeError(f"curl error {result.returncode}: {result.stderr}")
            raw = result.stdout
            if not raw.strip():
                raise ValueError("Empty response body")
            return json.loads(raw)
        except Exception as e:
            if attempt < retries:
                time.sleep(delay)
            else:
                return {"error": str(e), "attempts": attempt}

def bound_to_api_dir(bound):
    if bound == "O": return "outbound"
    if bound == "I": return "inbound"
    return bound

def get_stop_map():
    stops = load_cache("stops_all", ttl_seconds=3600)
    if stops is None:
        data = curl_fetch(f"{BASE}/stop")
        if "error" not in data:
            stops = data.get("data", [])
            save_cache("stops_all", stops)
    if stops:
        return {s["stop"]: {"name_en": s.get("name_en",""), "name_tc": s.get("name_tc","")} for s in stops}
    return {}

def get_route_direction(route):
    validate_route(route)
    data = curl_fetch(f"{BASE}/route/?route={route}")
    if "error" in data:
        print(json.dumps({"error": data["error"]})); return
    entries = data.get("data") or data
    if not isinstance(entries, list):
        entries = [entries] if entries else []
    matching = [e for e in entries if e.get("route") == route]
    if not matching:
        print(json.dumps({"error": "Route not found"})); return
    directions = []
    for entry in matching:
        directions.append({
            "bound": entry.get("bound"),
            "name_en": (entry.get("orig_en") + " → " + entry.get("dest_en")) if entry.get("orig_en") and entry.get("dest_en") else "",
            "name_tc": (entry.get("orig_tc") + " → " + entry.get("dest_tc")) if entry.get("orig_tc") and entry.get("dest_tc") else ""
        })
    print(json.dumps({"route": route, "directions": directions}, ensure_ascii=False))

def get_route_info(route, direction):
    validate_route(route)
    direction = validate_direction(direction)
    api_dir = bound_to_api_dir(direction)
    data = curl_fetch(f"{BASE}/route-stop/{route}/{api_dir}/1")
    if "error" in data:
        print(json.dumps({"error": data["error"]})); return
    stops = data.get("data", [])
    stop_map = get_stop_map()
    result = []
    for s in stops:
        stop_id = s["stop"]
        names = stop_map.get(stop_id, {"name_en": "", "name_tc": ""})
        result.append({
            "seq": s["seq"],
            "stop": stop_id,
            "name_en": names["name_en"],
            "name_tc": names["name_tc"]
        })
    print(json.dumps({"route": route, "direction": direction, "stops": result}, ensure_ascii=False))

def get_bus_stop_id(name):
    validate_name(name)
    cache_key = "stops_all"
    stops = load_cache(cache_key, ttl_seconds=3600)
    if stops is None:
        data = curl_fetch(f"{BASE}/stop")
        if "error" in data:
            print(json.dumps({"error": data["error"]})); return
        stops = data.get("data", [])
        save_cache(cache_key, stops)
    q = name.lower()
    matches = [s for s in stops if q in s.get("name_tc","").lower() or q in s.get("name_en","").lower()]
    print(json.dumps(matches, ensure_ascii=False))

def get_next_arrivals(route, direction, stop_id):
    validate_route(route)
    direction = validate_direction(direction)
    validate_stop_id(stop_id)
    api_dir = bound_to_api_dir(direction)
    route_stop = curl_fetch(f"{BASE}/route-stop/{route}/{api_dir}/1")
    if "error" in route_stop:
        print(json.dumps({"error": route_stop["error"]})); return
    stops = route_stop.get("data", [])
    seq = None
    for s in stops:
        if s["stop"] == stop_id:
            seq = int(s["seq"])
            break
    if seq is None:
        print(json.dumps({"error": f"Stop {stop_id} not found on route {route} direction {direction}"})); return
    stop_map = get_stop_map()
    stop_name = stop_map.get(stop_id, {}).get("name_tc") or stop_map.get(stop_id, {}).get("name_en", "")
    eta_data = curl_fetch(f"{BASE}/route-eta/{route}/1")
    arrivals = []
    if "error" not in eta_data:
        items = eta_data if isinstance(eta_data, list) else eta_data.get("data", [])
        filtered = [it for it in items if it.get("dir") == direction and int(it.get("seq", 0)) == seq]
        filtered.sort(key=lambda x: x.get("eta_seq") or 0)
        for it in filtered[:3]:
            eta_str = it.get("eta")
            if not eta_str:
                continue
            try:
                dt = datetime.fromisoformat(eta_str.replace("Z", "+00:00"))
                arrivals.append(dt.strftime("%H:%M HKT"))
            except Exception:
                arrivals.append(eta_str)
    if not arrivals:
        stop_eta = curl_fetch(f"{BASE}/stop-eta/{stop_id}/1")
        if "error" not in stop_eta:
            items = stop_eta if isinstance(stop_eta, list) else stop_eta.get("data", [])
            filtered = [it for it in items if it.get("route") == route and it.get("dir") == direction]
            filtered.sort(key=lambda x: x.get("eta_seq") or 0)
            for it in filtered[:3]:
                eta_str = it.get("eta")
                if not eta_str:
                    continue
                try:
                    dt = datetime.fromisoformat(eta_str.replace("Z", "+00:00"))
                    arrivals.append(dt.strftime("%H:%M HKT"))
                except Exception:
                    arrivals.append(eta_str)
    result = {
        "stopId": stop_id,
        "stopName": stop_name,
        "route": route,
        "direction": direction,
        "arrivals": arrivals if arrivals else ["No active ETAs"]
    }
    print(json.dumps(result, ensure_ascii=False))

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing subcommand"})); return
    cmd = sys.argv[1]
    try:
        if cmd == "getRouteDirection":
            if len(sys.argv) < 3: raise ValueError("Missing route")
            get_route_direction(sys.argv[2])
        elif cmd == "getRouteInfo":
            if len(sys.argv) < 4: raise ValueError("Missing route or direction")
            get_route_info(sys.argv[2], sys.argv[3])
        elif cmd == "getBusStopID":
            if len(sys.argv) < 3: raise ValueError("Missing name")
            get_bus_stop_id(sys.argv[2])
        elif cmd == "getNextArrivals":
            if len(sys.argv) < 5: raise ValueError("Missing route, direction, stopId")
            get_next_arrivals(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            print(json.dumps({"error": f"Unknown command: {cmd}"}))
    except ValueError as ve:
        print(json.dumps({"error": str(ve)}))
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))

if __name__ == "__main__":
    main()
