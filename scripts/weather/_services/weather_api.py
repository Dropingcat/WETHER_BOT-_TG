# scripts/weather/_services/weather_api.py
import logging
import requests
from datetime import datetime
from core.models.weather_response import (
    WeatherForecast, WeatherPoint, WeatherTrend,
    HourlyForecast, HourlyWeatherPoint
)

logger = logging.getLogger(__name__)
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"  # ← УБРАЛИ ПРОБЕЛ В КОНЦЕ

def _deg_to_dir(deg):
    """Преобразует градусы ветра в направление (С, СВ и т.д.)."""
    if deg is None:
        return "–"
    try:
        deg = float(deg)
        dirs = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
        return dirs[round(deg / 45) % 8]
    except (ValueError, TypeError):
        return "–"

def _weather_code_to_emoji(code: int) -> str:
    """Преобразует WMO weather code в эмодзи."""
    if code == 0:
        return "☀️"
    elif 1 <= code <= 3:
        return "⛅"
    elif 45 <= code <= 48:
        return "🌫️"
    elif 51 <= code <= 57:
        return "🌧️"
    elif 61 <= code <= 67:
        return "🌧️"
    elif 71 <= code <= 77:
        return "❄️"
    elif 80 <= code <= 82:
        return "🌧️"
    elif 95 <= code <= 96:
        return "⛈️"
    else:
        return "🌤️"

def _get_weather_openmeteo(lat: float, lon: float) -> WeatherForecast:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,pressure_msl,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code",
        "hourly": "temperature_2m,precipitation,pressure_msl,relative_humidity_2m,wind_speed_10m,wind_direction_10m",
        "timezone": "auto"
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    current = data["current"]
    current_point = WeatherPoint(
        timestamp=datetime.fromisoformat(current["time"]),
        temp=current["temperature_2m"],
        pressure=round(current["pressure_msl"] * 0.750062, 1),
        humidity=current.get("relative_humidity_2m", 0),
        # Иконка для текущей погоды
        description=_weather_code_to_emoji(int(current["weather_code"])),
        wind_speed=current.get("wind_speed_10m", 0),
        wind_direction=_deg_to_dir(current.get("wind_direction_10m")),
        visibility=10.0
    )

    hourly = data["hourly"]
    trends = WeatherTrend(
        temp_change=round(hourly["temperature_2m"][1] - current["temperature_2m"], 1),
        pressure_change=round((hourly["pressure_msl"][1] - current["pressure_msl"]) * 0.750062, 1),
        humidity_change=round(hourly["relative_humidity_2m"][1] - current.get("relative_humidity_2m", 0), 1)
    )

    return WeatherForecast(
        location_name="",  # будет подставлено в обработчике
        current=current_point,
        trends=trends,
        source="open-meteo"
    )

def _get_weather24_openmeteo(lat: float, lon: float) -> HourlyForecast:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation,pressure_msl,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code",
        "timezone": "auto",
        "forecast_days": 2
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    hourly_data = data["hourly"]
    hourly = []
    for i in range(min(24, len(hourly_data["time"]))):
        temp = hourly_data["temperature_2m"][i]
        precip = hourly_data["precipitation"][i] or 0.0
        pressure = hourly_data["pressure_msl"][i] or 0.0
        humidity = hourly_data["relative_humidity_2m"][i] or 0.0
        wind_speed = hourly_data["wind_speed_10m"][i] or 0.0
        wind_dir = _deg_to_dir(hourly_data["wind_direction_10m"][i])
        # ← ДОБАВЛЕНО: получение иконки
        weather_code = int(hourly_data["weather_code"][i])
        weather_icon = _weather_code_to_emoji(weather_code)

        hourly.append(HourlyWeatherPoint(
            timestamp=datetime.fromisoformat(hourly_data["time"][i]),
            temp=temp,
            pressure=round(pressure * 0.750062, 1),
            precipitation=precip,
            humidity=round(humidity, 1),        # ← ДОБАВЛЕНО
            wind_dir=wind_dir,
            wind_speed=round(wind_speed, 1),
            weather_icon=weather_icon          # ← ДОБАВЛЕНО
        ))
    
    return HourlyForecast(location_name="", hourly=hourly, source="open-meteo")

# Публичные функции
def get_weather_real(lat: float, lon: float) -> WeatherForecast:
    return _get_weather_openmeteo(lat, lon)

def get_weather24_real(lat: float, lon: float) -> HourlyForecast:  # ← УБРАЛИ location_name
    return _get_weather24_openmeteo(lat, lon)

def get_forecast5d_chart(lat: float, lon: float, location_name: str) -> bytes:
    # Этот метод можно удалить — график генерируется в forecast_handler.py
    from scripts.weather._services.forecast_chart_generator import generate_forecast_chart_by_day
    hourly_forecast = _get_weather24_openmeteo(lat, lon)
    # Для 5 дней нужно больше данных — но для теста можно использовать 24ч
    return generate_forecast_chart_by_day(hourly_forecast.hourly, location_name)