# scripts/weather/weather24_handler.py
import requests  # ← для обработки Timeout
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from jinja2 import Template
import os
import logging

from process_manager import process_manager
from scripts.weather._services.weather_api import get_weather24_real

logger = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "_io", "templates", "weather_24h.html.j2")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    TEMPLATE = f.read()
    
    
async def weather24_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await show_weather24(update, context, loc["location_id"], loc["display_name"])
        return

    buttons = []
    for loc in locations:
        name = loc["display_name"][:25]
        buttons.append([InlineKeyboardButton(f"📍 {name}", callback_data=f"weather24_loc:{loc['location_id']}")])
    buttons.append([InlineKeyboardButton("🏠 В главное меню", callback_data="nav_main")])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите локацию для 24-часового прогноза:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def weather24_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("weather24_loc:"):
        location_id = data.split(":", 1)[1]
        user_id = update.effective_user.id
        db = process_manager.central_db
        locations = db.get_user_locations(user_id)
        loc = next((l for l in locations if l["location_id"] == location_id), None)
        if loc:
            await show_weather24(update, context, location_id, loc["display_name"])

async def show_weather24(update: Update, context: ContextTypes.DEFAULT_TYPE, location_id: str, name: str):
    user_id = update.effective_user.id
    db = process_manager.central_db
    loc = db.get_location_by_id(user_id, location_id)
    if not loc or "lat" not in loc or "lon" not in loc:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Координаты локации не найдены."
        )
        return

    lat, lon = loc["lat"], loc["lon"]

    try:
        forecast = get_weather24_real(lat, lon)
    except requests.exceptions.Timeout:
        logger.error("Таймаут при запросе к Open-Meteo")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⏱️ Сервис Open-Meteo не отвечает. Попробуйте позже."
        )
        return
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети Open-Meteo: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Проблема с подключением к Open-Meteo. Проверьте интернет."
        )
        return
    except Exception as e:
        logger.error(f"Неизвестная ошибка 24h: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Не удалось получить 24-часовой прогноз. Обратитесь к разработчику."
        )
        return

    # Рендеринг полного текста
    template = Template(TEMPLATE, autoescape=True)
    full_text = template.render(forecast=forecast)

    # Разбивка длинного сообщения
    MAX_LENGTH = 4000
    parts = []
    remaining = full_text

    while remaining:
        if len(remaining) <= MAX_LENGTH:
            parts.append(remaining)
            break
        # Ищем последний символ новой строки в пределах лимита
        split_pos = remaining.rfind("\n", 0, MAX_LENGTH)
        if split_pos == -1:  # если нет \n — режем по лимиту
            split_pos = MAX_LENGTH
        parts.append(remaining[:split_pos])
        remaining = remaining[split_pos:].lstrip()  # убираем начальные пробелы/переносы

    # Отправка частей
    for i, part in enumerate(parts):
        # В первую часть добавляем заголовок
        if i == 0:
            message_text = f"🌤️ <b>Прогноз на 24 часа: {name}</b>\n\n" + part
        else:
            message_text = part

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text,
            parse_mode=ParseMode.HTML
        )

    # Отправка кнопок отдельным сообщением
    buttons = [
        [InlineKeyboardButton("↩️ Назад к выбору", callback_data="weather24_back")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="nav_main")]
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите действие:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def weather24_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await weather24_menu(update, context)