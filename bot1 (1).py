from asyncio import tasks
from email.mime import application
import json
import random
from datetime import datetime, timedelta
import sqlite3
from turtle import update


def safe_json(data, fallback):

    if data is None:
        return fallback

    if data == "":
        return fallback

    try:
        return json.loads(data)

    except Exception as e:
        print("JSON ERROR:", e)
        print("BROKEN DATA:", data)
        return fallback


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = "8715373848:AAH5haypVdsaOSdHox3SRDlvArrWo3Axwww"

import sqlite3

conn = sqlite3.connect("hunters.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,

    xp INTEGER,
    level INTEGER,
    gold INTEGER,
    streak INTEGER,
    last_daily TEXT,

    strength INTEGER,
    intelligence INTEGER,
    agility INTEGER,
    vitality INTEGER,
    sense INTEGER,

    hidden_rolls INTEGER,
    active_quests TEXT,
    quest_progress INTEGER,

    awakened INTEGER,
    job_changed INTEGER,

    class_stage1 TEXT,
    class_stage2 TEXT,

    dungeon_active TEXT,
    dungeon_progress INTEGER,
    dungeon_end TEXT,               
    boss_active INTEGER    
)                
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS equipment (
    user_id INTEGER PRIMARY KEY,

    weapon_id INTEGER,
    armor_id INTEGER,
    charm_id INTEGER
)
""")
conn.commit()

conn.commit()

print("✅ DATABASE INITIALIZED")
# ---------------- QUESTS ---------------- #

quests = [
    ("Do 10 pushups", 20),
    ("Do 20 pushups", 40),
    ("Do 30 pushups", 60),
    ("Do 5 pull-ups", 35),
    ("Do 8 pull-ups", 50),
    ("Do 12 pull-ups", 70),
    ("Do 20 squats", 25),
    ("Do 40 squats", 45),
    ("Do 60 squats", 65),
    ("Plank 1 min", 25),
    ("Plank 2 min", 45),
    ("15 burpees", 40),
    ("25 burpees", 60),
]

hidden_quests = [
    ("Do 50 pushups", 80, "rare"),
    ("Do 100 pushups", 140, "epic"),
    ("Do 200 pushups", 300, "legendary"),
]

awakening_classes = {
    "tank": "Tank (Beginner)",
    "assassin": "Assassin (Beginner)",
    "mage": "Mage (Beginner)",
    "berserker": "Berserker (Beginner)",
}

job_classes = {
    "tank": "Titan Guardian",
    "assassin": "Shadow Reaper",
    "mage": "Arcane Sovereign",
    "berserker": "War God",
}

classes = {
    "tank": {"hp": 20, "str": 2},
    "assassin": {"agi": 3},
    "berserker": {"str": 3},
    "mage": {"int": 3},
}
# ---------------- DUNGEONS ---------------- #

dungeons = {
    "E": {
        "xp": 50,
        "time": 300,
        "enemies": [
            {"name": "Goblin", "task": "10 Pushups"},
            {"name": "Slime", "task": "20 Squats"},
            {"name": "Skeleton", "task": "30 Sec Plank"},
            {"name": "Bat", "task": "15 Jumping Jacks"},
            {"name": "Crawler", "task": "10 Situps"},
        ],
        "boss": {"name": "Goblin King", "task": "50 Pushups"},
    },
    "D": {
        "xp": 120,
        "time": 420,
        "enemies": [
            {"name": "Orc", "task": "20 Pushups"},
            {"name": "Wolf", "task": "30 Squats"},
            {"name": "Zombie", "task": "15 Burpees"},
            {"name": "Bandit", "task": "20 Situps"},
            {"name": "Lizardman", "task": "45 Sec Plank"},
        ],
        "boss": {"name": "Orc Commander", "task": "80 Pushups"},
    },
    "C": {
        "xp": 250,
        "time": 600,
        "enemies": [
            {"name": "Dark Knight", "task": "30 Pushups"},
            {"name": "Ogre", "task": "50 Squats"},
            {"name": "Assassin", "task": "25 Burpees"},
            {"name": "Specter", "task": "1 Min Plank"},
            {"name": "War Beast", "task": "40 Situps"},
        ],
        "boss": {"name": "Dungeon Tyrant", "task": "120 Pushups"},
    },
}
shop_items = [
    ("Iron Sword", 50),
    ("Leather Armor", 40),
    ("Hunter Boots", 60),
    ("Mana Ring", 80),
]
# ---------------- DB ---------------- #


# ---------------- HELPERS ---------------- #


def get_rank(level):
    return (
        "E"
        if level < 5
        else (
            "D"
            if level < 10
            else (
                "C"
                if level < 15
                else (
                    "B"
                    if level < 20
                    else (
                        "A"
                        if level < 30
                        else "S" if level < 40 else "SS" if level < 60 else "SSS"
                    )
                )
            )
        )
    )


def try_hidden():
    return random.random() < 0.01


def apply_stat_bonuses(xp, str_, int_, sense):
    # INT gives XP boost
    xp = int(xp * (1 + int_ * 0.02))

    # STR gives small flat bonus
    xp += str_ * 2

    return xp


def loot_chance(sense):
    return min(0.8, 0.1 + sense * 0.03)


def get_equipped_stats(user_id):
    cursor.execute(
        """
        SELECT weapon_id, armor_id, charm_id
        FROM equipment
        WHERE user_id=?
    """,
        (user_id,),
    )

    row = cursor.fetchone()

    if not row:
        return {"str": 0, "int": 0, "agi": 0, "vit": 0, "sense": 0}

    stats = {"str": 0, "int": 0, "agi": 0, "vit": 0, "sense": 0}

    for item_id in row:
        if item_id:
            cursor.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
            item = cursor.fetchone()
            if item:
                stats["str"] += item["strength"]
                stats["int"] += item["intelligence"]
                stats["agi"] += item["agility"]
                stats["vit"] += item["vitality"]
                stats["sense"] += item["sense"]

    return stats


# ---------------- USER ---------------- #


def get_user(user_id):

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user is None:

        cursor.execute(
            """
        INSERT INTO users (
            user_id, xp, level, gold, streak, last_daily,
            strength, intelligence, agility, vitality, sense,
            hidden_rolls, active_quests, quest_progress,
            awakened, job_changed,
            class_stage1, class_stage2,
            dungeon_active, dungeon_progress, dungeon_end, boss_active
        ) VALUES (
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?,
            ?, ?, ?, ?, ?, ?
        )
        """,
            (
                user_id,
                0,
                1,
                0,
                0,
                "0",
                1,
                1,
                1,
                1,
                1,
                0,
                "",
                0,
                0,
                0,
                "none",
                "none",
                "",
                0,
                "",
                0,
            ),
        )

        conn.commit()

        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = cursor.fetchone()

    return user


cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    item_name TEXT,
    slot TEXT,
    rarity TEXT,

    strength INTEGER,
    intelligence INTEGER,
    agility INTEGER,
    vitality INTEGER,
    sense INTEGER,

    equipped INTEGER
)
""")

