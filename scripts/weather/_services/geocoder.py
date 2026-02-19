# scripts/weather/_services/geocoder.py
import os
import requests
from typing import Optional, Tuple

OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json"

def geocode_location(query: str) -> Optional[Tuple[float, float, str]]:
    """
    Возвращает (lat, lon, display_name) или None.
    Пример display_name: "Россия, Москва"
    """
    if not OPENCAGE_API_KEY:
        raise ValueError("OPENCAGE_API_KEY not set in .env")
    
    params = {
        "q": query,
        "key": OPENCAGE_API_KEY,
        "language": "ru",
        "limit": 1,
        "no_annotations": 1
    }
    try:
        resp = requests.get(OPENCAGE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if not data["results"]:
            return None
        
        result = data["results"][0]
        lat = result["geometry"]["lat"]
        lon = result["geometry"]["lng"]
        
        # Формируем компактное название: Страна, Город/Населённый пункт
        components = result["components"]
        country = components.get("country", "Неизвестно")
        city = (components.get("city") or 
                components.get("town") or 
                components.get("village") or 
                components.get("_normalized_city"))
        display_name = f"{country}, {city}" if city else country
        
        return round(lat, 4), round(lon, 4), display_name
    except Exception as e:
        print(f"Ошибка геокодинга: {e}")
        return None
        

def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Обратный геокодинг: координаты → человекочитаемое название.
    Возвращает "Страна, Город" или None.
    """
    if not OPENCAGE_API_KEY:
        raise ValueError("OPENCAGE_API_KEY not set in .env")
    
    params = {
        "q": f"{lat},{lon}",
        "key": OPENCAGE_API_KEY,
        "language": "ru",
        "limit": 1,
        "no_annotations": 1
    }
    try:
        resp = requests.get(OPENCAGE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if not data["results"]:
            return None
        
        result = data["results"][0]
        components = result["components"]
        country = components.get("country", "Неизвестно")
        city = (components.get("city") or 
                components.get("town") or 
                components.get("village") or 
                "Координаты")
        return f"{country}, {city}"
    except Exception as e:
        print(f"Ошибка обратного геокодинга: {e}")
        return None