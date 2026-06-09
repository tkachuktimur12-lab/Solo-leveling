"""User stats and stat-spending endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from api.models import SpendRequest
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


@router.get("/stats")
def stats(user: sqlite3.Row = Depends(get_current_user)):
    equip = get_equipped_stats(user["user_id"])
    return {
        "user_id": user["user_id"],
        "level": user["level"],
        "rank": get_rank(user["level"]),
        "xp": user["xp"],
        "gold": user["gold"],
        "streak": user["streak"],
        "stat_points": user["stat_points"],
        "strength": user["strength"],
        "intelligence": user["intelligence"],
        "agility": user["agility"],
        "vitality": user["vitality"],
        "sense": user["sense"],
        "equipped_bonus": equip,
        "total_str": user["strength"] + equip["str"],
        "total_int": user["intelligence"] + equip["int"],
        "total_agi": user["agility"] + equip["agi"],
        "total_vit": user["vitality"] + equip["vit"],
        "total_sense": user["sense"] + equip["sense"],
        "hidden_rolls": user["hidden_rolls"],
        "dungeon_rolls": user["dungeon_rolls"] or 0,
        "awakened": user["awakened"],
        "job_changed": user["job_changed"],
        "class_stage1": user["class_stage1"],
        "class_stage2": user["class_stage2"],
    }


@router.post("/spend")
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
        "strength": updated["strength"],
        "intelligence": updated["intelligence"],
        "agility": updated["agility"],
        "vitality": updated["vitality"],
        "sense": updated["sense"],
        "equipped_bonus": equip,
    }
