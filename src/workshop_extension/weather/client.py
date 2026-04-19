"""Open-Meteo weather client — free, no API key required."""

import httpx

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Pittsburgh, PA default coordinates
DEFAULT_LAT = 40.4406
DEFAULT_LON = -79.9959
DEFAULT_NAME = "Pittsburgh, PA"

# WMO weather codes that indicate precipitation (bring an umbrella)
PRECIP_CODES = {
    51, 53, 55,      # Drizzle
    61, 63, 65,      # Rain
    71, 73, 75,      # Snow
    80, 81, 82,      # Rain showers
    85, 86,          # Snow showers
    95, 96, 99,      # Thunderstorm
}

WMO_DESCRIPTIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Light snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Light rain showers", 81: "Moderate rain showers", 82: "Heavy rain showers",
    85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


def geocode(location: str) -> tuple[float, float, str]:
    """Return (lat, lon, display_name) for a Pittsburgh-area location string."""
    query = (
        location
        if any(k in location.lower() for k in ("pittsburgh", ", pa", "15"))
        else f"{location}, Pittsburgh, PA"
    )
    resp = httpx.get(
        GEOCODE_URL,
        params={"name": query, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if results:
        r = results[0]
        return r["latitude"], r["longitude"], r.get("name", location)
    return DEFAULT_LAT, DEFAULT_LON, DEFAULT_NAME


def get_forecast(lat: float, lon: float) -> dict:
    """Fetch a one-day weather forecast from Open-Meteo."""
    resp = httpx.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "daily": "weathercode,precipitation_sum,precipitation_probability_max",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "America/New_York",
            "forecast_days": 1,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def umbrella_summary(location: str) -> dict:
    """
    Return a weather summary dict for the given Pittsburgh-area location.

    Keys: display_name, current_desc, temp_f, wind_mph,
          daily_desc, precip_in, precip_pct, needs_umbrella
    """
    lat, lon, display_name = geocode(location)
    data = get_forecast(lat, lon)

    current = data.get("current_weather", {})
    current_code = int(current.get("weathercode", 0))

    daily = data.get("daily", {})
    daily_code = int((daily.get("weathercode") or [0])[0])
    precip_in = float((daily.get("precipitation_sum") or [0.0])[0] or 0.0)
    precip_pct = int((daily.get("precipitation_probability_max") or [0])[0] or 0)

    needs_umbrella = daily_code in PRECIP_CODES or precip_pct >= 40

    return {
        "display_name": display_name,
        "current_desc": WMO_DESCRIPTIONS.get(current_code, "Unknown"),
        "temp_f": current.get("temperature"),
        "wind_mph": current.get("windspeed"),
        "daily_desc": WMO_DESCRIPTIONS.get(daily_code, "Unknown"),
        "precip_in": precip_in,
        "precip_pct": precip_pct,
        "needs_umbrella": needs_umbrella,
    }
