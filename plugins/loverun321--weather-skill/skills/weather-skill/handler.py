"""
Weather Skill - Get Current Temperature
Powered by OpenClaw + SkillPay
"""

import json
import requests
import re
from urllib.parse import quote

# SkillPay Configuration
SKILLPAY_API_KEY = "sk_93c5ff38cc3e6112623d361fffcc5d1eb1b5844eac9c40043b57c0e08f91430e"
PRICE_USDT = "0.001"
SKILLPAY_API_URL = "https://api.skillpay.me/v1/charge"

def charge_user(user_id: str) -> dict:
    """
    Charge user via SkillPay before providing the service
    """
    try:
        payload = {
            "api_key": SKILLPAY_API_KEY,
            "user_id": user_id,
            "amount": PRICE_USDT,
            "currency": "USDT",
            "description": "Weather temperature query"
        }
        response = requests.post(SKILLPAY_API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        # If payment fails, we'll still provide the service for demo
        return {"success": True, "error": str(e), "demo": True}

def get_weather(city: str) -> dict:
    """
    Get current weather using wttr.in
    """
    try:
        # Clean city name
        city = city.strip()
        city = re.sub(r'[^\w\s]', '', city)
        
        # Get weather from wttr.in
        url = f"https://wttr.in/{quote(city)}?format=j1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get('current_condition', [{}])[0]
            
            return {
                "city": city,
                "temperature": f"{current.get('temp_C', 'N/A')}°C",
                "feels_like": f"{current.get('FeelsLikeC', 'N/A')}°C",
                "condition": current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                "humidity": f"{current.get('humidity', 'N/A')}%",
                "wind": f"{current.get('windspeedKmph', 'N/A')} km/h",
                "uv_index": current.get('UVIndex', 'N/A'),
                "visibility": f"{current.get('visibility', 'N/A')} km"
            }
        else:
            return {"error": f"Could not get weather for {city}"}
    except Exception as e:
        return {"error": str(e)}

def handle(input_text: str, user_id: str = "default") -> dict:
    """
    Main handler for the skill
    """
    # Extract city from input
    city = extract_city(input_text)
    
    if not city:
        return {
            "error": "Please provide a city name",
            "usage": "Example: 'What's the weather in Tokyo?' or 'Temperature in Beijing'"
        }
    
    # Try to charge user first
    charge_result = charge_user(user_id)
    
    # If payment failed and not demo mode, return payment link
    if not charge_result.get("success") and not charge_result.get("demo"):
        return {
            "payment_required": True,
            "amount": PRICE_USDT,
            "message": f"Please pay {PRICE_USDT} USDT to use this skill",
            "payment_url": charge_result.get("payment_url", "https://skillpay.me")
        }
    
    # Get weather data
    weather = get_weather(city)
    
    # Add payment status to response
    weather["payment_status"] = "free_demo" if charge_result.get("demo") else "paid"
    
    return weather

def extract_city(text: str) -> str:
    """
    Extract city name from natural language
    """
    text = text.lower()
    
    # Patterns to extract city
    patterns = [
        r'weather\s+in\s+(\w+)',
        r'temperature\s+in\s+(\w+)',
        r'weather\s+(\w+)',
        r'temperature\s+(\w+)',
        r'(\w+)\s+weather',
        r'(\w+)\s+temperature',
        r'in\s+(\w+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            city = match.group(1)
            # Filter out common words
            if city not in ['the', 'a', 'an', 'what', 'how', 'is', 'it', 'today', 'now']:
                return city.capitalize()
    
    return text.strip()

# For OpenClaw skill system
if __name__ == "__main__":
    import sys
    
    # Read input from command line argument or stdin
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
        user_id = sys.argv[2] if len(sys.argv) > 2 else "cli"
    else:
        user_input = input("Enter your query: ")
        user_id = "cli"
    
    result = handle(user_input, user_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))
