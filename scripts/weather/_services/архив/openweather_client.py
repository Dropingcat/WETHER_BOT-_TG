# scripts/weather/_services/openweather_client.py
import os
import requests
from datetime import datetime
from core.models.weather_response import WeatherPoint

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

def get_weather_openweather(lat: float, lon: float) -> WeatherPoint:
    """Возвращает WeatherPoint или None при ошибке."""
    if not API_KEY:
        return None

    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()["current"]
        
        return WeatherPoint(
            timestamp=datetime.fromtimestamp(data["dt"]),
            temp_c=data["temp"],
            pressure_mm=round(data["pressure"] * 0.75, 1),
            humidity_percent=data["humidity"],
            precipitation_mm_h=data.get("rain", {}).get("1h", 0.0),
            cloud_cover_percent=data["clouds"],
            visibility_km=data.get("visibility", 10000) / 1000,
            wind_speed_m_s=data.get("wind_speed", 0.0),
            wind_dir=deg_to_8dir(data.get("wind_deg", 0.0))
        )
    except Exception as e:
        print(f"OpenWeather error: {e}")
        return None

from .unified_parameters import deg_to_8dir