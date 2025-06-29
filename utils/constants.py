from enum import Enum

# Game constants
GRID_SIZE = 100  # 100x100 grid
CELL_SIZE = 8    # Size of each cell in pixels
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
MENU_BG = (50, 50, 60, 200)  # Semi-transparent dark blue
MENU_TEXT = (255, 255, 255)
MENU_HIGHLIGHT = (100, 150, 255)
SQUAD_BG = (40, 40, 40, 180)  # Semi-transparent dark gray for squad info

# Unit Types
class UnitType(Enum):
    # Starting classes
    RECRUIT = "Recruit"
    APPRENTICE = "Apprentice"
    SCOUT = "Scout"
    
    # Soldier line
    SOLDIER = "Soldier"
    VETERAN = "Veteran"
    CHAMPION = "Champion"
    
    # Archer line
    ARCHER = "Archer"
    RANGER = "Ranger"
    SNIPER = "Sniper"
    
    # Knight line
    KNIGHT = "Knight"
    PALADIN = "Paladin"
    TEMPLAR = "Templar"
    
    # Mage line
    MAGE = "Mage"
    WIZARD = "Wizard"
    ARCHMAGE = "Archmage"
    
    # Cleric line
    CLERIC = "Cleric"
    PRIEST = "Priest"
    BISHOP = "Bishop"
    
    # Rogue line
    ROGUE = "Rogue"
    ASSASSIN = "Assassin"
    NINJA = "Ninja"

