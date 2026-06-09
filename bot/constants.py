QUESTS = [
    ("Do 10 pushups", 20),
    ("Do 20 pushups", 40),
    ("Do 30 pushups", 60),
    ("Do 5 pull-ups", 35),
    ("Do 8 pull-ups", 50),
    ("Do 12 pull-ups", 70),
    ("Do 20 squats", 25),
    ("Do 40 squats", 45),
    ("Do 60 squats", 65),
    ("Plank 1 min", 25),
    ("Plank 2 min", 45),
    ("15 burpees", 40),
    ("25 burpees", 60),
]

HIDDEN_QUESTS = [
    ("Do 50 pushups", 800, "rare"),
    ("Do 100 pushups", 1400, "epic"),
    ("Do 200 pushups", 3000, "legendary"),
]

AWAKENING_CLASSES = {
    "tank": "Tank (Beginner)",
    "assassin": "Assassin (Beginner)",
    "mage": "Mage (Beginner)",
    "berserker": "Berserker (Beginner)",
}

JOB_CLASSES = {
    "tank": "Titan Guardian",
    "assassin": "Shadow Reaper",
    "mage": "Arcane Sovereign",
    "berserker": "War God",
}

CLASSES = {
    "tank": {"hp": 20, "str": 2},
    "assassin": {"agi": 3},
    "berserker": {"str": 3},
    "mage": {"int": 3},
}

DUNGEONS = {
    "E": {
        "xp": 50,
        "time": 300,
        "enemy_pool": [
            {"name": "Goblin", "task": "10 Pushups"},
            {"name": "Slime", "task": "20 Squats"},
            {"name": "Skeleton", "task": "30 Sec Plank"},
            {"name": "Bat", "task": "15 Jumping Jacks"},
            {"name": "Crawler", "task": "10 Situps"},
            {"name": "Imp", "task": "15 Lunges"},
            {"name": "Rat", "task": "20 Mountain Climbers"},
            {"name": "Mimic", "task": "20 Situps"},
            {"name": "Horned Beetle", "task": "25 Bodyweight Squats"},
            {"name": "Slime Archer", "task": "30 Sec Wall Sit"},
        ],
        "boss_pool": [
            {"name": "Goblin King", "task": "50 Pushups"},
            {"name": "Slime Monarch", "task": "60 Squats"},
            {"name": "Bone General", "task": "90 Sec Plank"},
        ],
    },
    "D": {
        "xp": 120,
        "time": 420,
        "enemy_pool": [
            {"name": "Orc", "task": "20 Pushups"},
            {"name": "Wolf", "task": "30 Squats"},
            {"name": "Zombie", "task": "15 Burpees"},
            {"name": "Bandit", "task": "20 Situps"},
            {"name": "Lizardman", "task": "45 Sec Plank"},
            {"name": "Ghoul", "task": "25 Burpees"},
            {"name": "Boar", "task": "40 Squats"},
            {"name": "Cultist", "task": "30 Situps"},
        ],
        "boss_pool": [
            {"name": "Orc Commander", "task": "80 Pushups"},
            {"name": "Wolf King", "task": "70 Squats"},
            {"name": "Zombie Lord", "task": "30 Burpees"},
        ],
    },
    "C": {
        "xp": 250,
        "time": 600,
        "enemy_pool": [
            {"name": "Dark Knight", "task": "30 Pushups"},
            {"name": "Ogre", "task": "50 Squats"},
            {"name": "Assassin", "task": "25 Burpees"},
            {"name": "Specter", "task": "1 Min Plank"},
            {"name": "War Beast", "task": "40 Situps"},
            {"name": "Abyss Hound", "task": "35 Burpees"},
            {"name": "Flame Golem", "task": "1 Min Wall Sit"},
            {"name": "Blade Dancer", "task": "40 Pushups"},
        ],
        "boss_pool": [
            {"name": "Dungeon Tyrant", "task": "120 Pushups"},
            {"name": "War Beast Alpha", "task": "80 Squats"},
            {"name": "Void Specter", "task": "2 Min Plank"},
        ],
    },
    "B": {
        "xp": 500,
        "time": 900,
        "enemy_pool": [
            {"name": "Elite Knight", "task": "40 Pushups"},
            {"name": "Armored Ogre", "task": "70 Squats"},
            {"name": "Shadow Assassin", "task": "35 Burpees"},
            {"name": "High Specter", "task": "90 Sec Plank"},
            {"name": "War Troll", "task": "50 Situps"},
        ],
        "boss_pool": [
            {"name": "Gate Warden", "task": "150 Pushups"},
            {"name": "Blood Ogre King", "task": "100 Squats"},
        ],
    },
    "A": {
        "xp": 900,
        "time": 1200,
        "enemy_pool": [
            {"name": "Arch Knight", "task": "50 Pushups"},
            {"name": "Gigant", "task": "80 Squats"},
            {"name": "Reaper", "task": "40 Burpees"},
            {"name": "Void Shade", "task": "2 Min Plank"},
            {"name": "War Dragonling", "task": "60 Situps"},
        ],
        "boss_pool": [
            {"name": "Red Gate Monarch", "task": "200 Pushups"},
            {"name": "Dragon General", "task": "120 Squats"},
        ],
    },
    "S": {
        "xp": 1500,
        "time": 1500,
        "enemy_pool": [
            {"name": "Archfiend", "task": "60 Pushups"},
            {"name": "Chaos Golem", "task": "100 Squats"},
            {"name": "Void Reaver", "task": "50 Burpees"},
            {"name": "Shadow Lord", "task": "3 Min Plank"},
            {"name": "Elder Dragon", "task": "80 Situps"},
        ],
        "boss_pool": [
            {"name": "Catastrophe Dragon", "task": "250 Pushups"},
            {"name": "World Eater", "task": "150 Squats"},
        ],
    },
}

SHOP_ITEMS = [
    ("Iron Sword", 50),
    ("Leather Armor", 40),
    ("Hunter Boots", 60),
    ("Mana Ring", 80),
]
