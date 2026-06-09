import random

from telegram import InlineKeyboardButton

from ..db import conn, cursor, get_equipped_stats, get_user


def class_keyboard():
    return [
        [InlineKeyboardButton("Tank", callback_data="class1_tank")],
        [InlineKeyboardButton("Assassin", callback_data="class1_assassin")],
        [InlineKeyboardButton("Mage", callback_data="class1_mage")],
        [InlineKeyboardButton("Berserker", callback_data="class1_berserker")],
    ]


def spend_keyboard():
    return [
        [InlineKeyboardButton("➕ STR", callback_data="spend_str")],
        [InlineKeyboardButton("➕ INT", callback_data="spend_int")],
        [InlineKeyboardButton("➕ AGI", callback_data="spend_agi")],
        [InlineKeyboardButton("➕ VIT", callback_data="spend_vit")],
        [InlineKeyboardButton("➕ SENSE", callback_data="spend_sense")],
    ]


def render_spend_text(stat_points, strength, intelligence, agility, vitality, sense):
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


def build_dungeon_task_keyboard(enemies, progress):
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


def build_daily_keyboard(tasks, progress):
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


def dungeon_roll_gate_rank(hunter_rank):
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


def boss_reward_config(rank):
    if rank in ["E", "D", "C"]:
        return 1.5, 20, 50, 0.0
    if rank == "B":
        return 2.0, 50, 100, 0.10
    if rank == "A":
        return 2.5, 80, 150, 0.20
    if rank == "S":
        return 3.0, 120, 200, 0.30
    return 1.5, 20, 50, 0.0


def rarity_for_rank(rank):
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


def load_button_context(user_id):
    """Load user data and compute derived stats for callback handling."""
    raw_user = get_user(user_id)

    base_str = raw_user["strength"]
    base_int = raw_user["intelligence"]
    base_agi = raw_user["agility"]
    base_vit = raw_user["vitality"]
    base_sense = raw_user["sense"]

    equip = get_equipped_stats(user_id)

    return {
        "xp": raw_user["xp"],
        "level": raw_user["level"],
        "streak": raw_user["streak"],
        "gold": raw_user["gold"],
        "last": raw_user["last_daily"],
        "base_str": base_str,
        "base_int": base_int,
        "base_agi": base_agi,
        "base_vit": base_vit,
        "base_sense": base_sense,
        "stat_points": raw_user["stat_points"],
        "rolls": raw_user["hidden_rolls"],
        "dungeon_rolls": raw_user["dungeon_rolls"] or 0,
        "quests_data": raw_user["active_quests"],
        "progress": raw_user["quest_progress"],
        "awakened": raw_user["awakened"],
        "job": raw_user["job_changed"],
        "class1": raw_user["class_stage1"],
        "class2": raw_user["class_stage2"],
        "dungeon_active": raw_user["dungeon_active"],
        "dungeon_progress": raw_user["dungeon_progress"],
        "dungeon_end": raw_user["dungeon_end"],
        "total_str": base_str + equip["str"],
        "total_int": base_int + equip["int"],
        "total_agi": base_agi + equip["agi"],
        "total_vit": base_vit + equip["vit"],
        "total_sense": base_sense + equip["sense"],
    }
