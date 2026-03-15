#!/usr/bin/env python3
"""
Gaode Map All-in-One Search Script
Usage: python gaode_map.py <command> [options]

Commands:
- ip        : IP location - get user location
- geo       : Geocoding - address to coordinates
- poi       : POI search (keyword, nearby, city)
- route     : Route planning (driving, walking, transit)
- weather   : Weather query
- bus       : Bus/Transit search
- traffic   : Traffic status
- tip       : Input tips (autocomplete)
"""

import argparse
import json
import math
import urllib.parse
import urllib.request
import sys


# ============ IP Location ============
def ip_location(key, ip=None):
    """IP location - Get user's current city"""
    base_url = "https://restapi.amap.com/v3/ip"
    params = {"key": key, "output": "json"}
    if ip:
        params["ip"] = ip
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


# ============ Geocoding ============
def geocode(key, address, city=None):
    """Geocoding - Address to coordinates"""
    base_url = "https://restapi.amap.com/v3/geocode/geo"
    params = {"key": key, "address": address, "output": "json"}
    if city:
        params["city"] = city
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


def regeo(key, location):
    """Reverse geocoding - Coordinates to address"""
    base_url = "https://restapi.amap.com/v3/geocode/regeo"
    params = {"key": key, "location": location, "output": "json"}
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


# ============ POI Search ============
def search_poi(key, keyword, city=None, citylimit=False, page=1, offset=20):
    """Keyword search POI"""
    base_url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": key,
        "keywords": keyword,
        "offset": offset,
        "page": page,
        "extensions": "all",
        "output": "json"
    }
    if city:
        params["city"] = city
    if citylimit:
        params["citylimit"] = "true"
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


