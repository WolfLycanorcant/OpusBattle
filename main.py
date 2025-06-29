import sys
import pygame
import random
import time
from typing import List, Tuple, Optional, Dict, Any

# Initialize pygame
pygame.init()

# Import game components
from game_state import GameState
from ui.menu import Menu, ArmyInterface, SaveDialog
from utils.constants import *
from unit import Unit

# Create game window
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Opus Battle")
clock = pygame.time.Clock()

# Initialize game state
game_state = None

def load_game(filename='savegame.json'):
    """Load a saved game from file."""
    global game_state
    loaded_state = GameState.load_from_file(filename)
    if loaded_state:
        game_state = loaded_state
        print("Game loaded successfully!")
    else:
        print("No saved game found or error loading, starting new game.")
        game_state = GameState()

# Try to load a saved game, or start a new one if none exists
load_game()

# Create UI components
def create_main_menu() -> Menu:
    """Create the main menu with all options."""
    def resume_game():
        menu.toggle_visibility()
    
    def change_color():
        game_state.player_color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
    
    def show_army():
        if game_state.squads:  # Only proceed if there are squads
            army_interface.viewing_squad = 0  # Reset to first squad
            army_interface.viewing_unit = 0  # Reset to first unit
            army_interface.visible = True
            menu.visible = False
    
    def recruit_unit():
        if game_state.squads:
            squad = game_state.squads[0]  # Add to first squad for now
            unit_types = [UnitType.RECRUIT, UnitType.APPRENTICE, UnitType.SCOUT]
            if len(squad.units) < 9:  # Max 9 units per squad
                unit_type = random.choice(unit_types)
                squad.add_unit(Unit(unit_type, 1))
                print(f"Recruited a new {unit_type.value} to squad!")
    
    def save_game():
        if game_state.save_to_file('savegame.json'):
            print("Game saved successfully!")
        else:
            print("Failed to save game!")
    
    def load_game_menu():
        load_game('savegame.json')
        menu.visible = False
    
    def end_turn():
        game_state.end_turn()
        menu.visible = False
    
    def quit_game():
        menu.visible = False
        save_dialog.show()
    
    menu = Menu([
        ("Resume", resume_game),
        ("Change Color", change_color),
        ("Army", show_army),
        ("Recruit", recruit_unit),
        ("Save Game", save_game),
        ("Load Game", load_game_menu),
        ("End Turn", end_turn),
        ("Quit", quit_game)
    ])
    
    return menu

# Create UI instances
menu = create_main_menu()
army_interface = ArmyInterface(game_state)

# Create save dialog
def on_save_selected(slot):
    game_state.save_to_file(f'savegame_{slot}.json')
    print(f"Game saved to savegame_{slot}.json")
    save_dialog.hide()
    save_dialog.load_save_slots()  # Refresh the save slots

def on_save_canceled():
    save_dialog.hide()

def on_quit_without_save():
    global running
    running = False

save_dialog = SaveDialog(on_save_selected, on_save_canceled, on_quit_without_save)

# Font for grid coordinates
font = pygame.font.Font(None, 16)

def draw_grid():
    """Draw the game grid."""
    # Draw grid lines
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, SCREEN_SIZE))
    for y in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (SCREEN_SIZE, y))
    
    # Draw coordinate labels every 10 cells
    for x in range(0, GRID_SIZE, 10):
        for y in range(0, GRID_SIZE, 10):
            coord_text = font.render(f"{x},{y}", True, (100, 100, 100))
            screen.blit(coord_text, (x * CELL_SIZE + 2, y * CELL_SIZE + 2))

