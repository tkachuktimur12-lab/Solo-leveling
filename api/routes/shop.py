"""Shop endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from api.schemas import BuyResult, ShopList
from game.constants import SHOP_ITEMS
from game.db import conn, cursor, get_equipped_stats
from game.game_logic import generate_item

router = APIRouter()


@router.get("", response_model=ShopList)
def list_shop(user: sqlite3.Row = Depends(get_current_user)):
    items = [{"name": name, "price": price} for name, price in SHOP_ITEMS]
    return {"items": items, "gold": user["gold"]}


@router.post("/buy/{item_name}", response_model=BuyResult)
def buy_item(item_name: str, user: sqlite3.Row = Depends(get_current_user)):
    price = dict(SHOP_ITEMS).get(item_name)
    if price is None:
        raise HTTPException(status_code=404, detail="Item not found")

    gold = user["gold"]
    if gold < price:
        raise HTTPException(status_code=400, detail="Not enough gold")

    user_id = user["user_id"]
    equip = get_equipped_stats(user_id)
    total_sense = user["sense"] + equip["sense"]

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

    return {
        "gold": gold,
        "item": {
            "name": item["name"],
            "rarity": item["rarity"],
            "slot": "weapon",
            "strength": item["strength"],
            "intelligence": item["intelligence"],
            "agility": item["agility"],
            "vitality": item["vitality"],
            "sense": item["sense"],
        },
    }
