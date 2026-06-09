from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚔Daily", callback_data="daily")],
        [InlineKeyboardButton("📊Stats", callback_data="stats")],
        [InlineKeyboardButton("🎲Roll", callback_data="roll")],
        [InlineKeyboardButton("🎲 Dungeon Roll", callback_data="dungeon_roll")],
        [InlineKeyboardButton("🏰 Dungeons", callback_data="dungeons")],
        [InlineKeyboardButton("🎒 Inventory", callback_data="inventory")],
        [InlineKeyboardButton("🛒 Shop", callback_data="shop")],
    ]
    await update.message.reply_text("MENU", reply_markup=InlineKeyboardMarkup(keyboard))
