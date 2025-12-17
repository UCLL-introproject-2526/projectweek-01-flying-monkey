import pygame
import sys
import os
from io import BytesIO

# Prepare system cursors (hand/arrow) with safe fallbacks
try:
    hand_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)
    arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
except Exception:
    hand_cursor = None
    arrow_cursor = None

def set_mouse_hand(enable: bool):
    """Set mouse cursor to hand if enabled and supported, otherwise arrow."""
    try:
        if hand_cursor and arrow_cursor:
            pygame.mouse.set_cursor(hand_cursor if enable else arrow_cursor)
    except Exception:
        try:
            # older pygame: accept system constant directly
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if enable else pygame.SYSTEM_CURSOR_ARROW)
        except Exception:
            pass
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

# Settings icon and runtime flags
SETTINGS_TINT = (237, 174, 0)
settings_icon = None
try:
    svg_path = os.path.join("assets", "settings.svg")
    png_path = os.path.join("assets", "settings.png")
    if os.path.exists(svg_path):
        try:
            import cairosvg
            png_bytes = cairosvg.svg2png(url=svg_path, output_width=40, output_height=40)
            surf = pygame.image.load(BytesIO(png_bytes)).convert_alpha()
            # tint the icon to the settings color
            tint = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            tint.fill(SETTINGS_TINT)
            tint.blit(surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            settings_icon = tint
        except Exception:
            settings_icon = None
    elif os.path.exists(png_path):
        try:
            surf = pygame.image.load(png_path).convert_alpha()
            surf = pygame.transform.scale(surf, (40, 40))
            tint = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            tint.fill(SETTINGS_TINT)
            tint.blit(surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            settings_icon = tint
        except Exception:
            settings_icon = None
    else:
        settings_icon = None
except Exception:
    settings_icon = None

# Runtime toggles
SOUND_ON = True
FULLSCREEN = False
# expose a flag on the mixer so other modules can check mute state
setattr(pygame.mixer, 'SOUND_ON', SOUND_ON)

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

    # Draw a lighter outline by blitting the outline surface at the left/right neighbors only
    for ox, oy in [(-1, 0), (1, 0)]:
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
        shadow_surf.fill((0, 0, 0, 80))
        # smaller offset so shadow doesn't overlap box edges as much
        screen.blit(shadow_surf, (menu_x + 6, menu_y + 8))

        # main menu box
        pygame.draw.rect(screen, (245, 245, 245), (menu_x, menu_y, menu_w, menu_h))
        # black outline slightly around the box for a stronger edge
        pygame.draw.rect(screen, (0, 0, 0), (menu_x - 4, menu_y - 4, menu_w + 8, menu_h + 8), 3)
        # thin inner white border
        pygame.draw.rect(screen, WHITE, (menu_x, menu_y, menu_w, menu_h), 2)
        # title with outline (add extra top padding so it doesn't touch the box)
        draw_text_centered("PAUSED", BIG_FONT, menu_y + 30, (20, 20, 20))

        # Prepare texts and compute sizes using font.size so we can draw outlined text later
        resume_label = "Resume (ESC or R)"
        menu_label = "Main Menu (M)"

        # Make both option boxes the same width for alignment
        padding_x = 24
        padding_y = 12
        max_text_w = max(SMALL_FONT.size(resume_label)[0], SMALL_FONT.size(menu_label)[0])
        box_w = max_text_w + padding_x * 2
        box_h = SMALL_FONT.get_height() + padding_y * 2

        # nudge slightly to the right so centered content doesn't overlap the right box border
        center_x = WIDTH // 2 + 6

        # Resume box (move down a bit to create more spacing under the title)
        resume_box = pygame.Rect(center_x - box_w // 2, menu_y + 100 - box_h // 2, box_w, box_h)
        pygame.draw.rect(screen, (220, 220, 220), resume_box)
        pygame.draw.rect(screen, (20, 20, 20), resume_box, 2)
        # draw plain, thinner text (no outline) for readability
        resume_surf = SMALL_FONT.render(resume_label, True, (20, 20, 20))
        resume_rect = resume_surf.get_rect(center=resume_box.center)
        screen.blit(resume_surf, resume_rect)

        # Main Menu box (same width)
        menu_box = pygame.Rect(center_x - box_w // 2, menu_y + 160 - box_h // 2, box_w, box_h)
        pygame.draw.rect(screen, (220, 220, 220), menu_box)
        pygame.draw.rect(screen, (20, 20, 20), menu_box, 2)
        # draw plain, thinner text (no outline) for readability
        menu_surf = SMALL_FONT.render(menu_label, True, (20, 20, 20))
        menu_rect = menu_surf.get_rect(center=menu_box.center)
        screen.blit(menu_surf, menu_rect)

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

    # draw settings icon bottom-left
    if settings_icon:
        icon_x = 10
        icon_y = HEIGHT - 10 - settings_icon.get_height()
        SCREEN.blit(settings_icon, (icon_x, icon_y))
        settings_rect = pygame.Rect(icon_x, icon_y, settings_icon.get_width(), settings_icon.get_height())

    # change cursor when hovering settings
    try:
        mx, my = pygame.mouse.get_pos()
        if settings_icon and settings_rect and settings_rect.collidepoint((mx, my)):
            set_mouse_hand(True)
        else:
            set_mouse_hand(False)
    except Exception:
        pass

    pygame.display.update()
    CLOCK.tick(60)

    # Input checken
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # mouse click: open settings when icon pressed
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            try:
                mx, my = event.pos
                if settings_icon and settings_rect.collidepoint((mx, my)):
                    in_settings = True
                    while in_settings:
                        for se in pygame.event.get():
                            if se.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if se.type == pygame.KEYDOWN and se.key in (pygame.K_ESCAPE, pygame.K_q):
                                in_settings = False
                            if se.type == pygame.MOUSEBUTTONDOWN and se.button == 1:
                                sx, sy = se.pos
                                modal_w, modal_h = 360, 200
                                modal_x = WIDTH//2 - modal_w//2
                                modal_y = HEIGHT//2 - modal_h//2
                                fs_yes = pygame.Rect(modal_x + 140, modal_y + 40, 60, 30)
                                fs_no = pygame.Rect(modal_x + 210, modal_y + 40, 60, 30)
                                sound_on_rect = pygame.Rect(modal_x + 140, modal_y + 100, 60, 30)
                                sound_off_rect = pygame.Rect(modal_x + 210, modal_y + 100, 60, 30)
                                close_rect = pygame.Rect(modal_x + modal_w - 90, modal_y + modal_h - 40, 80, 30)
                                if fs_yes.collidepoint((sx, sy)):
                                    if not FULLSCREEN:
                                        SCREEN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                                        FULLSCREEN = True
                                        WIDTH, HEIGHT = SCREEN.get_size()
                                        # rescale menu background to new size if available
                                        try:
                                            if menu_bg_original is not None:
                                                menu_bg = pygame.transform.scale(menu_bg_original, (WIDTH, HEIGHT))
                                        except Exception:
                                            pass
                                if fs_no.collidepoint((sx, sy)):
                                    if FULLSCREEN:
                                        SCREEN = pygame.display.set_mode((800, 450))
                                        FULLSCREEN = False
                                        WIDTH, HEIGHT = 800, 450
                                        try:
                                            if menu_bg_original is not None:
                                                menu_bg = pygame.transform.scale(menu_bg_original, (WIDTH, HEIGHT))
                                        except Exception:
                                            pass
                                if sound_on_rect.collidepoint((sx, sy)):
                                    SOUND_ON = True
                                    setattr(pygame.mixer, 'SOUND_ON', True)
                                    try:
                                        pygame.mixer.music.set_volume(1.0)
                                    except Exception:
                                        pass
                                    try:
                                        for i in range(pygame.mixer.get_num_channels()):
                                            ch = pygame.mixer.Channel(i)
                                            ch.set_volume(1.0)
                                    except Exception:
                                        pass
                                if sound_off_rect.collidepoint((sx, sy)):
                                    SOUND_ON = False
                                    setattr(pygame.mixer, 'SOUND_ON', False)
                                    try:
                                        pygame.mixer.music.set_volume(0.0)
                                    except Exception:
                                        pass
                                    try:
                                        for i in range(pygame.mixer.get_num_channels()):
                                            ch = pygame.mixer.Channel(i)
                                            ch.set_volume(0.0)
                                    except Exception:
                                        pass
                                if close_rect.collidepoint((sx, sy)):
                                    in_settings = False
                            # draw modal with current state highlighted
                            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                            overlay.fill((0,0,0,160))
                            SCREEN.blit(overlay, (0,0))
                            modal_w, modal_h = 360, 200
                            modal_x = WIDTH//2 - modal_w//2
                            modal_y = HEIGHT//2 - modal_h//2
                            pygame.draw.rect(SCREEN, (245,245,245), (modal_x, modal_y, modal_w, modal_h))
                            pygame.draw.rect(SCREEN, (0,0,0), (modal_x, modal_y, modal_w, modal_h), 2)
                            draw_text_centered("SETTINGS", BIG_FONT, modal_y + 28, (20,20,20))
                            fs_label = SMALL_FONT.render("Fullscreen:", True, (20,20,20))
                            SCREEN.blit(fs_label, (modal_x + 30, modal_y + 45))
                            fs_yes = pygame.Rect(modal_x + 140, modal_y + 40, 60, 30)
                            fs_no = pygame.Rect(modal_x + 210, modal_y + 40, 60, 30)
                            # highlight current fullscreen choice
                            if FULLSCREEN:
                                pygame.draw.rect(SCREEN, (120,200,140), fs_yes)
                                pygame.draw.rect(SCREEN, (200,200,200), fs_no)
                            else:
                                pygame.draw.rect(SCREEN, (200,200,200), fs_yes)
                                pygame.draw.rect(SCREEN, (120,200,140), fs_no)
                            SCREEN.blit(SMALL_FONT.render("Yes", True, (0,0,0)), fs_yes.move(15,5))
                            SCREEN.blit(SMALL_FONT.render("No", True, (0,0,0)), fs_no.move(20,5))
                            s_label = SMALL_FONT.render("Sound:", True, (20,20,20))
                            SCREEN.blit(s_label, (modal_x + 30, modal_y + 105))
                            sound_on_rect = pygame.Rect(modal_x + 140, modal_y + 100, 60, 30)
                            sound_off_rect = pygame.Rect(modal_x + 210, modal_y + 100, 60, 30)
                            # highlight current sound choice
                            if getattr(pygame.mixer, 'SOUND_ON', True):
                                pygame.draw.rect(SCREEN, (120,200,140), sound_on_rect)
                                pygame.draw.rect(SCREEN, (200,200,200), sound_off_rect)
                            else:
                                pygame.draw.rect(SCREEN, (200,200,200), sound_on_rect)
                                pygame.draw.rect(SCREEN, (120,200,140), sound_off_rect)
                            SCREEN.blit(SMALL_FONT.render("On", True, (0,0,0)), sound_on_rect.move(20,5))
                            SCREEN.blit(SMALL_FONT.render("Off", True, (0,0,0)), sound_off_rect.move(10,5))
                            close_rect = pygame.Rect(modal_x + modal_w - 90, modal_y + modal_h - 40, 80, 30)
                            pygame.draw.rect(SCREEN, (180,180,180), close_rect)
                            SCREEN.blit(SMALL_FONT.render("Close", True, (0,0,0)), close_rect.move(12,5))
                            pygame.display.update()
                            CLOCK.tick(30)

            except Exception:
                pass

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