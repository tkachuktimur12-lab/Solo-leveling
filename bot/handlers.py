import json
import random
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from .constants import DUNGEONS, HIDDEN_QUESTS, QUESTS, SHOP_ITEMS
from .db import conn, cursor, get_equipped_stats, get_user
from .game_logic import (
    apply_stat_bonuses,
    generate_item,
    get_rank,
    loot_chance,
    safe_json,
)


def _class_keyboard():
    return [
        [InlineKeyboardButton("Tank", callback_data="class1_tank")],
        [InlineKeyboardButton("Assassin", callback_data="class1_assassin")],
        [InlineKeyboardButton("Mage", callback_data="class1_mage")],
        [InlineKeyboardButton("Berserker", callback_data="class1_berserker")],
    ]


def _spend_keyboard():
    return [
        [InlineKeyboardButton("➕ STR", callback_data="spend_str")],
        [InlineKeyboardButton("➕ INT", callback_data="spend_int")],
        [InlineKeyboardButton("➕ AGI", callback_data="spend_agi")],
        [InlineKeyboardButton("➕ VIT", callback_data="spend_vit")],
        [InlineKeyboardButton("➕ SENSE", callback_data="spend_sense")],
    ]


def _render_spend_text(stat_points, strength, intelligence, agility, vitality, sense):
    return (
        "📈 DISTRIBUTE STAT POINTS 📈\n\n"
        f"Available points: {stat_points}\n\n"
        f"💪 STR: {strength}\n"
        f"🧠 INT: {intelligence}\n"
        f"⚡ AGI: {agility}\n"
        f"❤️ VIT: {vitality}\n"
        f"👁 SENSE: {sense}\n\n"
        "Tap a button to spend 1 point."
    )


def _build_dungeon_task_keyboard(enemies, progress):
    keyboard = []
    for i, enemy in enumerate(enemies):
        label = "✅" if i < progress else "⬜"
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{label} {enemy['name']} → {enemy['task']}",
                    callback_data=f"dungeon_task_{i}",
                )
            ]
        )
    if progress >= len(enemies):
        keyboard.append([InlineKeyboardButton("⚔ FACE BOSS", callback_data="boss")])
    return keyboard


def _build_daily_keyboard(tasks, progress):
    keyboard = []
    for i, task in enumerate(tasks):
        if i < progress:
            keyboard.append(
                [InlineKeyboardButton(f"✅ {task[0]}", callback_data="done_disabled")]
            )
        else:
            keyboard.append(
                [InlineKeyboardButton(f"⬜ {task[0]}", callback_data=f"task_{i}")]
            )
    keyboard.append([InlineKeyboardButton("🏁 CLAIM", callback_data="claim")])
    return keyboard


def _dungeon_roll_gate_rank(hunter_rank):
    r = random.random()
    if hunter_rank == "B":
        return "B" if r < 0.05 else None
    if hunter_rank == "A":
        if r < 0.07:
            return "B"
        if r < 0.09:
            return "A"
        return None
    if hunter_rank in ["S", "SS", "SSS"]:
        if r < 0.10:
            return "B"
        if r < 0.15:
            return "A"
        if r < 0.16:
            return "S"
    return None


def _boss_reward_config(rank):
    if rank in ["E", "D", "C"]:
        return 1.5, 20, 50, 0.0
    if rank == "B":
        return 2.0, 50, 100, 0.10
    if rank == "A":
        return 2.5, 80, 150, 0.20
    if rank == "S":
        return 3.0, 120, 200, 0.30
    return 1.5, 20, 50, 0.0


def _rarity_for_rank(rank):
    rarity_roll = random.random()
    if rank in ["E", "D", "C"]:
        if rarity_roll < 0.7:
            return "common"
        if rarity_roll < 0.95:
            return "rare"
        return "epic"
    if rank == "B":
        if rarity_roll < 0.4:
            return "common"
        if rarity_roll < 0.85:
            return "rare"
        return "epic"
    if rank == "A":
        if rarity_roll < 0.3:
            return "common"
        if rarity_roll < 0.8:
            return "rare"
        return "epic"
    if rank == "S":
        if rarity_roll < 0.2:
            return "common"
        if rarity_roll < 0.7:
            return "rare"
        return "epic"
    return "common"


