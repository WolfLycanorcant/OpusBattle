from typing import List
from utils.constants import UnitType, UNIT_STATS

import random
from typing import List, Dict, Any
from enum import Enum, auto
from utils.constants import UnitType, UNIT_STATS

class Unit:
    def __init__(self, unit_type: UnitType, level: int = 1, **kwargs):
        self.unit_type = unit_type if isinstance(unit_type, UnitType) else UnitType(unit_type)
        self.level = level
        self.experience = kwargs.get('experience', 0)
        self.kills = kwargs.get('kills', 0)
        self.battles = kwargs.get('battles', 0)
        self.abilities = kwargs.get('abilities', [])
        self.future_points = kwargs.get('future_points', 0)  # FP for promotion
        
        # Initialize base stats
        if 'base_stats' in kwargs:
            self.base_stats = kwargs['base_stats']
        else:
            # Generate new base stats with random variation
            self.base_stats = self._generate_base_stats()
        
        # Initialize stats
        self.update_stats()
        
        # Set current HP, using saved value if available
        self.current_hp = kwargs.get('current_hp', self.max_hp)
        
        # Initialize speed from base stats
        self.speed = self.base_stats.get('speed', 5)  # Default to 5 if not specified
    
    def _generate_base_stats(self) -> Dict[str, int]:
        """Generate base stats with random variation."""
        stats = UNIT_STATS[self.unit_type]
        return {
            'max_hp': stats['base_hp'] + random.randint(-stats['hp_var']//2, stats['hp_var']//2),
            'strength': stats['base_str'] + random.randint(-stats['str_var']//2, stats['str_var']//2),
            'agility': stats['base_agi'] + random.randint(-stats['agi_var']//2, stats['agi_var']//2),
            'intelligence': stats['base_int'] + random.randint(-stats['int_var']//2, stats['int_var']//2),
            'move': stats['move'],
            'range': stats['range']
        }
    
    def update_stats(self):
        """Update unit stats based on level, base stats, and growth rates."""
        stats = UNIT_STATS[self.unit_type]
        
        # Calculate stats based on level and growth rates
        self.max_hp = self.base_stats['max_hp'] + (self.level - 1) * stats['growth_hp']
        self.strength = self.base_stats['strength'] + (self.level - 1) * stats['growth_str'] // 2
        self.agility = self.base_stats['agility'] + (self.level - 1) * stats['growth_agi'] // 2
        self.intelligence = self.base_stats['intelligence'] + (self.level - 1) * stats['growth_int'] // 2
        
        # Ensure minimum values
        self.max_hp = max(1, self.max_hp)
        self.strength = max(1, self.strength)
        self.agility = max(1, self.agility)
        self.intelligence = max(1, self.intelligence)
        
        # Update movement, range, and speed from base stats
        self.move = self.base_stats['move']
        self.range = self.base_stats['range']
        self.speed = self.base_stats.get('speed', 5)  # Default to 5 if not specified
        
        # Set abilities
        self.abilities = stats['abilities']
        
        # Ensure current HP doesn't exceed max HP
        if hasattr(self, 'current_hp'):
            self.current_hp = min(self.current_hp, self.max_hp)
        else:
            self.current_hp = self.max_hp
    
    def get_attack_power(self) -> int:
        """Calculate attack power based on unit stats."""
        # Melee units use strength, ranged/magic units use intelligence
        if self.unit_type in [UnitType.ARCHER, UnitType.RANGER, UnitType.SNIPER, 
                             UnitType.MAGE, UnitType.WIZARD, UnitType.ARCHMAGE,
                             UnitType.CLERIC, UnitType.PRIEST, UnitType.BISHOP]:
            return self.intelligence + self.level
        return self.strength + self.level // 2
    
    def get_defense(self) -> int:
        """Calculate defense power based on unit stats."""
        # Physical defense is based on strength, magical defense on intelligence
        # Agile units get a dodge bonus
        dodge_chance = min(30, self.agility // 2)  # Up to 30% dodge chance
        if random.randint(1, 100) <= dodge_chance:
            return 999  # Attack will miss
            
        # Base defense is average of strength and agility
        return (self.strength + self.agility) // 2
    
    def take_damage(self, damage: int) -> bool:
        """Apply damage to the unit. Returns True if unit is defeated."""
        self.current_hp = max(0, self.current_hp - damage)
        return self.current_hp <= 0
    
    def heal(self, amount: int) -> int:
        """Heal the unit. Returns actual amount healed."""
        original_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - original_hp
    
    def add_experience(self, xp: int) -> bool:
        """Add experience to the unit. Returns True if leveled up."""
        self.experience += xp
        xp_needed = self.level * 100
        
        # Gain FP based on XP (1 FP per 10 XP, min 1)
        fp_gain = max(1, xp // 10)
        self.add_future_points(fp_gain)
        
        if self.experience >= xp_needed:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Increase unit level and update stats."""
        self.level += 1
        self.experience = 0
        self.update_stats()
        
        # Heal 25% of max HP on level up (but not over max)
        heal_amount = self.max_hp // 4
        self.current_hp = min(self.max_hp, self.current_hp + heal_amount)
    
    def can_promote(self) -> bool:
        """Check if unit can promote to a higher class."""
        return len(self.get_promotion_options()) > 0
    
    def get_promotion_options(self) -> List[UnitType]:
        """Get list of possible promotion options."""
        return UNIT_STATS[self.unit_type].get('promotes_to', [])
    
    def add_future_points(self, amount: int) -> bool:
        """Add future points to the unit. Returns True if ready to promote."""
        if not self.can_promote():
            return False
            
        self.future_points = min(100, self.future_points + amount)
        return self.future_points >= 100
        
    def get_fp_percentage(self) -> float:
        """Get the percentage of FP needed for next promotion."""
        if not self.can_promote():
            return 100.0
        return (self.future_points / 100.0) * 100
        
    def promote(self, new_type: UnitType):
        """Promote unit to a new class."""
        if new_type not in self.get_promotion_options():
            return False
            
        # Check if unit has enough FP to promote
        if self.future_points < 100:
            return False
            
        # Keep a portion of stats on promotion (80% of current)
        stat_preservation = 0.8
        self.unit_type = new_type
        
        # Update base stats for the new class
        self.base_stats = self._generate_base_stats()
        
        # Preserve some stats from previous class
        self.base_stats['max_hp'] = int(max(
            self.base_stats['max_hp'], 
            self.max_hp * stat_preservation
        ))
        
        # Update all stats
        self.update_stats()
        
        # Ensure HP doesn't go down on promotion
        self.current_hp = max(self.current_hp, self.max_hp // 2)
        
        # Reset FP after promotion
        self.future_points = 0
        
        return True
    
    def is_alive(self) -> bool:
        """Check if the unit is still alive."""
        return self.current_hp > 0
    
    def to_dict(self) -> dict:
        """Convert unit to a dictionary for saving."""
        return {
            'unit_type': self.unit_type.value,
            'level': self.level,
            'experience': self.experience,
            'kills': self.kills,
            'battles': self.battles,
            'abilities': self.abilities,
            'future_points': self.future_points,
            'base_stats': self.base_stats,
            'current_hp': self.current_hp
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Unit':
        """Create a Unit instance from a dictionary."""
        return cls(
            unit_type=data['unit_type'],
            level=data['level'],
            experience=data['experience'],
            kills=data['kills'],
            battles=data['battles'],
            abilities=data['abilities'],
            future_points=data['future_points'],
            base_stats=data['base_stats'],
            current_hp=data['current_hp']
        )
    
    def __str__(self):
        """String representation of the unit."""
        return f"{self.unit_type.value} (Lv.{self.level} HP:{self.current_hp}/{self.max_hp})"
    
    def get_stat_summary(self) -> str:
        """Get a formatted string of the unit's stats."""
        fp_text = ""
        if self.can_promote():
            fp_text = f"FP: {self.future_points}/100 ({self.get_fp_percentage():.1f}%)\n"
            
        return (
            f"Level: {self.level}\n"
            f"HP: {self.current_hp}/{self.max_hp}\n"
            f"Str: {self.strength}  Agi: {self.agility}\n"
            f"Int: {self.intelligence}  Mv: {self.move}\n"
            f"Range: {self.range}  XP: {self.experience}/{self.level * 100}\n"
            f"{fp_text}"
            f"Abilities: {', '.join(self.abilities)}\n"
            f"Kills: {self.kills}  Battles: {self.battles}"
        )
        
        # Base stats from unit type
        base_hp = stats["hp"]
        base_str = stats["str"]
        base_agi = stats["agi"]
        base_int = stats["int"]
        
        # Level scaling factors (different for each stat)
        hp_scale = 3.0
        str_scale = 1.5
        agi_scale = 1.2
        int_scale = 1.5
        
        # Calculate stats with level scaling
        self.max_hp = int(base_hp + (self.level - 1) * hp_scale)
        self.strength = int(base_str + (self.level - 1) * str_scale)
        self.agility = int(base_agi + (self.level - 1) * agi_scale)
        self.intelligence = int(base_int + (self.level - 1) * int_scale)
        
        # Set current HP if not set, otherwise cap at max_hp
        if not hasattr(self, 'current_hp') or self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
            
        # Movement range (doesn't scale with level)
        self.move_range = stats["move"]
        
        # Special abilities based on class
        self.abilities = self._get_class_abilities()
    
    def _get_class_abilities(self) -> List[str]:
        """Get special abilities based on unit class."""
        abilities = []
        
        # Melee classes
        if self.unit_type in [UnitType.SOLDIER, UnitType.VETERAN, UnitType.CHAMPION]:
            abilities.append("Power Strike")
        if self.unit_type in [UnitType.KNIGHT, UnitType.PALADIN, UnitType.TEMPLAR]:
            abilities.append("Shield Block")
            
        # Ranged classes
        if self.unit_type in [UnitType.ARCHER, UnitType.RANGER, UnitType.SNIPER]:
            abilities.append("Precise Shot")
            
        # Magic classes
        if self.unit_type in [UnitType.MAGE, UnitType.WIZARD, UnitType.ARCHMAGE]:
            abilities.append("Fireball")
        if self.unit_type in [UnitType.CLERIC, UnitType.PRIEST, UnitType.BISHOP]:
            abilities.append("Heal")
            
        # Rogue classes
        if self.unit_type in [UnitType.ROGUE, UnitType.ASSASSIN, UnitType.NINJA]:
            abilities.append("Backstab")
            
        # Special abilities for advanced classes
        if self.unit_type in [UnitType.ARCHMAGE, UnitType.TEMPLAR, UnitType.BISHOP]:
            abilities.append("Aura of Power")
            
        return abilities
    
    def get_attack_power(self, is_ranged: bool = False, is_magic: bool = False) -> int:
        """Calculate attack power based on unit stats and attack type."""
        if is_magic:
            return self.intelligence
        elif is_ranged:
            return (self.agility * 2 + self.strength) // 3
        else:  # Melee
            return (self.strength * 2 + self.agility) // 3
    
    def get_defense(self, is_magic: bool = False) -> int:
        """Calculate defense against physical or magical attacks."""
        if is_magic:
            return (self.intelligence + self.agility) // 2
        else:
            return (self.agility + self.strength) // 2
    
    def add_experience(self, amount: int):
        """Add experience and level up if needed."""
        self.experience += amount
        while self.experience >= self.get_exp_to_next_level():
            self.level_up()
    
    def get_exp_to_next_level(self) -> int:
        """Calculate experience needed for next level."""
        return 100 + (self.level * 20)  # Increasing XP requirement
    
    def level_up(self):
        """Increase level and update stats."""
        old_max_hp = self.max_hp
        old_stats = {
            'str': self.strength,
            'agi': self.agility,
            'int': self.intelligence
        }
        
        self.level += 1
        self.experience = 0
        self.update_stats()
        
        # Calculate stat increases
        stat_increases = {
            'HP': self.max_hp - old_max_hp,
            'Str': self.strength - old_stats['str'],
            'Agi': self.agility - old_stats['agi'],
            'Int': self.intelligence - old_stats['int']
        }
        
        # Fully heal on level up
        self.current_hp = self.max_hp
        
        return stat_increases
    
    def can_promote(self) -> bool:
        """Check if unit can promote."""
        return len(UNIT_STATS[self.unit_type].get("promotes_to", [])) > 0
    
    def promote(self, new_type: UnitType) -> bool:
        """Promote unit to a new class."""
        if new_type in UNIT_STATS[self.unit_type].get("promotes_to", []):
            self.unit_type = new_type
            # Keep a percentage of current HP after promotion
            hp_percent = self.current_hp / self.max_hp
            self.update_stats()
            self.current_hp = int(self.max_hp * hp_percent)
            return True
        return False
    
    def get_promotion_options(self) -> List[UnitType]:
        """Get available promotion options."""
        return UNIT_STATS[self.unit_type].get("promotes_to", [])
    
    def get_stats_summary(self) -> dict:
        """Get a detailed summary of the unit's stats and abilities."""
        return {
            "Level": self.level,
            "HP": f"{self.current_hp}/{self.max_hp}",
            "Strength": self.strength,
            "Agility": self.agility,
            "Intelligence": self.intelligence,
            "Move": self.move,  # Changed from move_range to move
            "XP": f"{self.experience}/{self.get_exp_to_next_level()}",
            "Kills": self.kills,
            "Battles": self.battles,
            "Abilities": ", ".join(self.abilities) if self.abilities else "None"
        }

    def __str__(self):
        return f"{self.unit_type.value} Lv.{self.level} (HP: {self.current_hp}/{self.max_hp})"
