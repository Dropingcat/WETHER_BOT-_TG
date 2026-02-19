# scripts/test_openmeteo.py
import sys
import os

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.weather._services.weather_api import get_weather24_real

if __name__ == "__main__":
    # Пример координат: Москва
    LAT = 55.7558
    LON = 37.6176
    LOCATION_NAME = "Москва"

    print("📡 Запрос 24-часового прогноза через Open-Meteo...")
    try:
        forecast = get_weather24_real(LAT, LON, LOCATION_NAME)
        print("✅ Успех!")
        print(f"Получено точек: {len(forecast.hourly)}")
        for i, pt in enumerate(forecast.hourly[:3]):  # первые 3 часа
            print(f"  {i}: {pt.timestamp} | {pt.temp}°C | {pt.precipitation} мм | {pt.wind_dir}{pt.wind_speed}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()