# scripts/weather/_services/forecast_chart_generator.py
import plotly.graph_objects as go
import io
from datetime import datetime, timezone
from math import cos, sin, radians
from collections import defaultdict

DAYS_RU = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

def get_new_year_title(location_name: str, hours_left: int) -> str:
    if hours_left < 0:
        return f"🎇 С Новым {new_year.year} годом!\n🍾 Прогноз на 5 дней: {location_name}"
    elif hours_left == 0:
        return f"🎉 Наступает Новый год!\n❄️ Прогноз на 5 дней: {location_name}"
    elif hours_left <= 24:
        return f"🎅 До Нового года: {hours_left} час(ов)!\n🌨️ Прогноз на 5 дней: {location_name}"
    elif hours_left <= 72:
        return f"🎄 До Нового года: {hours_left} час(ов)!\n🌤️ Прогноз на 5 дней: {location_name}"
    else:
        return f"🕰️ До Нового года: {hours_left} час(ов)!\n🌦️ Прогноз на 5 дней: {location_name}"

def generate_forecast_chart_by_day(points: list, location_name: str) -> bytes:
    """
    Генерирует один график на 5 дней с несколькими шкалами (без подграфиков).
    """
    
        # Рассчитываем диапазоны
    temps = [p.temp for p in points]
    pressures = [p.pressure for p in points]
    humidities = [p.humidity for p in points]
    precipitations = [p.precipitation for p in points]

    # Температура: от –30 до +45, но не уже, чем данные ±5°
    temp_min = max(-30, min(temps) - 5)
    temp_max = min(45, max(temps) + 5)

    # Давление: 700–800, но не уже, чем данные ±10 мм
    press_min = max(700, min(pressures) - 10)
    press_max = min(800, max(pressures) + 10)

    # Влажность: строго 0–100
    hum_min, hum_max = 0, 100

    # Осадки: от 0 до 120% от максимума
    precip_max = max(precipitations) * 1.2 if max(precipitations) > 0 else 5.0
    precip_max = max(precip_max, 5.0)  # минимум до 5 мм для масштаба  

    if not points:
        raise ValueError("Нет данных для графика")
    #новый год

    # === 1. РАСЧЁТ ВРЕМЕНИ ДО НОВОГО ГОДА ===
    now_utc = datetime.now(timezone.utc)
    current_point = min(points, key=lambda p: abs((p.timestamp - now_utc).total_seconds()))
    now_local = current_point.timestamp

    new_year_naive = datetime(now_local.year + 1, 1, 1, 0, 0, 0)
    new_year = new_year_naive.replace(tzinfo=now_local.tzinfo)

    if new_year > now_local:
        delta = new_year - now_local
        hours_left = int(delta.total_seconds() // 3600)
    else:
        hours_left = -1

    # === 2. ФОРМИРОВАНИЕ ЗАГОЛОВКА ===
    if hours_left < 0:
        title = f"🎇 С Новым {new_year.year} годом!\n🍾 Прогноз на 5 дней: {location_name}"
    elif hours_left == 0:
        title = f"🎉 Наступает Новый год!\n❄️ Прогноз на 5 дней: {location_name}"
    else:
        if hours_left <= 24:
            emoji = "🎅"
        elif hours_left <= 72:
            emoji = "🎄"
        else:
            emoji = "🕰️"
        title = f"{emoji} До Нового года: {hours_left} час(ов)!\n🌦️ Прогноз на 5 дней: {location_name}"

    # === 3. СОЗДАНИЕ ГРАФИКА ===
    fig = go.Figure()
    #конец новый год

    # Объединяем все данные
    times = [p.timestamp for p in points]
    temps = [p.temp for p in points]
    pressures = [p.pressure for p in points]
    humidities = [p.humidity for p in points]
    precipitations = [p.precipitation for p in points]
    wind_dirs = [p.wind_dir for p in points]
    wind_speeds = [p.wind_speed for p in points]
    icons = [p.weather_icon for p in points]
    
    # Создаём фигуру
    fig = go.Figure()
        # Иконки погоды — размещаем НАД всеми графиками
    for i, t in enumerate(times):
        fig.add_annotation(
            x=t,
            y=temps[i] + 1,
            xref="x",
            yref="y",
            text=icons[i],
            showarrow=False,
            font=dict(size=16, color="red"),
            bgcolor="rgba(255, 255, 255, 0.2)",        # ← cthsq фон прозрачность
            borderpad=3,           # отступ от текста до рамки
            #bordercolor="black",
            #borderwidth=1
            xanchor="center",
            yanchor="bottom" 
        )
    # Температура (основная ось Y)
    fig.add_trace(go.Scatter(
        x=times, y=temps,
        mode='lines+markers',
        name='Температура',
        line=dict(color='orange')
    ))
    
    # Давление (ось Y2)
    fig.add_trace(go.Scatter(
        x=times, y=pressures,
        mode='lines+markers',
        name='Давление',
        line=dict(color='green'),
        yaxis='y2'
    ))
    
    # Влажность (ось Y3)
    fig.add_trace(go.Scatter(
        x=times, y=humidities,
        mode='lines+markers',
        name='Влажность',
        line=dict(color='blue', dash='dot'),
        yaxis='y3'
    ))
    
    # Осадки (ось Y4)
    fig.add_trace(go.Bar(
        x=times, y=precipitations,
        name='Осадки',
        marker_color='blue',
        opacity=0.7,
        yaxis='y4'
    ))
    
    # Настройка осей
    fig.update_layout(
        title=title,
        #f"Прогноз на 5 дней: {location_name}",
        xaxis=dict(showticklabels=False),
#        xaxis=dict(
#            title="Время",
#            showgrid=True,
#            dtick=10800000,            # метки каждые 3 часа
#            tickformat="%a\n%d.%m",    # "Пн\n31.12"
#            tickangle=0,
#            nticks=6,
#            rangeslider=dict(visible=False)  # отключаем слайдер
#        ),
        yaxis=dict(
            title=dict(text="Темп, °C", font=dict(color="orange")),
            tickfont=dict(color="orange"),
            side="left",
            range=[temp_min, temp_max]  # ← ДОБАВЛЕНО
        ),
        yaxis2=dict(
            title=dict(text="P, мм.рт.ст.", font=dict(color="green")),
            tickfont=dict(color="green"),
            side="right",
            overlaying="y",
            showgrid=False,
            range=[press_min, press_max]  # ← ДОБАВЛЕНО
        ),
        yaxis3=dict(
            title=dict(text="Влажн, %", font=dict(color="blue")),
            tickfont=dict(color="blue"),
            side="right",
            overlaying="y",
            position=0.95,
            range=[hum_min, hum_max]  # ← ДОБАВЛЕНО
        ),
        yaxis4=dict(
            title=dict(text="Осадки, мм", font=dict(color="darkblue")),
            tickfont=dict(color="darkblue"),
            side="right",
            overlaying="y",
            position=0.90,
            range=[0, precip_max]  # ← ДОБАВЛЕНО
        ),
        width=1400,
        height=600,
        showlegend=False,
        margin=dict(l=50, r=100, t=80, b=50)
    )
   
    days = defaultdict(list)
    # === Добавление подписей дней недели ===
    for date, day_points in days.items():
        # Находим точку, ближайшую к 12:00
        t = min(day_points, key=lambda p: abs(p.timestamp.hour - 12)).timestamp
        label = f"{DAYS_RU[t.weekday()]}\n{date.strftime('%d.%m')}"
        
        fig.add_annotation(
            x=t,
            y=1.02,
            xref="x",
            yref="paper",
            text=label,
            showarrow=False,
            font=dict(size=12, weight="bold"),
            xanchor="center"
        )
    #подписи к оси Х
    for p in points:
        t = p.timestamp
        
        # Часы под каждой точкой
        fig.add_annotation(
            x=t, y=-0.04,
            xref="x", yref="paper",
            text=t.strftime("%H:%M"),
            showarrow=False,
            font=dict(size=9),
            xanchor="center"
        )
        
        # Дата только в 00:00
        if t.hour == 0:
            fig.add_annotation(
                x=t, y=-0.08,
                xref="x", yref="paper",
                text=t.strftime("%d.%m"),
                showarrow=False,
                font=dict(size=11, color="black"),
                xanchor="center"
            )
    # Вертикальные линии — границы дней

    days = defaultdict(list)
    for p in points:
        days[p.timestamp.date()].append(p.timestamp)
    
    sorted_dates = sorted(days.keys())
    for i in range(1, len(sorted_dates)):
        first_time_next_day = min(days[sorted_dates[i]])
        fig.add_vline(x=first_time_next_day, line_dash="dash", line_color="gray")
    

    # Стрелки ветра
    for i, t in enumerate(times):
        dir_angle = {"С": 0, "СВ": 45, "В": 90, "ЮВ": 135, "Ю": 180, "ЮЗ": 225, "З": 270, "СЗ": 315}.get(wind_dirs[i], 0)
        dx = 20 * cos(radians(dir_angle))  # масштабируем
        dy = 20 * sin(radians(dir_angle))
        fig.add_annotation(
            x=t, y=0,
            ax=dx, ay=dy,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="black",
            showarrow=True,
            xref="x", yref="y"
        )
    
    # Сохранение
    img_bytes = fig.to_image(format="png", width=1200, height=600, scale=2)
    return img_bytes