def draw_squads():
    """Draw all squads and their units on the grid."""
    for squad in game_state.squads:
        if not squad.is_alive():
            continue
            
        # Get all living units in the squad
        living_units = [u for u in squad.units if u.current_hp > 0]
        if not living_units:
            continue
            
        # Draw each unit in formation
        for i, unit in enumerate(living_units):
            if i >= 9:  # Max 9 units per squad (3x3 formation)
                break
                
            # Get formation position
            if i < len(squad.formation):
                dx, dy = squad.formation[i]
            else:
                dx, dy = 0, 0
                
            # Calculate screen position
            grid_x = squad.x + dx
            grid_y = squad.y + dy
            
            # Only draw if within bounds
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                x = grid_x * CELL_SIZE + CELL_SIZE // 2
                y = grid_y * CELL_SIZE + CELL_SIZE // 2
                
                # Draw unit circle with class color
                unit_color = UNIT_COLORS.get(unit.unit_type, (200, 200, 200))
                pygame.draw.circle(screen, unit_color, (x, y), CELL_SIZE // 2 - 2)
                
                # Draw unit level
                level_text = font.render(str(unit.level), True, (255, 255, 255))
                text_rect = level_text.get_rect(center=(x, y))
                screen.blit(level_text, text_rect)
                
                # Draw HP bar
                hp_ratio = unit.current_hp / unit.max_hp
                hp_bar_width = CELL_SIZE - 4
                hp_fill = max(2, int(hp_ratio * hp_bar_width))
                
                # HP bar background (red)
                pygame.draw.rect(screen, (150, 0, 0), 
                               (x - hp_bar_width//2, y + CELL_SIZE//2 + 2, 
                                hp_bar_width, 2))
                # HP bar fill (green)
                pygame.draw.rect(screen, (0, 200, 0), 
                               (x - hp_bar_width//2, y + CELL_SIZE//2 + 2, 
                                hp_fill, 2))
        
        # Draw squad selection indicator on the center unit
        if squad.selected and living_units:
            x = squad.x * CELL_SIZE + CELL_SIZE // 2
            y = squad.y * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(screen, (255, 255, 0), (x, y), CELL_SIZE // 2 + 2, 2)

def draw_ui():
    """Draw UI elements like turn counter and controls help."""
    # Draw turn counter
    turn_text = font.render(f"Turn: {game_state.current_turn}", True, (255, 255, 255))
    screen.blit(turn_text, (10, 10))
    
    # Draw controls help
    controls = [
        "TAB: Toggle Menu",
        "ARROWS: Move/Select",
        "CLICK: Select Squad"
    ]
    
    for i, text in enumerate(controls):
        text_surface = font.render(text, True, (200, 200, 200))
        screen.blit(text_surface, (SCREEN_SIZE - 150, 10 + i * 20))

# Track last click time for double-click detection
last_click_time = 0
DOUBLE_CLICK_DELAY = 0.5  # seconds

def handle_input(event):
    """Handle a single input event."""
    global last_click_time, running
    
    if event.type == pygame.QUIT:
        running = False
        return
    
    # Handle save dialog events first if visible
    if save_dialog.visible:
        if save_dialog.handle_event(event):
            return
    # Then handle menu events if menu is visible
    if menu.visible:
        menu.handle_event(event)
    # Then handle army interface events if visible
    elif army_interface.visible:
        army_interface.handle_event(event)
    # Otherwise handle game input
    else:
        # Handle keyboard input
        if event.type == pygame.KEYDOWN:
            # Toggle menu
            if event.key == pygame.K_TAB:
                menu.toggle_visibility()
        
            # Handle movement when menu is closed
            elif not menu.visible and not army_interface.visible and game_state.selected_squad:
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                
                if dx != 0 or dy != 0:
                    new_x = game_state.selected_squad.x + dx
                    new_y = game_state.selected_squad.y + dy
                    
                    # Check bounds
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                        game_state.move_squad(game_state.selected_squad, new_x, new_y)
        
        # Handle mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            current_time = time.time()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            
            # Check for double click
            if (current_time - last_click_time) < DOUBLE_CLICK_DELAY:
                # Double click detected
                clicked_squad = game_state.get_squad_at(grid_x, grid_y)
                if clicked_squad:
                    # Open army management for this squad
                    squad_index = game_state.squads.index(clicked_squad)
                    army_interface.viewing_squad = squad_index
                    army_interface.viewing_unit = 0  # Reset to first unit
                    army_interface.visible = True
                    last_click_time = 0  # Reset to prevent accidental triple-clicks
                    return
            
            # Single click handling
            last_click_time = current_time
            
            if not menu.visible and not army_interface.visible:
                # Check if clicking on a squad
                clicked_squad = game_state.get_squad_at(grid_x, grid_y)
                
                if clicked_squad:
                    # Select the clicked squad
                    game_state.select_squad(grid_x, grid_y)
                elif game_state.selected_squad:
                    # Try to move selected squad to empty space
                    game_state.move_squad(game_state.selected_squad, grid_x, grid_y)

def main():
    """Main game loop."""
    global running
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Show save dialog when clicking the window close button
                menu.visible = False
                save_dialog.show()
                
                # Show the save dialog
                save_dialog.show()
                
                # Wait for the dialog to be closed
                while save_dialog.visible and running:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            running = False
                            break
                        save_dialog.handle_event(e)
                    
                    # Draw everything
                    screen.fill(BLACK)
                    draw_grid()
                    draw_squads()
                    draw_ui()
                    menu.draw(screen) if menu.visible else None
                    army_interface.draw(screen) if army_interface.visible else None
                    save_dialog.draw(screen)
                    
                    pygame.display.flip()
                    clock.tick(60)
                
                if not running:
                    break
            
            # Handle input for the current event
            handle_input(event)
        
        # Draw everything
        screen.fill(BLACK)
        draw_grid()
        draw_squads()
        draw_ui()
        
        # Draw UI elements on top
        if menu.visible:
            menu.draw(screen)
        if army_interface.visible:
            army_interface.draw(screen)
        if save_dialog.visible:
            save_dialog.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
