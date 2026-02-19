import numpy as np
from datetime import datetime

def calculate_turbulence_from_gfs(gfs_data: dict) -> list:
    """
    Рассчитывает индекс турбулентности по данным GFS.
    Возвращает список значений по времени.
    """
    # Извлекаем данные по уровням давления (1000, 925, 850, ...)
    levels = [1000, 925, 850, 700, 500, 400, 300, 250]
    time_count = len(gfs_data["hourly"]["time"])
    turbulence = []

    for t in range(time_count):
        # Извлекаем профиль температуры, ветра по уровням
        temps = [gfs_data["hourly"][f"temperature_{l}hPa"][t] for l in levels]
        winds_u = [gfs_data["hourly"][f"u_component_{l}hPa"][t] for l in levels]
        winds_v = [gfs_data["hourly"][f"v_component_{l}hPa"][t] for l in levels]
        heights = [gfs_data["hourly"][f"geopotential_height_{l}hPa"][t] for l in levels]

        # Рассчитываем градиенты, Ri, турбулентность
        # ... (упрощённая логика)
        turb_index = 0.5  # заглушка
        turbulence.append(turb_index)

    return turbulence