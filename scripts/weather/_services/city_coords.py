# scripts/weather/_services/city_coords.py
# Минимальная база городов (можно расширять)
CITY_COORDINATES = {
    "москва": (55.7558, 37.6176),
    "санкт-петербург": (59.9343, 30.3351),
    "сочи": (43.5852, 39.7231),
    "екатеринбург": (56.8389, 60.6057),
    "новосибирск": (55.0084, 82.9357),
    "владивосток": (43.1056, 131.8735),
}

def get_city_coordinates(city_name: str):
    """Возвращает (lat, lon) или None."""
    key = city_name.strip().lower()
    return CITY_COORDINATES.get(key)