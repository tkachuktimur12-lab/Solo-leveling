from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..db import conn, cursor, get_user


async def jobchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if user["level"] < 100:
        await update.message.reply_text("❌ Job Change unlocks at Level 100")
        return
    if user["job_changed"] == 0:
        await update.message.reply_text("❌ You have not unlocked Job Change yet")
        return

    keyboard = [
        [InlineKeyboardButton("Tank → Titan Guardian", callback_data="class2_tank")],
        [
            InlineKeyboardButton(
                "Assassin → Shadow Reaper", callback_data="class2_assassin"
            )
        ],
        [InlineKeyboardButton("Mage → Arcane Sovereign", callback_data="class2_mage")],
        [InlineKeyboardButton("Berserker → War God", callback_data="class2_berserker")],
    ]
    await update.message.reply_text(
        "🔥 JOB CHANGE AVAILABLE 🔥\nEvolve your class:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_jobchange_callback(q, user_id, action, ctx):
    class_choice = action.split("_")[1]
    cursor.execute(
        "UPDATE users SET class_stage2=? WHERE user_id=?",
        (class_choice, user_id),
    )
    conn.commit()
    await q.edit_message_text(f"🔥 Job Class Set: {class_choice.upper()}")
