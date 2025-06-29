from typing import List, Tuple, Optional, Dict, Any
import random
from unit import Unit
from utils.constants import UnitType, UNIT_COLORS, UNIT_STATS

class Squad:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int] = None, name: str = None, **kwargs):
        self.units: List[Unit] = []
        self.x = x
        self.y = y
        self.color = color or self._generate_squad_color()
        self.name = name or f"Squad ({x},{y})"  # Default name based on position
        self.selected = kwargs.get('selected', False)
        self.has_acted = kwargs.get('has_acted', False)
        self.formation = kwargs.get('formation', self._get_default_formation())
        self.leader = None  # Will be set when adding units
        
        # Load units if provided
        if 'units' in kwargs and kwargs['units']:
            for unit_data in kwargs['units']:
                self.add_unit(Unit.from_dict(unit_data))

    def _generate_squad_color(self) -> Tuple[int, int, int]:
        """Generate a random but pleasant color for the squad."""
        # Generate colors in a more controlled range for better visibility
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)
        # Ensure the color isn't too dark or too light
        if (r + g + b) < 180:  # Too dark
            r = min(255, r + 50)
            g = min(255, g + 50)
            b = min(255, b + 50)
        return (r, g, b)

    def _get_default_formation(self) -> List[Tuple[int, int]]:
        """Get the default formation positions for units in the squad."""
        return [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)
        ]

    def add_unit(self, unit: Unit) -> bool:
        """Add a unit to the squad if there's space."""
        if len(self.units) < 9:  # Max 9 units per squad
            self.units.append(unit)
            return True
        return False

    def remove_unit(self, unit: Unit) -> bool:
        """Remove a unit from the squad."""
        if unit in self.units:
            self.units.remove(unit)
            return True
        return False

    def is_alive(self) -> bool:
        """Check if any unit in the squad is alive."""
        return any(unit.is_alive() for unit in self.units)

    def get_effective_move_range(self) -> int:
        """
        Get the squad's movement range based on the average speed of living units.
        The base move range is determined by the slowest unit, but is then adjusted
        by the squad's average speed relative to the base speed of 5.
        """
        living_units = [u for u in self.units if u.is_alive()]
        if not living_units:
            return 0

        # Get the base move range from the slowest unit
        base_move = min(unit.move for unit in living_units)

        # Calculate average speed of the squad (weighted by unit health)
        total_speed = 0
        total_health = 0
        for unit in living_units:
            health_ratio = unit.current_hp / unit.max_hp
            total_speed += unit.speed * health_ratio
            total_health += health_ratio

        if total_health == 0:
            return base_move

        avg_speed = total_speed / total_health

        # Speed modifier: 0.8x at speed 1, 1.0x at speed 5, 1.2x at speed 10
        speed_modifier = 0.8 + (avg_speed - 1) * (0.2 / 4)  # 0.8-1.0 for speed 1-5
        if avg_speed > 5:
            speed_modifier = 1.0 + (avg_speed - 5) * (0.2 / 5)  # 1.0-1.2 for speed 5-10

        # Calculate effective move range
        effective_move = int(round(base_move * speed_modifier))

        # Ensure minimum move of 1 and maximum of 10
        return max(1, min(10, effective_move))

    def get_effective_attack_range(self) -> Tuple[int, int]:
        """Get the min and max attack range of the squad."""
        living_units = [u for u in self.units if u.is_alive()]
        if not living_units:
            return (0, 0)
        min_range = min(unit.range for unit in living_units)
        max_range = max(unit.range for unit in living_units)
        return (min_range, max_range)

    def get_strongest_unit(self, stat: str = 'combat') -> Optional[Unit]:
        """Get the strongest living unit in the squad based on specified stat.
        
        Args:
            stat: 'combat' (default), 'strength', 'agility', or 'intelligence'
        """
        living_units = [u for u in self.units if u.is_alive()]
        if not living_units:
            return None
            
        if stat == 'strength':
            return max(living_units, key=lambda u: u.strength)
        elif stat == 'agility':
            return max(living_units, key=lambda u: u.agility)
        elif stat == 'intelligence':
            return max(living_units, key=lambda u: u.intelligence)
        else:  # Default to combat effectiveness
            return max(living_units, key=lambda u: u.strength + u.agility * 0.8 + u.intelligence * 0.6)
    
    def get_average_level(self) -> float:
        """Get the average level of all living units in the squad."""
        living_units = [u for u in self.units if u.is_alive()]
        if not living_units:
            return 0
        return sum(unit.level for unit in living_units) / len(living_units)
    
    def get_total_power(self) -> float:
        """Calculate the total combat power of the squad."""
        return sum(
            unit.strength * 1.0 + 
            unit.agility * 0.8 + 
            unit.intelligence * 0.6 + 
            unit.max_hp * 0.2
            for unit in self.units 
            if unit.is_alive()
        )
    
    def get_formation_bonus(self) -> Dict[str, float]:
        """Calculate formation bonuses based on unit composition."""
        living_units = [u for u in self.units if u.is_alive()]
        if not living_units:
            return {}
            
        # Count unit types
        type_counts = {}
        for unit in living_units:
            unit_type = unit.unit_type
            type_counts[unit_type] = type_counts.get(unit_type, 0) + 1
        
        bonuses = {}
        
        # Melee bonus for having multiple melee units
        melee_units = sum(1 for u in living_units if u.range == 1)
        if melee_units >= 3:
            bonuses['melee_attack'] = 0.1 * melee_units  # +10% per melee unit
            
        # Ranged bonus for having multiple ranged units
        ranged_units = sum(1 for u in living_units if u.range > 1)
        if ranged_units >= 2:
            bonuses['ranged_accuracy'] = 0.05 * ranged_units  # +5% per ranged unit
            
        # Balance bonus for mixed units
        if melee_units >= 2 and ranged_units >= 2:
            bonuses['defense'] = 0.15  # +15% defense for balanced composition
            
        return bonuses
    
    def get_commander_bonus(self) -> Dict[str, float]:
        """Calculate commander bonuses if the squad has a commander-type unit."""
        commander_types = [
            UnitType.CHAMPION, UnitType.PALADIN, UnitType.TEMPLAR,
            UnitType.ARCHMAGE, UnitType.BISHOP, UnitType.NINJA
        ]
        
        for unit in self.units:
            if unit.unit_type in commander_types and unit.is_alive():
                # Return commander bonuses based on unit type
                if unit.unit_type in [UnitType.CHAMPION, UnitType.PALADIN, UnitType.TEMPLAR]:
                    return {'attack': 0.15, 'defense': 0.1}  # +15% attack, +10% defense
                elif unit.unit_type == UnitType.ARCHMAGE:
                    return {'magic': 0.2}  # +20% magic power
                elif unit.unit_type == UnitType.BISHOP:
                    return {'healing': 0.25}  # +25% healing
                elif unit.unit_type == UnitType.NINJA:
                    return {'evasion': 0.2}  # +20% dodge chance
        
        return {}  # No commander bonus
    
    def heal(self, amount: int) -> int:
        """Heal all living units in the squad. Returns total amount healed."""
        total_healed = 0
        for unit in self.units:
            if unit.is_alive():
                healed = unit.heal(amount)
                total_healed += healed
        return total_healed
    
    def get_leader(self) -> Optional[Unit]:
        """Get the highest level living unit, or None if all dead."""
        living_units = [u for u in self.units if u.is_alive()]
        if not living_units:
            return None
        return max(living_units, key=lambda u: u.level)
    
    def get_unit_positions(self) -> List[Tuple[int, int, Unit]]:
        """Get the positions of all living units in formation."""
        positions = []
        for i, unit in enumerate(self.units):
            if not unit.is_alive():
                continue
                
            if i < len(self.formation):
                dx, dy = self.formation[i]
            else:
                dx, dy = 0, 0
                
            x = self.x + dx
            y = self.y + dy
            positions.append((x, y, unit))
            
        return positions
    
    def get_unit_at(self, x: int, y: int) -> Optional[Unit]:
        """Get the unit at the specified position, if any."""
        positions = self.get_unit_positions()
        for px, py, unit in positions:
            if px == x and py == y:
                return unit
        return None
    
    def to_dict(self) -> dict:
        """Convert squad to a dictionary for saving."""
        return {
            'x': self.x,
            'y': self.y,
            'color': self.color,
            'name': self.name,
            'selected': self.selected,
            'has_acted': self.has_acted,
            'formation': self.formation,
            'units': [unit.to_dict() for unit in self.units]
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Squad':
        """Create a Squad instance from a dictionary."""
        return cls(
            x=data['x'],
            y=data['y'],
            color=tuple(data['color']),
            name=data['name'],
            selected=data.get('selected', False),
            has_acted=data.get('has_acted', False),
            formation=data.get('formation'),
            units=data.get('units', [])
        )
    
    def __str__(self):
        living_units = [u for u in self.units if u.is_alive()]
        return (
            f"Squad at ({self.x}, {self.y}) with {len(living_units)}/{len(self.units)} units\n"
            f"Levels: {[f'Lv.{u.level} {u.unit_type.value}' for u in living_units]}\n"
            f"Power: {self.get_total_power():.1f}  Avg Level: {self.get_average_level():.1f}"
        )
