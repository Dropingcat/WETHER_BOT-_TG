# scripts/weather/forecast_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import io
import logging

from process_manager import process_manager
from scripts.weather._services._5day_openmeteo_client import get_forecast_120h_step6h
from scripts.weather._services.forecast_chart_generator import generate_forecast_chart_by_day

logger = logging.getLogger(__name__)


async def forecast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await show_forecast_chart(update, context, loc["location_id"], loc["display_name"])
        return

    buttons = []
    for loc in locations:
        name = loc["display_name"][:25]
        buttons.append([InlineKeyboardButton(f"📍 {name}", callback_data=f"forecast_loc:{loc['location_id']}")])
    buttons.append([InlineKeyboardButton("🏠 В главное меню", callback_data="nav_main")])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите локацию для 5-дневного прогноза:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def forecast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("forecast_loc:"):
        location_id = data.split(":", 1)[1]
        user_id = update.effective_user.id
        db = process_manager.central_db
        locations = db.get_user_locations(user_id)
        loc = next((l for l in locations if l["location_id"] == location_id), None)
        if loc:
            await show_forecast_chart(update, context, location_id, loc["display_name"])

async def show_forecast_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, location_id: str, name: str):
    """Показывает 5-дневный график на основе Open-Meteo."""
    user_id = update.effective_user.id
    db = process_manager.central_db
    locations = db.get_user_locations(user_id)
    loc = next((l for l in locations if l["location_id"] == location_id), None)
    
    if loc is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Локация не найдена."
        )
        return

    try:
        # Получаем реальные данные
        points = get_forecast_120h_step6h(loc["lat"], loc["lon"])
        image_bytes = generate_forecast_chart_by_day(points, name)
    except Exception as e:
        logging.error(f"Ошибка Open-Meteo: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Не удалось получить прогноз. Попробуйте позже."
        )
        return

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=InputFile(io.BytesIO(image_bytes), filename="forecast_5d.png"),
        caption=f"📅 <b>Прогноз на 5 дней: {name}</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ Назад к выбору", callback_data="forecast_back")],
            [InlineKeyboardButton("🏠 В главное меню", callback_data="nav_main")]
        ]),
        parse_mode=ParseMode.HTML
    )
async def forecast_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await forecast_menu(update, context)