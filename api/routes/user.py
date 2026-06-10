"""User stats and stat-spending endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from api.schemas import SpendRequest, SpendResult, UserStats
from game.constants import AWAKENING_CLASSES, JOB_CLASSES
from game.db import conn, cursor, get_equipped_stats
from game.game_logic import get_rank

router = APIRouter()

STAT_MAP = {
    "str": "strength",
    "int": "intelligence",
    "agi": "agility",
    "vit": "vitality",
    "sense": "sense",
}


def _class_display(mapping, key):
    """Map a stored class key to its display name, or None if unchosen."""
    if not key or key == "none":
        return None
    return mapping.get(key)


@router.get("/stats", response_model=UserStats)
def stats(user: sqlite3.Row = Depends(get_current_user)):
    equip = get_equipped_stats(user["user_id"])
    level = user["level"]
    return {
        "user_id": user["user_id"],
        "name": user["name"] or "Hunter",
        "level": level,
        "rank": get_rank(level),
        "xp": user["xp"],
        "xp_needed": level * 100,
        "gold": user["gold"],
        "streak": user["streak"],
        "stat_points": user["stat_points"],
        "str": user["strength"],
        "int": user["intelligence"],
        "agi": user["agility"],
        "vit": user["vitality"],
        "sense": user["sense"],
        "equipped_bonuses": equip,
        "hidden_rolls": user["hidden_rolls"],
        "dungeon_rolls": user["dungeon_rolls"] or 0,
        "awakened": user["awakened"],
        "job_changed": user["job_changed"],
        "awakening_class": _class_display(AWAKENING_CLASSES, user["class_stage1"]),
        "job_class": _class_display(JOB_CLASSES, user["class_stage2"]),
    }


@router.post("/spend", response_model=SpendResult)
def spend(body: SpendRequest, user: sqlite3.Row = Depends(get_current_user)):
    if body.stat not in STAT_MAP:
        raise HTTPException(status_code=400, detail="Invalid stat key")

    if user["stat_points"] <= 0:
        raise HTTPException(status_code=400, detail="No stat points available")

    col = STAT_MAP[body.stat]
    cursor.execute(
        f"UPDATE users SET {col} = {col} + 1, stat_points = stat_points - 1 WHERE user_id=?",
        (user["user_id"],),
    )
    conn.commit()

    # Return refreshed stats
    from game.db import get_user

    updated = get_user(user["user_id"])
    equip = get_equipped_stats(user["user_id"])
    return {
        "stat_points": updated["stat_points"],
        "str": updated["strength"],
        "int": updated["intelligence"],
        "agi": updated["agility"],
        "vit": updated["vitality"],
        "sense": updated["sense"],
        "equipped_bonuses": equip,
    }
