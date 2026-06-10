"""Pydantic request/response schemas.

These models are the single source of truth for the API contract. They are
attached to every route via ``response_model=`` so that FastAPI emits a fully
typed OpenAPI schema, which the frontend consumes through generated TypeScript
types (see ``webapp/src/api/schema.d.ts``). Changing a shape here surfaces as a
TypeScript compile error in the web app instead of a silent runtime bug.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------


class SpendRequest(BaseModel):
    stat: str  # "str" | "int" | "agi" | "vit" | "sense"


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class StatBlock(BaseModel):
    """The five core stats, using the short keys the UI is built around.

    Field names intentionally mirror the UI keys (``str``/``int``/...). They
    shadow builtins only as attribute names, which is harmless for a schema.
    """

    str: int
    int: int
    agi: int
    vit: int
    sense: int


class Enemy(BaseModel):
    name: str
    task: str


# ---------------------------------------------------------------------------
# User / stats
# ---------------------------------------------------------------------------


class UserStats(BaseModel):
    user_id: int
    name: str
    level: int
    rank: str
    xp: int
    xp_needed: int
    gold: int
    streak: int
    stat_points: int
    str: int
    int: int
    agi: int
    vit: int
    sense: int
    equipped_bonuses: StatBlock
    hidden_rolls: int
    dungeon_rolls: int
    awakened: int
    job_changed: int
    awakening_class: Optional[str] = None
    job_class: Optional[str] = None


class SpendResult(BaseModel):
    stat_points: int
    str: int
    int: int
    agi: int
    vit: int
    sense: int
    equipped_bonuses: StatBlock


# ---------------------------------------------------------------------------
# Daily quests
# ---------------------------------------------------------------------------


class Quest(BaseModel):
    name: str
    xp: int


class DailyState(BaseModel):
    active_quests: list[Quest]
    quest_progress: int
    cooldown_active: bool
    cooldown_remaining: int
    streak: int


class DailyStartResult(BaseModel):
    active_quests: list[Quest]
    quest_progress: int


class TaskProgress(BaseModel):
    quest_progress: int
    total: int


class ClaimResult(BaseModel):
    xp_gained: int
    xp: int
    level: int
    level_ups: int
    streak: int
    stat_points: int
    hidden_rolls: int


# ---------------------------------------------------------------------------
# Dungeons
# ---------------------------------------------------------------------------


class DungeonList(BaseModel):
    available_ranks: list[str]


class EnterDungeon(BaseModel):
    rank: str
    enemies: list[Enemy]
    time_limit: int
    dungeon_end: str


class DungeonTask(BaseModel):
    dungeon_progress: int
    total_enemies: int
    boss_available: bool


class BossRoom(BaseModel):
    boss: Enemy
    time_left: int


class LootItem(BaseModel):
    item_name: str
    slot: str
    rarity: str
    strength: int
    intelligence: int
    agility: int
    vitality: int
    sense: int


class BossDefeat(BaseModel):
    xp_reward: int
    gold_reward: int
    xp: int
    gold: int
    loot: Optional[LootItem] = None


# ---------------------------------------------------------------------------
# Rolls
# ---------------------------------------------------------------------------


class HiddenQuest(BaseModel):
    index: int
    name: str
    xp: int
    rarity: str
    rarity_label: str


class HiddenRollResult(BaseModel):
    found: bool
    hidden_rolls: int
    quest: Optional[HiddenQuest] = None


class HiddenClaimResult(BaseModel):
    quest_name: str
    xp_gained: int
    rarity: str
    rarity_label: str
    xp: int


class DungeonRollResult(BaseModel):
    found: bool
    dungeon_rolls: int
    gate_rank: Optional[str] = None
    enemies: Optional[list[Enemy]] = None
    time_limit: Optional[int] = None
    dungeon_end: Optional[str] = None


# ---------------------------------------------------------------------------
# Shop
# ---------------------------------------------------------------------------


class ShopItem(BaseModel):
    name: str
    price: int


class ShopList(BaseModel):
    items: list[ShopItem]
    gold: int


class BoughtItem(BaseModel):
    name: str
    rarity: str
    slot: str
    strength: int
    intelligence: int
    agility: int
    vitality: int
    sense: int


class BuyResult(BaseModel):
    gold: int
    item: BoughtItem


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------


class InventoryItem(BaseModel):
    item_id: int
    item_name: str
    slot: str
    rarity: str
    strength: int
    intelligence: int
    agility: int
    vitality: int
    sense: int
    equipped: int


class InventoryList(BaseModel):
    items: list[InventoryItem]


class Equipment(BaseModel):
    weapon: Optional[InventoryItem] = None
    armor: Optional[InventoryItem] = None
    charm: Optional[InventoryItem] = None


class EquipResult(BaseModel):
    equipped: InventoryItem


# ---------------------------------------------------------------------------
# Class progression
# ---------------------------------------------------------------------------


class AwakeningResult(BaseModel):
    class_stage1: str
    class_name: str


class JobChangeResult(BaseModel):
    class_stage2: str
    class_name: str
