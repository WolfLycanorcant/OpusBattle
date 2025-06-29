import pygame
import sys
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Constants
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

# Set up the display
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Grid Game")
clock = pygame.time.Clock()

# Game state
player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]  # Starting at center
player_color = RED
menu_open = False
menu_options = ["Resume", "Change Color", "Army", "Recruit", "Quit"]
selected_option = 0

def draw_grid():
    # Fill background
    screen.fill(WHITE)
    
    # Draw grid lines
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_SIZE))
    for y in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_SIZE, y))

def draw_player():
    # Draw player as a square
    x = player_pos[0] * CELL_SIZE
    y = player_pos[1] * CELL_SIZE
    pygame.draw.rect(screen, player_color, (x, y, CELL_SIZE, CELL_SIZE))

# Store menu item rectangles for click detection
menu_item_rects = []

def draw_menu():
    global menu_item_rects, selected_option
    
    if not menu_open:
        menu_item_rects = []
        return
        
    # Create semi-transparent overlay
    overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Reset menu item rectangles
    menu_item_rects = []
    
    # Calculate required dimensions based on content
    option_font = pygame.font.Font(None, 32)
    title_font = pygame.font.Font(None, 36)
    
    # Find the widest menu item
    max_width = title_font.size("GAME MENU")[0]  # Start with title width
    for option in menu_options:
        width = option_font.size(option)[0]
        if width > max_width:
            max_width = width
    
    # Set padding
    padding = 40
    item_height = 40
    title_padding = 30
    
    # Calculate menu dimensions
    menu_width = max_width + 2 * padding
    menu_height = title_padding * 2 + len(menu_options) * item_height + padding
    menu_x = (SCREEN_SIZE - menu_width) // 2
    menu_y = (SCREEN_SIZE - menu_height) // 2
    
    # Draw menu background
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    pygame.draw.rect(screen, MENU_BG, menu_rect, border_radius=10)
    
    # Draw menu title
    title = title_font.render("GAME MENU", True, MENU_TEXT)
    title_rect = title.get_rect(centerx=menu_rect.centerx, y=menu_y + title_padding // 2)
    screen.blit(title, title_rect)
    
    # Draw menu options
    for i, option in enumerate(menu_options):
        # Check if mouse is hovering over this option
        mouse_x, mouse_y = pygame.mouse.get_pos()
        text = option_font.render(option, True, MENU_TEXT)
        text_rect = text.get_rect(centerx=menu_rect.centerx, 
                                 y=menu_y + title_padding * 2 + i*item_height + 10)
        
        # Create a slightly larger rectangle for better click detection
        hover_rect = pygame.Rect(
            menu_rect.left + padding // 2,
            text_rect.y - 5,
            menu_rect.width - padding,
            text_rect.height + 10
        )
        
        # Store the rectangle for click detection
        menu_item_rects.append((hover_rect, i))
        
        # Change color if hovered or selected
        if hover_rect.collidepoint(mouse_x, mouse_y) or i == selected_option:
            color = MENU_HIGHLIGHT
            # Update selected option if hovered with mouse
            if i != selected_option and hover_rect.collidepoint(mouse_x, mouse_y):
                selected_option = i
        else:
            color = MENU_TEXT
            
        # Draw the option with the appropriate color
        text = option_font.render(option, True, color)
        screen.blit(text, text_rect)

def change_player_color():
    global player_color
    # Cycle through different colors
    colors = [RED, (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    current_index = colors.index(player_color) if player_color in colors else 0
    player_color = colors[(current_index + 1) % len(colors)]

def show_army_menu():
    # This function will be called when Army is selected
    # For now, we'll just print a message
    print("Army menu selected!")

def show_recruit_menu():
    # This function will be called when Recruit is selected
    print("Recruit menu selected!")

def main():
    global player_pos, menu_open, selected_option, player_color, running
    
    # Initialize pygame
    pygame.mouse.set_visible(False)  # Start with mouse hidden
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB or event.key == pygame.K_ESCAPE:
                    # Toggle menu visibility
                    menu_open = not menu_open
                    # Show/hide mouse cursor based on menu state
                    pygame.mouse.set_visible(menu_open)
                elif menu_open:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # Resume
                            menu_open = False
                            pygame.mouse.set_visible(False)
                        elif selected_option == 1:  # Change Color
                            change_player_color()
                        elif selected_option == 2:  # Army
                            show_army_menu()
                        elif selected_option == 3:  # Recruit
                            show_recruit_menu()
                        elif selected_option == 4:  # Quit
                            running = False
                # Game controls when menu is closed
                elif not menu_open:
                    if event.key == pygame.K_UP and player_pos[1] > 0:
                        player_pos[1] -= 1
                    elif event.key == pygame.K_DOWN and player_pos[1] < GRID_SIZE - 1:
                        player_pos[1] += 1
                    elif event.key == pygame.K_LEFT and player_pos[0] > 0:
                        player_pos[0] -= 1
                    elif event.key == pygame.K_RIGHT and player_pos[0] < GRID_SIZE - 1:
                        player_pos[0] += 1
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False
            
            # Handle mouse button down
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if menu_open:
                    mouse_pos = pygame.mouse.get_pos()
                    for rect, option_index in menu_item_rects:
                        if rect.collidepoint(mouse_pos):
                            selected_option = option_index
                            # Simulate pressing Enter to select the option
                            if option_index == 0:  # Resume
                                menu_open = False
                                pygame.mouse.set_visible(False)
                            elif option_index == 1:  # Change Color
                                change_player_color()
                            elif option_index == 2:  # Army
                                show_army_menu()
                            elif option_index == 3:  # Recruit
                                show_recruit_menu()
                            elif option_index == 4:  # Quit
                                running = False
                            break
        
        # Drawing
        draw_grid()
        draw_player()
        draw_menu()
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
