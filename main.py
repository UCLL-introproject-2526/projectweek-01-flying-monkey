import pygame
import sys
import level1  # We importeren je level bestanden
import level2

# Setup
pygame.init()
WIDTH, HEIGHT = 800, 450
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monkey Game Menu")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 50)
SMALL_FONT = pygame.font.SysFont(None, 30)
BIG_FONT = pygame.font.SysFont(None, 64)

# Menu background image (use same logic as level1: try .jpg and scale to window size)
try:
    menu_bg_original = pygame.image.load("assets/background.jpg").convert()
    menu_bg = pygame.transform.scale(menu_bg_original, (WIDTH, HEIGHT))
except Exception:
    menu_bg = None
    print("Kan background.jpg niet vinden voor het menu.")

# Kleuren voor menu
BG_COLOR = (30, 30, 50)
WHITE = (255, 255, 255)
HOVER_COLOR = (100, 100, 150)
DARK_YELLOW =(237, 174, 0)

def draw_text_centered(text, font, y, color):
    # Draw text with a thin black outline for readability
    draw_text_with_outline(SCREEN, font, text, WIDTH // 2, y, color, center=True)


def draw_text_with_outline(surface, font, text, x, y, color, outline_color=(0,0,0), center=False):
    """Render text with a 1px black outline by drawing the outline around the main text.
    If center=True, x,y are the center coordinates; otherwise they are the top-left.
    """
    # Main text surface and outline surface
    text_surf = font.render(text, True, color)
    outline_surf = font.render(text, True, outline_color)

    if center:
        text_rect = text_surf.get_rect(center=(x, y))
        outline_rect = outline_surf.get_rect(center=(x, y))
    else:
        text_rect = text_surf.get_rect(topleft=(x, y))
        outline_rect = outline_surf.get_rect(topleft=(x, y))

    # Draw outline by blitting the outline surface at the 4 cardinal neighbors
    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        surface.blit(outline_surf, outline_rect.move(ox, oy))

    # Draw main text
    surface.blit(text_surf, text_rect)


def pause_menu(screen):
    """Show a pause menu overlay. Returns 'RESUME' or 'MENU'.
    This function is passed into a level and only called from inside a level's loop.
    """
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_r):
                    return "RESUME"
                if event.key == pygame.K_m:
                    return "MENU"

        menu_w, menu_h = 420, 220
        menu_x = WIDTH // 2 - menu_w // 2
        menu_y = HEIGHT // 2 - menu_h // 2

        # subtle drop shadow for depth (semi-transparent surface)
        shadow_surf = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 100))
        screen.blit(shadow_surf, (menu_x + 8, menu_y + 11))

        # main menu box
        pygame.draw.rect(screen, (245, 245, 245), (menu_x, menu_y, menu_w, menu_h))
        # black outline slightly around the box for a stronger edge
        pygame.draw.rect(screen, (0, 0, 0), (menu_x - 4, menu_y - 4, menu_w + 8, menu_h + 8), 3)
        # thin inner white border
        pygame.draw.rect(screen, WHITE, (menu_x, menu_y, menu_w, menu_h), 2)
        # title with outline
        draw_text_centered("PAUSED", BIG_FONT, menu_y + 18, (20, 20, 20))

        # Prepare texts and compute sizes using font.size so we can draw outlined text later
        resume_label = "Resume (ESC or R)"
        menu_label = "Main Menu (M)"

        # Make both option boxes the same width for alignment
        padding_x = 24
        padding_y = 12
        max_text_w = max(SMALL_FONT.size(resume_label)[0], SMALL_FONT.size(menu_label)[0])
        box_w = max_text_w + padding_x * 2
        box_h = SMALL_FONT.get_height() + padding_y * 2

        center_x = WIDTH // 2

        # Resume box (move down a bit to create more spacing under the title)
        resume_box = pygame.Rect(center_x - box_w // 2, menu_y + 100 - box_h // 2, box_w, box_h)
        pygame.draw.rect(screen, (220, 220, 220), resume_box)
        pygame.draw.rect(screen, (20, 20, 20), resume_box, 2)
        draw_text_with_outline(screen, SMALL_FONT, resume_label, resume_box.centerx, resume_box.centery, (20,20,20), center=True)

        # Main Menu box (same width)
        menu_box = pygame.Rect(center_x - box_w // 2, menu_y + 160 - box_h // 2, box_w, box_h)
        pygame.draw.rect(screen, (220, 220, 220), menu_box)
        pygame.draw.rect(screen, (20, 20, 20), menu_box, 2)
        draw_text_with_outline(screen, SMALL_FONT, menu_label, menu_box.centerx, menu_box.centery, (20,20,20), center=True)

        pygame.display.update()
        clock.tick(30)

# ====================
# MENU LOOP
# ====================
while True:
    # Draw background image if available, otherwise fall back to solid color
    if menu_bg:
        SCREEN.blit(menu_bg, (0, 0))
    else:
        SCREEN.fill(BG_COLOR)

    # Darken the background slightly so the menu text is more readable
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))  # alpha: 0 (transparent) .. 255 (opaque)
    SCREEN.blit(overlay, (0, 0))
    
    # Tekst op het scherm
    draw_text_centered("MONKEY ADVENTURE", FONT, 100, DARK_YELLOW)
    draw_text_centered("Druk op 1 voor Level 1 (Simpel)", SMALL_FONT, 200, DARK_YELLOW)
    draw_text_centered("Druk op 2 voor Level 2 (Survival)", SMALL_FONT, 250, DARK_YELLOW)
    draw_text_centered("Druk op Q om te stoppen", SMALL_FONT, 350, DARK_YELLOW)

    pygame.display.update()
    CLOCK.tick(60)

    # Input checken
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            
            # Start Level 1
            if event.key == pygame.K_1:
                # We roepen de functie 'speel' aan uit het bestand 'level1'
                # We geven 'SCREEN' mee zodat hij op hetzelfde scherm tekent
                resultaat = level1.speel(SCREEN, pause_menu)
                
                # Als level 'QUIT' terugstuurt (kruisje geklikt), stoppen we alles
                if resultaat == "QUIT":
                    pygame.quit()
                    sys.exit()
            
            # Start Level 2
            if event.key == pygame.K_2:
                resultaat = level2.speel(SCREEN, pause_menu)
                if resultaat == "QUIT":
                    pygame.quit()
                    sys.exit()