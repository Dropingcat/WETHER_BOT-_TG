# process_manager.py
# -*- coding: utf-8 -*-
"""
Глобальный координатор зависимостей.
Инициализирует все сервисы один раз и предоставляет к ним доступ.
"""

import os
from typing import Optional
from config.bot_config import BotConfig
from core.utils.validator import sanitize_user_input
from core.db.central_db import CentralDB
from config.db_config import CENTRAL_DB_PATH
from config.logging_config import setup_logging

# Импорты новых сервисов


class ProcessManager:
    """
    Единый контекст приложения. Все зависимости инициализируются здесь.
    """

    def __init__(self):
        self._initialized = False
        # Конфигурация
        self.config: Optional[BotConfig] = None
        # Базы данных
        self.central_db: Optional[CentralDB] = None
        # Флаги
        self.use_simulator = os.getenv("USE_SIMULATOR", "false").lower() == "true"
        # Утилиты
        self.sanitize_user_input = sanitize_user_input

    def initialize_sync(self):
        """Синхронная инициализация всех компонентов."""
        if self._initialized:
            return

        # 1. Логирование (если ещё не настроено)
        setup_logging()

        # 2. Загрузка конфигурации
        self.config = BotConfig.load()

        # 3. Инициализация центральной БД
        self.central_db = CentralDB(db_path=CENTRAL_DB_PATH)

        self._initialized = True
        print("✅ ProcessManager: initialized (central_db ready)")

    def shutdown_sync(self):
        """Синхронное завершение (закрытие ресурсов)."""
        if not self._initialized:
            return
        print("🛑 ProcessManager: shut down")

# Глобальный экземпляр — точка доступа для всех модулей
process_manager = ProcessManager()