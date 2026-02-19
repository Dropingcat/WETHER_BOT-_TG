## [Unreleased]
### Added
- Команда `/forecast`: 5-дневный прогноз с графиком (заглушка)
### Added
- Обратный геокодинг для геопозиций (заглушка)
- Эмодзи-префиксы для локаций: 🏙️, 🏖️, 🏔️ и др.
### Added
- Детальный прогноз: давление, влажность, ветер, видимость
- Тренды изменений за час
- Эмодзи для состояния погоды
### Added
- Команда `/weather24`: почасовой прогноз на 24 часа
- Текстовая псевдотаблица с параметрами погоды
### Added
- Умный выбор метеомодели: по географической близости и поддержке параметров
- Поддержка региональных моделей для всей России
### Added
- Автоматический выбор метеомодели Open-Meteo по географическому региону
- Поддержка локальных моделей: ECMWF, ICON, AROME, HARMONIE
### Added
- Умный выбор метеомодели: по географической близости и поддержке параметров
- Поддержка региональных моделей для всей России

scripts/weather/_services/
├── unified_parameters.py      # только преобразование имён и единиц
├── model_capabilities.py      # ТОЛЬКО MODEL_CAPABILITIES (без MODEL_CENTERS!)
├── geo_utils.py               # только haversine()
├── model_registry.py          # MODEL_CENTERS + логика выбора
└── openmeteo_client.py        # запрос к API

теперь 
.
├── .env                          ← секреты (не в Git)
├── .gitignore
├── CHANGELOG.md
├── bot.py                        ← основной скрипт
├── process_manager.py            ← управление БД и конфигом
├── requirements.txt              ← зависимости
│
├── core/
│   └── models/
│       └── weather_response.py   ← актуальные модели
│
├── docs/
│   └── decisions/                ← ADR (001–010)
│
├── scripts/
│   └── weather/
│       ├── location_fsm.py       ← управление локациями (актуально)
│       ├── weather_handler.py    ← /weather (актуально)
│       ├── weather24_handler.py  ← /weather24 (актуально)
│       ├── forecast_handler.py   ← /forecast (актуально)
│       │
│       └── _services/
│           ├── weather_api.py     ← ЕДИНЫЙ ENTRYPOINT (актуально)
│           ├── weather_simulator.py    ← fallback (актуально)
│           ├── weather24_simulator.py  ← fallback (актуально)
│           ├── forecast_simulator.py   ← fallback (актуально)
│           ├── openweather_client.py   ← ❌ УДАЛЕНО (встроено в weather_api.py)
│           └── openmeteo_client.py     ← ❌ УДАЛЕНО (встроено в weather_api.py)
│
└── _io/
    └── templates/
        ├── weather_today.html.j2   ← актуально
        └── weather_24h.html.j2     ← актуально
		### Added
- Эмодзи погоды в /weather24 на основе WMO-кодов Open-Meteo
🌧️ 14:00  🌡️+2°C  💧1.2  📉745  💨ЮЗ4
❄️ 15:00  🌡️-1°C  💧0.3  📉746  💨С5
☀️ 16:00  🌡️+3°C  💧–    📉748  💨В2
### Changed
- Отправка геопозиции теперь определяет реальное название через OpenCage

- убрать дельту из сегодня!!

### Added
- Поддержка OpenWeather API (One Call 3.0)
- Автоматическое переключение: симулятор ↔ реальные данные
### Added
- `/forecast`: многострочный график на 5 дней (температура, давление, осадки, влажность)
[ Прогноз на 5 дней: 🏖️ Россия, Сочи ]

Погода    Пн    Вт    Ср    Чт    Пт
          ☀️    ⛅    🌧️    ❄️    ☀️

Темп    +8°C  +6°C  +4°C  +2°C  +5°C
        -2°C  -3°C  -5°C  -7°C  -4°C

Давление  758   760   755   750   756

Влажность 60%  70%   85%   90%   75%

Осадки    0     0.2   5.1   3.2   0

### Added
- Интеграция с Open-Meteo API (без ключа, без лимитов)отдельный файл
- Реальные данные для /weather, /weather24, /forecast
core/
└── models/
    └── weather_response.py       ← обновлён (добавлены DailyWeatherPoint, FiveDayForecast)

scripts/weather/_services/
├── weather_simulator.py          ← текущая погода (заглушка)
├── weather24_simulator.py        ← почасовой 24ч (заглушка)
├── forecast5d_simulator.py       ← 5-дневный (заглушка)
└── openmeteo_client.py           ← ← ← НОВЫЙ: реальный клиент