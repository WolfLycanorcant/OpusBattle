import pygame
from typing import List, Tuple, Optional, Callable, Dict, Any
from utils.constants import MENU_BG, MENU_TEXT, MENU_HIGHLIGHT, SQUAD_BG, WHITE, BLACK

class Menu:
    def __init__(self, options: List[Tuple[str, Optional[Callable]]]):
        self.options = options
        self.selected_option = 0
        self.visible = False
        self.item_rects: List[pygame.Rect] = []
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the menu on the screen."""
        if not self.visible:
            return
        
        # Calculate menu dimensions
        font = pygame.font.Font(None, 36)
        padding = 20
        item_height = 40
        max_width = 0
        
        # Calculate maximum text width
        for option, _ in self.options:
            text_surface = font.render(option, True, MENU_TEXT)
            max_width = max(max_width, text_surface.get_width())
        
        menu_width = max_width + 2 * padding
        menu_height = len(self.options) * item_height + 2 * padding
        
        # Center the menu on screen
        screen_width, screen_height = screen.get_size()
        menu_x = (screen_width - menu_width) // 2
        menu_y = (screen_height - menu_height) // 2
        
        # Draw menu background
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(screen, MENU_BG, menu_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, menu_rect, 2, border_radius=10)
        
        # Draw menu items
        self.item_rects = []
        for i, (option, _) in enumerate(self.options):
            text_surface = font.render(option, True, MENU_TEXT)
            text_rect = text_surface.get_rect(
                centerx=screen_width // 2,
                top=menu_y + padding + i * item_height
            )
            
            # Highlight selected item
            if i == self.selected_option:
                highlight_rect = pygame.Rect(
                    menu_x + 5, 
                    menu_y + padding + i * item_height - 5,
                    menu_width - 10,
                    item_height - 5
                )
                pygame.draw.rect(screen, MENU_HIGHLIGHT, highlight_rect, border_radius=5)
            
            screen.blit(text_surface, text_rect)
            self.item_rects.append(text_rect.inflate(20, 10))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for the menu."""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                return True
            elif event.key == pygame.K_RETURN:
                self.select_option()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Update selected option based on mouse position
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_option = i
                    return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_option = i
                    self.select_option()
                    return True
        
        return False
    
    def select_option(self) -> None:
        """Trigger the action for the currently selected option."""
        if self.visible and self.options[self.selected_option][1]:
            self.options[self.selected_option][1]()
    
    def toggle_visibility(self) -> None:
        """Toggle the visibility of the menu."""
        self.visible = not self.visible
        if self.visible:
            self.selected_option = 0  # Reset selection when showing menu