# Base stats for each unit type at level 1
# Each unit gets a small random variation (+/- 10%) to make them unique
UNIT_STATS = {
    # Starting Classes
    UnitType.RECRUIT: {
        'base_hp': 20, 'hp_var': 4,  # 18-22 HP
        'base_str': 10, 'str_var': 2,  # 9-11 Str
        'base_agi': 8, 'agi_var': 1,   # 7-9 Agi
        'base_int': 5, 'int_var': 1,   # 4-6 Int
        'growth_hp': 5, 'growth_str': 3, 'growth_agi': 2, 'growth_int': 1,
        'move': 3, 'range': 1,
        'abilities': ['Power Strike']
    },
    UnitType.APPRENTICE: {
        'base_hp': 15, 'hp_var': 3,    # 14-16 HP
        'base_str': 4, 'str_var': 1,   # 3-5 Str
        'base_agi': 6, 'agi_var': 1,   # 5-7 Agi
        'base_int': 12, 'int_var': 2,  # 11-13 Int
        'growth_hp': 3, 'growth_str': 1, 'growth_agi': 1, 'growth_int': 4,
        'move': 2, 'range': 2,
        'abilities': ['Fireball']
    },
    UnitType.SCOUT: {
        'base_hp': 18, 'hp_var': 3,    # 17-19 HP
        'base_str': 6, 'str_var': 1,   # 5-7 Str
        'base_agi': 12, 'agi_var': 2,  # 11-13 Agi
        'base_int': 6, 'int_var': 1,   # 5-7 Int
        'growth_hp': 4, 'growth_str': 1, 'growth_agi': 4, 'growth_int': 1,
        'move': 4, 'range': 1,
        'abilities': ['Quick Attack']
    },
    # First Promotions
    UnitType.SOLDIER: {
        'base_hp': 25, 'hp_var': 5,
        'base_str': 14, 'str_var': 2,
        'base_agi': 10, 'agi_var': 1,
        'base_int': 6, 'int_var': 1,
        'growth_hp': 6, 'growth_str': 4, 'growth_agi': 2, 'growth_int': 1,
        'move': 3, 'range': 1,
        'abilities': ['Power Strike', 'Shield Bash']
    },
    UnitType.ARCHER: {
        'base_hp': 22, 'hp_var': 4,
        'base_str': 12, 'str_var': 2,
        'base_agi': 14, 'agi_var': 2,
        'base_int': 8, 'int_var': 1,
        'growth_hp': 5, 'growth_str': 3, 'growth_agi': 5, 'growth_int': 2,
        'move': 3, 'range': 3,
        'abilities': ['Precise Shot', 'Quick Draw']
    },
    UnitType.VETERAN: {
        'base_hp': 35, 'hp_var': 6,
        'base_str': 18, 'str_var': 3,
        'base_agi': 12, 'agi_var': 2,
        'base_int': 8, 'int_var': 1,
        'growth_hp': 7, 'growth_str': 5, 'growth_agi': 3, 'growth_int': 2,
        'move': 3, 'range': 1,
        'abilities': ['Power Strike', 'Shield Bash', 'Second Wind']
    },
    UnitType.CHAMPION: {
        'base_hp': 50, 'hp_var': 8,
        'base_str': 25, 'str_var': 4,
        'base_agi': 15, 'agi_var': 3,
        'base_int': 10, 'int_var': 2,
        'growth_hp': 9, 'growth_str': 6, 'growth_agi': 4, 'growth_int': 3,
        'move': 4, 'range': 1,
        'abilities': ['Power Strike', 'Shield Bash', 'Second Wind', 'Battle Focus']
    },
    UnitType.RANGER: {
        'base_hp': 30, 'hp_var': 5,
        'base_str': 15, 'str_var': 3,
        'base_agi': 18, 'agi_var': 3,
        'base_int': 10, 'int_var': 2,
        'growth_hp': 6, 'growth_str': 4, 'growth_agi': 6, 'growth_int': 3,
        'move': 4, 'range': 4,
        'abilities': ['Precise Shot', 'Quick Draw', 'Camouflage']
    },
    UnitType.SNIPER: {
        'base_hp': 40, 'hp_var': 7,
        'base_str': 18, 'str_var': 3,
        'base_agi': 22, 'agi_var': 4,
        'base_int': 12, 'int_var': 2,
        'growth_hp': 8, 'growth_str': 5, 'growth_agi': 7, 'growth_int': 4,
        'move': 4, 'range': 5,
        'abilities': ['Precise Shot', 'Quick Draw', 'Camouflage', 'Critical Shot']
    },
    UnitType.KNIGHT: {
        'base_hp': 40, 'hp_var': 7,
        'base_str': 20, 'str_var': 4,
        'base_agi': 10, 'agi_var': 2,
        'base_int': 6, 'int_var': 1,
        'growth_hp': 8, 'growth_str': 6, 'growth_agi': 3, 'growth_int': 2,
        'move': 3, 'range': 1,
        'abilities': ['Charge', 'Shield Bash']
    },
    UnitType.PALADIN: {
        'base_hp': 50, 'hp_var': 8,
        'base_str': 25, 'str_var': 5,
        'base_agi': 12, 'agi_var': 2,
        'base_int': 8, 'int_var': 2,
        'growth_hp': 9, 'growth_str': 7, 'growth_agi': 4, 'growth_int': 3,
        'move': 3, 'range': 1,
        'abilities': ['Charge', 'Shield Bash', 'Healing Aura']
    },
    UnitType.TEMPLAR: {
        'base_hp': 60, 'hp_var': 10,
        'base_str': 30, 'str_var': 6,
        'base_agi': 15, 'agi_var': 3,
        'base_int': 10, 'int_var': 2,
        'growth_hp': 11, 'growth_str': 8, 'growth_agi': 5, 'growth_int': 4,
        'move': 4, 'range': 1,
        'abilities': ['Charge', 'Shield Bash', 'Healing Aura', 'Battle Focus']
    },
    UnitType.MAGE: {
        'base_hp': 20, 'hp_var': 4,
        'base_str': 6, 'str_var': 1,
        'base_agi': 8, 'agi_var': 2,
        'base_int': 20, 'int_var': 4,
        'growth_hp': 4, 'growth_str': 2, 'growth_agi': 3, 'growth_int': 6,
        'move': 2, 'range': 3,
        'abilities': ['Fireball', 'Mana Shield']
    },
    UnitType.WIZARD: {
        'base_hp': 25, 'hp_var': 5,
        'base_str': 8, 'str_var': 2,
        'base_agi': 10, 'agi_var': 2,
        'base_int': 25, 'int_var': 5,
        'growth_hp': 5, 'growth_str': 3, 'growth_agi': 4, 'growth_int': 7,
        'move': 2, 'range': 4,
        'abilities': ['Fireball', 'Mana Shield', 'Teleport']
    },
    UnitType.ARCHMAGE: {
        'base_hp': 30, 'hp_var': 6,
        'base_str': 10, 'str_var': 2,
        'base_agi': 12, 'agi_var': 3,
        'base_int': 30, 'int_var': 6,
        'growth_hp': 6, 'growth_str': 4, 'growth_agi': 5, 'growth_int': 8,
        'move': 3, 'range': 5,
        'abilities': ['Fireball', 'Mana Shield', 'Teleport', 'Elemental Mastery']
    },
    UnitType.CLERIC: {
        'base_hp': 25, 'hp_var': 5,
        'base_str': 8, 'str_var': 2,
        'base_agi': 10, 'agi_var': 2,
        'base_int': 15, 'int_var': 3,
        'growth_hp': 5, 'growth_str': 3, 'growth_agi': 4, 'growth_int': 5,
        'move': 2, 'range': 2,
        'abilities': ['Healing Touch', 'Shield Bash']
    },
    UnitType.PRIEST: {
        'base_hp': 30, 'hp_var': 6,
        'base_str': 10, 'str_var': 2,
        'base_agi': 12, 'agi_var': 3,
        'base_int': 20, 'int_var': 4,
        'growth_hp': 6, 'growth_str': 4, 'growth_agi': 5, 'growth_int': 6,
        'move': 2, 'range': 3,
        'abilities': ['Healing Touch', 'Shield Bash', 'Resurrection']
    },
    UnitType.BISHOP: {
        'base_hp': 35, 'hp_var': 7,
        'base_str': 12, 'str_var': 3,
        'base_agi': 15, 'agi_var': 3,
        'base_int': 25, 'int_var': 5,
        'growth_hp': 7, 'growth_str': 5, 'growth_agi': 6, 'growth_int': 7,
        'move': 3, 'range': 4,
        'abilities': ['Healing Touch', 'Shield Bash', 'Resurrection', 'Holy Aura']
    },
    UnitType.ROGUE: {
        'base_hp': 22, 'hp_var': 4,
        'base_str': 10, 'str_var': 2,
        'base_agi': 16, 'agi_var': 3,
        'base_int': 8, 'int_var': 2,
        'growth_hp': 5, 'growth_str': 3, 'growth_agi': 6, 'growth_int': 2,
        'move': 4, 'range': 1,
        'abilities': ['Quick Attack', 'Stealth']
    },
    UnitType.ASSASSIN: {
        'base_hp': 28, 'hp_var': 5,
        'base_str': 14, 'str_var': 3,
        'base_agi': 20, 'agi_var': 4,
        'base_int': 10, 'int_var': 2,
        'growth_hp': 6, 'growth_str': 4, 'growth_agi': 7, 'growth_int': 3,
        'move': 5, 'range': 1,
        'abilities': ['Quick Attack', 'Stealth', 'Critical Strike']
    },
    UnitType.NINJA: {
        'base_hp': 35, 'hp_var': 7,
        'base_str': 18, 'str_var': 4,
        'base_agi': 25, 'agi_var': 5,
        'base_int': 12, 'int_var': 3,
        'growth_hp': 7, 'growth_str': 5, 'growth_agi': 8, 'growth_int': 4,
        'move': 5, 'range': 2,
        'abilities': ['Quick Attack', 'Stealth', 'Critical Strike', 'Smoke Bomb'],
        'promotes_to': []
    }
}

# Unit Colors
UNIT_COLORS = {
    UnitType.RECRUIT: (180, 180, 180),
    UnitType.APPRENTICE: (200, 200, 255),
    UnitType.SCOUT: (180, 220, 180),
    UnitType.SOLDIER: (200, 50, 50),
    UnitType.VETERAN: (220, 70, 70),
    UnitType.CHAMPION: (240, 100, 100),
    UnitType.ARCHER: (50, 200, 50),
    UnitType.RANGER: (70, 220, 70),
    UnitType.SNIPER: (100, 240, 100),
    UnitType.KNIGHT: (100, 100, 255),
    UnitType.PALADIN: (120, 120, 255),
    UnitType.TEMPLAR: (150, 150, 255),
    UnitType.MAGE: (200, 50, 200),
    UnitType.WIZARD: (220, 70, 220),
    UnitType.ARCHMAGE: (240, 100, 240),
    UnitType.CLERIC: (255, 255, 100),
    UnitType.PRIEST: (255, 255, 120),
    UnitType.BISHOP: (255, 255, 150),
    UnitType.ROGUE: (255, 150, 50),
    UnitType.ASSASSIN: (255, 170, 70),
    UnitType.NINJA: (255, 190, 100)
}