async def check_unlocks(level, user_id, context):
    msg = ""

    if level == 10:
        msg += "⚡ AWAKENING UNLOCKED ⚡\nYou can now choose your first class.\n"
        cursor.execute("UPDATE users SET awakened=1 WHERE user_id=?", (user_id,))

    if level == 100:
        msg += "🔥 JOB CHANGE UNLOCKED 🔥\nYou can now evolve your class.\n"
        cursor.execute("UPDATE users SET job_changed=1 WHERE user_id=?", (user_id,))

    conn.commit()

    if msg:
        await context.bot.send_message(chat_id=user_id, text=msg)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    print("USER LOADED:", user["user_id"])
    await update.message.reply_text("SYSTEM ONLINE\nWelcome Hunter.")


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


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"LEVEL {user['level']}\n"
        f"XP {user['xp']}\n"
        f"STREAK {user['streak']}\n"
        f"CLASS {user['class_stage1']}\n"
        f"STAT POINTS {user['stat_points']}"
    )


async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    stat_points = user["stat_points"]

    if stat_points <= 0:
        await update.message.reply_text("❌ No stat points available.")
        return

    await update.message.reply_text(
        _render_spend_text(
            stat_points,
            user["strength"],
            user["intelligence"],
            user["agility"],
            user["vitality"],
            user["sense"],
        ),
        reply_markup=InlineKeyboardMarkup(_spend_keyboard()),
    )


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
        reply_markup=InlineKeyboardMarkup(_class_keyboard()),
    )


