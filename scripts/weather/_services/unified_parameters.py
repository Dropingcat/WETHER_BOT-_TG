# scripts/weather/_services/unified_parameters.py

# Группировка параметров
LOCAL_PARAMS = {"temperature_2m", "pressure_msl", "precipitation"}
GLOBAL_PARAMS = {
    "relative_humidity_2m", "cloud_cover", "visibility",
    "wind_speed_10m", "wind_direction_10m"
}

# Единый внутренний формат
UNIFIED_MAPPING = {
    "temperature_2m": "temp_c",
    "pressure_msl": "pressure_mm",
    "relative_humidity_2m": "humidity_percent",
    "precipitation": "precipitation_mm_h",
    "cloud_cover": "cloud_cover_percent",
    "visibility": "visibility_km",
    "wind_speed_10m": "wind_speed_m_s",
    "wind_direction_10m": "wind_dir_deg"  # временно в градусах
}

def api_to_internal(api_data: dict):
    """Преобразует API-данные в единый формат."""
    internal = {}
    for api_key, value in api_data.items():
        if api_key in UNIFIED_MAPPING:
            internal_key = UNIFIED_MAPPING[api_key]
            # Особая обработка давления: гПа → мм рт.ст.
            if api_key == "pressure_msl":
                value = round(value * 0.75, 1)
            # Особая обработка видимости: метры → км
            elif api_key == "visibility":
                value = value / 1000.0
            internal[internal_key] = value
    return internal

def deg_to_8dir(deg: float) -> str:
    """Преобразует градусы в 8-розу ветров."""
    dirs = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    return dirs[round(deg / 45) % 8]