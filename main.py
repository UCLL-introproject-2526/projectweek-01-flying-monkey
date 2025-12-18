import pygame
import sys

# We importeren de levels vanuit de map 'levels'
from levels import level1
from levels import level2

# NIEUW: Importeer de AssetManager uit de entities map
from entities.asset_manager import AssetManager

# ====================
# SETUP
# ====================
pygame.init()
WIDTH, HEIGHT = 800, 450
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monkey Game Menu")
CLOCK = pygame.time.Clock()

# Fonts
FONT = pygame.font.SysFont(None, 50)
SMALL_FONT = pygame.font.SysFont(None, 30)
BIG_FONT = pygame.font.SysFont(None, 64)

# Kleuren
BG_COLOR = (30, 30, 50)
WHITE = (255, 255, 255)
DARK_YELLOW = (237, 174, 0)
BLACK = (0, 0, 0)
GRAY_BOX = (240, 240, 240)

# ====================
# HULP FUNCTIES
# ====================

def draw_text_centered(surface, font, text, y, color):
    """Hulpfunctie om tekst in het midden te zetten"""
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect(center=(WIDTH//2, y))
    surface.blit(text_obj, rect)

def draw_text_with_outline(surface, font, text, x, y, color):
    """Tekst met een zwart randje eromheen voor betere leesbaarheid"""
    text_surf = font.render(text, True, color)
    outline_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x, y))
    
    # Teken outline in 4 richtingen
    surface.blit(outline_surf, (text_rect.x - 1, text_rect.y))
    surface.blit(outline_surf, (text_rect.x + 1, text_rect.y))
    surface.blit(outline_surf, (text_rect.x, text_rect.y - 1))
    surface.blit(outline_surf, (text_rect.x, text_rect.y + 1))
    # Teken eigenlijke tekst
    surface.blit(text_surf, text_rect)

# ====================
# PAUZE MENU FUNCTIE
# ====================
def pause_menu(screen):
    """
    Dit menu wordt aangeroepen vanuit level1 of level2.
    """
    pause_clock = pygame.time.Clock()
    
    while True:
        # 1. Inputs checken in het pauze menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                    return "RESUME"
                if event.key == pygame.K_m:
                    return "MENU"

        # 2. Tekenen
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100)) # Zwart met transparantie
        screen.blit(overlay, (0,0))

        box_w, box_h = 400, 250
        box_x = WIDTH//2 - box_w//2
        box_y = HEIGHT//2 - box_h//2
        
        pygame.draw.rect(screen, (0,0,0,80), (box_x+6, box_y+6, box_w, box_h))
        pygame.draw.rect(screen, GRAY_BOX, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_w, box_h), 3)

        draw_text_centered(screen, BIG_FONT, "PAUSED", box_y + 45, BLACK)
        draw_text_centered(screen, SMALL_FONT, "Press R to Resume", box_y + 120, (50, 50, 50))
        draw_text_centered(screen, SMALL_FONT, "Press M for Main Menu", box_y + 170, (50, 50, 50))

        pygame.display.update()
        pause_clock.tick(30)

# ====================
# HOOFDMENU LOOP
# ====================
def main_menu():
    # NIEUW: Hier maken we de AssetManager aan!
    # Dit laadt alle plaatjes 1 keer in het geheugen.
    assets = AssetManager(WIDTH, HEIGHT)

    while True:
        # 1. Achtergrond Tekenen (via assets object)
        bg = assets.get("bg")
        if bg:
            SCREEN.blit(bg, (0, 0))
        else:
            SCREEN.fill(BG_COLOR)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        SCREEN.blit(overlay, (0, 0))
        
        # 2. Tekst Tekenen
        draw_text_with_outline(SCREEN, FONT, "MONKEY ADVENTURE", WIDTH//2, 100, DARK_YELLOW)
        draw_text_with_outline(SCREEN, SMALL_FONT, "1. Level 1 (Simpel)", WIDTH//2, 200, WHITE)
        draw_text_with_outline(SCREEN, SMALL_FONT, "2. Level 2 (Survival)", WIDTH//2, 250, WHITE)
        draw_text_with_outline(SCREEN, SMALL_FONT, "Q. Stoppen", WIDTH//2, 350, WHITE)

        pygame.display.update()
        CLOCK.tick(60)

        # 3. Inputs Checken
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                
                # LEVEL 1 STARTEN (geef assets mee!)
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    result = level1.speel(SCREEN, pause_menu, assets)
                    if result == "QUIT":
                        pygame.quit()
                        sys.exit()
                
                # LEVEL 2 STARTEN (geef assets mee!)
                if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    result = level2.speel(SCREEN, pause_menu, assets)
                    if result == "QUIT":
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    main_menu()