# scripts/weather/weather_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from jinja2 import Template
import os
import logging

from scripts.weather._services.weather_simulator import simulate_weather_today
from process_manager import process_manager
from scripts.weather._services.weather_api import get_weather_real  # ← новый импорт

# Настройка логгера
logger = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "_io", "templates", "weather_today.html.j2")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    WEATHER_TEMPLATE = f.read()

async def weather_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = process_manager.central_db
    locations = db.get_user_locations(user_id)

    if not locations:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🌍 У вас нет локаций. Добавьте через /locations."
        )
        return

    if len(locations) == 1:
        loc = locations[0]
        await show_weather_forecast(update, context, loc["location_id"], loc["display_name"])
        return

    buttons = []
    for loc in locations:
        name = loc["display_name"][:25]
        buttons.append([InlineKeyboardButton(f"📍 {name}", callback_data=f"weather_loc:{loc['location_id']}")])
    buttons.append([InlineKeyboardButton("🏠 В главное меню", callback_data="nav_main")])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите локацию для прогноза:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("weather_loc:"):
        location_id = data.split(":", 1)[1]
        user_id = update.effective_user.id
        db = process_manager.central_db
        locations = db.get_user_locations(user_id)
        loc = next((l for l in locations if l["location_id"] == location_id), None)
        if loc:
            await show_weather_forecast(update, context, location_id, loc["display_name"])


async def show_weather_forecast(update: Update, context: ContextTypes.DEFAULT_TYPE, location_id: str, name: str):
    user_id = update.effective_user.id
    db = process_manager.central_db
    locations = db.get_user_locations(user_id)
    loc = next((l for l in locations if l["location_id"] == location_id), None)
    
    if loc is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Локация не найдена.")
        return

    forecast = None
    try:
        forecast = get_weather_real(loc["lat"], loc["lon"])
        forecast.location_name = name
    except Exception as e:
        logging.error(f"Open-Meteo error: {e}")
        # Fallback на симулятор
        try:
            forecast = simulate_weather_today(name)
        except Exception as e2:
            logging.error(f"Simulator error: {e2}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Не удалось получить прогноз. Попробуйте позже."
            )
            return

    # Отправка прогноза (реального или симулятора)
    template = Template(WEATHER_TEMPLATE, autoescape=True)
    text = template.render(forecast=forecast)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ Назад к выбору", callback_data="weather_back")],
            [InlineKeyboardButton("🏠 В главное меню", callback_data="nav_main")]
        ])
    )




async def weather_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await weather_menu(update, context)