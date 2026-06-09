import sqlite3


conn = sqlite3.connect("hunters.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


def init_db():
    cursor.execute(
        """
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
        stat_points INTEGER,
        hidden_rolls INTEGER,
        dungeon_rolls INTEGER,
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
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS equipment (
        user_id INTEGER PRIMARY KEY,
        weapon_id INTEGER,
        armor_id INTEGER,
        charm_id INTEGER
    )
    """
    )

    cursor.execute(
        """
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
    """
    )

    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()


def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute(
            """
            INSERT INTO users (
                user_id, xp, level, gold, streak, last_daily,
                strength, intelligence, agility, vitality, sense,
                stat_points,
                hidden_rolls, dungeon_rolls, active_quests, quest_progress,
                awakened, job_changed,
                class_stage1, class_stage2,
                dungeon_active, dungeon_progress, dungeon_end, boss_active
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?,
                ?, ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?, ?, ?
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
                0,
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