async def choose_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await awakening(update, context)


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


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"{item} - 💰{price}", callback_data=f"buy_{item}")]
        for item, price in SHOP_ITEMS
    ]
    await update.message.reply_text(
        "🛒 SHOP 🛒", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM inventory WHERE user_id=?", (user_id,))
    items = cursor.fetchall()

    if not items:
        await update.message.reply_text("🎒 Inventory is empty")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{item['item_name']} ({item['rarity']})",
                callback_data=f"equip_{item['item_id']}",
            )
        ]
        for item in items
    ]
    await update.message.reply_text(
        "🎒 INVENTORY", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    action = q.data
    raw_user = get_user(user_id)

    user = {
        "xp": raw_user["xp"],
        "level": raw_user["level"],
        "streak": raw_user["streak"],
        "gold": raw_user["gold"],
        "last": raw_user["last_daily"],
        "base_str": raw_user["strength"],
        "base_int": raw_user["intelligence"],
        "base_agi": raw_user["agility"],
        "base_vit": raw_user["vitality"],
        "base_sense": raw_user["sense"],
        "stat_points": raw_user["stat_points"],
        "rolls": raw_user["hidden_rolls"],
        "dungeon_rolls": raw_user["dungeon_rolls"] or 0,
        "quests_data": raw_user["active_quests"],
        "prog": raw_user["quest_progress"],
        "awakened": raw_user["awakened"],
        "job": raw_user["job_changed"],
        "class1": raw_user["class_stage1"],
        "class2": raw_user["class_stage2"],
        "dungeon_active": raw_user["dungeon_active"],
        "dungeon_progress": raw_user["dungeon_progress"],
        "dungeon_end": raw_user["dungeon_end"],
    }

    xp = user["xp"]
    level = user["level"]
    gold = user["gold"]
    streak = user["streak"]
    last = user["last"]
    base_str = user["base_str"]
    base_int = user["base_int"]
    base_agi = user["base_agi"]
    base_vit = user["base_vit"]
    base_sense = user["base_sense"]
    stat_points = user["stat_points"]
    rolls = user["rolls"]
    dungeon_rolls = user["dungeon_rolls"]

    equip = get_equipped_stats(user_id)
    total_str = base_str + equip["str"]
    total_int = base_int + equip["int"]
    total_agi = base_agi + equip["agi"]
    total_vit = base_vit + equip["vit"]
    total_sense = base_sense + equip["sense"]

    quests_data = user["quests_data"]
    progress = user["prog"]

    if action.startswith("class1_"):
        class_choice = action.split("_")[1]
        if user["class1"] != "none":
            await q.edit_message_text("❌ You already chose your awakening class")
            return
        cursor.execute(
            "UPDATE users SET class_stage1=? WHERE user_id=?",
            (class_choice, user_id),
        )
        conn.commit()
        await q.edit_message_text(f"⚡ Awakening Class Chosen: {class_choice.upper()}")
        return

    if action.startswith("class2_"):
        class_choice = action.split("_")[1]
        cursor.execute(
            "UPDATE users SET class_stage2=? WHERE user_id=?",
            (class_choice, user_id),
        )
        conn.commit()
        await q.edit_message_text(f"🔥 Job Class Set: {class_choice.upper()}")
        return

    if action.startswith("equip_"):
        item_id = int(action.split("_")[1])
        cursor.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
        item = cursor.fetchone()

        if not item:
            await q.edit_message_text("❌ Item not found")
            return

        cursor.execute(
            "INSERT OR IGNORE INTO equipment (user_id) VALUES (?)", (user_id,)
        )
        if item["slot"] == "weapon":
            cursor.execute(
                "UPDATE equipment SET weapon_id=? WHERE user_id=?", (item_id, user_id)
            )
        elif item["slot"] == "armor":
            cursor.execute(
                "UPDATE equipment SET armor_id=? WHERE user_id=?", (item_id, user_id)
            )
        elif item["slot"] == "charm":
            cursor.execute(
                "UPDATE equipment SET charm_id=? WHERE user_id=?", (item_id, user_id)
            )

        conn.commit()
        await q.edit_message_text(f"⚔ Equipped: {item['item_name']}")
        return

    if action == "dungeons":
        keyboard = [
            [InlineKeyboardButton("🟢 E Rank", callback_data="dungeon_E")],
            [InlineKeyboardButton("🔵 D Rank", callback_data="dungeon_D")],
            [InlineKeyboardButton("🟣 C Rank", callback_data="dungeon_C")],
        ]
        await q.edit_message_text(
            "🏰 DUNGEON GATES 🏰\n\nChoose a dungeon rank.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if action.startswith("buy_"):
        item_name = action.replace("buy_", "")
        price = dict(SHOP_ITEMS).get(item_name)

        if price is None:
            await q.edit_message_text("Item not found")
            return
        if gold < price:
            await q.edit_message_text("❌ Not enough gold")
            return

        gold -= price
        item = generate_item({"sense": total_sense})

        cursor.execute(
            """
            INSERT INTO inventory (
                user_id, item_name, slot, rarity,
                strength, intelligence, agility, vitality, sense, equipped
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                user_id,
                item["name"],
                "weapon",
                item["rarity"],
                item["strength"],
                item["intelligence"],
                item["agility"],
                item["vitality"],
                item["sense"],
            ),
        )
        cursor.execute("UPDATE users SET gold=? WHERE user_id=?", (gold, user_id))
        conn.commit()

        await q.edit_message_text(
            f"🛒 Purchased {item_name}\n\n"
            f"🎁 Loot received:\n"
            f"{item['rarity'].upper()} {item['name']}\n"
            f"+STR {item['strength']} +AGI {item['agility']}"
        )
        return

    if action in ["dungeon_E", "dungeon_D", "dungeon_C"]:
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

        keyboard = _build_dungeon_task_keyboard(enemies, 0)
        await q.edit_message_text(
            f"🏰 {rank} DUNGEON STARTED\n\n⏳ Time Limit: {dungeon['time']} sec",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if action == "class":
        await q.edit_message_text(
            "⚡ Choose your Awakening Class:",
            reply_markup=InlineKeyboardMarkup(_class_keyboard()),
        )
        return

    if action.startswith("dungeon_task_"):
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

        keyboard = _build_dungeon_task_keyboard(dungeon_data["enemies"], progress)
        await q.edit_message_text(
            f"🏰 DUNGEON IN PROGRESS\n\nProgress: {progress}/{len(dungeon_data['enemies'])}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if action == "boss":
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
        return

    if action == "boss_defeat":
        current_user = get_user(user_id)
        dungeon_data = safe_json(current_user["dungeon_active"], None)
        if dungeon_data is None:
            await q.edit_message_text("❌ Dungeon corrupted. Restart.")
            return

        end_time = datetime.fromisoformat(current_user["dungeon_end"])
        if datetime.now() > end_time:
            await q.edit_message_text("💀 Dungeon Failed - Time Expired")
            return

        rank = dungeon_data["rank"]
        base_xp = DUNGEONS[rank]["xp"]
        xp_mult, gold_min, gold_max, loot_bonus = _boss_reward_config(rank)
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
            rarity = _rarity_for_rank(rank)
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
        return

    if action == "daily":
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
            reply_markup=InlineKeyboardMarkup(_build_daily_keyboard(tasks, 0)),
        )
        return

    if action.startswith("task_"):
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
            reply_markup=InlineKeyboardMarkup(_build_daily_keyboard(tasks, progress)),
        )
        return

    if action == "done_disabled":
        await q.answer()
        return

    if action == "claim":
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
        return

    if action == "roll":
        if rolls <= 0:
            await q.edit_message_text("No rolls")
            return

        rolls -= 1
        chance = min(0.05, 0.01 + total_sense * 0.003)

        if random.random() < chance:
            hidden = random.choice(HIDDEN_QUESTS)
            xp += hidden[1]
            await q.edit_message_text(f"{hidden[0]} +{hidden[1]} XP")
            cursor.execute(
                "UPDATE users SET xp=?, hidden_rolls=? WHERE user_id=?",
                (xp, rolls, user_id),
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
        return

    if action == "dungeon_roll":
        if dungeon_rolls <= 0:
            await q.edit_message_text(
                "❌ No dungeon rolls available.\n\nClear C-rank dungeons to earn rolls."
            )
            return

        dungeon_rolls -= 1
        hunter_rank = get_rank(level)
        gate_rank = _dungeon_roll_gate_rank(hunter_rank)

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

        keyboard = _build_dungeon_task_keyboard(enemies, 0)
        await q.edit_message_text(
            f"[SYSTEM MESSAGE]\n"
            f"A government-locked Gate has summoned you.\n"
            f"Gate Rank: {gate_rank}\n\n"
            f"🏰 SPECIAL {gate_rank}-RANK DUNGEON STARTED\n"
            f"⏳ Time Limit: {dungeon['time']} sec",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if action == "stats":
        await q.edit_message_text(
            f"📊 PRECISE HUNTER DATA 📊\n\n"
            f"⚔ Level: {level}\n"
            f"🏆 Rank: {get_rank(level)}\n"
            f"✨ XP: {xp}\n"
            f"🔥 Streak: {streak}\n\n"
            f"💪 STR: {total_str}\n"
            f"🧠 INT: {total_int}\n"
            f"⚡ AGI: {total_agi}\n"
            f"❤️ VIT: {total_vit}\n"
            f"👁 SENSE: {total_sense}\n\n"
            f"📈 Unspent Stat Points: {stat_points}\n\n"
            f"🎲 Hidden Rolls: {rolls}\n"
            f"🎲 Dungeon Rolls: {dungeon_rolls}\n"
            f"⚡ Awakened: {user['awakened']}\n"
            f"🔥 Job Changed: {user['job']}\n\n"
            f"🛡 Class 1: {user['class1']}\n"
            f"⚔ Class 2: {user['class2']}",
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
        return

    if action == "inventory":
        cursor.execute(
            """
            SELECT * FROM inventory
            WHERE user_id=?
            ORDER BY rarity DESC
            """,
            (user_id,),
        )
        items = cursor.fetchall()

        if not items:
            await q.edit_message_text("🎒 Inventory is empty")
            return

        text = "🎒 INVENTORY\n\n"
        keyboard = []
        for item in items:
            text += (
                f"{item['item_id']}. {item['rarity'].upper()} {item['item_name']}\n"
                f"⚔ STR {item['strength']} | "
                f"🧠 INT {item['intelligence']} | "
                f"⚡ AGI {item['agility']} | "
                f"❤️ VIT {item['vitality']} | "
                f"👁 SENSE {item['sense']}\n\n"
            )
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"Equip {item['item_name']}",
                        callback_data=f"equip_{item['item_id']}",
                    )
                ]
            )

        keyboard.append(
            [InlineKeyboardButton("🛡 Equipped Gear", callback_data="equipment")]
        )
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if action == "equipment":
        cursor.execute("SELECT * FROM equipment WHERE user_id=?", (user_id,))
        equipment = cursor.fetchone()

        if not equipment:
            await q.edit_message_text("❌ No equipment")
            return

        def get_item(item_id):
            if not item_id:
                return None
            cursor.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
            return cursor.fetchone()

        weapon = get_item(equipment["weapon_id"])
        armor = get_item(equipment["armor_id"])
        charm = get_item(equipment["charm_id"])

        await q.edit_message_text(
            "🛡 EQUIPPED GEAR 🛡\n\n"
            f"⚔ Weapon: {weapon['item_name'] if weapon else 'None'}\n"
            f"🛡 Armor: {armor['item_name'] if armor else 'None'}\n"
            f"💍 Charm: {charm['item_name'] if charm else 'None'}\n"
        )
        return

    if action == "shop":
        text = "🛒 HUNTER SHOP 🛒\n\n"
        keyboard = []
        for item_name, price in SHOP_ITEMS:
            text += f"{item_name} — 💰 {price} Gold\n"
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"Buy {item_name}", callback_data=f"buy_{item_name}"
                    )
                ]
            )
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if action in ["spend_str", "spend_int", "spend_agi", "spend_vit", "spend_sense"]:
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
            _render_spend_text(
                stat_points, base_str, base_int, base_agi, base_vit, base_sense
            ),
            reply_markup=InlineKeyboardMarkup(_spend_keyboard()),
        )
        return


def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("class", choose_class))
    app.add_handler(CommandHandler("awakening", awakening))
    app.add_handler(CommandHandler("jobchange", jobchange))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("inventory", inventory))
    app.add_handler(CommandHandler("spend", spend))
    app.add_handler(CallbackQueryHandler(button))
