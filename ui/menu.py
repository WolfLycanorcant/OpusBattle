import pygame
import json
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


class SaveDialog:
    def __init__(self, on_save, on_cancel, on_quit_without_save=None):
        self.visible = False
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.on_quit_without_save = on_quit_without_save or on_cancel
        self.selected_slot = 0
        self.save_slots = ["Empty", "Empty", "Empty"]
        self.load_save_slots()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def load_save_slots(self):
        """Load save slot information."""
        for i in range(3):
            try:
                with open(f'savegame_{i+1}.json', 'r') as f:
                    data = json.load(f)
                    turn = data.get('current_turn', 1)
                    squad_count = len(data.get('squads', []))
                    self.save_slots[i] = f"Slot {i+1}: Turn {turn}, {squad_count} squads"
            except (FileNotFoundError, json.JSONDecodeError):
                self.save_slots[i] = f"Slot {i+1}: Empty"
    
    def draw(self, screen):
        if not self.visible:
            return
            
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Dialog box - make it taller to fit the new button
        dialog_rect = pygame.Rect(0, 0, 500, 450)
        dialog_rect.center = screen.get_rect().center
        pygame.draw.rect(screen, (50, 50, 70), dialog_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, dialog_rect, 2, border_radius=10)
        
        # Title
        title = self.font.render("Save Game", True, WHITE)
        title_rect = title.get_rect(centerx=dialog_rect.centerx, top=dialog_rect.top + 20)
        screen.blit(title, title_rect)
        
        # Save slots
        for i in range(3):
            slot_rect = pygame.Rect(0, 0, 400, 60)
            slot_rect.centerx = dialog_rect.centerx
            slot_rect.top = dialog_rect.top + 80 + i * 80
            
            # Highlight selected slot
            if i == self.selected_slot:
                pygame.draw.rect(screen, (100, 100, 140), slot_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, slot_rect, 2, border_radius=5)
            
            # Slot text
            slot_text = self.small_font.render(self.save_slots[i], True, WHITE)
            text_rect = slot_text.get_rect(center=slot_rect.center)
            screen.blit(slot_text, text_rect)
        
        # Buttons
        button_width = 150
        button_height = 40
        button_spacing = 20
        
        # Don't Save button
        quit_rect = pygame.Rect(0, 0, button_width, button_height)
        quit_rect.bottom = dialog_rect.bottom - 20
        quit_rect.left = dialog_rect.left + 20
        pygame.draw.rect(screen, (150, 50, 50), quit_rect, border_radius=5)
        quit_text = self.small_font.render("Don't Save", True, WHITE)
        screen.blit(quit_text, quit_text.get_rect(center=quit_rect.center))
        
        # Cancel button
        cancel_rect = pygame.Rect(0, 0, button_width, button_height)
        cancel_rect.bottom = dialog_rect.bottom - 20
        cancel_rect.centerx = dialog_rect.centerx
        pygame.draw.rect(screen, (150, 100, 50), cancel_rect, border_radius=5)
        cancel_text = self.small_font.render("Cancel", True, WHITE)
        screen.blit(cancel_text, cancel_text.get_rect(center=cancel_rect.center))
        
        # Save button
        save_rect = pygame.Rect(0, 0, button_width, button_height)
        save_rect.bottom = dialog_rect.bottom - 20
        save_rect.right = dialog_rect.right - 20
        pygame.draw.rect(screen, (50, 150, 50), save_rect, border_radius=5)
        save_text = self.small_font.render("Save", True, WHITE)
        screen.blit(save_text, save_text.get_rect(center=save_rect.center))
        
        # Store button rects for click detection
        self.slot_rects = [
            pygame.Rect(0, 0, 400, 60).move(
                dialog_rect.centerx - 200,
                dialog_rect.top + 80 + i * 80
            ) for i in range(3)
        ]
        self.quit_rect = quit_rect
        self.cancel_rect = cancel_rect
        self.save_rect = save_rect
    
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_slot = (self.selected_slot - 1) % 3
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_slot = (self.selected_slot + 1) % 3
                return True
            elif event.key == pygame.K_RETURN:
                self.on_save(self.selected_slot + 1)
                return True
            elif event.key == pygame.K_ESCAPE:
                self.on_cancel()
                return True
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if a save slot was clicked
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_slot = i
                    return True
            
            # Check if save button was clicked
            if self.save_rect.collidepoint(mouse_pos):
                self.on_save(self.selected_slot + 1)  # +1 because slots are 1-indexed
                self.visible = False
                return True
                
            # Check if cancel button was clicked
            if self.cancel_rect.collidepoint(mouse_pos):
                self.on_cancel()
                self.visible = False
                return True
                
            # Check if quit without saving button was clicked
            if self.quit_rect.collidepoint(mouse_pos):
                self.on_quit_without_save()
                self.visible = False
                return True
        
        return False
    
    def show(self):
        self.visible = True
        self.load_save_slots()
    
    def hide(self):
        self.visible = False

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
            promo_options = selected_unit.get_promotion_options()
            if promo_options:
                # Show FP progress
                fp_percent = selected_unit.get_fp_percentage()
                fp_color = (100, 255, 100) if fp_percent >= 100 else (255, 255, 0)
                fp_text = f"FP: {selected_unit.future_points}/100 ({fp_percent:.0f}%)"
                fp_surface = self.font_small.render(fp_text, True, fp_color)
                screen.blit(fp_surface, (detail_rect.x + 30, detail_rect.y + 350))
                
                # Draw FP progress bar
                fp_bar_rect = pygame.Rect(detail_rect.x + 30, detail_rect.y + 375, 200, 10)
                pygame.draw.rect(screen, (50, 50, 50), fp_bar_rect)
                filled_width = int(fp_bar_rect.width * (fp_percent / 100))
                pygame.draw.rect(screen, fp_color, 
                               (fp_bar_rect.x, fp_bar_rect.y, 
                                min(filled_width, fp_bar_rect.width), 
                                fp_bar_rect.height))
                
                # Show promotion info if FP is 100%
                if fp_percent >= 100:
                    promo_text = self.font_small.render("PROMOTION AVAILABLE!", True, (255, 255, 0))
                    screen.blit(promo_text, (detail_rect.x + 30, detail_rect.y + 400))
                    
                    if len(promo_options) == 1:
                        promo_help = self.font_small.render(
                            f"Press P to promote to {promo_options[0].value}", 
                            True, (200, 200, 255)
                        )
                        screen.blit(promo_help, (detail_rect.x + 30, detail_rect.y + 430))
                else:
                    # Show FP needed for promotion
                    needed_fp = 100 - selected_unit.future_points
                    needed_text = self.font_small.render(
                        f"{needed_fp} more FP needed to promote", 
                        True, (200, 200, 200)
                    )
                    screen.blit(needed_text, (detail_rect.x + 30, detail_rect.y + 400))
        
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
                if unit.can_promote() and unit.future_points >= 100:
                    options = unit.get_promotion_options()
                    if len(options) == 1:
                        if unit.promote(options[0]):
                            # Play promotion sound if available
                            if hasattr(self.game_state, 'play_sound'):
                                self.game_state.play_sound('promote')
                            return True
        
        return False
    
    def toggle_visibility(self) -> None:
        """Toggle the visibility of the army interface."""
        self.visible = not self.visible
        if self.visible and self.game_state.squads:
            # Reset to first squad and unit when opening
            self.viewing_squad = 0
            self.viewing_unit = 0