class ArmyInterface:
    def __init__(self, game_state):
        self.game_state = game_state
        self.visible = False
        self.viewing_squad = 0
        self.viewing_unit = 0
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 36)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the army management interface."""
        if not self.visible or not self.game_state.squads:
            return
        
        # Create semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw header
        header_text = self.font_large.render("ARMY MANAGEMENT", True, (255, 255, 255))
        screen.blit(header_text, (screen.get_width() // 2 - header_text.get_width() // 2, 20))
        
        # Draw squad info
        squad = self.game_state.squads[self.viewing_squad]
        unit = squad.units[self.viewing_unit] if squad.units and len(squad.units) > self.viewing_unit else None
        
        # Squad info box
        squad_rect = pygame.Rect(50, 80, 300, 100)
        pygame.draw.rect(screen, SQUAD_BG, squad_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, squad_rect, 2, border_radius=10)
        
        # Draw squad info
        squad_text = self.font_medium.render(f"Squad {self.viewing_squad + 1}/{len(self.game_state.squads)}", True, WHITE)
        screen.blit(squad_text, (squad_rect.x + 20, squad_rect.y + 15))
        
        # Draw unit list
        unit_list_rect = pygame.Rect(50, 200, 200, 400)
        pygame.draw.rect(screen, SQUAD_BG, unit_list_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, unit_list_rect, 2, border_radius=10)
        
        # Draw unit names in the list
        unit_header = self.font_medium.render("UNITS", True, WHITE)
        screen.blit(unit_header, (unit_list_rect.x + 20, unit_list_rect.y + 15))
        
        for i, unit in enumerate(squad.units):
            y_pos = unit_list_rect.y + 50 + i * 40
            color = (100, 255, 100) if i == self.viewing_unit else WHITE
            unit_name = f"{unit.unit_type.value} Lv.{unit.level}"
            unit_text = self.font_small.render(unit_name, True, color)
            screen.blit(unit_text, (unit_list_rect.x + 20, y_pos))
            
            # HP bar
            hp_pct = unit.current_hp / unit.max_hp
            hp_bar_rect = pygame.Rect(unit_list_rect.x + 20, y_pos + 20, 100, 5)
            pygame.draw.rect(screen, (50, 50, 50), hp_bar_rect)
            pygame.draw.rect(screen, (255, 0, 0), 
                           (hp_bar_rect.x, hp_bar_rect.y, 
                            int(hp_bar_rect.width * hp_pct), 
                            hp_bar_rect.height))
        
        # Draw unit details
        if squad.units and 0 <= self.viewing_unit < len(squad.units):
            selected_unit = squad.units[self.viewing_unit]
            detail_rect = pygame.Rect(270, 200, 400, 400)
            pygame.draw.rect(screen, SQUAD_BG, detail_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, detail_rect, 2, border_radius=10)
            
            # Unit name and level
            name_text = self.font_medium.render(f"{selected_unit.unit_type.value} Lv.{selected_unit.level}", True, WHITE)
            screen.blit(name_text, (detail_rect.x + 20, detail_rect.y + 20))
            
            # Unit stats
            stats = selected_unit.get_stats_summary()
            y_offset = 60
            for stat, value in stats.items():
                stat_text = self.font_small.render(f"{stat}: {value}", True, WHITE)
                screen.blit(stat_text, (detail_rect.x + 30, detail_rect.y + y_offset))
                y_offset += 30
            
            # Promotion info
            if selected_unit.can_promote():
                promo_text = self.font_small.render("PROMOTION AVAILABLE!", True, (255, 255, 0))
                screen.blit(promo_text, (detail_rect.x + 30, detail_rect.y + 350))
                
                promo_options = selected_unit.get_promotion_options()
                if len(promo_options) == 1:
                    promo_help = self.font_small.render("Press P to promote to " + promo_options[0].value, True, (200, 200, 255))
                    screen.blit(promo_help, (detail_rect.x + 30, detail_rect.y + 380))
        
        # Draw help text
        help_text = [
            "A/D: Switch Squads",
            "W/S: Select Unit",
            "P: Promote Unit",
            "ESC: Back to Game"
        ]
        
        for i, text in enumerate(help_text):
            text_surface = self.font_small.render(text, True, (200, 200, 200))
            screen.blit(text_surface, (screen.get_width() - 200, 100 + i * 30))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for the army interface."""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            
            if not self.game_state.squads:
                return False
                
            squad = self.game_state.squads[self.viewing_squad]
            
            if event.key == pygame.K_a:  # Previous squad
                self.viewing_squad = (self.viewing_squad - 1) % len(self.game_state.squads)
                self.viewing_unit = 0
                return True
            elif event.key == pygame.K_d:  # Next squad
                self.viewing_squad = (self.viewing_squad + 1) % len(self.game_state.squads)
                self.viewing_unit = 0
                return True
            elif event.key == pygame.K_w and squad.units:  # Previous unit
                self.viewing_unit = (self.viewing_unit - 1) % len(squad.units)
                return True
            elif event.key == pygame.K_s and squad.units:  # Next unit
                self.viewing_unit = (self.viewing_unit + 1) % len(squad.units)
                return True
            elif event.key == pygame.K_p and squad.units:  # Promote unit
                unit = squad.units[self.viewing_unit]
                if unit.can_promote():
                    options = unit.get_promotion_options()
                    if len(options) == 1:
                        unit.promote(options[0])
                        return True
        
        return False
    
    def toggle_visibility(self) -> None:
        """Toggle the visibility of the army interface."""
        self.visible = not self.visible
        if self.visible and self.game_state.squads:
            # Reset to first squad and unit when opening
            self.viewing_squad = 0
            self.viewing_unit = 0
