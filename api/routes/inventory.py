"""Inventory and equipment endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from game.db import conn, cursor

router = APIRouter()


def _row_to_dict(row):
    if row is None:
        return None
    return {
        "item_id": row["item_id"],
        "item_name": row["item_name"],
        "slot": row["slot"],
        "rarity": row["rarity"],
        "strength": row["strength"],
        "intelligence": row["intelligence"],
        "agility": row["agility"],
        "vitality": row["vitality"],
        "sense": row["sense"],
        "equipped": row["equipped"],
    }


@router.get("")
def list_inventory(user: sqlite3.Row = Depends(get_current_user)):
    cursor.execute(
        "SELECT * FROM inventory WHERE user_id=? ORDER BY rarity DESC",
        (user["user_id"],),
    )
    items = cursor.fetchall()
    return {"items": [_row_to_dict(i) for i in items]}


@router.get("/equipment")
def get_equipment(user: sqlite3.Row = Depends(get_current_user)):
    cursor.execute("SELECT * FROM equipment WHERE user_id=?", (user["user_id"],))
    eq = cursor.fetchone()

    if not eq:
        return {"weapon": None, "armor": None, "charm": None}

    def get_item(item_id):
        if not item_id:
            return None
        cursor.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
        return _row_to_dict(cursor.fetchone())

    return {
        "weapon": get_item(eq["weapon_id"]),
        "armor": get_item(eq["armor_id"]),
        "charm": get_item(eq["charm_id"]),
    }


@router.post("/equip/{item_id}")
def equip_item(item_id: int, user: sqlite3.Row = Depends(get_current_user)):
    cursor.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
    item = cursor.fetchone()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your item")

    user_id = user["user_id"]
    cursor.execute(
        "INSERT OR IGNORE INTO equipment (user_id) VALUES (?)", (user_id,)
    )

    slot = item["slot"]
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
    else:
        raise HTTPException(status_code=400, detail="Unknown item slot")

    conn.commit()
    return {"equipped": _row_to_dict(item)}
