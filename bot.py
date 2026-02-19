# bot.py
# -*- coding: utf-8 -*-
"""
Основной скрипт бота с обновлённым интерфейсом управления локациями.
"""
import logging
import sys
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
from process_manager import process_manager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# Импорт обработчиков локаций
from scripts.weather.location_fsm import (
    show_locations_menu,
    handle_location_callback,
    handle_text_input,
    cancel_add,
    ADD_LOCATION_INPUT,
    handle_location_geo
)
from scripts.weather.weather_handler import (
    weather_menu,
    weather_callback,
    weather_back_callback
)
from scripts.weather.forecast_handler import (
    forecast_menu,
    forecast_callback,
    forecast_back_callback
)
from scripts.weather.weather24_handler import (
    weather24_menu,
    weather24_callback,
    weather24_back_callback
)

# === Обработчики команд ===
async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "nav_weather":
        await weather_menu(update, context)
    elif query.data == "nav_weather24":  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
        await weather24_menu(update, context)
    elif query.data == "nav_forecast":
        await forecast_menu(update, context)
    elif query.data == "nav_locations":
        await show_locations_menu(update, context)
        
        
async def global_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка глобальных навигационных кнопок."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "nav_main":
        await start(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню с кнопками."""
    buttons = [
        [InlineKeyboardButton("🌤️ Погода сегодня", callback_data="nav_weather")],
        [InlineKeyboardButton("📆 Прогноз на 24ч", callback_data="nav_weather24")],
        [InlineKeyboardButton("📅 Прогноз на 5 дней", callback_data="nav_forecast")],
        [InlineKeyboardButton("📍 Управление локациями", callback_data="nav_locations")]
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🌤️ <b>Метео-бот</b>\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"⚠️ Исключение при обработке: {context.error}", exc_info=True)
    if update and hasattr(update, 'update_id'):
        logging.error(f"Update ID: {update.update_id}")
    # Можно отправить сообщение админу
# === Основная функция запуска ===
def main():
    # Инициализация
    process_manager.initialize_sync()
    logging.info("🚀 Запуск бота")
    if not process_manager.config.telegram_token:
        logging.critical("❌ TELEGRAM_BOT_TOKEN не задан")
        raise ValueError(" TELEGRAM_BOT_TOKEN не задан в .env!")

    # Создание приложения
    app = Application.builder().token(process_manager.config.telegram_token).build()

    # === Регистрация обработчиков ===
    app.add_handler(CommandHandler("start", start))

    # Основное меню локаций — обычный CommandHandler
    app.add_handler(CommandHandler("locations", show_locations_menu))

    # FSM только для текстового ввода (запускается через inline-кнопку "add_text")
    add_text_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_location_callback, pattern="^add_text$")
        ],
        states={
            ADD_LOCATION_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_add)
        ],
        per_user=True,
        allow_reentry=True
    )

    
    
    # === РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ===

    # 1. Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("locations", show_locations_menu))
    app.add_handler(CommandHandler("weather", weather_menu))
    app.add_handler(CommandHandler("forecast", forecast_menu))
    app.add_handler(CommandHandler("cancel", cancel_add))
    app.add_handler(CommandHandler("weather24", weather24_menu))

    # 2. FSM
    app.add_handler(add_text_conv)

    # 3. MessageHandler'ы
    app.add_handler(MessageHandler(filters.LOCATION, handle_location_geo))

    # 4. СПЕЦИФИЧНЫЕ CallbackQueryHandler'ы (с pattern)
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^nav_(weather24|weather|forecast|locations)$"))
    app.add_handler(CallbackQueryHandler(weather_callback, pattern="^weather_loc:"))
    app.add_handler(CallbackQueryHandler(weather_back_callback, pattern="^weather_back$"))
    app.add_handler(CallbackQueryHandler(weather24_callback, pattern="^weather24_loc:"))
    app.add_handler(CallbackQueryHandler(weather24_back_callback, pattern="^weather24_back$"))
    app.add_handler(CallbackQueryHandler(forecast_callback, pattern="^forecast_loc:"))
    app.add_handler(CallbackQueryHandler(forecast_back_callback, pattern="^forecast_back$"))
    app.add_handler(CallbackQueryHandler(global_navigation_handler, pattern="^nav_main$"))

    # 5. УНИВЕРСАЛЬНЫЙ обработчик — последним
    app.add_handler(CallbackQueryHandler(handle_location_callback))
    # 6. Обработчик ошибок
    app.add_error_handler(error_handler)
    print("🚀 Бот запущен. Используйте /locations.")
    print("Нажмите Ctrl+C для остановки.")

    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n🛑 Остановка по запросу пользователя.")
    finally:
        process_manager.shutdown_sync()
        print("✅ Бот завершил работу.")


if __name__ == "__main__":  # ← Без пробела: `__name__`
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    main()