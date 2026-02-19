from .geo_utils import haversine
from .model_capabilities import MODEL_CAPABILITIES
from .model_capabilities import MODEL_CENTERS 
from functools import lru_cache

# Центры моделей (lat, lon)

@lru_cache(maxsize=128)  # ← кэширование выбора модели
def select_best_model(lat: float, lon: float, required_params: frozenset) -> str:
    """Выбирает модель по расстоянию и поддержке параметров."""
    # Сортируем модели по расстоянию
    required = set(required_params_frozen)
    distances = [
        (model, haversine(lat, lon, center[0], center[1]))
        for model, center in MODEL_CENTERS.items()
    ]
    distances.sort(key=lambda x: x[1])

    # Ищем первую модель, поддерживающую все параметры
    for model, _ in distances:
        caps = MODEL_CAPABILITIES.get(model, {})
        if required_params.issubset(caps.get("hourly", set())):
            return model

    return "gfs_seamless"  # fallback

# Вспомогательная функция для внешнего вызова
def get_model_for_location(lat: float, lon: float, params: list) -> str:
    return select_best_model(lat, lon, frozenset(params))