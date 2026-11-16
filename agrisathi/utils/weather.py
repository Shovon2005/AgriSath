"""
Weather Service Client for AgriSathi.
Fetches real-time agro-meteorological data and short-term precipitation forecasts via Open-Meteo.
Backs regional baselines via dynamic configuration file (data/regional_weather_baselines.json).
"""

from typing import Dict, Any, Optional
import urllib.request
import urllib.parse
import json
from agrisathi.config import Config
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.utils.weather")

_DEFAULT_FALLBACK_PRESETS = {
    "punjab": {"temperature": 22.0, "humidity": 65.0, "rainfall": 45.0, "wind_speed": 3.8, "expected_rain": 2.0, "latitude": 30.9, "longitude": 75.8},
    "bengal": {"temperature": 27.5, "humidity": 82.0, "rainfall": 210.0, "wind_speed": 4.2, "expected_rain": 12.0, "latitude": 22.57, "longitude": 88.36},
    "maharashtra": {"temperature": 29.0, "humidity": 55.0, "rainfall": 75.0, "wind_speed": 3.5, "expected_rain": 0.0, "latitude": 19.75, "longitude": 75.71},
    "kerala": {"temperature": 28.0, "humidity": 85.0, "rainfall": 240.0, "wind_speed": 4.0, "expected_rain": 25.0, "latitude": 10.85, "longitude": 76.27},
    "rajasthan": {"temperature": 32.0, "humidity": 30.0, "rainfall": 25.0, "wind_speed": 5.5, "expected_rain": 0.0, "latitude": 27.02, "longitude": 74.22},
    "default": {"temperature": 25.0, "humidity": 70.0, "rainfall": 120.0, "wind_speed": 3.5, "expected_rain": 5.0, "latitude": 20.59, "longitude": 78.96},
}

_BASELINES_CACHE: Optional[Dict[str, Any]] = None


def reload_weather_baselines() -> Dict[str, Any]:
    """Force reload of dynamic regional weather baselines from JSON file."""
    global _BASELINES_CACHE
    path = Config.REGIONAL_WEATHER_PATH
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _BASELINES_CACHE = data.get("regions", _DEFAULT_FALLBACK_PRESETS)
        except Exception as e:
            logger.warning("Failed loading regional weather baselines: %s; using defaults.", e)
            _BASELINES_CACHE = _DEFAULT_FALLBACK_PRESETS
    else:
        _BASELINES_CACHE = _DEFAULT_FALLBACK_PRESETS

    DEFAULT_REGIONAL_PRESETS.clear()
    DEFAULT_REGIONAL_PRESETS.update(_BASELINES_CACHE)
    return _BASELINES_CACHE


def get_regional_weather_baselines() -> Dict[str, Any]:
    """Retrieve dynamic regional agro-climatic baseline normals."""
    global _BASELINES_CACHE
    if _BASELINES_CACHE is None:
        reload_weather_baselines()
    return _BASELINES_CACHE


def update_weather_baselines(new_baselines: Dict[str, Any]) -> Dict[str, Any]:
    """Dynamically update regional weather baselines and persist to configuration JSON."""
    global _BASELINES_CACHE
    current_baselines = get_regional_weather_baselines()
    current_baselines.update(new_baselines)

    path = Config.REGIONAL_WEATHER_PATH
    payload = {
        "version": "1.0",
        "description": "Agro-climatic regional baseline normals for offline fallback & baseline reference",
        "regions": current_baselines,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    _BASELINES_CACHE = current_baselines
    reload_weather_baselines()
    return _BASELINES_CACHE


# Exported dictionary for backward-compatibility
DEFAULT_REGIONAL_PRESETS: Dict[str, Any] = dict(_DEFAULT_FALLBACK_PRESETS)
reload_weather_baselines()


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
    Gracefully falls back to dynamic regional agro-climatic baselines on network failure or offline mode.
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
            logger.debug("Live weather fetch failed: %s; using dynamic regional baseline.", e)

    # Dynamic Regional Baseline Matching
    baselines = get_regional_weather_baselines()
    loc_lower = loc_clean.lower()
    preset = next((v for k, v in baselines.items() if k in loc_lower), baselines.get("default", _DEFAULT_FALLBACK_PRESETS["default"]))

    return {
        "status": "cached_fallback",
        "source": "AgriSathi Regional Agro-Climatic Baseline",
        "location": loc_clean,
        "latitude": lat if lat is not None else preset.get("latitude", 20.59),
        "longitude": lon if lon is not None else preset.get("longitude", 78.96),
        "temperature": preset["temperature"],
        "humidity": preset["humidity"],
        "rainfall": preset["rainfall"],
        "wind_speed": preset["wind_speed"],
        "expected_rainfall_24h": preset["expected_rain"],
    }
