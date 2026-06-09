"""Awakening and job-change endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from game.constants import AWAKENING_CLASSES, JOB_CLASSES
from game.db import conn, cursor

router = APIRouter()


@router.post("/awakening/{class_key}")
def choose_awakening(class_key: str, user: sqlite3.Row = Depends(get_current_user)):
    if class_key not in AWAKENING_CLASSES:
        raise HTTPException(status_code=400, detail="Invalid class key")

    if user["level"] < 10:
        raise HTTPException(status_code=400, detail="Awakening unlocks at Level 10")
    if not user["awakened"]:
        raise HTTPException(status_code=400, detail="Awakening not unlocked")
    if user["class_stage1"] != "none":
        raise HTTPException(status_code=400, detail="Already chose awakening class")

    cursor.execute(
        "UPDATE users SET class_stage1=? WHERE user_id=?",
        (class_key, user["user_id"]),
    )
    conn.commit()

    return {
        "class_stage1": class_key,
        "class_name": AWAKENING_CLASSES[class_key],
    }


@router.post("/jobchange/{class_key}")
def choose_jobchange(class_key: str, user: sqlite3.Row = Depends(get_current_user)):
    if class_key not in JOB_CLASSES:
        raise HTTPException(status_code=400, detail="Invalid class key")

    if user["level"] < 100:
        raise HTTPException(status_code=400, detail="Job Change unlocks at Level 100")
    if not user["job_changed"]:
        raise HTTPException(status_code=400, detail="Job Change not unlocked")
    if user["class_stage2"] != "none":
        raise HTTPException(status_code=400, detail="Already chose job class")

    cursor.execute(
        "UPDATE users SET class_stage2=? WHERE user_id=?",
        (class_key, user["user_id"]),
    )
    conn.commit()

    return {
        "class_stage2": class_key,
        "class_name": JOB_CLASSES[class_key],
    }
