import random
from datetime import datetime, timedelta
from core.models.weather_response import HourlyForecast, HourlyWeatherPoint

def simulate_weather_24h(location_name: str) -> HourlyForecast:
    """
    Симулирует почасовой прогноз на 24 часа в компактном формате.
    
    # TODO: replace precipitation simulation with real data from OpenWeather API
    # FIXME: precipitation is randomly generated, not based on temperature or weather type
    """
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    hourly = []
    
    base_temp = 5 + random.uniform(-10, 20)
    base_pressure = 740 + random.uniform(0, 30)
    
    for hour in range(24):
        dt = now + timedelta(hours=hour)
        temp = round(base_temp + random.uniform(-3, 3), 1)
        pressure = round(base_pressure + random.uniform(-5, 5), 1)
        # Осадки: 0.0–5.0 мм/ч
        precipitation = round(random.uniform(0, 5), 1)
        wind_dir = random.choice(["С", "Ю", "З", "В", "СЗ", "ЮВ", "СВ", "ЮЗ"])
        wind_speed = random.randint(0, 10)
        
        hourly.append(HourlyWeatherPoint(
            timestamp=dt,
            temp=temp,
            pressure=pressure,
            precipitation=precipitation,
            wind_dir=wind_dir,
            wind_speed=wind_speed
        ))
    
    return HourlyForecast(location_name=location_name, hourly=hourly)