"""Dungeon endpoints."""

import json
import random
import sqlite3
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from api.schemas import BossDefeat, BossRoom, DungeonList, DungeonTask, EnterDungeon
from game.constants import DUNGEONS
from game.db import conn, cursor, get_equipped_stats, get_user
from game.game_logic import loot_chance, safe_json

router = APIRouter()


def _boss_reward_config(rank: str):
    if rank in ("E", "D", "C"):
        return 1.5, 20, 50, 0.0
    if rank == "B":
        return 2.0, 50, 100, 0.10
    if rank == "A":
        return 2.5, 80, 150, 0.20
    if rank == "S":
        return 3.0, 120, 200, 0.30
    return 1.5, 20, 50, 0.0


def _rarity_for_rank(rank: str):
    r = random.random()
    if rank in ("E", "D", "C"):
        if r < 0.7:
            return "common"
        if r < 0.95:
            return "rare"
        return "epic"
    if rank == "B":
        if r < 0.4:
            return "common"
        if r < 0.85:
            return "rare"
        return "epic"
    if rank == "A":
        if r < 0.3:
            return "common"
        if r < 0.8:
            return "rare"
        return "epic"
    if rank == "S":
        if r < 0.2:
            return "common"
        if r < 0.7:
            return "rare"
        return "epic"
    return "common"


@router.get("", response_model=DungeonList)
def list_dungeons(user: sqlite3.Row = Depends(get_current_user)):
    available = ["E", "D", "C"]
    return {"available_ranks": available}


@router.post("/enter/{rank}", response_model=EnterDungeon)
def enter_dungeon(rank: str, user: sqlite3.Row = Depends(get_current_user)):
    rank = rank.upper()
    if rank not in DUNGEONS:
        raise HTTPException(status_code=400, detail="Invalid dungeon rank")

    dungeon = DUNGEONS[rank]
    enemies = random.sample(dungeon["enemy_pool"], 3)
    end_time = datetime.now() + timedelta(seconds=dungeon["time"])

    dungeon_save = {"rank": rank, "enemies": enemies}
    cursor.execute(
        """
        UPDATE users
        SET dungeon_active=?, dungeon_progress=0, dungeon_end=?, boss_active=0
        WHERE user_id=?
        """,
        (json.dumps(dungeon_save), end_time.isoformat(), user["user_id"]),
    )
    conn.commit()

    return {
        "rank": rank,
        "enemies": enemies,
        "time_limit": dungeon["time"],
        "dungeon_end": end_time.isoformat(),
    }


@router.post("/task/{index}", response_model=DungeonTask)
def dungeon_task(index: int, user: sqlite3.Row = Depends(get_current_user)):
    current = get_user(user["user_id"])
    dungeon_data = safe_json(current["dungeon_active"], None)
    if not dungeon_data:
        raise HTTPException(status_code=400, detail="No active dungeon")

    end_raw = current["dungeon_end"]
    if not end_raw:
        raise HTTPException(status_code=400, detail="Dungeon expired or corrupted")

    if datetime.now() > datetime.fromisoformat(end_raw):
        raise HTTPException(status_code=400, detail="Dungeon failed — time expired")

    progress = current["dungeon_progress"]
    if index != progress:
        raise HTTPException(status_code=400, detail="Invalid task index")

    progress += 1
    cursor.execute(
        "UPDATE users SET dungeon_progress=? WHERE user_id=?",
        (progress, user["user_id"]),
    )
    conn.commit()

    return {
        "dungeon_progress": progress,
        "total_enemies": len(dungeon_data["enemies"]),
        "boss_available": progress >= len(dungeon_data["enemies"]),
    }


@router.post("/boss", response_model=BossRoom)
def enter_boss(user: sqlite3.Row = Depends(get_current_user)):
    current = get_user(user["user_id"])
    dungeon_data = safe_json(current["dungeon_active"], None)
    if not dungeon_data:
        raise HTTPException(status_code=400, detail="No active dungeon")

    boss = random.choice(DUNGEONS[dungeon_data["rank"]]["boss_pool"])
    cursor.execute("UPDATE users SET boss_active=1 WHERE user_id=?", (user["user_id"],))
    conn.commit()

    end_time = datetime.fromisoformat(current["dungeon_end"])
    time_left = max(int((end_time - datetime.now()).total_seconds()), 0)

    return {
        "boss": boss,
        "time_left": time_left,
    }


@router.post("/boss/defeat", response_model=BossDefeat)
def defeat_boss(user: sqlite3.Row = Depends(get_current_user)):
    current = get_user(user["user_id"])
    dungeon_data = safe_json(current["dungeon_active"], None)
    if not dungeon_data:
        raise HTTPException(status_code=400, detail="No active dungeon")

    end_time = datetime.fromisoformat(current["dungeon_end"])
    if datetime.now() > end_time:
        raise HTTPException(status_code=400, detail="Dungeon failed — time expired")

    user_id = user["user_id"]
    equip = get_equipped_stats(user_id)
    total_sense = current["sense"] + equip["sense"]

    rank = dungeon_data["rank"]
    base_xp = DUNGEONS[rank]["xp"]
    xp_mult, gold_min, gold_max, loot_bonus = _boss_reward_config(rank)
    reward = int(base_xp * xp_mult)
    gold_reward = random.randint(gold_min, gold_max)

    xp = current["xp"] + reward
    gold = current["gold"] + gold_reward

    loot = None
    drop_chance = min(loot_chance(total_sense) + loot_bonus, 0.95)
    if random.random() < drop_chance:
        item_choice = random.choice(
            [
                ("Iron Sword", "weapon"),
                ("Leather Armor", "armor"),
                ("Hunter Ring", "charm"),
                ("Steel Boots", "armor"),
            ]
        )
        rarity = _rarity_for_rank(rank)
        stats = {
            "strength": random.randint(1, 3),
            "intelligence": random.randint(0, 2),
            "agility": random.randint(0, 2),
            "vitality": random.randint(0, 2),
            "sense": random.randint(0, 2),
        }
        cursor.execute(
            """
            INSERT INTO inventory (
                user_id, item_name, slot, rarity,
                strength, intelligence, agility, vitality, sense, equipped
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                user_id,
                item_choice[0],
                item_choice[1],
                rarity,
                stats["strength"],
                stats["intelligence"],
                stats["agility"],
                stats["vitality"],
                stats["sense"],
            ),
        )
        loot = {
            "item_name": item_choice[0],
            "slot": item_choice[1],
            "rarity": rarity,
            **stats,
        }

    cursor.execute(
        """
        UPDATE users
        SET xp=?, gold=?,
            dungeon_active='', dungeon_progress=0, dungeon_end='', boss_active=0
        WHERE user_id=?
        """,
        (xp, gold, user_id),
    )
    conn.commit()

    return {
        "xp_reward": reward,
        "gold_reward": gold_reward,
        "xp": xp,
        "gold": gold,
        "loot": loot,
    }
