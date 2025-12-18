
## ALLE SHARED CODES, DIE DUS VAKER TERUGKOMEN EN HERGEBRUIKT 
## WORDEN BIJ ALLE LEVELS ZOALS MONKEY ANIMATIE KASTEEL OVERWINNING, SONG...


import pygame
import os

# ==========================================
# 1. ASSET LOADER
# ==========================================
def load_assets(WIDTH, HEIGHT):
    assets = {}

    # --- ACHTERGRONDEN ---
    try:
        bg = pygame.image.load("assets/background.jpg").convert()
        assets["bg"] = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        assets["bg"] = None
    
    # Level 2 Background
    try:
        bg2 = pygame.image.load("assets/BACKKKground.jpg").convert()
        assets["bg2"] = pygame.transform.scale(bg2, (WIDTH, HEIGHT))
    except:
        assets["bg2"] = assets.get("bg")

    # --- SPELER ---
    try:
        monkey = pygame.image.load("assets/monkey.png").convert_alpha()
        assets["idle"] = pygame.transform.scale(monkey, (60, 60))
        
        # Loop animaties
        try:
            rau = pygame.image.load("assets/monkey_rau.png").convert_alpha()
            lau = pygame.image.load("assets/monkey_lau.png").convert_alpha()
            f0 = pygame.transform.scale(rau, (60, 60))
            f1 = pygame.transform.scale(lau, (60, 60))
            assets["walk_right"] = [f0, f1]
            assets["walk_left"] = [pygame.transform.flip(f, True, False) for f in assets["walk_right"]]
        except:
            assets["walk_right"] = []
            assets["walk_left"] = []

        # Spring animatie
        try:
            jump = pygame.image.load("assets/monkey_jumping.png").convert_alpha()
            assets["jump_right"] = pygame.transform.scale(jump, (60, 60))
            assets["jump_left"] = pygame.transform.flip(assets["jump_right"], True, False)
        except:
            assets["jump_right"] = None
            assets["jump_left"] = None
    except:
        print("FOUT: monkey.png niet gevonden!")
        assets["idle"] = None

    # --- VIJANDEN & ITEMS (NIEUW TOEGEVOEGD) ---
    try: 
        mush = pygame.image.load("assets/mushroom.png").convert_alpha()
        assets["enemy"] = pygame.transform.scale(mush, (65, 65))
    except: 
        assets["enemy"] = None

    try: 
        coin = pygame.image.load("assets/coin.png").convert_alpha()
        assets["coin"] = pygame.transform.scale(coin, (30, 30)) # Iets groter geschaald
    except: 
        assets["coin"] = None

    try: 
        knife = pygame.image.load("assets/knifes.png")
        assets["knife"] = pygame.transform.scale(knife, (50, 100))
    except: 
        assets["knife"] = None

    # --- OMGEVING ---
    try: assets["castle"] = pygame.image.load("assets/castle.png").convert_alpha()
    except: assets["castle"] = None
    
    try: assets["flag"] = pygame.image.load("assets/flag.png").convert_alpha()
    except: assets["flag"] = None

    try: assets["ground"] = pygame.image.load("assets/ground.jpg").convert_alpha()
    except: 
        try: assets["ground"] = pygame.image.load("assets/grond.png").convert_alpha()
        except: assets["ground"] = None

    # --- GELUID ---
    pygame.mixer.init()
    win_path = os.path.join("assets", "Sounds", "VSE.mp3")
    if os.path.exists(win_path):
        assets["win_sound"] = win_path
    else:
        assets["win_sound"] = None

    return assets

# ==========================================
# 2. SPELER TEKENEN
# ==========================================
def draw_player(screen, assets, player_rect, vel_y, on_ground, direction, walk_frame, camera_x):
    img_to_draw = assets["idle"]

    if not on_ground:
        if direction == 1 and assets.get("jump_right"): img_to_draw = assets["jump_right"]
        elif direction == -1 and assets.get("jump_left"): img_to_draw = assets["jump_left"]
    elif (walk_frame is not None) and on_ground and assets.get("walk_right"):
        if direction == 1: img_to_draw = assets["walk_right"][walk_frame]
        elif direction == -1: img_to_draw = assets["walk_left"][walk_frame]
    elif direction == -1:
        img_to_draw = pygame.transform.flip(assets["idle"], True, False)

    if img_to_draw:
        draw_pos = (player_rect.x - camera_x, player_rect.bottom - img_to_draw.get_height())
        screen.blit(img_to_draw, draw_pos)
    else:
        pygame.draw.rect(screen, (255, 0, 0), (player_rect.x - camera_x, player_rect.y, 60, 60))

# ==========================================
# 3. KASTEEL TEKENEN
# ==========================================
def draw_castle_system(screen, assets, castle_rect, flag_rect, camera_x, win_state, anim_progress, HEIGHT):
    if assets["castle"]:
        scale_factor = 1.5
        w = int(castle_rect.width * scale_factor)
        h = int(castle_rect.height * scale_factor)
        draw_y = castle_rect.bottom - h
        screen.blit(pygame.transform.scale(assets["castle"], (w, h)), (castle_rect.x - camera_x, draw_y))
    else:
        pygame.draw.rect(screen, (200, 50, 50), (castle_rect.x - camera_x, castle_rect.y, 120, 150))

    if win_state and assets["flag"]:
        flag_w = int(flag_rect.width * 2)
        flag_h = int(flag_rect.height * 0.7)
        img = pygame.transform.scale(assets["flag"], (flag_w, flag_h))
        
        start_y = HEIGHT + 50
        end_y = castle_rect.top - 50
        current_y = start_y + (end_y - start_y) * anim_progress
        pole_x = (castle_rect.x - camera_x) - 30
        
        pygame.draw.rect(screen, (100, 100, 100), (pole_x, current_y, 5, 300))
        screen.blit(img, (pole_x, current_y))