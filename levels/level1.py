import pygame
import sys
import math

# Zorg dat we shared.py kunnen vinden in de map erboven
sys.path.append("..") 
import shared 

def speel(SCREEN, pause_func=None):
    WIDTH, HEIGHT = SCREEN.get_size()
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont(None, 32)
    BIG_FONT = pygame.font.SysFont(None, 64)

    # 1. ASSETS LADEN
    ASSETS = shared.load_assets(WIDTH, HEIGHT)
    
    # Haal de specifieke plaatjes op
    platform_original = ASSETS.get("platform") 
    grond_original = ASSETS.get("ground")
    
    # Check of ze geladen zijn
    grond_img_loaded = (grond_original is not None)
    platform_img_loaded = (platform_original is not None)

    # KLEUREN
    SKY_BLUE = (135, 206, 235)
    GROUND_COLOR = (17, 184, 2)
    BLACK = (20, 20, 20)
    YELLOW = (255, 223, 0)
    RED = (220, 50, 50)

    # GAME VARIABELEN
    player = pygame.Rect(100, HEIGHT - 150, 60, 60)
    player_vel_y = 0
    speed = 5
    jump_power = -15
    gravity = 1
    
    on_ground = False
    game_over = False
    win = False
    camera_x = 0
    score = 0
    
    # Animatie vars
    direction = 1
    walk_frame = 0
    anim_timer = 0
    flag_anim_progress = 0.0

    # ==========================================
    # LEVEL DESIGN
    # ==========================================
    platforms = [
        pygame.Rect(0, HEIGHT - 70, 2500, 70),  # De grote vloer
        pygame.Rect(300, HEIGHT - 150, 120, 20),
        pygame.Rect(520, HEIGHT - 220, 120, 20),
        pygame.Rect(800, HEIGHT - 170, 120, 20),
        pygame.Rect(650, HEIGHT - 100, 80, 20),
        pygame.Rect(900, HEIGHT - 250, 100, 20),
    ]
    
    castle = pygame.Rect(1800, HEIGHT - 200, 120, 150)
    flag_rect = pygame.Rect(1750, HEIGHT - 250, 24, 200)

    coins = [
        pygame.Rect(660, HEIGHT - 140, 20, 20),
        pygame.Rect(850, HEIGHT - 330, 20, 20),
        pygame.Rect(990, HEIGHT - 290, 20, 20),
    ]

    enemies_def = [
        {"rect": pygame.Rect(450, HEIGHT - 100, 50, 40), "dir": -1},
        {"rect": pygame.Rect(750, HEIGHT - 100, 50, 40), "dir": 1},
        {"rect": pygame.Rect(1100, HEIGHT - 100, 50, 40), "dir": -1},
        {"rect": pygame.Rect(820, HEIGHT - 100, 50, 40), "dir": -1},
        {"rect": pygame.Rect(990, HEIGHT - 100, 50, 40), "dir": -1},
    ]
    
    enemies = []
    for e in enemies_def:
        enemies.append({"rect": e["rect"].copy(), "dir": e["dir"]})

    def reset_level():
        nonlocal player, player_vel_y, score, coins, enemies, win, game_over, flag_anim_progress, camera_x
        player.x = 100
        player.y = HEIGHT - 150
        player_vel_y = 0
        score = 0
        win = False
        game_over = False
        flag_anim_progress = 0.0
        camera_x = 0
        coins = [pygame.Rect(660, HEIGHT - 140, 20, 20), pygame.Rect(910, HEIGHT - 290, 20, 20), pygame.Rect(930, HEIGHT - 290, 20, 20)]
        enemies.clear()
        for e in enemies_def:
            enemies.append({"rect": e["rect"].copy(), "dir": e["dir"]})

    # ==========================================
    # GAME LOOP
    # ==========================================
    running = True
    while running:
        dt = CLOCK.tick(60)

        # Achtergrond
        if ASSETS["bg"]: SCREEN.blit(ASSETS["bg"], (0,0))
        else: SCREEN.fill(SKY_BLUE)

        # Inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pause_func and not (game_over or win):
                        if pause_func(SCREEN) == "MENU": return "MENU"
                    else: return "MENU"
                
                if event.key == pygame.K_UP and on_ground and not (win or game_over):
                    player_vel_y = jump_power
                
                if (event.key == pygame.K_r and win) or (event.key == pygame.K_RETURN and game_over):
                    reset_level()

        keys = pygame.key.get_pressed()

        if not (win or game_over):
            # Beweging
            is_moving = False
            if keys[pygame.K_LEFT]:
                player.x -= speed
                direction = -1
                is_moving = True
            if keys[pygame.K_RIGHT]:
                player.x += speed
                direction = 1
                is_moving = True
            
            if is_moving and on_ground:
                anim_timer += dt
                if anim_timer > 150:
                    walk_frame = 1 - walk_frame
                    anim_timer = 0
            else:
                walk_frame = 0

            # Fysica
            player_vel_y += gravity
            player.y += player_vel_y

            # Botsing Platformen
            on_ground = False
            for plat in platforms:
                if player.colliderect(plat) and player_vel_y >= 0:
                    if player.bottom <= plat.top + 20:
                        player.bottom = plat.top
                        player_vel_y = 0
                        on_ground = True

            # Vijanden
            for e in enemies[:]:
                e["rect"].x += e["dir"] * 2
                if e["rect"].x < 300: e["dir"] = 1
                elif e["rect"].x > 1900: e["dir"] = -1
                
                if player.colliderect(e["rect"]):
                    if player_vel_y > 0 and player.bottom < e["rect"].centery + 10:
                        enemies.remove(e)
                        player_vel_y = -10
                        score += 50
                    else:
                        game_over = True

            # Muntjes
            for c in coins[:]:
                if player.colliderect(c):
                    coins.remove(c)
                    score += 10

            if player.y > HEIGHT: game_over = True

            if player.colliderect(castle):
                win = True
                if ASSETS["win_sound"]:
                    try:
                        pygame.mixer.music.load(ASSETS["win_sound"])
                        pygame.mixer.music.play()
                    except: pass

            camera_x = player.x - WIDTH // 3
            if camera_x < 0: camera_x = 0

        # ================= TEKENEN =================
        
        if not game_over:
            
            # --- PLATFORMS VISUALS (CORRECTE TILING) ---
            for plat in platforms:
                draw_rect = (plat.x - camera_x, plat.y, plat.width, plat.height)
                is_main_ground = (plat.x == 0 and plat.width >= 1000)

                # 1. ZWEVENDE PLATFORMEN (TILING MET platform.jpg)
                if not is_main_ground and platform_img_loaded:
                    try:
                        # Bereken dimensies
                        orig_w, orig_h = platform_original.get_size()
                        tile_h = plat.height
                        # Behoud aspect ratio (verhouding) zodat hij niet uitrekt
                        tile_w = int(orig_w * (tile_h / orig_h)) if orig_h else tile_h
                        if tile_w <= 0: tile_w = 40

                        # Maak het kleine tegeltje
                        tile_img = pygame.transform.scale(platform_original, (tile_w, tile_h))

                        # Maak een tijdelijke surface precies ter grootte van het platform
                        # Dit zorgt ervoor dat plaatjes die over de rand gaan netjes worden afgesneden
                        plat_surface = pygame.Surface((plat.width, plat.height), pygame.SRCALPHA)
                        
                        # Vul de surface met tegeltjes
                        current_x = 0
                        while current_x < plat.width:
                            plat_surface.blit(tile_img, (current_x, 0))
                            current_x += tile_w

                        # Voeg schaduw toe aan de surface
                        shadow_h = max(4, int(plat.height / 3))
                        shadow_surf = pygame.Surface((plat.width, shadow_h), pygame.SRCALPHA)
                        for i in range(shadow_h):
                            alpha = int(100 * ((i + 1) / shadow_h))
                            pygame.draw.rect(shadow_surf, (0, 0, 0, alpha), (0, i, plat.width, 1))
                        plat_surface.blit(shadow_surf, (0, plat.height - shadow_h)) # Schaduw onderaan of randje
                        
                        # Teken het complete platform op het scherm
                        SCREEN.blit(plat_surface, (plat.x - camera_x, plat.y))

                    except Exception as e:
                        # Fallback
                        pygame.draw.rect(SCREEN, GROUND_COLOR, draw_rect)

                # 2. DE GROND (Level vloer) - OOK TILING
                elif is_main_ground and grond_img_loaded:
                    try:
                        orig_w, orig_h = grond_original.get_size()
                        tile_h = plat.height
                        tile_w = int(orig_w * (tile_h / orig_h)) if orig_h else tile_h
                        if tile_w <= 0: tile_w = 64 
                        
                        tile_img = pygame.transform.scale(grond_original, (tile_w, tile_h))

                        # Optimalisatie: teken alleen wat in beeld is direct op scherm
                        # (Grond is te groot voor een tijdelijke Surface van 2500px elke frame)
                        start_x = max(0, camera_x - plat.x)
                        end_x = min(plat.width, start_x + WIDTH + tile_w)
                        
                        # Zorg dat we op een veelvoud van tile_w beginnen voor naadloze aansluiting
                        offset = start_x % tile_w
                        draw_cursor = start_x - offset

                        while draw_cursor < end_x:
                            blit_x = plat.x + draw_cursor - camera_x
                            SCREEN.blit(tile_img, (blit_x, plat.y))
                            draw_cursor += tile_w

                        # Schaduwrandje
                        shadow_h = max(4, int(plat.height / 3))
                        shadow_surf = pygame.Surface((plat.width, shadow_h), pygame.SRCALPHA)
                        for i in range(shadow_h):
                            alpha = int(100 * ((i + 1) / shadow_h))
                            pygame.draw.rect(shadow_surf, (0, 0, 0, alpha), (0, i, plat.width, 1))
                        SCREEN.blit(shadow_surf, (plat.x - camera_x, plat.y))

                    except Exception:
                        pygame.draw.rect(SCREEN, GROUND_COLOR, draw_rect)
                
                # 3. FALLBACK
                else:
                    pygame.draw.rect(SCREEN, GROUND_COLOR, draw_rect)
            # --- EINDE PLATFORMS VISUALS ---


            # Kasteel & Vlag
            if win: flag_anim_progress = min(flag_anim_progress + 0.01, 1.0)
            shared.draw_castle_system(SCREEN, ASSETS, castle, flag_rect, camera_x, win, flag_anim_progress, HEIGHT)

            # Muntjes Animatie (Originele kwaliteit, niet uitvergroot)
            for c in coins:
                if ASSETS["coin"]:
                    # 1. Animatie (op en neer zweven)
                    t = pygame.time.get_ticks() / 1000.0
                    freq = 0.7
                    amp = 5
                    bob = math.sin(t * 2 * math.pi * freq) * amp
                    
                    # 2. Gebruik de ORIGINELE afbeelding (geen scale/resize)
                    img = ASSETS["coin"]
                    
                    
                    img_w = img.get_width()
                    img_h = img.get_height()
                    
                    center_x = (c.x - camera_x) + (c.width // 2)
                    center_y = c.y + (c.height // 2)
                    
                    draw_x = center_x - (img_w // 2)
                    draw_y = center_y - (img_h // 2) + bob
                    
                    SCREEN.blit(img, (draw_x, draw_y))
                else:
                    # Fallback
                    pygame.draw.rect(SCREEN, YELLOW, (c.x - camera_x, c.y, c.width, c.height))


            # Vijanden
            for e in enemies:
                draw_x = e["rect"].x - camera_x
                if ASSETS["enemy"]:
                    img = ASSETS["enemy"]
                    if e["dir"] == 1: img = pygame.transform.flip(img, True, False)
                    SCREEN.blit(img, (draw_x - 5, e["rect"].bottom - img.get_height()))
                else:
                    pygame.draw.rect(SCREEN, RED, (draw_x, e["rect"].y, e["rect"].width, e["rect"].height))

            # Speler
            shared.draw_player(SCREEN, ASSETS, player, player_vel_y, on_ground, direction, walk_frame, camera_x)

            # Score UI
            score_text = FONT.render(f"Score: {score}", True, BLACK)
            SCREEN.blit(score_text, (20, 20))
            
            if win and flag_anim_progress >= 1.0:
                SCREEN.blit(BIG_FONT.render("LEVEL GEHAALD!", True, YELLOW), (WIDTH//2 - 180, HEIGHT//2))
                SCREEN.blit(FONT.render("Druk op R voor menu/replay", True, BLACK), (WIDTH//2 - 140, HEIGHT//2 + 50))

        else: 
            SCREEN.fill(BLACK)
            text1 = BIG_FONT.render("YOU DIED", True, RED)
            text2 = FONT.render("Press Enter to restart", True, (135, 206, 235))
            SCREEN.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 30))
            SCREEN.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 30))

        pygame.display.update()