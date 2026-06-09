from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..db import conn, cursor, get_user
from ._helpers import class_keyboard


async def awakening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if user["level"] < 10:
        await update.message.reply_text("❌ Awakening unlocks at Level 10")
        return
    if user["awakened"] == 0:
        await update.message.reply_text("❌ You have not unlocked awakening yet")
        return

    await update.message.reply_text(
        "⚡ AWAKENING COMPLETE ⚡\nChoose your FIRST class:",
        reply_markup=InlineKeyboardMarkup(class_keyboard()),
    )


async def choose_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await awakening(update, context)


async def handle_awakening_callback(q, user_id, action, ctx):
    if action == "class":
        await q.edit_message_text(
            "⚡ Choose your Awakening Class:",
            reply_markup=InlineKeyboardMarkup(class_keyboard()),
        )
        return

    # class1_* actions
    class_choice = action.split("_")[1]
    if ctx["class1"] != "none":
        await q.edit_message_text("❌ You already chose your awakening class")
        return
    cursor.execute(
        "UPDATE users SET class_stage1=? WHERE user_id=?",
        (class_choice, user_id),
    )
    conn.commit()
    await q.edit_message_text(f"⚡ Awakening Class Chosen: {class_choice.upper()}")
