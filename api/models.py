"""Pydantic models for request/response schemas."""

from pydantic import BaseModel
from typing import Optional


class SpendRequest(BaseModel):
    stat: str  # "str" | "int" | "agi" | "vit" | "sense"
