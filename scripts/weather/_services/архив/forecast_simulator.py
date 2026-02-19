# scripts/weather/_services/forecast_simulator.py
"""
Симулятор 5-дневного прогноза с генерацией графика (заглушка).
"""
import matplotlib
matplotlib.use('Agg')  # важно для работы без GUI
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta

def generate_forecast_chart(location_name: str) -> bytes:
    """
    Генерирует график температуры на 5 дней и возвращает его как bytes.
    
    # TODO: заменить matplotlib-график на изображение из OpenWeather API
    # FIXME: данные симулированы, нет реальных метеоданных
    """
    # Симуляция данных
    dates = [datetime.now().date() + timedelta(days=i) for i in range(5)]
    temps = [15 + 5 * (i % 3) - 2 * i for i in range(5)]  # условная температура

    # Построение графика
    plt.figure(figsize=(10, 4))
    plt.plot(dates, temps, marker='o', linestyle='-', color='#1f77b4')
    plt.title(f"Прогноз погоды на 5 дней: {location_name}", fontsize=12)
    plt.xlabel("Дата")
    plt.ylabel("Температура, °C")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=15)

    # Сохранение в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf.read()