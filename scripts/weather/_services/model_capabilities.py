from typing import Dict, Set

MODEL_CAPABILITIES = {
    "ecmwf_ifs04": {
        "hourly": {"temperature_2m", "pressure_msl", "relative_humidity_2m", "precipitation", "cloud_cover"},
        "turbulence": False
    },
    "icon_seamless": {
        "hourly": {"temperature_2m", "pressure_msl", "relative_humidity_2m", "precipitation", "cloud_cover"},
        "turbulence": False
    },
    "arome_seamless": {
        "hourly": {"temperature_2m", "pressure_msl", "relative_humidity_2m", "precipitation", "cloud_cover"},
        "turbulence": False
    },
    "harmonie_seamless": {
        "hourly": {"temperature_2m", "pressure_msl", "relative_humidity_2m", "precipitation", "cloud_cover"},
        "turbulence": False
    },
    "cma_seamless": {
        "hourly": {"temperature_2m", "pressure_msl", "relative_humidity_2m", "precipitation", "cloud_cover"},
        "turbulence": False
    },
    "gfs_seamless": {
        "hourly": {"temperature_2m", "pressure_msl", "relative_humidity_2m", "precipitation", "cloud_cover", "visibility"},
        "turbulence": True  # поддерживает расчёт
    }
}
MODEL_CENTERS = {
    "ecmwf_ifs04": (55.0, 15.0),      # Центральная Европа / ЦР России
    "icon_seamless": (51.0, 10.0),    # Германия / Запад РФ
    "arome_seamless": (46.0, 2.0),    # Франция
    "harmonie_seamless": (63.0, 15.0),# Скандинавия / Север РФ
    "cma_seamless": (40.0, 110.0),    # Китай / Восточная Сибирь
    "gfs_seamless": (40.0, -100.0),   # Глобальный fallback
}
