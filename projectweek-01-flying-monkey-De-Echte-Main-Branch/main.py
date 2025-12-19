import pygame
import sys
import os

# We importeren de levels vanuit de map 'levels'
from levels import level1
from levels import level2

# NIEUW: Importeer de AssetManager uit de entities map
from entities.asset_manager import AssetManager


# ====================
# SETUP
# ====================
pygame.init()
BASE_WIDTH, BASE_HEIGHT = 1920, 1080
START_WIDTH, START_HEIGHT = 800, 450
WIDTH, HEIGHT = START_WIDTH, START_HEIGHT
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monkey Game Menu")
CLOCK = pygame.time.Clock()

# Settings state
settings_open = False
fullscreen = False
music_on = True
sfx_on = True

# Music paths
SONG_MARIO = os.path.join("assets", "music", "songMario.mp3")
DANGER_BOSS = os.path.join("assets", "music", "Danger-bossLevel.mp3")

def play_music(path):
    if music_on and os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
        except:
            pass

def stop_music():
    pygame.mixer.music.stop()

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
def pause_menu(screen, frozen_bg=None):
    """
    Dit menu wordt aangeroepen vanuit level1 of level2.
    frozen_bg: a Surface with the last game frame, to show behind the pause box.
    """
    pause_clock = pygame.time.Clock()
    BASE_WIDTH, BASE_HEIGHT = 1920, 1080
    GAME_SURF = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
    # If no frozen_bg is provided, just use a transparent surface
    if frozen_bg is None:
        frozen_bg = pygame.Surface(screen.get_size())
        frozen_bg.fill((0,0,0,0))
    while True:
        mouse_pos = pygame.mouse.get_pos()
        DISP_W, DISP_H = screen.get_size()
        scale = min(DISP_W / BASE_WIDTH, DISP_H / BASE_HEIGHT)
        surf_w, surf_h = int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)
        surf_x = (DISP_W - surf_w) // 2
        surf_y = (DISP_H - surf_h) // 2
        scaled_mouse = (int((mouse_pos[0] - surf_x) / scale), int((mouse_pos[1] - surf_y) / scale))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                    return "RESUME"
                if event.key == pygame.K_m:
                    return "MENU"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if resume_rect.collidepoint(scaled_mouse):
                    return "RESUME"
                if menu_rect.collidepoint(scaled_mouse):
                    return "MENU"

        # Draw the frozen game frame as background
        screen.blit(frozen_bg, (0, 0))
        # Draw pause box overlay
        GAME_SURF.fill((0,0,0,0))
        box_w, box_h = 900, 560  # Increased height for more bottom padding
        box_x = BASE_WIDTH//2 - box_w//2
        box_y = BASE_HEIGHT//2 - box_h//2
        pygame.draw.rect(GAME_SURF, GRAY_BOX, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(GAME_SURF, BLACK, (box_x, box_y, box_w, box_h), 6)
        pause_title_font = pygame.font.SysFont(None, 120)
        pause_btn_font = pygame.font.SysFont(None, 80)
        draw_text_centered(GAME_SURF, pause_title_font, "PAUSED", box_y + 90, BLACK)

        # Button sizes and positions
        btn_w, btn_h = 420, 110
        btn_gap = 60
        btn_x = BASE_WIDTH//2 - btn_w//2
        btn1_y = box_y + 180
        btn2_y = btn1_y + btn_h + btn_gap
        resume_rect = pygame.Rect(btn_x, btn1_y, btn_w, btn_h)
        menu_rect = pygame.Rect(btn_x, btn2_y, btn_w, btn_h)

        # Hover effect and pointer
        hovered = None
        if resume_rect.collidepoint(scaled_mouse):
            hovered = 'resume'
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif menu_rect.collidepoint(scaled_mouse):
            hovered = 'menu'
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Draw Resume button
        pygame.draw.rect(GAME_SURF, DARK_YELLOW if hovered=='resume' else WHITE, resume_rect, border_radius=0)
        pygame.draw.rect(GAME_SURF, BLACK, resume_rect, 4, border_radius=0)
        resume_label = pause_btn_font.render("Resume", True, BLACK)
        GAME_SURF.blit(resume_label, (resume_rect.centerx - resume_label.get_width()//2, resume_rect.centery - resume_label.get_height()//2))

        # Draw Main Menu button
        pygame.draw.rect(GAME_SURF, DARK_YELLOW if hovered=='menu' else WHITE, menu_rect, border_radius=0)
        pygame.draw.rect(GAME_SURF, BLACK, menu_rect, 4, border_radius=0)
        menu_label = pause_btn_font.render("Main Menu", True, BLACK)
        GAME_SURF.blit(menu_label, (menu_rect.centerx - menu_label.get_width()//2, menu_rect.centery - menu_label.get_height()//2))

        # Scale and blit pause box to screen
        scaled_surf = pygame.transform.smoothscale(GAME_SURF, (surf_w, surf_h))
        screen.blit(scaled_surf, (surf_x, surf_y))
        pygame.display.update()
        pause_clock.tick(30)

# ====================
# HOOFDMENU LOOP
# ====================

def main_menu():
    global settings_open, fullscreen, music_on, sfx_on, WIDTH, HEIGHT, SCREEN
    def recreate_screen_and_assets(new_size, fullscreen_flag):
        global SCREEN, WIDTH, HEIGHT, assets
        WIDTH, HEIGHT = new_size
        if fullscreen_flag:
            SCREEN = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.FULLSCREEN)
        else:
            SCREEN = pygame.display.set_mode((START_WIDTH, START_HEIGHT))
        assets = AssetManager(BASE_WIDTH, BASE_HEIGHT)

    # Create a fixed internalz resolution surface for crisp scaling
    GAME_SURF = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

    assets = AssetManager(WIDTH, HEIGHT)
    play_music(SONG_MARIO)
    settings_icon = pygame.image.load(os.path.join("assets", "settings.png")).convert_alpha()
    settings_icon = pygame.transform.smoothscale(settings_icon, (48, 48))
    settings_rect = pygame.Rect(20, HEIGHT - 68, 48, 48)
    running = True
    select_level_open = False
    while running:
        DISP_W, DISP_H = SCREEN.get_size()
        mouse_pos = pygame.mouse.get_pos()
        WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT
        GAME_SURF.fill(BG_COLOR)
        bg = assets.get("bg")
        if bg:
            bg_scaled = pygame.transform.smoothscale(bg, (WIDTH, HEIGHT))
            GAME_SURF.blit(bg_scaled, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        GAME_SURF.blit(overlay, (0, 0))
        menu_title_font = pygame.font.SysFont(None, 160)
        btn_font = pygame.font.SysFont(None, 90)
        # Draw main menu title
        title_font = pygame.font.SysFont(None, 160)
        draw_text_centered(GAME_SURF, title_font, "MONKEY ADVENTURE", HEIGHT//2 - 220, DARK_YELLOW)

        # If settings menu is open, draw settings menu and skip main menu boxes
        if settings_open:
            # Use much larger fonts for settings
            settings_title_font = pygame.font.SysFont(None, 120)
            settings_label_font = pygame.font.SysFont(None, 64)
            settings_toggle_font = pygame.font.SysFont(None, 54)
            box_w = int(WIDTH * 0.75)
            box_h = int(HEIGHT * 0.85)
            box_x = WIDTH // 2 - box_w // 2
            box_y = int(HEIGHT * 0.075)
            box_inner_w = int(box_w * 0.7)
            box_inner_x = box_x + (box_w - box_inner_w) // 2
            toggle_height = 90
            toggle_gap = 40
            fs_box = pygame.Rect(int(box_inner_x), int(box_y + 140), int(box_inner_w), toggle_height)
            yes_rect = pygame.Rect(fs_box.right - 220, fs_box.top + 18, 100, 54)
            no_rect = pygame.Rect(fs_box.right - 110, fs_box.top + 18, 100, 54)
            music_box = pygame.Rect(int(box_inner_x), fs_box.bottom + toggle_gap, int(box_inner_w), toggle_height)
            music_on_rect = pygame.Rect(music_box.right - 220, music_box.top + 18, 100, 54)
            music_off_rect = pygame.Rect(music_box.right - 110, music_box.top + 18, 100, 54)
            sfx_box = pygame.Rect(int(box_inner_x), music_box.bottom + toggle_gap, int(box_inner_w), toggle_height)
            sfx_on_rect = pygame.Rect(sfx_box.right - 220, sfx_box.top + 18, 100, 54)
            sfx_off_rect = pygame.Rect(sfx_box.right - 110, sfx_box.top + 18, 100, 54)
            pygame.draw.rect(GAME_SURF, GRAY_BOX, (box_x, box_y, box_w, box_h))
            pygame.draw.rect(GAME_SURF, BLACK, (box_x, box_y, box_w, box_h), 5)
            draw_text_centered(GAME_SURF, settings_title_font, "Settings", box_y + 80, DARK_YELLOW)
            # Fullscreen toggle
            pygame.draw.rect(GAME_SURF, WHITE, fs_box)
            pygame.draw.rect(GAME_SURF, BLACK, fs_box, 3)
            fs_label = settings_label_font.render("Full screen", True, BLACK)
            GAME_SURF.blit(fs_label, (fs_box.left + 30, fs_box.centery - fs_label.get_height() // 2))
            pygame.draw.rect(GAME_SURF, DARK_YELLOW if fullscreen else WHITE, yes_rect)
            pygame.draw.rect(GAME_SURF, DARK_YELLOW if not fullscreen else WHITE, no_rect)
            yes_label = settings_toggle_font.render("Yes", True, BLACK)
            no_label = settings_toggle_font.render("No", True, BLACK)
            GAME_SURF.blit(yes_label, (yes_rect.centerx - yes_label.get_width() // 2, yes_rect.centery - yes_label.get_height() // 2))
            GAME_SURF.blit(no_label, (no_rect.centerx - no_label.get_width() // 2, no_rect.centery - no_label.get_height() // 2))
            # Music toggle
            pygame.draw.rect(GAME_SURF, WHITE, music_box)
            pygame.draw.rect(GAME_SURF, BLACK, music_box, 3)
            music_label = settings_label_font.render("Music", True, BLACK)
            GAME_SURF.blit(music_label, (music_box.left + 30, music_box.centery - music_label.get_height() // 2))
            pygame.draw.rect(GAME_SURF, DARK_YELLOW if music_on else WHITE, music_on_rect)
            pygame.draw.rect(GAME_SURF, DARK_YELLOW if not music_on else WHITE, music_off_rect)
            on_label = settings_toggle_font.render("On", True, BLACK)
            off_label = settings_toggle_font.render("Off", True, BLACK)
            GAME_SURF.blit(on_label, (music_on_rect.centerx - on_label.get_width() // 2, music_on_rect.centery - on_label.get_height() // 2))
            GAME_SURF.blit(off_label, (music_off_rect.centerx - off_label.get_width() // 2, music_off_rect.centery - off_label.get_height() // 2))
            # SFX toggle
            pygame.draw.rect(GAME_SURF, WHITE, sfx_box)
            pygame.draw.rect(GAME_SURF, BLACK, sfx_box, 3)
            sfx_label = settings_label_font.render("Sound FX", True, BLACK)
            GAME_SURF.blit(sfx_label, (sfx_box.left + 30, sfx_box.centery - sfx_label.get_height() // 2))
            pygame.draw.rect(GAME_SURF, DARK_YELLOW if sfx_on else WHITE, sfx_on_rect)
            pygame.draw.rect(GAME_SURF, DARK_YELLOW if not sfx_on else WHITE, sfx_off_rect)
            sfx_on_label = settings_toggle_font.render("On", True, BLACK)
            sfx_off_label = settings_toggle_font.render("Off", True, BLACK)
            GAME_SURF.blit(sfx_on_label, (sfx_on_rect.centerx - sfx_on_label.get_width() // 2, sfx_on_rect.centery - sfx_on_label.get_height() // 2))
            GAME_SURF.blit(sfx_off_label, (sfx_off_rect.centerx - sfx_off_label.get_width() // 2, sfx_off_rect.centery - sfx_off_label.get_height() // 2))
        else:
            # Centered box positions. 
            box_w, box_h = 700, 120
            box_gap = 60
            box_x = WIDTH // 2 - box_w // 2
            box1_y = HEIGHT // 2 - box_h//2
            box2_y = box1_y + box_h + box_gap
            # Draw Select Level box
            select_rect = pygame.Rect(box_x, box1_y, box_w, box_h)
            select_overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            select_overlay.fill((240,240,240,140))
            GAME_SURF.blit(select_overlay, (box_x, box1_y))
            pygame.draw.rect(GAME_SURF, BLACK, select_rect, 4)
            select_label = btn_font.render("Select Level", True, BLACK)
            GAME_SURF.blit(select_label, (select_rect.centerx - select_label.get_width()//2, select_rect.centery - select_label.get_height()//2))
            # Draw Exit Game box
            exit_rect = pygame.Rect(box_x, box2_y, box_w, box_h)
            exit_overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            exit_overlay.fill((240,240,240,140))
            GAME_SURF.blit(exit_overlay, (box_x, box2_y))
            pygame.draw.rect(GAME_SURF, BLACK, exit_rect, 4)
            exit_label = btn_font.render("Exit Game", True, BLACK)
            GAME_SURF.blit(exit_label, (exit_rect.centerx - exit_label.get_width()//2, exit_rect.centery - exit_label.get_height()//2))

        # Hover logic
        scale = min(DISP_W / WIDTH, DISP_H / HEIGHT)
        surf_w, surf_h = int(WIDTH * scale), int(HEIGHT * scale)
        surf_x = (DISP_W - surf_w) // 2
        surf_y = (DISP_H - surf_h) // 2
        scaled_mouse = (int((mouse_pos[0] - surf_x) / scale), int((mouse_pos[1] - surf_y) / scale))
        # Only allow main menu hover if settings menu is NOT open
        hovered = None
        if settings_open:
            # Settings menu: check if mouse is over any toggle
            if (
                yes_rect.collidepoint(scaled_mouse) or
                no_rect.collidepoint(scaled_mouse) or
                music_on_rect.collidepoint(scaled_mouse) or
                music_off_rect.collidepoint(scaled_mouse) or
                sfx_on_rect.collidepoint(scaled_mouse) or
                sfx_off_rect.collidepoint(scaled_mouse)
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif not select_level_open:
            if select_rect.collidepoint(scaled_mouse):
                hovered = 'select'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif exit_rect.collidepoint(scaled_mouse):
                hovered = 'exit'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        # Highlight hover
        if not settings_open:
            if hovered == 'select':
                pygame.draw.rect(GAME_SURF, DARK_YELLOW, select_rect, 4)
            elif hovered == 'exit':
                pygame.draw.rect(GAME_SURF, DARK_YELLOW, exit_rect, 4)

        # Select Level submenu
        if select_level_open:
            overlay2 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay2.fill((0,0,0,120))
            GAME_SURF.blit(overlay2, (0,0))
            # Draw level select box
            lvl_box_w, lvl_box_h = 600, 480  # Increased height for more space
            lvl_box_x = WIDTH//2 - lvl_box_w//2
            lvl_box_y = HEIGHT//2 - lvl_box_h//2
            pygame.draw.rect(GAME_SURF, GRAY_BOX, (lvl_box_x, lvl_box_y, lvl_box_w, lvl_box_h))
            pygame.draw.rect(GAME_SURF, BLACK, (lvl_box_x, lvl_box_y, lvl_box_w, lvl_box_h), 5)
            lvl_font = pygame.font.SysFont(None, 80)
            draw_text_centered(GAME_SURF, lvl_font, "Select Level", lvl_box_y + 55, DARK_YELLOW)
            # Level buttons
            lvl_btn_w, lvl_btn_h = 400, 80
            lvl_btn_gap = 30
            lvl1_y = lvl_box_y + 110
            lvl2_y = lvl1_y + lvl_btn_h + lvl_btn_gap
            lvl3_y = lvl2_y + lvl_btn_h + lvl_btn_gap
            lvl1_rect = pygame.Rect(WIDTH//2 - lvl_btn_w//2, lvl1_y, lvl_btn_w, lvl_btn_h)
            lvl2_rect = pygame.Rect(WIDTH//2 - lvl_btn_w//2, lvl2_y, lvl_btn_w, lvl_btn_h)
            lvl3_rect = pygame.Rect(WIDTH//2 - lvl_btn_w//2, lvl3_y, lvl_btn_w, lvl_btn_h)
            # Hover for level buttons
            hovered_lvl = None
            if lvl1_rect.collidepoint(scaled_mouse):
                hovered_lvl = 'lvl1'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif lvl2_rect.collidepoint(scaled_mouse):
                hovered_lvl = 'lvl2'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif lvl3_rect.collidepoint(scaled_mouse):
                hovered_lvl = 'lvl3'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            # Draw level buttons
            for rect, label, key in [
                (lvl1_rect, "Level 1", 'lvl1'),
                (lvl2_rect, "Level 2", 'lvl2'),
                (lvl3_rect, "Level 3", 'lvl3')]:
                lvl_overlay = pygame.Surface((lvl_btn_w, lvl_btn_h), pygame.SRCALPHA)
                lvl_overlay.fill((240,240,240,140))
                GAME_SURF.blit(lvl_overlay, (rect.x, rect.y))
                pygame.draw.rect(GAME_SURF, DARK_YELLOW if hovered_lvl==key else BLACK, rect, 4)
                lbl = lvl_font.render(label, True, BLACK)
                GAME_SURF.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))

        # Draw settings icon (unchanged)
        icon_color = WHITE
        settings_icon_size = 120
        settings_rect = pygame.Rect(60, HEIGHT - settings_icon_size - 60, settings_icon_size, settings_icon_size)
        if settings_rect.collidepoint(scaled_mouse):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        settings_icon_tinted = pygame.transform.smoothscale(settings_icon, (settings_icon_size, settings_icon_size))
        settings_icon_tinted.fill(icon_color, special_flags=pygame.BLEND_RGBA_MULT)
        GAME_SURF.blit(settings_icon_tinted, settings_rect.topleft)

        # Scale and blit
        scaled_surf = pygame.transform.smoothscale(GAME_SURF, (surf_w, surf_h))
        SCREEN.fill((0,0,0))
        SCREEN.blit(scaled_surf, (surf_x, surf_y))
        pygame.display.update()
        CLOCK.tick(60)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if select_level_open and event.key == pygame.K_ESCAPE:
                    select_level_open = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Only allow opening settings if not in level select submenu
                if settings_rect.collidepoint(scaled_mouse) and not select_level_open:
                    settings_open = not settings_open
                elif settings_open:
                    # Handle settings toggles
                    if yes_rect.collidepoint(scaled_mouse):
                        fullscreen = True
                        recreate_screen_and_assets((BASE_WIDTH, BASE_HEIGHT), True)
                    elif no_rect.collidepoint(scaled_mouse):
                        fullscreen = False
                        recreate_screen_and_assets((START_WIDTH, START_HEIGHT), False)
                    elif music_on_rect.collidepoint(scaled_mouse):
                        music_on = True
                        play_music(SONG_MARIO)
                    elif music_off_rect.collidepoint(scaled_mouse):
                        music_on = False
                        stop_music()
                    elif sfx_on_rect.collidepoint(scaled_mouse):
                        sfx_on = True
                    elif sfx_off_rect.collidepoint(scaled_mouse):
                        sfx_on = False
                elif not select_level_open:
                    if select_rect.collidepoint(scaled_mouse):
                        select_level_open = True
                    elif exit_rect.collidepoint(scaled_mouse):
                        pygame.quit()
                        sys.exit()
                else:
                    if lvl1_rect.collidepoint(scaled_mouse):
                        stop_music()
                        play_music(SONG_MARIO)
                        result = level1.speel(SCREEN, pause_menu, assets, sfx_on)
                        play_music(SONG_MARIO)
                        select_level_open = False
                        if result == "QUIT":
                            pygame.quit()
                            sys.exit()
                    elif lvl2_rect.collidepoint(scaled_mouse):
                        stop_music()
                        play_music(DANGER_BOSS)
                        from levels import level2
                        result = level2.speel(SCREEN, pause_menu, assets, sfx_on)
                        play_music(SONG_MARIO)
                        select_level_open = False
                        if result == "QUIT":
                            pygame.quit()
                            sys.exit()
                    elif lvl3_rect.collidepoint(scaled_mouse):
                        from levels import level3
                        stop_music()
                        play_music(SONG_MARIO)
                        result = level3.speel(SCREEN, pause_menu, assets, sfx_on)
                        play_music(SONG_MARIO)
                        select_level_open = False
                        if result == "QUIT":
                            pygame.quit()
                            sys.exit()

if __name__ == "__main__":
    main_menu()