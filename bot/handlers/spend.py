from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..db import conn, cursor, get_user
from ._helpers import render_spend_text, spend_keyboard


async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    stat_points = user["stat_points"]

    if stat_points <= 0:
        await update.message.reply_text("❌ No stat points available.")
        return

    await update.message.reply_text(
        render_spend_text(
            stat_points,
            user["strength"],
            user["intelligence"],
            user["agility"],
            user["vitality"],
            user["sense"],
        ),
        reply_markup=InlineKeyboardMarkup(spend_keyboard()),
    )


async def handle_spend_callback(q, user_id, action, ctx):
    stat_points = ctx["stat_points"]
    base_str = ctx["base_str"]
    base_int = ctx["base_int"]
    base_agi = ctx["base_agi"]
    base_vit = ctx["base_vit"]
    base_sense = ctx["base_sense"]

    if stat_points <= 0:
        await q.edit_message_text("❌ No stat points available.")
        return

    stat_points -= 1
    if action == "spend_str":
        base_str += 1
    elif action == "spend_int":
        base_int += 1
    elif action == "spend_agi":
        base_agi += 1
    elif action == "spend_vit":
        base_vit += 1
    elif action == "spend_sense":
        base_sense += 1

    cursor.execute(
        """
        UPDATE users
        SET strength=?, intelligence=?, agility=?, vitality=?, sense=?, stat_points=?
        WHERE user_id=?
        """,
        (base_str, base_int, base_agi, base_vit, base_sense, stat_points, user_id),
    )
    conn.commit()

    await q.edit_message_text(
        render_spend_text(
            stat_points, base_str, base_int, base_agi, base_vit, base_sense
        ),
        reply_markup=InlineKeyboardMarkup(spend_keyboard()),
    )
