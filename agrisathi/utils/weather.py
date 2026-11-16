"""
Weather Service Client for AgriSathi.
Fetches real-time agro-meteorological data and short-term precipitation forecasts via Open-Meteo.
Includes robust offline fallback presets.
"""

from typing import Dict, Any, Optional
import urllib.request
import urllib.parse
import json
from agrisathi.config import Config
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.utils.weather")

# Fallback regional agro-climatic presets
DEFAULT_REGIONAL_PRESETS = {
    "punjab": {"temperature": 22.0, "humidity": 65.0, "rainfall": 45.0, "wind_speed": 3.8, "expected_rain": 2.0},
    "bengal": {"temperature": 27.5, "humidity": 82.0, "rainfall": 210.0, "wind_speed": 4.2, "expected_rain": 12.0},
    "maharashtra": {"temperature": 29.0, "humidity": 55.0, "rainfall": 75.0, "wind_speed": 3.5, "expected_rain": 0.0},
    "kerala": {"temperature": 28.0, "humidity": 85.0, "rainfall": 240.0, "wind_speed": 4.0, "expected_rain": 25.0},
    "rajasthan": {"temperature": 32.0, "humidity": 30.0, "rainfall": 25.0, "wind_speed": 5.5, "expected_rain": 0.0},
    "default": {"temperature": 25.0, "humidity": 70.0, "rainfall": 120.0, "wind_speed": 3.5, "expected_rain": 5.0},
}


def geocode_location(location_name: str, timeout: float = 3.0) -> Optional[Dict[str, float]]:
    """Resolve location name to latitude and longitude using Open-Meteo Geocoding API."""
    if not location_name or location_name.strip() in ("", "Local Farm"):
        return None

    try:
        query = urllib.parse.urlencode({"name": location_name.strip(), "count": 1, "language": "en", "format": "json"})
        url = f"{Config.GEOCODING_API_BASE_URL}?{query}"
        req = urllib.request.Request(url, headers={"User-Agent": "AgriSathi-App/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results")
            if results and len(results) > 0:
                loc = results[0]
                return {
                    "latitude": float(loc["latitude"]),
                    "longitude": float(loc["longitude"]),
                    "name": loc.get("name", location_name),
                    "country": loc.get("country", ""),
                    "admin1": loc.get("admin1", ""),
                }
    except Exception as e:
        logger.debug("Geocoding lookup failed for '%s': %s", location_name, e)
    return None


def fetch_weather_data(
    location: str = "Local Farm",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timeout: float = 3.0,
) -> Dict[str, Any]:
    """
    Fetch current weather and 48-hour rainfall forecast from Open-Meteo.
    Gracefully falls back to representative agro-climatic presets on network failure or timeout.
    """
    loc_clean = (location or "Local Farm").strip()
    lat = latitude
    lon = longitude
    resolved_name = loc_clean

    if (lat is None or lon is None) and loc_clean != "Local Farm":
        geo = geocode_location(loc_clean, timeout=timeout)
        if geo:
            lat = geo["latitude"]
            lon = geo["longitude"]
            resolved_name = f"{geo['name']}, {geo.get('admin1', '')} {geo.get('country', '')}".strip()

    if lat is not None and lon is not None:
        try:
            params = urllib.parse.urlencode({
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
                "daily": "precipitation_sum",
                "timezone": "auto",
                "forecast_days": 2,
            })
            url = f"{Config.WEATHER_API_BASE_URL}?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "AgriSathi-App/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                current = data.get("current", {})
                daily = data.get("daily", {})

                precip_sums = daily.get("precipitation_sum", [])
                expected_rain_24h = float(precip_sums[0]) if precip_sums else 0.0

                return {
                    "status": "online",
                    "source": "Open-Meteo Live API",
                    "location": resolved_name,
                    "latitude": lat,
                    "longitude": lon,
                    "temperature": round(float(current.get("temperature_2m", 25.0)), 1),
                    "humidity": round(float(current.get("relative_humidity_2m", 70.0)), 1),
                    "rainfall": round(float(current.get("precipitation", 0.0)) * 24.0, 1),
                    "wind_speed": round(float(current.get("wind_speed_10m", 3.5)) / 3.6, 1),  # convert km/h to m/s
                    "expected_rainfall_24h": round(expected_rain_24h, 1),
                }
        except Exception as e:
            logger.debug("Live weather fetch failed: %s; using regional fallback.", e)

    # Regional Fallback Preset
    loc_lower = loc_clean.lower()
    preset = DEFAULT_REGIONAL_PRESETS["default"]
    for k, v in DEFAULT_REGIONAL_PRESETS.items():
        if k in loc_lower:
            preset = v
            break

    return {
        "status": "cached_fallback",
        "source": "AgriSathi Agro-Climatic Baseline",
        "location": loc_clean,
        "latitude": lat or 28.6,
        "longitude": lon or 77.2,
        "temperature": preset["temperature"],
        "humidity": preset["humidity"],
        "rainfall": preset["rainfall"],
        "wind_speed": preset["wind_speed"],
        "expected_rainfall_24h": preset["expected_rain"],
    }
