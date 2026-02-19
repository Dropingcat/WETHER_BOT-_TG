"""Module placeholder."""
# config/logging_config.py
import logging
import logging.handlers
from pathlib import Path

def setup_logging(log_level: str = "INFO"):
    """Настраивает глобальное логирование с ротацией."""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    # Создаём root-логгер
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Форматтер
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-15s | %(funcName)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Обработчик для файла (с ротацией 10 МБ, 5 файлов)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Добавляем обработчики
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # Подавляем дублирующие логи от httpx/telegram
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)

    logging.info("🔧 Логирование инициализировано")