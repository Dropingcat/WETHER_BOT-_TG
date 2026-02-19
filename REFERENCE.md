
---

## 📝 `REFERENCE.md` — Памятка по именованию и соглашениям (обновлённый)

---

### 🧱 **БЛОК 0: Инфраструктура**

| Компонент | Назначение | Пример |
|-----------|------------|--------|
| `config/*.py` | Конфигурация | `bot_config.py`, `db_config.py`, `process_config.py`, `logging_config.py` |
| `logs/` | Логи | `app.log`, `errors.log`, `debug.log` |
| `data/` | Временные файлы | графики, HTML-отчёты |
| `temp/` | Кэш и промежуточные данные | |
| `docs/` | Документация | `architecture.md`, `api_docs.md`, `deployment.md` |

---

### 🔌 **БЛОК 1: Система событий**

| Функция | Назначение | Пример вызова |
|---------|------------|---------------|
| `subscribe(event_type, handler)` | Синхронный обработчик | `subscribe("task_result", handler)` |
| `subscribe_async(event_type, handler)` | Асинхронный обработчик | `subscribe_async("task_complete", handler)` |
| `emit_event(event_type, event_data)` | Асинхронная отправка | `await emit_event("task_result", {"user_id": 123, ...})` |
| `emit_event_sync(...)` | Синхронная отправка | |
| `clear_all_handlers()` | Очистка обработчиков | (для тестов) |

---

### 🗃️ **БЛОК 2: Базы данных**

#### Центральная БД (`central_db.py`)
| Функция | Назначение | Аргументы |
|---------|------------|-----------|
| `init_db()` | Инициализация | — |
| `add_user(user_id)` | Добавить пользователя | `int` |
| `get_user_locations(user_id)` | Получить локации | `int` → `List[Dict]` |
| `add_user_location(...)` | Добавить локацию | `user_id, name, lat, lon, is_default` |
| `set_default_location(...)` | Установить локацию по умолчанию | `user_id, location_id` |
| `get_or_create_user_profile(...)` | Получить/создать профиль | `user_id` |
| `add_user_plant(...)` | Добавить растение | `user_id, name, species, location_id` |

#### Локальные БД (`local_db_*.py`)
| Функция | Назначение | Аргументы |
|---------|------------|-----------|
| `init_db()` | Инициализация | — |
| `cache_*_data(...)` | Кэшировать | `user_id, lat, lon, date/forecast_datetime, data, ttl_hours` |
| `get_cached_*_data(...)` | Получить кэш | `lat, lon, date/forecast_datetime, user_id` → `Optional[Dict]` |
| `cleanup_expired_*_cache()` | Очистка устаревшего | — → `int` (удалено) |

---

### 🔄 **БЛОК 3: Process Manager**

| Функция | Назначение | Аргументы |
|---------|------------|-----------|
| `enqueue_script(script_path, args, retries_left)` | Поставить задачу в очередь | `str`, `list[str]`, `int` → `str` (task_id) |
| `generate_task_id(script_path, args)` | Генерация ID задачи | `str`, `list` → `str` |
| `_execute_task(...)` | Внутреннее выполнение | (для внутреннего использования) |
| `_parse_script_output(output)` | Парсинг stdout скрипта | `str` → `list[Dict]` |

#### Вывод скрипта (stdout) — формат:
```
EVENT_TYPE:task_result
RESULT_TYPE:graph
USER_ID:123
FILE_PATH:/app/data/graph.png
SUMMARY:Сегодня +15°C
```

---

### 🛠️ **БЛОК 4: Утилиты (`core/utils/`)**

| Файл | Назначение |
|------|------------|
| `api_client.py` | Запросы к API (Open-Meteo, ECMWF и др.) |
| `data_processor.py` | Обработка, интерполяция, нормализация |
| `coordinate_manager.py` | Работа с координатами (геокодирование, безопасное добавление/выбор) |
| `error_handler.py` | Централизованная обработка ошибок |
| `validator.py` | Валидация (координаты, user_id, location) |
| `cache_manager.py` | Сохранение графиков, кэширование файлов |

