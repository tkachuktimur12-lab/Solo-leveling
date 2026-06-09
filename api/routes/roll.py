"""Hidden-roll and dungeon-roll endpoints."""

import json
import random
import sqlite3
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from game.constants import DUNGEONS, HIDDEN_QUESTS
from game.db import conn, cursor, get_equipped_stats, get_user
from game.game_logic import get_rank

router = APIRouter()

_RARITY_DISPLAY = {
    "rare": "Rare",
    "epic": "Epic",
    "legendary": "Legendary",
}


def _dungeon_roll_gate_rank(hunter_rank: str):
    r = random.random()
    if hunter_rank == "B":
        return "B" if r < 0.05 else None
    if hunter_rank == "A":
        if r < 0.07:
            return "B"
        if r < 0.09:
            return "A"
        return None
    if hunter_rank in ("S", "SS", "SSS"):
        if r < 0.10:
            return "B"
        if r < 0.15:
            return "A"
        if r < 0.16:
            return "S"
    return None


@router.post("/hidden")
def hidden_roll(user: sqlite3.Row = Depends(get_current_user)):
    user_id = user["user_id"]
    rolls = user["hidden_rolls"]
    if rolls <= 0:
        raise HTTPException(status_code=400, detail="No hidden rolls available")

    equip = get_equipped_stats(user_id)
    total_sense = user["sense"] + equip["sense"]

    rolls -= 1
    chance = min(0.05, 0.01 + total_sense * 0.003)

    if random.random() < chance:
        idx = random.randrange(len(HIDDEN_QUESTS))
        quest_name, quest_xp, rarity = HIDDEN_QUESTS[idx]
        rarity_label = _RARITY_DISPLAY.get(rarity, rarity)

        cursor.execute(
            "UPDATE users SET hidden_rolls=? WHERE user_id=?",
            (rolls, user_id),
        )
        conn.commit()

        return {
            "found": True,
            "hidden_rolls": rolls,
            "quest": {
                "index": idx,
                "name": quest_name,
                "xp": quest_xp,
                "rarity": rarity,
                "rarity_label": rarity_label,
            },
        }
    else:
        cursor.execute(
            "UPDATE users SET hidden_rolls=? WHERE user_id=?",
            (rolls, user_id),
        )
        conn.commit()
        return {"found": False, "hidden_rolls": rolls}


@router.post("/hidden/claim/{index}")
def claim_hidden(index: int, user: sqlite3.Row = Depends(get_current_user)):
    if index < 0 or index >= len(HIDDEN_QUESTS):
        raise HTTPException(status_code=400, detail="Invalid hidden quest index")

    quest_name, quest_xp, rarity = HIDDEN_QUESTS[index]
    rarity_label = _RARITY_DISPLAY.get(rarity, rarity)

    user_id = user["user_id"]
    xp = user["xp"] + quest_xp
    cursor.execute("UPDATE users SET xp=? WHERE user_id=?", (xp, user_id))
    conn.commit()

    return {
        "quest_name": quest_name,
        "xp_gained": quest_xp,
        "rarity": rarity,
        "rarity_label": rarity_label,
        "xp": xp,
    }


@router.post("/dungeon")
def dungeon_roll(user: sqlite3.Row = Depends(get_current_user)):
    user_id = user["user_id"]
    dungeon_rolls = user["dungeon_rolls"] or 0
    if dungeon_rolls <= 0:
        raise HTTPException(status_code=400, detail="No dungeon rolls available")

    dungeon_rolls -= 1
    level = user["level"]
    hunter_rank = get_rank(level)
    gate_rank = _dungeon_roll_gate_rank(hunter_rank)

    cursor.execute(
        "UPDATE users SET dungeon_rolls=? WHERE user_id=?",
        (dungeon_rolls, user_id),
    )

    if gate_rank is None:
        conn.commit()
        return {"found": False, "dungeon_rolls": dungeon_rolls}

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

    return {
        "found": True,
        "dungeon_rolls": dungeon_rolls,
        "gate_rank": gate_rank,
        "enemies": enemies,
        "time_limit": dungeon["time"],
        "dungeon_end": end_time.isoformat(),
    }
