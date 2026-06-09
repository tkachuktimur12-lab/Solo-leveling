"""Telegram Mini App authentication dependency."""

import os
import sqlite3

from fastapi import Depends, HTTPException, Request
from telegram_init_data import parse, validate

from game.db import get_user

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
        user_id = parsed["user"]["id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Cannot parse init data")

    return get_user(int(user_id))
