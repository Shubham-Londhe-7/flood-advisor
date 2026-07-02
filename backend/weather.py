"""
Live rainfall integration - OpenWeatherMap API, cached 15 min per zone
to avoid rate limits and keep response fast.
"""
import os
import requests
from cachetools import TTLCache

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# cache rainfall lookups for 15 min, keyed by rounded lat/lon
_rain_cache = TTLCache(maxsize=200, ttl=900)


def get_rainfall_mm(lat: float, lon: float) -> float:
    """
    Returns rainfall volume in mm for the last 1 hour at given coords.
    Returns 0.0 if API key missing or call fails (fail-safe, never crash risk calc).
    """
    if not OPENWEATHER_API_KEY:
        return 0.0

    key = (round(lat, 2), round(lon, 2))
    if key in _rain_cache:
        return _rain_cache[key]

    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"},
            timeout=5,
        )
        data = resp.json()
        rain_mm = data.get("rain", {}).get("1h", 0.0)
        _rain_cache[key] = rain_mm
        return rain_mm
    except Exception:
        return 0.0


def rainfall_risk_boost(rain_mm: float) -> float:
    """
    Convert rainfall mm into a risk score boost (0-4 scale).
    Pune monsoon reference: >15mm/hr = heavy, >30mm/hr = very heavy (IMD scale).
    """
    if rain_mm >= 30:
        return 4.0
    elif rain_mm >= 15:
        return 2.5
    elif rain_mm >= 5:
        return 1.0
    else:
        return 0.0
