"""Telegram Mini App authentication dependency."""

import os
import sqlite3

from fastapi import Depends, HTTPException, Request
from telegram_init_data import parse, validate

from game.db import get_user, set_user_name

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


def get_current_user(request: Request) -> sqlite3.Row:
    """FastAPI dependency: validate TMA auth header, return user row."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("tma "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    raw = auth[4:]

    try:
        validate(raw, BOT_TOKEN)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")

    try:
        parsed = parse(raw)
        tg_user = parsed["user"]
        user_id = int(tg_user["id"])
    except Exception:
        raise HTTPException(status_code=401, detail="Cannot parse init data")

    user = get_user(user_id)

    # Keep the stored display name in sync with the Telegram profile.
    display_name = tg_user.get("first_name") or tg_user.get("username") or "Hunter"
    if user["name"] != display_name:
        set_user_name(user_id, display_name)
        user = get_user(user_id)

    return user
