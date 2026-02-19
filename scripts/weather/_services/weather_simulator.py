# scripts/weather/_services/weather_simulator.py
import random
from datetime import datetime
from core.models.weather_response import WeatherForecast, WeatherPoint, WeatherTrend

def simulate_weather_today(location_name: str) -> WeatherForecast:
    """
    Симулирует детальный прогноз на сегодня.
    
    # TODO: заменить на OpenWeather API
    # FIXME: данные симулированы, не отражают реальность
    """
    now = datetime.now()
    
    # Текущие условия
    temp = round(10 + random.uniform(-5, 15), 1)
    pressure = round(740 + random.uniform(0, 30), 1)
    humidity = random.randint(30, 95)
    wind_speed = round(random.uniform(0, 10), 1)
    visibility = round(random.uniform(1, 20), 1)
    
    descriptions = ["Солнечно", "Пасмурно", "Дождь", "Снег", "Туман", "Гроза"]
    description = random.choice(descriptions)
    
    wind_dirs = ["С", "Ю", "З", "В", "СЗ", "ЮВ", "СВ", "ЮЗ"]
    wind_direction = random.choice(wind_dirs)
    
    current = WeatherPoint(
        timestamp=now,
        temp=temp,
        pressure=pressure,
        humidity=humidity,
        description=description,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        visibility=visibility
    )
    
    # Тренды за последний час
    trends = WeatherTrend(
        temp_change=round(random.uniform(-2, 2), 1),
        pressure_change=round(random.uniform(-5, 5), 1),
        humidity_change=round(random.uniform(-10, 10), 1)
    )
    
    return WeatherForecast(location_name=location_name, current=current, trends=trends)