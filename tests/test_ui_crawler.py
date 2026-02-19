# tests/test_fuzz_crawler.py
import random
import logging
import uuid
from datetime import datetime
from process_manager import process_manager
from core.db.central_db import CentralDB

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)

def dump_user_state(db, user_id: int, step: int = None):
    """Дамп всех локаций пользователя для диагностики."""
    try:
        locations = db.get_user_locations(user_id)
        if step is not None:
            logging.info(f"  [Шаг {step}] Состояние БД:")
        else:
            logging.info(f"  Состояние БД при ошибке:")
        if not locations:
            logging.info("    — Нет локаций")
            return []
        for loc in locations:
            mark = " ✅" if loc["is_default"] else ""
            logging.info(f"    • {loc['display_name']}{mark} | ID: {loc['location_id']}")
        return locations
    except Exception as e:
        logging.error(f"  Ошибка дампа БД: {e}")
        return []

def test_edge_cases(db, user_id: int):
    """Тестирование крайних случаев."""
    logging.info("🔍 Тестирование крайних случаев...")
    
    # 1. Удаление последней локации
    db.add_location(user_id, "last_geo", "Последняя", 55.0, 37.0, is_default=True)
    locs = db.get_user_locations(user_id)
    assert len(locs) == 1 and locs[0]["is_default"]
    
    db.remove_location(user_id, "last_geo")
    locs = db.get_user_locations(user_id)
    assert len(locs) == 0
    logging.info("  ✅ Удаление последней локации — OK")

    # 2. Попытка назначить несуществующую локацию
    success = db.set_default_location(user_id, "nonexistent_id")
    assert not success
    logging.info("  ✅ Назначение несуществующей локации — OK")

    # 3. Добавление локации в пустое состояние — должна стать текущей
    db.add_location(user_id, "first_after_empty", "Первая", 55.0, 37.0, is_default=False)
    locs = db.get_user_locations(user_id)
    assert len(locs) == 1 and locs[0]["is_default"]
    logging.info("  ✅ Добавление в пустое состояние — OK")

    # Очистка
    for loc in locs:
        db.remove_location(user_id, loc["location_id"])
    logging.info("  ✅ Крайние случаи пройдены")

def test_random_actions(db, user_id: int, test_id: str, max_steps: int = 100):
    """Fuzz-тест с расширенным набором действий."""
    location_ids = []
    actions = ["add_geo", "add_text", "set_default", "delete", "delete_all"]

    for step in range(max_steps):
        action = random.choice(actions)
        current_locations = db.get_user_locations(user_id)
        action_details = {"type": action, "location_id": None}

        try:
            if action in ("add_geo", "add_text"):
                is_geo = (action == "add_geo")
                loc_id = f"{'geo' if is_geo else 'text'}_{test_id}_{step}"
                display_name = f"{'Гео' if is_geo else 'Текст'}-{step}"
                is_default = len(current_locations) == 0
                lat, lon = (55.0 + step*0.01, 37.0) if is_geo else (0.0, 0.0)
                db.add_location(user_id, loc_id, display_name, lat, lon, is_default=is_default)
                location_ids.append(loc_id)
                logging.info(f"✅ [Шаг {step}] Добавлена {'гео' if is_geo else 'текстовая'} локация: {display_name} (по умолчанию: {is_default})")

            elif action == "set_default":
                if location_ids:
                    target_id = random.choice(location_ids)
                    success = db.set_default_location(user_id, target_id)
                    if not success:
                        # Проверяем, существует ли локация
                        exists = any(loc["location_id"] == target_id for loc in current_locations)
                        if not exists:
                            logging.warning(f"⚠️ [Шаг {step}] Локация {target_id} отсутствует")
                        else:
                            logging.error(f"❌ [Шаг {step}] set_default неожиданно провалился для существующей локации")
                            return False
                # else: нет локаций — пропускаем

            elif action == "delete":
                if location_ids:
                    target_id = random.choice(location_ids)
                    db.remove_location(user_id, target_id)
                    if target_id in location_ids:
                        location_ids.remove(target_id)
                    logging.info(f"✅ [Шаг {step}] Удалена локация: ID {target_id}")

            elif action == "delete_all":
                # Удаляем все локации
                for loc_id in location_ids[:]:
                    db.remove_location(user_id, loc_id)
                location_ids.clear()
                logging.info(f"🧹 [Шаг {step}] Удалены все локации")

            # === Проверка инварианта ===
            locations = dump_user_state(db, user_id, step)
            defaults = [l for l in locations if l["is_default"]]
            
            if locations and len(defaults) != 1:
                logging.error(f"❌ ТУПИК НА ШАГЕ {step} [ID: {test_id}]")
                logging.error(f"  Действие: {action_details}")
                logging.error(f"  Обнаружено локаций по умолчанию: {len(defaults)} (ожидалось 1)")
                return False

        except Exception as e:
            logging.exception(f"💥 Исключение на шаге {step} при действии {action_details}:")
            dump_user_state(db, user_id)
            return False

    return True

def run_stress_test():
    """Запуск стресс-теста и крайних случаев."""
    test_id = str(uuid.uuid4())[:8]
    logging.info(f"🔥 Запуск стресс-теста [ID: {test_id}]")
    
    process_manager.initialize_sync()
    db = process_manager.central_db
    user_id = 999999999

    # Очистка
    try:
        locations = db.get_user_locations(user_id)
        for loc in locations:
            db.remove_location(user_id, loc["location_id"])
    except Exception as e:
        logging.warning(f"⚠️ Очистка вызвала: {e}")

    start_time = datetime.now()

    # 1. Тест крайних случаев
    try:
        test_edge_cases(db, user_id)
    except Exception as e:
        logging.exception("❌ Крайние случаи не пройдены:")
        return False

    # 2. Fuzz-тест с 100 шагами
    if not test_random_actions(db, user_id, test_id, max_steps=100):
        return False

    # 3. Дополнительный стресс: 10 быстрых операций подряд
    for i in range(10):
        db.add_location(user_id, f"stress_{i}", f"Стресс-{i}", 0, 0, is_default=False)
    locs = db.get_user_locations(user_id)
    if len(locs) != 10:
        logging.error("❌ Стресс-тест: не все локации добавлены")
        return False
    logging.info("✅ Стресс-тест: быстрые операции — OK")

    duration = datetime.now() - start_time
    logging.info(f"✅ Стресс-тест [ID: {test_id}] пройден успешно за {duration}")
    return True

if __name__ == "__main__":
    if run_stress_test():
        exit(0)
    else:
        exit(1)