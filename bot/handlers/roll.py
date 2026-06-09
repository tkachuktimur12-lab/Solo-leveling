import json
import random
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..constants import DUNGEONS, HIDDEN_QUESTS
from ..db import conn, cursor
from ..game_logic import get_rank
from ._helpers import build_dungeon_task_keyboard, dungeon_roll_gate_rank

_RARITY_DISPLAY = {
    "rare": "💙 Rare",
    "epic": "💜 Epic",
    "legendary": "🧡 Legendary",
}


async def handle_roll_callback(q, user_id, action, ctx):
    xp = ctx["xp"]
    rolls = ctx["rolls"]
    total_sense = ctx["total_sense"]

    if rolls <= 0:
        await q.edit_message_text("No rolls")
        return

    rolls -= 1
    chance = min(0.05, 0.01 + total_sense * 0.003)

    if random.random() < chance:
        idx = random.randrange(len(HIDDEN_QUESTS))
        hidden = HIDDEN_QUESTS[idx]
        quest_name, quest_xp, rarity = hidden
        rarity_label = _RARITY_DISPLAY.get(rarity, rarity)

        # Deduct the roll now; XP is granted only on claim
        cursor.execute(
            "UPDATE users SET hidden_rolls=? WHERE user_id=?",
            (rolls, user_id),
        )
        conn.commit()

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✨ CLAIM QUEST", callback_data=f"claim_hidden_{idx}")]]
        )
        await q.edit_message_text(
            "🎲 Hidden Roll Used\n\n"
            "❓ A HIDDEN QUEST HAS APPEARED!\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📜 {quest_name}\n"
            f"⭐ Rarity: {rarity_label}\n"
            f"💎 Reward: +{quest_xp} XP\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Tap below to claim your reward!",
            reply_markup=keyboard,
        )
    else:
        await q.edit_message_text(
            "🎲 Hidden Roll Used\n\n❌ No hidden quest appeared."
        )
        cursor.execute(
            "UPDATE users SET hidden_rolls=? WHERE user_id=?",
            (rolls, user_id),
        )
        conn.commit()


async def handle_claim_hidden_callback(q, user_id, action, ctx):
    idx = int(action.split("_")[-1])
    hidden = HIDDEN_QUESTS[idx]
    quest_name, quest_xp, rarity = hidden
    rarity_label = _RARITY_DISPLAY.get(rarity, rarity)

    xp = ctx["xp"] + quest_xp
    cursor.execute("UPDATE users SET xp=? WHERE user_id=?", (xp, user_id))
    conn.commit()

    await q.edit_message_text(
        "✅ HIDDEN QUEST CLAIMED!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📜 {quest_name}\n"
        f"⭐ Rarity: {rarity_label}\n"
        f"💎 +{quest_xp} XP earned!\n"
        "━━━━━━━━━━━━━━━━━━━━",
    )


async def handle_dungeon_roll_callback(q, user_id, action, ctx):
    dungeon_rolls = ctx["dungeon_rolls"]
    level = ctx["level"]

    if dungeon_rolls <= 0:
        await q.edit_message_text(
            "❌ No dungeon rolls available.\n\nClear C-rank dungeons to earn rolls."
        )
        return

    dungeon_rolls -= 1
    hunter_rank = get_rank(level)
    gate_rank = dungeon_roll_gate_rank(hunter_rank)

    cursor.execute(
        "UPDATE users SET dungeon_rolls=? WHERE user_id=?",
        (dungeon_rolls, user_id),
    )

    if gate_rank is None:
        conn.commit()
        await q.edit_message_text(
            "[SYSTEM MESSAGE]\n"
            "Dungeon Roll failed.\n"
            "No government-locked Gate appeared."
        )
        return

    dungeon = DUNGEONS[gate_rank]
    enemies = random.sample(dungeon["enemy_pool"], 3)
    end_time = datetime.now() + timedelta(seconds=dungeon["time"])

    cursor.execute(
        """
        UPDATE users
        SET dungeon_active=?, dungeon_progress=0, dungeon_end=?
        WHERE user_id=?
        """,
        (
            json.dumps({"rank": gate_rank, "enemies": enemies}),
            end_time.isoformat(),
            user_id,
        ),
    )
    conn.commit()

    keyboard = build_dungeon_task_keyboard(enemies, 0)
    await q.edit_message_text(
        f"[SYSTEM MESSAGE]\n"
        f"A government-locked Gate has summoned you.\n"
        f"Gate Rank: {gate_rank}\n\n"
        f"🏰 SPECIAL {gate_rank}-RANK DUNGEON STARTED\n"
        f"⏳ Time Limit: {dungeon['time']} sec",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
