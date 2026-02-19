"""Module placeholder."""
# core/models/weather_response.py
# core/models/weather_response.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class WeatherTrend:
    temp_change: float      # °C/ч
    pressure_change: float  # мм рт.ст./ч
    humidity_change: float  # %/ч

@dataclass
class WeatherPoint:
    timestamp: datetime
    temp: float
    pressure: float
    humidity: float
    description: str        # можно оставить как "Open-Meteo"
    wind_speed: float
    wind_direction: str     # ← из wind_direction_10m
    visibility: float

@dataclass
class WeatherForecast:
    location_name: str
    current: WeatherPoint
    trends: Optional[WeatherTrend] = None
    source: str = "simulator"
    
@dataclass

class HourlyWeatherPoint:
    timestamp: datetime
    temp: float
    pressure: float         # мм рт.ст.
    precipitation: float    # мм
    humidity: float         # % ← ОБЯЗАТЕЛЬНО ДОБАВЬТЕ ЭТО
    wind_dir: str
    wind_speed: float
    weather_icon: str

@dataclass
class HourlyForecast:
    location_name: str
    hourly: List[HourlyWeatherPoint]
    source: str = "simulator"
    
@dataclass
class DailyWeatherPoint:
    date: datetime                # дата (например, 2025-12-25)
    temp_day: float               # макс. температура днём
    temp_night: float             # мин. температура ночью
    pressure: float               # давление (если доступно)
    humidity: float               # влажность (если доступно)
    precipitation: float          # осадки за сутки (мм)
    weather_icon: str             # эмодзи: ☀️, 🌧️ и т.д.
    wind_dir: str                 # направление ветра
    wind_speed: float             # скорость ветра

@dataclass
class FiveDayForecast:
    location_name: str
    daily: List[DailyWeatherPoint]
    source: str = "open-meteo"    # "simulator" или "open-meteo"