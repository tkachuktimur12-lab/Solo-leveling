import json
import random


def safe_json(data, fallback):
    if data is None or data == "":
        return fallback
    try:
        return json.loads(data)
    except Exception:
        return fallback


def get_rank(level):
    if level < 5:
        return "E"
    elif level < 10:
        return "D"
    elif level < 15:
        return "C"
    elif level < 20:
        return "B"
    elif level < 30:
        return "A"
    elif level < 40:
        return "S"
    elif level < 50:
        return "SS"
    else:
        return "SSS"


def apply_stat_bonuses(xp, str_, int_, sense):
    xp = int(xp * (1 + int_ * 0.02))
    xp += str_ * 2
    return xp


def loot_chance(sense):
    return min(0.8, 0.1 + sense * 0.03)


def roll_rarity(sense):
    roll = random.random() - (sense * 0.003)
    if roll < 0.60:
        return "common"
    if roll < 0.85:
        return "rare"
    if roll < 0.95:
        return "epic"
    if roll < 0.99:
        return "legendary"
    return "mythic"


def generate_item(user):
    rarity = roll_rarity(user["sense"])

    base_stats = {
        "common": (1, 3),
        "rare": (2, 5),
        "epic": (4, 8),
        "legendary": (7, 12),
        "mythic": (10, 18),
    }

    min_stat, max_stat = base_stats[rarity]

    return {
        "name": random.choice(
            [
                "Shadow Blade",
                "Iron Gauntlets",
                "Arcane Ring",
                "Hunter Boots",
                "Titan Chestplate",
            ]
        ),
        "rarity": rarity,
        "strength": random.randint(min_stat, max_stat),
        "intelligence": random.randint(min_stat, max_stat),
        "agility": random.randint(min_stat, max_stat),
        "vitality": random.randint(min_stat, max_stat),
        "sense": random.randint(min_stat, max_stat),
    }
