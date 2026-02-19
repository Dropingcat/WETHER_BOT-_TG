# scripts/weather/_services/openmeteo_client.py
import requests
from datetime import datetime
from core.models.weather_response import WeatherForecast, WeatherPoint, WeatherTrend, HourlyForecast, HourlyWeatherPoint

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_openmeteo(lat: float, lon: float) -> WeatherForecast:
    """
    Получает текущую погоду из Open-Meteo (без API key).
    # TODO: добавить обработку weather_code → описание
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,pressure_msl,relative_humidity_2m,wind_speed_10m,weather_code",
        "hourly": "temperature_2m,precipitation,pressure_msl,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto"
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    current = data["current"]
    current_point = WeatherPoint(
        timestamp=datetime.fromisoformat(current["time"]),
        temp=current["temperature_2m"],
        pressure=round(current["pressure_msl"] * 0.750062, 1),  # hPa → мм рт.ст.
        humidity=current["relative_humidity_2m"],
        description="",  # Open-Meteo не даёт текст — только код
        wind_speed=current["wind_speed_10m"],
        wind_direction="–",  # направления нет
        visibility=10.0,  # фейковое значение
        weather_code=current.get("weather_code")
    )

    # Простой тренд: сравнение с первым часом
    hourly = data["hourly"]
    trends = WeatherTrend(
        temp_change=hourly["temperature_2m"][1] - current["temperature_2m"],
        pressure_change=(hourly["pressure_msl"][1] - current["pressure_msl"]) * 0.750062,
        humidity_change=hourly["relative_humidity_2m"][1] - current["relative_humidity_2m"]
    )

    return WeatherForecast(
        location_name="Open-Meteo",
        current=current_point,
        trends=trends,
        source="open-meteo"
    )