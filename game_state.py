from typing import List, Optional, Tuple, Dict, Any
import random
import math
from squad import Squad
from unit import Unit
from utils.constants import UnitType, SCREEN_SIZE, CELL_SIZE, GRID_SIZE

class GameState:
    def __init__(self, save_data: dict = None):
        self.player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]  # Starting at center
        self.player_color = (255, 0, 0)  # Red
        self.menu_open = False
        self.selected_option = 0
        self.squads: List[Squad] = []
        self.selected_squad: Optional[Squad] = None
        self.current_turn = 1
        self.highlighted_tiles: set[tuple[int, int]] = set()  # Tiles that can be moved to
        self.combat_log: list[str] = []  # Combat log messages
        
        if save_data:
            self.load_game(save_data)
        else:
            self.initialize_game()
    
    def initialize_game(self):
        """Initialize the game with starting squads."""
        if not self.squads:  # Only create squads if none exist
            # Create starting positions in a circle around the center
            center_x, center_y = GRID_SIZE // 2, GRID_SIZE // 2
            radius = min(GRID_SIZE, GRID_SIZE) // 3
            
            # Create 3 starting squads
            for i in range(3):
                # Calculate position in a circle
                angle = (2 * 3.14159 * i) / 3  # 0, 120, 240 degrees
                x = int(center_x + radius * math.cos(angle))
                y = int(center_y + radius * math.sin(angle))
                
                # Ensure position is within bounds
                x = max(1, min(GRID_SIZE - 2, x))
                y = max(1, min(GRID_SIZE - 2, y))
                
                # Create squad with 1-3 random units
                squad_name = f"Squad {i+1}"  # Name squads as Squad 1, Squad 2, etc.
                squad = self.create_random_squad(x, y, name=squad_name)
                self.squads.append(squad)
                
                # Add units to the squad
                num_units = random.randint(1, 3)
                for _ in range(num_units):
                    unit_type = random.choice([
                        UnitType.RECRUIT, 
                        UnitType.APPRENTICE, 
                        UnitType.SCOUT
                    ])
                    squad.add_unit(Unit(unit_type, random.randint(1, 3)))
            
            # Select the first squad by default
            if self.squads:
                self.selected_squad = self.squads[0]
                self.selected_squad.selected = True
    
    def load_game(self, save_data: dict):
        """Load game state from a dictionary."""
        self.player_pos = save_data.get('player_pos', [GRID_SIZE // 2, GRID_SIZE // 2])
        self.player_color = tuple(save_data.get('player_color', (255, 0, 0)))
        self.current_turn = save_data.get('current_turn', 1)
        self.combat_log = save_data.get('combat_log', [])
        
        # Clear existing squads
        self.squads = []
        
        # Rebuild squads from save data
        for squad_data in save_data.get('squads', []):
            squad = Squad(
                x=squad_data['x'],
                y=squad_data['y'],
                color=tuple(squad_data['color']),
                name=squad_data['name']
            )
            
            # Restore squad state
            squad.selected = squad_data.get('selected', False)
            squad.has_acted = squad_data.get('has_acted', False)
            squad.formation = squad_data.get('formation', squad._get_default_formation())
            
            # Add units to squad
            for unit_data in squad_data.get('units', []):
                unit = Unit.from_dict(unit_data)
                squad.add_unit(unit)
                
            self.squads.append(squad)
        
        # Restore selected squad
        selected_squad_index = save_data.get('selected_squad_index', -1)
        if 0 <= selected_squad_index < len(self.squads):
            self.selected_squad = self.squads[selected_squad_index]
    
    def create_random_squad(self, x: int, y: int, name: str = None) -> Squad:
        """
        Create a squad with random units at the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            name: Optional name for the squad. If None, a default name will be generated.
        """
        import random
        
        # Generate a default name if none provided
        if name is None:
            squad_number = len([s for s in self.squads if s is not None]) + 1
            name = f"Squad {squad_number}"
            
        squad = Squad(
            x, y, 
            color=(
                random.randint(50, 200),
                random.randint(50, 200),
                random.randint(50, 200)
            ),
            name=name
        )
        
        # Add 1-3 random units to the squad
        num_units = random.randint(1, 3)
        starting_classes = [UnitType.RECRUIT, UnitType.APPRENTICE, UnitType.SCOUT]
        
        for _ in range(num_units):
            unit_type = random.choice(starting_classes)
            level = 1  # Start at level 1
            squad.add_unit(Unit(unit_type, level))
        
        return squad
    
    def end_turn(self):
        """End the current turn and reset squad actions for the next turn."""
        self.current_turn += 1
        print(f"\n=== TURN {self.current_turn} ===")
        
        # Reset squad actions
        for squad in self.squads:
            squad.has_acted = False
            
    def get_squad_at(self, x: int, y: int) -> Optional[Squad]:
        """Get the squad at the given position, if any."""
        for squad in self.squads:
            for ux, uy, unit in squad.get_unit_positions():
                if ux == x and uy == y and unit.is_alive():
                    return squad
        return None
    
    def get_unit_at(self, x: int, y: int) -> Optional[Unit]:
        """Get the unit at the given position, if any."""
        for squad in self.squads:
            for ux, uy, unit in squad.get_unit_positions():
                if ux == x and uy == y and unit.is_alive():
                    return unit
        return None
        
    def select_squad(self, x: int, y: int) -> bool:
        """
        Select the squad at the given grid position.
        Returns True if a squad was selected, False otherwise.
        """
        clicked_squad = self.get_squad_at(x, y)
        if not clicked_squad:
            return False
            
        # Deselect current squad if different
        if self.selected_squad and self.selected_squad != clicked_squad:
            self.selected_squad = None
            
        # Select the clicked squad
        self.selected_squad = clicked_squad
        print(f"Selected {clicked_squad.name} at ({x}, {y})")
        
        # Update movement range for the selected squad
        if self.selected_squad.leader:
            leader_x, leader_y, _ = self.selected_squad.get_leader_position()
            self.get_movement_range(leader_x, leader_y)
            
        return True
    
    def get_movement_range(self, x: int, y: int) -> set[tuple[int, int]]:
        """Calculate all tiles a unit at (x,y) can move to and update highlighted_tiles."""
        # Clear previous highlighted tiles
        self.highlighted_tiles.clear()
        
        unit = self.get_unit_at(x, y)
        if not unit:
            return set()
            
        squad = self.get_squad_at(x, y)
        if not squad or squad.has_acted:
            return set()
            
        move_range = unit.move
        visited = set()
        queue = [(x, y, move_range)]
        
        while queue:
            cx, cy, remaining = queue.pop(0)
            if (cx, cy) in visited:
                continue
                
            visited.add((cx, cy))
            
            if remaining <= 0:
                continue
                
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and 
                    (nx, ny) not in visited and
                    not self.get_unit_at(nx, ny)):  # Can't move through other units
                    
                    # Check terrain movement cost
                    terrain_cost = self.terrain[ny][nx]['movement_cost']
                    if remaining >= terrain_cost:
                        queue.append((nx, ny, remaining - terrain_cost))
                        # Add to highlighted tiles if it's not the starting position
                        if (nx, ny) != (x, y):
                            self.highlighted_tiles.add((nx, ny))
                        
        return self.highlighted_tiles
    
    def move_squad(self, squad: Squad, new_x: int, new_y: int) -> bool:
        """Move a squad to a new position if the move is valid."""
        # Check if the new position is within movement range
        if (new_x, new_y) not in self.highlighted_tiles:
            return False
            
        # Check if the target position is occupied by an enemy
        target_squad = self.get_squad_at(new_x, new_y)
        if target_squad and target_squad != squad:
            if target_squad.color != squad.color:
                self.start_combat(squad, target_squad)
                squad.has_acted = True
                self.highlighted_tiles.clear()
                return True
            return False  # Can't move to ally square
            
        # Move the squad
        squad.x = new_x
        squad.y = new_y
        squad.has_acted = True
        self.highlighted_tiles.clear()
        return True
    
    def start_combat(self, attacker: Squad, defender: Squad):
        """Start combat between two squads with detailed unit-by-unit resolution."""
        self.combat_log.append(f"Combat: {attacker} vs {defender}")
        
        # Get all living units from both squads
        attackers = [u for u in attacker.units if u.is_alive()]
        defenders = [u for u in defender.units if u.is_alive()]
        
        # Each living unit in the attacking squad gets to attack
        for attack_unit in attackers:
            if not defenders:  # No more defenders
                break
                
            # Choose a random defender to attack
            defend_unit = random.choice(defenders)
            
            # Calculate hit chance based on agility difference
            hit_chance = 80 + (attack_unit.agility - defend_unit.agility) // 2
            hit_chance = max(30, min(95, hit_chance))  # Clamp between 30-95%
            
            if random.randint(1, 100) <= hit_chance:
                # Calculate damage
                attack_power = attack_unit.get_attack_power()
                defense = defend_unit.get_defense()
                
                # Apply terrain defense bonus
                terrain_bonus = self.terrain[defender.y][defender.x]['defense_bonus']
                defense = int(defense * (1 + terrain_bonus))
                
                damage = max(1, attack_power - defense // 2)
                is_dead = defend_unit.take_damage(damage)
                
                self.combat_log.append(
                    f"  {attack_unit.unit_type.value} hits {defend_unit.unit_type.value} "
                    f"for {damage} damage ({'defeated' if is_dead else f'{defend_unit.current_hp}/{defend_unit.max_hp} HP'})"
                )
                
                # Grant experience
                if is_dead:
                    attack_unit.add_experience(50 + defend_unit.level * 10)
                    attack_unit.kills += 1
                    defenders.remove(defend_unit)
            
            # Attacker gains experience for participating
            attack_unit.battles += 1
        
        # Clean up defeated units
        defender.units = [u for u in defender.units if u.is_alive()]
        
        # If defender was defeated, award bonus experience
        if not any(u.is_alive() for u in defender.units):
            self.combat_log.append(f"  {defender} was completely defeated!")
            # Additional XP for each surviving attacker
            for unit in attackers:
                if unit.is_alive():
                    unit.add_experience(25)  # Bonus for victory
        
        attacker.has_acted = True
        return True
        
    def to_dict(self) -> dict:
        """Convert game state to a dictionary for saving."""
        return {
            'player_pos': self.player_pos,
            'player_color': self.player_color,
            'current_turn': self.current_turn,
            'combat_log': self.combat_log[-10:],  # Keep last 10 combat log entries
            'squads': [squad.to_dict() for squad in self.squads],
            'selected_squad_index': self.squads.index(self.selected_squad) if self.selected_squad else -1
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'GameState':
        """Create a GameState instance from a dictionary."""
        game_state = cls()
        game_state.player_pos = data['player_pos']
        game_state.player_color = tuple(data['player_color'])
        game_state.current_turn = data['current_turn']
        game_state.combat_log = data.get('combat_log', [])
        
        # Rebuild squads
        game_state.squads = []
        for squad_data in data['squads']:
            squad = Squad.from_dict(squad_data)
            game_state.squads.append(squad)
        
        # Restore selected squad
        selected_index = data.get('selected_squad_index', -1)
        if 0 <= selected_index < len(game_state.squads):
            game_state.selected_squad = game_state.squads[selected_index]
            
        return game_state
        
    def save_to_file(self, filename: str = 'savegame.json') -> bool:
        """Save the current game state to a file."""
        import json
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    @classmethod
    def load_from_file(cls, filename: str = 'savegame.json') -> Optional['GameState']:
        """Load a game state from a file."""
        import json
        import os
        
        if not os.path.exists(filename):
            return None
            
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
