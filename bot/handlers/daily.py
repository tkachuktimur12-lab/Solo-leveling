import json
import random
from datetime import datetime, timedelta

from telegram import InlineKeyboardMarkup

from ..constants import QUESTS
from ..db import conn, cursor
from ..game_logic import apply_stat_bonuses, safe_json
from ._helpers import build_daily_keyboard, check_unlocks


async def handle_daily_callback(q, user_id, action, ctx):
    last = ctx["last"]

    if last != "0":
        if datetime.now() - datetime.fromisoformat(last) < timedelta(hours=24):
            await q.edit_message_text("⏳ Daily already completed")
            return

    tasks = random.sample(QUESTS, 5)
    cursor.execute(
        "UPDATE users SET active_quests=?, quest_progress=0 WHERE user_id=?",
        (json.dumps(tasks), user_id),
    )
    conn.commit()

    await q.edit_message_text(
        "📜 DAILY QUESTS ACTIVATED 📜\n\nComplete all 5 tasks.",
        reply_markup=InlineKeyboardMarkup(build_daily_keyboard(tasks, 0)),
    )


async def handle_task_callback(q, user_id, action, ctx):
    quests_data = ctx["quests_data"]
    progress = ctx["progress"]

    tasks = safe_json(quests_data, None)
    if not tasks:
        await q.edit_message_text("❌ No active daily quests")
        return

    index = int(action.split("_")[1])
    if index != progress:
        await q.edit_message_text("❌ Invalid task")
        return

    progress += 1
    cursor.execute(
        "UPDATE users SET quest_progress=? WHERE user_id=?",
        (progress, user_id),
    )
    conn.commit()

    await q.edit_message_text(
        f"📜 DAILY QUESTS\n\nProgress: {progress}/{len(tasks)}",
        reply_markup=InlineKeyboardMarkup(build_daily_keyboard(tasks, progress)),
    )


async def handle_claim_callback(q, user_id, action, ctx, context):
    progress = ctx["progress"]
    xp = ctx["xp"]
    level = ctx["level"]
    streak = ctx["streak"]
    base_str = ctx["base_str"]
    base_int = ctx["base_int"]
    base_agi = ctx["base_agi"]
    base_vit = ctx["base_vit"]
    base_sense = ctx["base_sense"]
    stat_points = ctx["stat_points"]
    rolls = ctx["rolls"]
    total_str = ctx["total_str"]
    total_int = ctx["total_int"]
    total_sense = ctx["total_sense"]

    if progress < 5:
        await q.edit_message_text("Not done")
        return

    gain = apply_stat_bonuses(100 + streak * 5, total_str, total_int, total_sense)
    xp += gain
    streak += 1
    rolls += 1

    level_up_msg = ""
    while xp >= level * 100:
        xp -= level * 100
        level += 1
        stat_points += 5
        await check_unlocks(level, user_id, context)
        level_up_msg += (
            "\n\n[SYSTEM MESSAGE]\n"
            "Level Up.\n"
            f"Current Level: {level}\n"
            "Stat Points +5.\n"
            "Use /spend to allocate points."
        )

    cursor.execute(
        """
        UPDATE users
        SET xp=?, level=?, streak=?, last_daily=?,
            strength=?, intelligence=?, agility=?, vitality=?, sense=?,
            stat_points=?, hidden_rolls=?, active_quests=?, quest_progress=?
        WHERE user_id=?
        """,
        (
            xp,
            level,
            streak,
            datetime.now().isoformat(),
            base_str,
            base_int,
            base_agi,
            base_vit,
            base_sense,
            stat_points,
            rolls,
            "[]",
            0,
            user_id,
        ),
    )
    conn.commit()

    await q.edit_message_text(
        f"🏁 DAILY COMPLETE 🏁\n\n"
        f"✨ +{gain} XP\n"
        f"🎲 +1 Hidden Roll\n"
        f"🔥 Streak: {streak}\n"
        f"{level_up_msg}"
    )
