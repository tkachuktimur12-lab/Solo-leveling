from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..db import get_user
from ..game_logic import get_rank


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"LEVEL {user['level']}\n"
        f"XP {user['xp']}\n"
        f"STREAK {user['streak']}\n"
        f"CLASS {user['class_stage1']}\n"
        f"STAT POINTS {user['stat_points']}"
    )


async def handle_stats_callback(q, user_id, action, ctx):
    await q.edit_message_text(
        f"📊 PRECISE HUNTER DATA 📊\n\n"
        f"⚔ Level: {ctx['level']}\n"
        f"🏆 Rank: {get_rank(ctx['level'])}\n"
        f"✨ XP: {ctx['xp']}\n"
        f"🔥 Streak: {ctx['streak']}\n\n"
        f"💪 STR: {ctx['total_str']}\n"
        f"🧠 INT: {ctx['total_int']}\n"
        f"⚡ AGI: {ctx['total_agi']}\n"
        f"❤️ VIT: {ctx['total_vit']}\n"
        f"👁 SENSE: {ctx['total_sense']}\n\n"
        f"📈 Unspent Stat Points: {ctx['stat_points']}\n\n"
        f"🎲 Hidden Rolls: {ctx['rolls']}\n"
        f"🎲 Dungeon Rolls: {ctx['dungeon_rolls']}\n"
        f"⚡ Awakened: {ctx['awakened']}\n"
        f"🔥 Job Changed: {ctx['job']}\n\n"
        f"🛡 Class 1: {ctx['class1']}\n"
        f"⚔ Class 2: {ctx['class2']}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎲 Dungeon Roll", callback_data="dungeon_roll"
                    )
                ]
            ]
        ),
    )
