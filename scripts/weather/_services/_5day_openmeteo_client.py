# scripts/weather/_services/openmeteo_client.py
import requests
from datetime import datetime, timezone
from core.models.weather_response import HourlyWeatherPoint
from typing import List, Optional
BASE_URL = "https://api.open-meteo.com/v1/forecast"

def _weather_code_to_emoji(code: int) -> str:
    """Преобразует WMO weather code в эмодзи с учётом интенсивности."""
    # Ясно / облачно
    if code == 0:
        return "☀️" #ясно
    elif 1 <= code <= 3:
        return "⛅"  #пасмурно
    elif code in (45, 48):
        return "🌫️" #облачно
    
    # Морось
    elif code == 51:
        return "🌦️"  # слабая морось
    elif code == 53:
        return "🌧️"  # умеренная морось
    elif code == 55:
        return "🌧️💦"  # густая — можно упростить до 🌧️
    
    # Дождь
    elif code == 61:
        return "🌦️"  # слабый дождь
    elif code == 63:
        return "🌧️"  # умеренный
    elif code == 65:
        return "⛈️"  # сильный дождь → гроза (условно)
    
    # Ледяной дождь
    elif code in (66, 67):
        return "🌧️❄️"
    
    # Снег
    elif code == 71:
        return "❄️"    # слабый
    elif code == 73:
        return "❄️❄️"  # умеренный
    elif code == 75:
        return "🌨️"    # сильный снег
    elif code == 77:
        return "❄️"
    
    # Ливни
    elif code == 80:
        return "🌦️"    # слабый ливень
    elif code == 81:
        return "🌧️"    # умеренный
    elif code == 82:
        return "⛈️"    # сильный ливень
    
    # Грозы
    elif code == 95:
        return "⛈️"
    elif code >= 96:
        return "⛈️❄️"  # гроза с градом/снегом
    
    # По умолчанию
    else:
        return "🌤️"
def _deg_to_dir(deg: float) -> str:
    """Преобразует градусы ветра в направление."""
    dirs = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    return dirs[round(deg / 45) % 8]

def fetch_hourly_data(lat: float, lon: float, hours: int = 120):
    """Получает почасовые данные на N часов вперёд."""
    params = {
        "latitude": lat,
        "longitude": lon,
        # ДОБАВЬТЕ weather_code в hourly!
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,pressure_msl,wind_speed_10m,wind_direction_10m,weather_code",
        "timezone": "auto",
        "forecast_days": 7
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_forecast_120h_step6h(lat: float, lon: float) -> List[HourlyWeatherPoint]:
    data = fetch_hourly_data(lat, lon, hours=120)
    hourly = data["hourly"]
    
    times = []
    for t_str in hourly["time"]:
        if t_str.endswith("Z"):
            t_str = t_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(t_str)  # ← парсим ОДИН раз
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    
        times.append(dt)  
    
    points = []
    for i, dt in enumerate(times):
        if dt.hour % 6 == 0 and len(points) < 24:
            # Получаем weather_code и конвертируем в emoji
            weather_code = int(hourly["weather_code"][i])
            icon = _weather_code_to_emoji(weather_code)
            
            points.append(HourlyWeatherPoint(
                timestamp=dt,
                temp=round(hourly["temperature_2m"][i], 1),
                pressure=round(hourly["pressure_msl"][i] * 0.750062, 1),
                precipitation=round(hourly["precipitation"][i], 1),
                humidity=round(hourly["relative_humidity_2m"][i], 1),
                wind_dir=_deg_to_dir(hourly["wind_direction_10m"][i]),
                wind_speed=round(hourly["wind_speed_10m"][i], 1),
                weather_icon=icon  # ← реальный emoji
            ))
    
    return points[:24]
    
def group_hourly_by_day(points: List[HourlyWeatherPoint]) -> dict:
    """Группирует почасовые точки по датам."""
    days = {}
    for p in points:
        date = p.timestamp.date()
        if date not in days:
            days[date] = []
        days[date].append(p)
    return days