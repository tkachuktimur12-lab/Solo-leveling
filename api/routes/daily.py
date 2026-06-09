"""Daily quest endpoints."""

import json
import random
import sqlite3
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from game.constants import QUESTS
from game.db import conn, cursor, get_equipped_stats, get_user
from game.game_logic import apply_stat_bonuses, safe_json

router = APIRouter()


@router.get("")
def daily_state(user: sqlite3.Row = Depends(get_current_user)):
    tasks = safe_json(user["active_quests"], [])
    last = user["last_daily"]

    cooldown_active = False
    cooldown_remaining = 0
    if last and last != "0":
        elapsed = datetime.now() - datetime.fromisoformat(last)
        if elapsed < timedelta(hours=24):
            cooldown_active = True
            cooldown_remaining = int((timedelta(hours=24) - elapsed).total_seconds())

    return {
        "active_quests": tasks,
        "quest_progress": user["quest_progress"],
        "cooldown_active": cooldown_active,
        "cooldown_remaining": cooldown_remaining,
        "streak": user["streak"],
    }


@router.post("/start")
def start_daily(user: sqlite3.Row = Depends(get_current_user)):
    last = user["last_daily"]
    if last and last != "0":
        if datetime.now() - datetime.fromisoformat(last) < timedelta(hours=24):
            raise HTTPException(status_code=400, detail="Daily already completed. On cooldown.")

    tasks = random.sample(QUESTS, 5)
    cursor.execute(
        "UPDATE users SET active_quests=?, quest_progress=0 WHERE user_id=?",
        (json.dumps(tasks), user["user_id"]),
    )
    conn.commit()

    return {"active_quests": tasks, "quest_progress": 0}


@router.post("/task/{index}")
def complete_task(index: int, user: sqlite3.Row = Depends(get_current_user)):
    tasks = safe_json(user["active_quests"], None)
    if not tasks:
        raise HTTPException(status_code=400, detail="No active daily quests")

    progress = user["quest_progress"]
    if index != progress:
        raise HTTPException(status_code=400, detail="Invalid task index")

    progress += 1
    cursor.execute(
        "UPDATE users SET quest_progress=? WHERE user_id=?",
        (progress, user["user_id"]),
    )
    conn.commit()

    return {"quest_progress": progress, "total": len(tasks)}


@router.post("/claim")
def claim_daily(user: sqlite3.Row = Depends(get_current_user)):
    progress = user["quest_progress"]
    if progress < 5:
        raise HTTPException(status_code=400, detail="Not all tasks completed")

    user_id = user["user_id"]
    equip = get_equipped_stats(user_id)
    total_str = user["strength"] + equip["str"]
    total_int = user["intelligence"] + equip["int"]
    total_sense = user["sense"] + equip["sense"]

    xp = user["xp"]
    level = user["level"]
    streak = user["streak"]
    stat_points = user["stat_points"]
    rolls = user["hidden_rolls"]

    gain = apply_stat_bonuses(100 + streak * 5, total_str, total_int, total_sense)
    xp += gain
    streak += 1
    rolls += 1

    level_ups = 0
    while xp >= level * 100:
        xp -= level * 100
        level += 1
        stat_points += 5
        level_ups += 1

        # Unlock awakening / job change
        if level == 10:
            cursor.execute("UPDATE users SET awakened=1 WHERE user_id=?", (user_id,))
        if level == 100:
            cursor.execute("UPDATE users SET job_changed=1 WHERE user_id=?", (user_id,))

    cursor.execute(
        """
        UPDATE users
        SET xp=?, level=?, streak=?, last_daily=?,
            stat_points=?, hidden_rolls=?, active_quests='[]', quest_progress=0
        WHERE user_id=?
        """,
        (xp, level, streak, datetime.now().isoformat(), stat_points, rolls, user_id),
    )
    conn.commit()

    return {
        "xp_gained": gain,
        "xp": xp,
        "level": level,
        "level_ups": level_ups,
        "streak": streak,
        "stat_points": stat_points,
        "hidden_rolls": rolls,
    }
