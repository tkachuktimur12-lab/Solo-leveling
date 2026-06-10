import os
import sqlite3
import threading


_DB_PATH = os.environ.get("SOLO_DB_PATH", "hunters.db")

# SQLite connections/cursors cannot be safely shared across threads. FastAPI
# serves sync endpoints from a threadpool, so concurrent requests (e.g. the
# inventory page loads /api/inventory and /api/inventory/equipment in parallel)
# previously used one shared cursor and raised "Recursive use of cursors not
# allowed", which could wedge the connection and hang the server until restart.
#
# Give every thread its own connection + cursor via thread-local storage. The
# module-level ``conn``/``cursor`` names are kept as transparent proxies so the
# rest of the codebase needs no changes.
_local = threading.local()


def _init_thread_state() -> None:
    connection = sqlite3.connect(_DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=5000")
    _local.connection = connection
    _local.cursor = connection.cursor()


def _get_connection() -> sqlite3.Connection:
    if getattr(_local, "connection", None) is None:
        _init_thread_state()
    return _local.connection


def _get_cursor() -> sqlite3.Cursor:
    if getattr(_local, "cursor", None) is None:
        _init_thread_state()
    return _local.cursor


class _ThreadLocalProxy:
    """Delegates attribute access to the calling thread's sqlite object."""

    def __init__(self, getter):
        self._getter = getter

    def __getattr__(self, name):
        return getattr(self._getter(), name)


conn = _ThreadLocalProxy(_get_connection)
cursor = _ThreadLocalProxy(_get_cursor)


def init_db():
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
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

    # Lightweight migration: add columns introduced after the initial release
    # so existing databases pick them up without a manual reset.
    existing_cols = {row["name"] for row in cursor.execute("PRAGMA table_info(users)").fetchall()}
    if "name" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")

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


def set_user_name(user_id, name):
    """Persist the hunter's display name (sourced from Telegram init data)."""
    if not name:
        return
    cursor.execute("UPDATE users SET name=? WHERE user_id=?", (name, user_id))
    conn.commit()


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
