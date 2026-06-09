import json
import random
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..constants import DUNGEONS
from ..db import conn, cursor, get_user
from ..game_logic import loot_chance, safe_json
from ._helpers import boss_reward_config, build_dungeon_task_keyboard, rarity_for_rank


async def handle_dungeons_callback(q, user_id, action, ctx):
    keyboard = [
        [InlineKeyboardButton("🟢 E Rank", callback_data="dungeon_E")],
        [InlineKeyboardButton("🔵 D Rank", callback_data="dungeon_D")],
        [InlineKeyboardButton("🟣 C Rank", callback_data="dungeon_C")],
    ]
    await q.edit_message_text(
        "🏰 DUNGEON GATES 🏰\n\nChoose a dungeon rank.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_dungeon_enter_callback(q, user_id, action, ctx):
    rank = action.split("_")[1]
    dungeon = DUNGEONS[rank]
    enemies = random.sample(dungeon["enemy_pool"], 3)
    end_time = datetime.now() + timedelta(seconds=dungeon["time"])

    dungeon_save = {"rank": rank, "enemies": enemies}
    cursor.execute(
        """
        UPDATE users
        SET dungeon_active=?, dungeon_progress=0, dungeon_end=?
        WHERE user_id=?
        """,
        (json.dumps(dungeon_save), end_time.isoformat(), user_id),
    )
    conn.commit()

    keyboard = build_dungeon_task_keyboard(enemies, 0)
    await q.edit_message_text(
        f"🏰 {rank} DUNGEON STARTED\n\n⏳ Time Limit: {dungeon['time']} sec",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_dungeon_task_callback(q, user_id, action, ctx):
    current_user = get_user(user_id)
    dungeon_data = safe_json(current_user["dungeon_active"], None)

    if not dungeon_data:
        await q.edit_message_text("❌ Dungeon expired or corrupted.")
        return

    index = int(action.replace("dungeon_task_", ""))
    progress = current_user["dungeon_progress"]
    end_raw = current_user["dungeon_end"]

    if not end_raw:
        await q.edit_message_text("❌ Dungeon expired or corrupted.")
        return

    end_time = datetime.fromisoformat(end_raw)
    if datetime.now() > end_time:
        await q.edit_message_text("💀 Dungeon Failed - Time Expired")
        return
    if index != progress:
        await q.edit_message_text("❌ Invalid action")
        return

    progress += 1
    cursor.execute(
        "UPDATE users SET dungeon_progress=? WHERE user_id=?",
        (progress, user_id),
    )
    conn.commit()

    keyboard = build_dungeon_task_keyboard(dungeon_data["enemies"], progress)
    await q.edit_message_text(
        f"🏰 DUNGEON IN PROGRESS\n\nProgress: {progress}/{len(dungeon_data['enemies'])}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_boss_callback(q, user_id, action, ctx):
    current_user = get_user(user_id)
    dungeon_data = safe_json(current_user["dungeon_active"], None)

    if dungeon_data is None:
        await q.edit_message_text("❌ Dungeon corrupted. Restart.")
        return

    boss = random.choice(DUNGEONS[dungeon_data["rank"]]["boss_pool"])
    cursor.execute("UPDATE users SET boss_active=1 WHERE user_id=?", (user_id,))
    conn.commit()

    end_time = datetime.fromisoformat(current_user["dungeon_end"])
    time_left = max(int((end_time - datetime.now()).total_seconds()), 0)
    minutes = time_left // 60
    seconds = time_left % 60

    keyboard = [
        [
            InlineKeyboardButton(
                f"⚔ DEFEAT BOSS: {boss['name']}", callback_data="boss_defeat"
            )
        ]
    ]
    await q.edit_message_text(
        f"👹 BOSS ROOM 👹\n\n"
        f"Boss: {boss['name']}\n"
        f"task: {boss['task']}\n\n"
        f"⏳ Time Left: {minutes:02d}:{seconds:02d}s",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_boss_defeat_callback(q, user_id, action, ctx):
    current_user = get_user(user_id)
    dungeon_data = safe_json(current_user["dungeon_active"], None)
    if dungeon_data is None:
        await q.edit_message_text("❌ Dungeon corrupted. Restart.")
        return

    end_time = datetime.fromisoformat(current_user["dungeon_end"])
    if datetime.now() > end_time:
        await q.edit_message_text("💀 Dungeon Failed - Time Expired")
        return

    xp = ctx["xp"]
    gold = ctx["gold"]
    total_sense = ctx["total_sense"]

    rank = dungeon_data["rank"]
    base_xp = DUNGEONS[rank]["xp"]
    xp_mult, gold_min, gold_max, loot_bonus = boss_reward_config(rank)
    reward = int(base_xp * xp_mult)
    gold_reward = random.randint(gold_min, gold_max)

    xp += reward
    gold += gold_reward

    loot_msg = ""
    drop_chance = min(loot_chance(total_sense) + loot_bonus, 0.95)
    if random.random() < drop_chance:
        item = random.choice(
            [
                ("Iron Sword", "weapon"),
                ("Leather Armor", "armor"),
                ("Hunter Ring", "charm"),
                ("Steel Boots", "armor"),
            ]
        )
        rarity = rarity_for_rank(rank)
        cursor.execute(
            """
            INSERT INTO inventory (
                user_id, item_name, slot, rarity,
                strength, intelligence, agility, vitality, sense, equipped
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                item[0],
                item[1],
                rarity,
                random.randint(1, 3),
                random.randint(0, 2),
                random.randint(0, 2),
                random.randint(0, 2),
                random.randint(0, 2),
                0,
            ),
        )
        loot_msg = f"\n🎁 Loot Dropped: {rarity.upper()} {item[0]}"

    cursor.execute(
        """
        UPDATE users
        SET xp=?,
            gold=?,
            dungeon_active='',
            dungeon_progress=0,
            dungeon_end='',
            boss_active=0
        WHERE user_id=?
        """,
        (xp, gold, user_id),
    )
    conn.commit()

    await q.edit_message_text(
        f"👹 BOSS DEFEATED 👹\n\n"
        f"🏆 Dungeon Cleared\n"
        f"✨ +{reward} XP\n"
        f"💰 +{gold_reward} Gold"
        f"{loot_msg}"
    )
