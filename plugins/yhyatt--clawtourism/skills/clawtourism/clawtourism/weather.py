"""
Weather forecasts via Open-Meteo — free, no API key required.
Used in D-3/D-1 pre-trip alerts and day planner.
"""
from __future__ import annotations
import requests
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@dataclass
class DayForecast:
    date: date
    temp_min: float       # °C
    temp_max: float       # °C
    description: str      # "sunny", "partly cloudy", "light rain", etc.
    rain_mm: float = 0.0
    wind_kph: float = 0.0

    @property
    def summary(self) -> str:
        return f"{self.temp_max:.0f}°C, {self.description}"

    @property
    def packing_hint(self) -> Optional[str]:
        if self.rain_mm > 5:
            return "pack a rain jacket"
        if self.temp_max < 15:
            return "pack a warm layer"
        if self.temp_max > 30:
            return "light clothes, sunscreen"
        if self.temp_max < 20:
            return "light jacket for evenings"
        return None


_WMO_DESCRIPTIONS = {
    0: "sunny", 1: "mainly sunny", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "foggy", 51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow",
    80: "light showers", 81: "showers", 82: "heavy showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with hail",
}


def _geocode(city: str) -> Optional[tuple[float, float]]:
    try:
        r = requests.get(GEOCODE_URL, params={"name": city, "count": 1, "language": "en"}, timeout=8)
        results = r.json().get("results", [])
        if results:
            return results[0]["latitude"], results[0]["longitude"]
    except Exception:
        pass
    return None


def get_forecast(city: str, start: date, days: int = 5) -> list[DayForecast]:
    """Fetch daily forecasts for a city starting from `start` date."""
    coords = _geocode(city)
    if not coords:
        return []
    lat, lon = coords
    end = start + timedelta(days=days - 1)
    try:
        r = requests.get(FORECAST_URL, params={
            "latitude": lat, "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,weathercode",
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "timezone": "auto", "forecast_days": days,
        }, timeout=10)
        data = r.json().get("daily", {})
    except Exception:
        return []

    forecasts = []
    for i, d in enumerate(data.get("time", [])):
        wmo = data["weathercode"][i] if i < len(data.get("weathercode", [])) else 0
        forecasts.append(DayForecast(
            date=date.fromisoformat(d),
            temp_min=data["temperature_2m_min"][i],
            temp_max=data["temperature_2m_max"][i],
            description=_WMO_DESCRIPTIONS.get(wmo, "mixed"),
            rain_mm=data.get("precipitation_sum", [0]*days)[i] or 0,
            wind_kph=data.get("windspeed_10m_max", [0]*days)[i] or 0,
        ))
    return forecasts


def format_forecast_block(city: str, forecasts: list[DayForecast]) -> str:
    """Format a weather block for Telegram alert."""
    if not forecasts:
        return ""
    lines = [f"🌤️ *Weather in {city}:*"]
    for f in forecasts:
        hint = f" — {f.packing_hint}" if f.packing_hint else ""
        lines.append(f"  {f.date.strftime('%a %b %-d')}: {f.summary}{hint}")
    return "\n".join(lines)