---

### 📦 **БЛОК 5: Модели (`core/models/`)**

#### Оркестратор (`data_orchestrator.py`)
| Функция | Назначение |
|---------|------------|
| `DataOrchestrator.fetch_and_cache_all_data(...)` | Собирает и кэширует все данные для моделей |
| `DataOrchestrator.run_models_for_user(...)` | Запускает `meteo → health → agro` в нужном порядке |

#### Физиологическая модель (`health_predictor.py`)
| Функция | Назначение |
|---------|------------|
| `run_health_predictor(...)` | Запускает модель на основе кэшированных данных |
| `get_average_profile()` | Возвращает средний профиль (p_avg, s_avg) |
| `align_s_with_p(...)` | Корректирует `s_current`, чтобы соответствовал `p_current` |
| `predict_7day_health_state(...)` | Основной цикл прогноза на 7 дней |
| `tensor_model_fixed_with_climate_norms(...)` | Модель физиологического отклика |
| `compute_stress_index(...)` | Расчёт метеостресса из `meteo_df` |
| `compute_physiological_deviation(...)` | Расчёт отклонения от ожидаемого |
| `evolve_s(...)` | Обновление вероятностей типов `s` |
| `plot_*` | Сохранение графиков в `data/` |

> ⚠️ **ВАЖНО**: `health_predictor` **не вызывает** `meteo_model` или `agro_model` напрямую. Всё через **кэш** (`local_db_*`).

#### Метеомодель (`meteo_model.py`)
| Функция | Назначение |
|---------|------------|
| `run_meteo_model(...)` | Заглушка для расчёта метео-влияний (например, стресс-индекс) |

#### Агромодель (`agro_model.py`)
| Функция | Назначение |
|---------|------------|
| `run_agro_model(...)` | Заглушка для агропрогноза (температура, полив, фронты и т.д.) |

---

### 📜 **БЛОК 6: Скрипты (`scripts/`)**

#### Структура модуля:
```
scripts/weather/
├── weather_today_script.py
├── __init__.py
└── _processes/
    ├── data_fetcher.py
    ├── interpolator.py
    └── formatter.py
```

#### Общие соглашения:
- Скрипты **не импортируют `bot.py`**
- Всё через `sys.argv`
- Вывод в `stdout` в формате `KEY:VALUE`
- Используют `core/utils/`, `core/db/local_db_*`, `core/models/*`

---

### 🧪 **БЛОК 7: Тесты**

| Папка | Назначение |
|-------|------------|
| `tests/unit/` | Модульные тесты (одна функция) |
| `tests/integration/` | Интеграционные (цепочка: bot → process → event → bot) |
| `tests/stress/` | Нагрузочные тесты |

---

### 🧩 **БЛОК 8: Обратная связь**

- Все события через `event_bus`
- Никаких импортов `bot.py` в `core/` или `scripts/`
- Бот **только подписывается** на события
- Скрипты **не знают** о Telegram

---

### 🧭 **БЛОК 9: Управление локациями**

- Используется `core/utils/coordinate_manager.py`
- `LocationManager` — центральный класс
- **Безопасное добавление** с автозаменой при лимите (10 локаций)
- **Изоляция логики** от модулей (погода, метео, агро)

---

### 📅 **БЛОК 10: Следующие шаги**

- [ ] **Дореализовать конвертацию кэшированных данных** в `pandas.DataFrame` в `health_predictor.py`
- [ ] **Реализовать `api_client.py`** с методами `get_hourly_forecast`, `get_gfs_data`
- [ ] **Реализовать `meteo_model.py`** и `agro_model.py` на основе `health_predictor` или отдельно
- [ ] **Протестировать `data_orchestrator`** с реальными данными
- [ ] **Добавить `core/db/process_log_db.py`** для логирования задач

---

