from telegram import Update
from telegram.ext import ContextTypes

from ..db import get_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    print("USER LOADED:", user["user_id"])
    await update.message.reply_text("SYSTEM ONLINE\nWelcome Hunter.")