conn.commit()


def init_db():
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()


init_db()
# ---------------- COMMANDS ---------------- #


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    print("USER LOADED:", u)
    await update.message.reply_text("SYSTEM ONLINE\nWelcome Hunter.")


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚔Daily", callback_data="daily")],
        [InlineKeyboardButton("📊Stats", callback_data="stats")],
        [InlineKeyboardButton("📊Precise Stats", callback_data="statsprecise")],
        [InlineKeyboardButton("🎲Roll", callback_data="roll")],
        [InlineKeyboardButton("🏰 Dungeons", callback_data="dungeons")],
        [InlineKeyboardButton("🎒 Inventory", callback_data="inventory")],
        [InlineKeyboardButton("🛒 Shop", callback_data="shop")],
    ]

    await update.message.reply_text("MENU", reply_markup=InlineKeyboardMarkup(keyboard))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    await update.message.reply_text(
        f"LEVEL {u[2]}\nXP {u[1]}\nSTREAK {u[3]}\nCLASS {u[16]}"
    )


async def awakening(update: Update, context: ContextTypes.DEFAULT_TYPE):

    u = get_user(update.effective_user.id)

    if u["level"] < 10:
        await update.message.reply_text("❌ Awakening unlocks at Level 10")
        return

    if u["awakened"] == 0:
        await update.message.reply_text("❌ You have not unlocked awakening yet")
        return

    keyboard = [
        [InlineKeyboardButton("Tank", callback_data="class1_tank")],
        [InlineKeyboardButton("Assassin", callback_data="class1_assassin")],
        [InlineKeyboardButton("Mage", callback_data="class1_mage")],
        [InlineKeyboardButton("Berserker", callback_data="class1_berserker")],
    ]

    await update.message.reply_text(
        "⚡ AWAKENING COMPLETE ⚡\nChoose your FIRST class:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def jobchange(update: Update, context: ContextTypes.DEFAULT_TYPE):

    u = get_user(update.effective_user.id)

    if u["level"] < 100:
        await update.message.reply_text("❌ Job Change unlocks at Level 100")
        return

    if u["job_changed"] == 0:
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
    keyboard = []

    for item, price in shop_items:
        keyboard.append(
            [InlineKeyboardButton(f"{item} - 💰{price}", callback_data=f"buy_{item}")]
        )

    await update.message.reply_text(
        "🛒 SHOP 🛒", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def roll_rarity(sense):
    base = random.random()

    boost = sense * 0.003  # sense increases luck slightly
    roll = base - boost

    if roll < 0.60:
        return "common"
    elif roll < 0.85:
        return "rare"
    elif roll < 0.95:
        return "epic"
    elif roll < 0.99:
        return "legendary"
    else:
        return "mythic"


def generate_item(user):
    rarity = roll_rarity(user["sense"])

    base_stats = {
        "common": (1, 3),
        "rare": (2, 5),
        "epic": (4, 8),
        "legendary": (7, 12),
        "mythic": (10, 18),
    }

    min_stat, max_stat = base_stats[rarity]

    item = {
        "name": random.choice(
            [
                "Shadow Blade",
                "Iron Gauntlets",
                "Arcane Ring",
                "Hunter Boots",
                "Titan Chestplate",
            ]
        ),
        "rarity": rarity,
        "strength": random.randint(min_stat, max_stat),
        "intelligence": random.randint(min_stat, max_stat),
        "agility": random.randint(min_stat, max_stat),
        "vitality": random.randint(min_stat, max_stat),
        "sense": random.randint(min_stat, max_stat),
    }

    return item


async def check_unlocks(level, user_id):
    msg = ""

    if level == 10:
        msg += "⚡ AWAKENING UNLOCKED ⚡\nYou can now choose your first class.\n"
        cursor.execute(
            "UPDATE users SET awakened=1 WHERE user_id=?",
            (user_id,),
        )
        conn.commit()

    if level == 100:
        msg += "🔥 JOB CHANGE UNLOCKED 🔥\nYou can now evolve your class.\n"
        cursor.execute(
            "UPDATE users SET job_changed=1 WHERE user_id=?",
            (user_id,),
        )
        conn.commit()

    if msg:
        await application.bot.send_message(user_id, msg)


# ---------------- BUTTONS ---------------- #


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    action = q.data

    u = get_user(user_id)

    user = {
        "xp": u["xp"],
        "level": u["level"],
        "streak": u["streak"],
        "gold": u["gold"],
        "last": u["last_daily"],
        "str": u["strength"],
        "int": u["intelligence"],
        "agi": u["agility"],
        "vit": u["vitality"],
        "sense": u["sense"],
        "rolls": u["hidden_rolls"],
        "quests_data": u["active_quests"],
        "prog": u["quest_progress"],
        "awakened": u["awakened"],
        "job": u["job_changed"],
        "class1": u["class_stage1"],
        "class2": u["class_stage2"],
        "dungeon_active": u["dungeon_active"],
        "dungeon_progress": u["dungeon_progress"],
        "dungeon_end": u["dungeon_end"],
    }
    xp = user["xp"]
    level = user["level"]
    gold = user["gold"]
    streak = user["streak"]
    last = user["last"]

    equip = get_equipped_stats(user_id)

    str_ = user["str"] + equip["str"]
    int_ = user["int"] + equip["int"]
    agi = user["agi"] + equip["agi"]
    vit = user["vit"] + equip["vit"]
    sense = user["sense"] + equip["sense"]
    rolls = user["rolls"]

    quests_data = user["quests_data"]
    prog = user["prog"]

    awakened = user["awakened"]
    job = user["job"]

    class1 = user["class1"]
    class2 = user["class2"]

    dungeon_active = user["dungeon_active"]
    dungeon_progress = user["dungeon_progress"]
    dungeon_end = user["dungeon_end"]

    if action.startswith("class1_"):

        class_choice = action.split("_")[1]

        # prevent double pick
        if user["class1"] != "none":
            await q.edit_message_text("❌ You already chose your awakening class")
            return

        cursor.execute(
            """
            UPDATE users
            SET class_stage1=?
            WHERE user_id=?
            """,
            (class_choice, user_id),
        )

        conn.commit()

        await q.edit_message_text(f"⚡ Awakening Class Chosen: {class_choice.upper()}")

        return

    elif action.startswith("class2_"):
        class_choice = action.split("_")[1]

        cursor.execute(
            """
        UPDATE users
        SET class_stage2=?
        WHERE user_id=?
        """,
            (class_choice, user_id),
        )

        conn.commit()

        await q.edit_message_text(f"🔥 Job Class Set: {class_choice.upper()}")
        return

    elif action.startswith("equip_"):

        item_id = int(action.split("_")[1])

        cursor.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
        item = cursor.fetchone()

        if not item:
            await q.edit_message_text("❌ Item not found")
            return

        slot = item["slot"]

        # ensure equipment row exists
        cursor.execute(
            "INSERT OR IGNORE INTO equipment (user_id) VALUES (?)", (user_id,)
        )

        if slot == "weapon":
            cursor.execute(
                "UPDATE equipment SET weapon_id=? WHERE user_id=?", (item_id, user_id)
            )

        elif slot == "armor":
            cursor.execute(
                "UPDATE equipment SET armor_id=? WHERE user_id=?", (item_id, user_id)
            )

        elif slot == "charm":
            cursor.execute(
                "UPDATE equipment SET charm_id=? WHERE user_id=?", (item_id, user_id)
            )

        conn.commit()

        await q.edit_message_text(f"⚔ Equipped: {item['item_name']}")
        return

    elif action == "dungeons":
        keyboard = [
            [InlineKeyboardButton("🟢 E Rank", callback_data="dungeon_E")],
            [InlineKeyboardButton("🔵 D Rank", callback_data="dungeon_D")],
            [InlineKeyboardButton("🟣 C Rank", callback_data="dungeon_C")],
        ]

        await q.edit_message_text(
            "🏰 DUNGEON GATES 🏰\n\n" "Choose a dungeon rank.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    elif action.startswith("buy_"):
        item_name = action.replace("buy_", "")

        price = dict(shop_items).get(item_name)

        if price is None:
            await q.edit_message_text("Item not found")
            return

        if gold < price:
            await q.edit_message_text("❌ Not enough gold")
            return

        gold -= price

        item = generate_item(user)

        cursor.execute(
            """
            INSERT INTO inventory (
                user_id, item_name, slot, rarity,
                strength, intelligence, agility, vitality, sense,
                equipped
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

        cursor.execute(
            """
        UPDATE users SET gold=? WHERE user_id=?
        """,
            (gold, user_id),
        )

        conn.commit()

        await q.edit_message_text(
            f"🛒 Purchased {item_name}\n\n"
            f"🎁 Loot received:\n"
            f"{item['rarity'].upper()} {item['name']}\n"
            f"+STR {item['strength']} +AGI {item['agility']}"
        )
        return
    # ---------------- DUNGEON START ---------------- #

    elif action in ["dungeon_E", "dungeon_D", "dungeon_C"]:

        rank = action.split("_")[1]

        dungeon = dungeons[rank]

        enemies = random.sample(dungeon["enemies"], 3)

        end_time = datetime.now() + timedelta(seconds=dungeon["time"])

        dungeon_save = {"rank": rank, "enemies": enemies}

        cursor.execute(
            """
            UPDATE users
            SET dungeon_active=?, 
                dungeon_progress=0, 
                dungeon_end=?
            WHERE user_id=?
            """,
            (
                json.dumps(dungeon_save),
                end_time.isoformat(),
                user_id,
            ),
        )

        conn.commit()

        keyboard = []

        for i, enemy in enumerate(enemies):

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"⬜ {enemy['name']} → {enemy['task']}",
                        callback_data=f"dungeon_task_{i}",
                    )
                ]
            )

        await q.edit_message_text(
            f"🏰 {rank} DUNGEON STARTED\n\n" f"⏳ Time Limit: {dungeon['time']} sec",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    elif action == "class":

        keyboard = [
            [InlineKeyboardButton("Tank", callback_data="class1_tank")],
            [InlineKeyboardButton("Assassin", callback_data="class1_assassin")],
            [InlineKeyboardButton("Mage", callback_data="class1_mage")],
            [InlineKeyboardButton("Berserker", callback_data="class1_berserker")],
        ]

        await q.edit_message_text(
            "⚡ Choose your Awakening Class:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    elif action.startswith("dungeon_task_"):

        u = get_user(user_id)
        print("RAW DUNGEON DATA:", u["dungeon_active"])
        dungeon_data = safe_json(u["dungeon_active"], None)

        if not dungeon_data:
            await q.edit_message_text("❌ Dungeon expired or corrupted.")
            return

        index = int(action.replace("dungeon_task_", ""))
        print("TASK BUTTON PRESSED:", index)

        progress = u["dungeon_progress"]

        end_time = datetime.fromisoformat(u["dungeon_end"])

        # TIME CHECK
        if datetime.now() > end_time:
            await q.edit_message_text("💀 Dungeon Failed - Time Expired")
            return

        # ONLY ALLOW NEXT TASK
        if index != progress:
            await q.edit_message_text("❌ Invalid action")
            return

        progress += 1

        cursor.execute(
            """
            UPDATE users
            SET dungeon_progress=?
            WHERE user_id=?
            """,
            (progress, user_id),
        )

        conn.commit()

        keyboard = []

        for i, enemy in enumerate(dungeon_data["enemies"]):

            label = "✅" if i < progress else "⬜"

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{label} {enemy['name']} → {enemy['task']}",
                        callback_data=f"dungeon_task_{i}",
                    )
                ]
            )

        # Boss unlock
        if progress >= len(dungeon_data["enemies"]):
            keyboard.append([InlineKeyboardButton("⚔ FACE BOSS", callback_data="boss")])

        await q.edit_message_text(
            f"🏰 DUNGEON IN PROGRESS\n\n"
            f"Progress: {progress}/{len(dungeon_data['enemies'])}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    elif action == "boss":

        u = get_user(user_id)

        dungeon_data = safe_json(u["dungeon_active"], None)

        if dungeon_data is None:
            await q.edit_message_text("❌ Dungeon corrupted. Restart.")
            return

        boss = dungeons[dungeon_data["rank"]]["boss"]

        cursor.execute(
            """
             UPDATE users
             SET boss_active=1
             WHERE user_id=?
             """,
            (user_id,),
        )
        conn.commit()

        end_time = datetime.fromisoformat(u["dungeon_end"])

        time_left = int((end_time - datetime.now()).total_seconds())

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
            f"\n⏳ Time Left: {minutes:02d}:{seconds:02d}s",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    elif action == "boss_defeat":
        u = get_user(user_id)
        dungeon_data = safe_json(u["dungeon_active"], None)

        if dungeon_data is None:
            await q.edit_message_text("❌ Dungeon corrupted. Restart.")
            return

        end_time = datetime.fromisoformat(u["dungeon_end"])

        if datetime.now() > end_time:
            await q.edit_message_text("💀 Dungeon Failed - Time Expired")
            return

        reward = int(dungeons[dungeon_data["rank"]]["xp"] * 1.5)

        gold_reward = random.randint(20, 50)

        cursor.execute(
            "UPDATE users SET xp=?, gold=? WHERE user_id=?",
            (xp + reward, gold + gold_reward, user_id),
        )
        conn.commit()

        loot_msg = ""

        # 🎁 LOOT DROP
        if random.random() < loot_chance(sense):

            item = random.choice(
                [
                    ("Iron Sword", "weapon"),
                    ("Leather Armor", "armor"),
                    ("Hunter Ring", "charm"),
                    ("Steel Boots", "armor"),
                ]
            )

            rarity_roll = random.random()

            rarity = (
                "common"
                if rarity_roll < 0.7
                else "rare" if rarity_roll < 0.95 else "epic"
            )

            cursor.execute(
                """
                INSERT INTO inventory (
                    user_id,
                    item_name,
                    slot,
                    rarity,
                    strength,
                    intelligence,
                    agility,
                    vitality,
                    sense,
                    equipped
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            (
                xp,
                gold,
                user_id,
            ),
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

    # ---------------- DAILY ---------------- #

    elif action == "daily":

        if last != "0":
            if datetime.now() - datetime.fromisoformat(last) < timedelta(hours=24):
                await q.edit_message_text("⏳ Daily already completed")
                return

        tasks = random.sample(quests, 5)

        # SAVE TASKS
        cursor.execute(
            """
        UPDATE users
        SET active_quests=?, quest_progress=0
        WHERE user_id=?
        """,
            (json.dumps(tasks), user_id),
        )

        conn.commit()

        keyboard = []

        for i, task in enumerate(tasks):
            keyboard.append(
                [InlineKeyboardButton(f"⬜ {task[0]}", callback_data=f"task_{i}")]
            )

        keyboard.append([InlineKeyboardButton("🏁 CLAIM", callback_data="claim")])

        await q.edit_message_text(
            "📜 DAILY QUESTS ACTIVATED 📜\n\n" "Complete all 5 tasks.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    # ---------------- TASK ---------------- #
    elif action.startswith("task_"):

        tasks = safe_json(quests_data, None)

        # FIX: allow only next task
        if not tasks:
            await q.edit_message_text("❌ No active daily quests")
            return

        index = int(action.split("_")[1])

        # FIX: allow only next task
        if index != prog:
            await q.edit_message_text("❌ Invalid task")
            return

        prog += 1

        cursor.execute(
            """
            UPDATE users
            SET quest_progress=?
            WHERE user_id=?
            """,
            (prog, user_id),
        )
        conn.commit()

        keyboard = []

        for i, task in enumerate(tasks):
            label = "✅" if i < prog else "⬜"
            keyboard.append(
                [InlineKeyboardButton(label + " " + task[0], callback_data=f"task_{i}")]
            )

        keyboard.append([InlineKeyboardButton("🏁 CLAIM", callback_data="claim")])

        await q.edit_message_text(
            f"📜 DAILY QUESTS\n\nProgress: {prog}/{len(tasks)}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    # ---------------- CLAIM ---------------- #

    elif action == "claim":

        if user["prog"] < 5:
            await q.edit_message_text("Not done")
            return

        base = 100 + streak * 5
        gain = apply_stat_bonuses(base, str_, int_, sense)

        xp += gain
        streak += 1
        rolls += 1

        level_up_msg = ""

        while xp >= level * 100:

            xp -= level * 100
            level += 1

            await check_unlocks(level, user_id)

            str_ += 1
            int_ += 1
            agi += 1
            vit += 1
            sense += 1

            level_up_msg += f"\n⚔ LEVEL UP → {level}"

            # AWAKENING UNLOCK
            if level == 10:
                level_up_msg += (
                    "\n\n⚡ AWAKENING UNLOCKED ⚡\n"
                    "You can now choose your first class."
                )

            # JOB CHANGE UNLOCK
            if level == 100:
                level_up_msg += (
                    "\n\n🔥 JOB CHANGE UNLOCKED 🔥\n" "You can now evolve your class."
                )
                cursor.execute(
                    "UPDATE users SET awakened=1 WHERE user_id=?",
                    (user_id,),
                )
        conn.commit()
        new_xp = xp + gain
        cursor.execute(
            """
        UPDATE users SET xp=?, level=?, streak=?, last_daily=?,
        strength=?, intelligence=?, agility=?, vitality=?, sense=?,
        hidden_rolls=?, active_quests=?, quest_progress=?
        WHERE user_id=?
        """,
            (
                new_xp,
                level,
                streak,
                datetime.now().isoformat(),
                str_,
                int_,
                agi,
                vit,
                sense,
                rolls,
                "[]",
                0,
                user_id,
            ),
        )

        conn.commit()

        msg = (
            f"🏁 DAILY COMPLETE 🏁\n\n"
            f"✨ +{gain} XP\n"
            f"🎲 +1 Hidden Roll\n"
            f"🔥 Streak: {streak}\n"
        )

        await q.edit_message_text(msg + level_up_msg)
        return

    # ---------------- ROLL ---------------- #

    elif action == "roll":

        if rolls <= 0:
            await q.edit_message_text("No rolls")
            return

        rolls -= 1
        chance = min(0.05, 0.01 + sense * 0.003)

        if random.random() < chance:
            h = random.choice(hidden_quests)
            await q.edit_message_text(f"{h[0]} +{h[1]} XP")
            xp += h[1]

            cursor.execute(
                "UPDATE users SET xp=?, hidden_rolls=? WHERE user_id=?",
                (xp, rolls, user_id),
            )
        else:
            await q.edit_message_text(
                "🎲 Hidden Roll Used\n\n" "❌ No hidden quest appeared."
            )

        cursor.execute(
            "UPDATE users SET hidden_rolls=? WHERE user_id=?", (rolls, user_id)
        )
        conn.commit()
        return

    # ---------------- STATS ---------------- #

    elif action == "stats":
        await q.edit_message_text(
            f"📊 HUNTER STATUS 📊\n\n"
            f"⚔ Level: {level}\n"
            f"🏆 Rank: {get_rank(level)}\n"
            f"✨ XP: {xp}\n"
            f"🔥 Streak: {streak}\n\n"
            f"🎲 Hidden Rolls: {rolls}"
        )
        return

    elif action == "statsprecise":
        await q.edit_message_text(
            f"📊 PRECISE HUNTER DATA 📊\n\n"
            f"⚔ Level: {level}\n"
            f"🏆 Rank: {get_rank(level)}\n"
            f"✨ XP: {xp}\n"
            f"🔥 Streak: {streak}\n\n"
            f"💪 STR: {str_}\n"
            f"🧠 INT: {int_}\n"
            f"⚡ AGI: {agi}\n"
            f"❤️ VIT: {vit}\n"
            f"👁 SENSE: {sense}\n\n"
            f"🎲 Hidden Rolls: {rolls}\n"
            f"⚡ Awakened: {user['awakened']}\n"
            f"🔥 Job Changed: {user['job']}\n\n"
            f"🛡 Class 1: {user['class1']}\n"
            f"⚔ Class 2: {user['class2']}"
        )
        return

    elif action == "inventory":

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
                f"{item['item_id']}. "
                f"{item['rarity'].upper()} "
                f"{item['item_name']}\n"
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

        await q.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    elif action == "equipment":

        cursor.execute(
            """
            SELECT * FROM equipment
            WHERE user_id=?
            """,
            (user_id,),
        )

        equip = cursor.fetchone()

        if not equip:
            await q.edit_message_text("❌ No equipment")
            return

        def get_item(item_id):

            if not item_id:
                return None

            cursor.execute(
                "SELECT * FROM inventory WHERE item_id=?",
                (item_id,),
            )

            return cursor.fetchone()

        weapon = get_item(equip["weapon_id"])
        armor = get_item(equip["armor_id"])
        charm = get_item(equip["charm_id"])

        text = "🛡 EQUIPPED GEAR 🛡\n\n"

        text += f"⚔ Weapon: " f"{weapon['item_name'] if weapon else 'None'}\n"

        text += f"🛡 Armor: " f"{armor['item_name'] if armor else 'None'}\n"

        text += f"💍 Charm: " f"{charm['item_name'] if charm else 'None'}\n"

        await q.edit_message_text(text)

        return

    elif action == "shop":

        text = "🛒 HUNTER SHOP 🛒\n\n"

        keyboard = []

        for item_name, price in shop_items:

            text += f"{item_name} — 💰 {price} Gold\n"

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"Buy {item_name}",
                        callback_data=f"buy_{item_name}",
                    )
                ]
            )

        await q.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return


# ---------------- INVENTORY ---------------- #
async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute("SELECT * FROM inventory WHERE user_id=?", (user_id,))
    items = cursor.fetchall()

    keyboard = []

    for item in items:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{item['item_name']} ({item['rarity']})",
                    callback_data=f"equip_{item['item_id']}",
                )
            ]
        )

    await update.message.reply_text(
        "🎒 INVENTORY", reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- CLASS SYSTEM ---------------- #


async def choose_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    u = get_user(user_id)

    if u["level"] < 10:
        await update.message.reply_text("❌ Awakening unlocks at Level 10")
        return

    if u["awakened"] == 0:
        await update.message.reply_text("❌ You have not unlocked awakening yet")
        return

    keyboard = [
        [InlineKeyboardButton("Tank", callback_data="class1_tank")],
        [InlineKeyboardButton("Assassin", callback_data="class1_assassin")],
        [InlineKeyboardButton("Mage", callback_data="class1_mage")],
        [InlineKeyboardButton("Berserker", callback_data="class1_berserker")],
    ]

    await update.message.reply_text(
        "⚡ AWAKENING COMPLETE ⚡\nChoose your FIRST class:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ---------------- APP ---------------- #

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("class", choose_class))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("awakening", awakening))
app.add_handler(CommandHandler("jobchange", jobchange))
app.add_handler(CommandHandler("shop", shop))
app.add_handler(CommandHandler("inventory", inventory))
print("Bot running...")
app.run_polling()