def search_nearby(key, location, radius, keyword, page=1, offset=20):
    """Nearby search POI"""
    base_url = "https://restapi.amap.com/v3/place/around"
    params = {
        "key": key,
        "location": location,
        "radius": radius,
        "keywords": keyword,
        "offset": offset,
        "page": page,
        "extensions": "all",
        "output": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


# ============ Route Planning ============
def route_driving(key, origin, destination, strategy=5):
    """Driving route planning"""
    base_url = "https://restapi.amap.com/v3/direction/driving"
    params = {
        "key": key,
        "origin": origin,
        "destination": destination,
        "strategy": strategy,  # 1-10: fastest, shortest, etc.
        "output": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


def route_walking(key, origin, destination):
    """Walking route planning"""
    base_url = "https://restapi.amap.com/v3/direction/walking"
    params = {
        "key": key,
        "origin": origin,
        "destination": destination,
        "output": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


def route_transit(key, origin, destination, city, strategy=0):
    """Transit/_bus route planning"""
    base_url = "https://restapi.amap.com/v3/direction/transit"
    params = {
        "key": key,
        "origin": origin,
        "destination": destination,
        "city": city,
        "strategy": strategy,  # 0: fastest, 1: least transfer, 2: least walk
        "output": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


# ============ Weather ============
def weather(key, city, extensions="base"):
    """Weather query"""
    base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": key,
        "city": city,
        "extensions": extensions,  # base: current, all: forecast
        "output": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


# ============ Traffic ============
def traffic(key, city, road=None):
    """Traffic status query"""
    base_url = "https://restapi.amap.com/v3/traffic/status/road"
    params = {"key": key, "city": city, "output": "json"}
    if road:
        params["roadname"] = road
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


# ============ Input Tips ============
def input_tips(key, keyword, city=None):
    """Input tips (autocomplete)"""
    base_url = "https://restapi.amap.com/v3/assistant/tips"
    params = {"key": key, "keywords": keyword, "output": "json"}
    if city:
        params["city"] = city
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "info": str(e)}


# ============ Distance Calculation ============
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points (in meters)"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


# ============ Output Formatters ============
def format_output(data, json_output=False, format_type="default"):
    """Format output data"""
    if data.get("status") != "1":
        msg = f"Error: {data.get('info', 'Unknown error')}"
        if json_output:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(msg)
        return
    
    if json_output:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    
    # Text format
    if format_type == "ip":
        print(f"Your location: {data.get('province', 'N/A')} {data.get('city', 'N/A')}")
        print(f"City code: {data.get('adcode', 'N/A')}")
    
    elif format_type == "geo" or format_type == "regeo":
        for gc in data.get("geocodes", [data]):
            print(f"Address: {gc.get('province','')}{gc.get('city','')}{gc.get('district','')}{gc.get('township','')}")
            print(f"Location: {gc.get('location', 'N/A')}")
    
    elif format_type == "poi":
        pois = data.get("pois", [])
        count = data.get("count", len(pois))
        print(f"Found {count} results:\n")
        for i, poi in enumerate(pois[:10], 1):
            print(f"{i}. {poi.get('name', 'N/A')}")
            print(f"   Address: {poi.get('address', 'N/A')}")
            print(f"   Location: {poi.get('location', 'N/A')}")
            if poi.get('tel'):
                print(f"   Phone: {poi.get('tel')}")
            print()
    
    elif format_type == "route":
        route = data.get("route", {})
        paths = route.get("paths", [])
        if paths:
            path = paths[0]
            print(f"Distance: {path.get('distance', 'N/A')} meters")
            print(f"Duration: {path.get('duration', 'N/A')} seconds")
            print(f"Strategy: {route.get('strategy', 'N/A')}")
            steps = path.get("steps", [])
            print(f"Steps ({len(steps)}):")
            for i, step in enumerate(steps[:5], 1):
                print(f"  {i}. {step.get('instruction', 'N/A')[:80]}")
            if len(steps) > 5:
                print(f"  ... and {len(steps)-5} more steps")
    
    elif format_type == "weather":
        lives = data.get("lives", [])
        forecasts = data.get("forecasts", [])
        if lives:
            live = lives[0]
            print(f"City: {live.get('city', 'N/A')}")
            print(f"Weather: {live.get('weather', 'N/A')}")
            print(f"Temperature: {live.get('temperature', 'N/A')}°C")
            print(f"Wind: {live.get('winddirection', 'N/A')} {live.get('windpower', 'N/A')}")
            print(f"Humidity: {live.get('humidity', 'N/A')}%")
        if forecasts:
            forecast = forecasts[0]
            print(f"\nForecast:")
            for fc in forecast.get("casts", []):
                print(f"  {fc.get('date')}: {fc.get('dayWeather')} / {fc.get('nightWeather')}, {fc.get('nightTemp')}°C ~ {fc.get('dayTemp')}°C")
    
    elif format_type == "traffic":
        roads = data.get("roads", [])
        print(f"Found {len(roads)} roads with traffic info:")
        for road in roads[:5]:
            print(f"  - {road.get('name', 'N/A')}: {road.get('status', 'N/A')}")
    
    elif format_type == "tips":
        tips = data.get("tips", [])
        print(f"Found {len(tips)} suggestions:\n")
        for i, tip in enumerate(tips[:10], 1):
            print(f"{i}. {tip.get('name', 'N/A')}")
            print(f"   Address: {tip.get('address', 'N/A')}")
            print(f"   Location: {tip.get('location', 'N/A')}")
            print()
    
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Gaode Map All-in-One Tool")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # IP
    ip_parser = subparsers.add_parser("ip", help="IP location")
    ip_parser.add_argument("--key", required=True, help="Gaode API Key")
    ip_parser.add_argument("--ip", help="IP address")
    
    # Geo
    geo_parser = subparsers.add_parser("geo", help="Geocoding - address to coordinates")
    geo_parser.add_argument("--key", required=True, help="Gaode API Key")
    geo_parser.add_argument("--address", required=True, help="Address")
    geo_parser.add_argument("--city", help="City")
    
    # Regeo
    regeo_parser = subparsers.add_parser("regeo", help="Reverse geocoding - coordinates to address")
    regeo_parser.add_argument("--key", required=True, help="Gaode API Key")
    regeo_parser.add_argument("--location", required=True, help="Coordinates (lon,lat)")
    
    # POI
    poi_parser = subparsers.add_parser("poi", help="POI search")
    poi_parser.add_argument("--key", required=True, help="Gaode API Key")
    poi_parser.add_argument("--keyword", required=True, help="Keyword")
    poi_parser.add_argument("--city", help="City")
    poi_parser.add_argument("--citylimit", action="store_true", help="Limit to city")
    poi_parser.add_argument("--location", help="Location (lon,lat) for nearby search")
    poi_parser.add_argument("--radius", type=int, default=5000, help="Radius (meters)")
    poi_parser.add_argument("--page", type=int, default=1, help="Page")
    
    # Route
    route_parser = subparsers.add_parser("route", help="Route planning")
    route_parser.add_argument("--key", required=True, help="Gaode API Key")
    route_parser.add_argument("--origin", required=True, help="Origin (lon,lat)")
    route_parser.add_argument("--destination", required=True, help="Destination (lon,lat)")
    route_parser.add_argument("--mode", default="driving", choices=["driving", "walking", "transit"], help="Mode")
    route_parser.add_argument("--city", help="City (for transit)")
    route_parser.add_argument("--strategy", type=int, default=5, help="Strategy")
    
    # Weather
    weather_parser = subparsers.add_parser("weather", help="Weather query")
    weather_parser.add_argument("--key", required=True, help="Gaode API Key")
    weather_parser.add_argument("--city", required=True, help="City")
    weather_parser.add_argument("--forecast", action="store_true", help="Include forecast")
    
    # Traffic
    traffic_parser = subparsers.add_parser("traffic", help="Traffic status")
    traffic_parser.add_argument("--key", required=True, help="Gaode API Key")
    traffic_parser.add_argument("--city", required=True, help="City")
    traffic_parser.add_argument("--road", help="Road name")
    
    # Tips
    tips_parser = subparsers.add_parser("tips", help="Input tips (autocomplete)")
    tips_parser.add_argument("--key", required=True, help="Gaode API Key")
    tips_parser.add_argument("--keyword", required=True, help="Keyword")
    tips_parser.add_argument("--city", help="City")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    json_out = args.json
    
    if args.command == "ip":
        data = ip_location(args.key, args.ip)
        format_output(data, json_out, "ip")
    
    elif args.command == "geo":
        data = geocode(args.key, args.address, args.city)
        format_output(data, json_out, "geo")
    
    elif args.command == "regeo":
        data = regeo(args.key, args.location)
        format_output(data, json_out, "regeo")
    
    elif args.command == "poi":
        if args.location:
            data = search_nearby(args.key, args.location, args.radius, args.keyword, args.page)
        else:
            data = search_poi(args.key, args.keyword, args.city, args.citylimit, args.page)
        format_output(data, json_out, "poi")
    
    elif args.command == "route":
        if args.mode == "driving":
            data = route_driving(args.key, args.origin, args.destination, args.strategy)
            format_output(data, json_out, "route")
        elif args.mode == "walking":
            data = route_walking(args.key, args.origin, args.destination)
            format_output(data, json_out, "route")
        elif args.mode == "transit":
            if not args.city:
                print("Error: --city is required for transit mode")
                return
            data = route_transit(args.key, args.origin, args.destination, args.city, args.strategy)
            format_output(data, json_out, "route")
    
    elif args.command == "weather":
        ext = "all" if args.forecast else "base"
        data = weather(args.key, args.city, ext)
        format_output(data, json_out, "weather")
    
    elif args.command == "traffic":
        data = traffic(args.key, args.city, args.road)
        format_output(data, json_out, "traffic")
    
    elif args.command == "tips":
        data = input_tips(args.key, args.keyword, args.city)
        format_output(data, json_out, "tips")


if __name__ == "__main__":
    main()
