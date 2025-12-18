import pygame
import sys
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
    # LEVEL DESIGN (SPECIFIEK VOOR LEVEL 1)
    # ==========================================
    # Dit zijn de platforms uit jouw originele code
    platforms = [
        pygame.Rect(0, HEIGHT - 70, 2000, 70),
        pygame.Rect(300, HEIGHT - 150, 120, 20),
        pygame.Rect(520, HEIGHT - 220, 120, 20),
        pygame.Rect(800, HEIGHT - 170, 120, 20),
        pygame.Rect(650, HEIGHT - 100, 80, 20),
        pygame.Rect(900, HEIGHT - 250, 100, 20),
    ]
    
    # Kasteel en Vlag
    castle = pygame.Rect(1800, HEIGHT - 200, 120, 150)
    flag_rect = pygame.Rect(1750, HEIGHT - 250, 24, 200)

    # Muntjes
    coins = [
        pygame.Rect(660, HEIGHT - 140, 20, 20),
        pygame.Rect(910, HEIGHT - 290, 20, 20),
        pygame.Rect(930, HEIGHT - 290, 20, 20),
    ]

    # Vijanden Definitie (Paddenstoelen/Slangen)
    # We slaan ze op als dictionary zodat we richting (dir) kunnen onthouden
    enemies_def = [
        {"rect": pygame.Rect(450, HEIGHT - 100, 50, 40), "dir": -1},
        {"rect": pygame.Rect(750, HEIGHT - 100, 50, 40), "dir": 1},
        {"rect": pygame.Rect(1100, HEIGHT - 100, 50, 40), "dir": -1},
        {"rect": pygame.Rect(820, HEIGHT - 100, 50, 40), "dir": -1},
        {"rect": pygame.Rect(990, HEIGHT - 100, 50, 40), "dir": -1},
    ]
    
    # Maak een kopie voor de live game
    enemies = []
    for e in enemies_def:
        enemies.append({"rect": e["rect"].copy(), "dir": e["dir"]})

    # Functie om alles terug te zetten bij restart
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
        # Reset coins en enemies
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
                
                # Springen
                if event.key == pygame.K_UP and on_ground and not (win or game_over):
                    player_vel_y = jump_power
                
                # Restart
                if (event.key == pygame.K_r and win) or (event.key == pygame.K_RETURN and game_over):
                    reset_level()

        keys = pygame.key.get_pressed()

        if not (win or game_over):
            # 1. SPELER BEWEGING
            is_moving = False
            if keys[pygame.K_LEFT]:
                player.x -= speed
                direction = -1
                is_moving = True
            if keys[pygame.K_RIGHT]:
                player.x += speed
                direction = 1
                is_moving = True
            
            # Animatie timer
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

            # 2. VIJANDEN LOGICA (Heen en weer lopen)
            for e in enemies[:]:
                # Bewegen
                e["rect"].x += e["dir"] * 2
                
                # Omkeren bij grenzen (zoals in jouw oude code)
                if e["rect"].x < 300: e["dir"] = 1
                elif e["rect"].x > 1900: e["dir"] = -1
                
                # Botsing met Speler
                if player.colliderect(e["rect"]):
                    # Als speler van boven komt (op hoofd springen)
                    if player_vel_y > 0 and player.bottom < e["rect"].centery + 10:
                        enemies.remove(e)
                        player_vel_y = -10 # Stuiter omhoog
                        score += 50
                    else:
                        game_over = True

            # 3. MUNTJES LOGICA
            for c in coins[:]:
                if player.colliderect(c):
                    coins.remove(c)
                    score += 10

            # Dood bij vallen
            if player.y > HEIGHT: game_over = True

            # Win check
            if player.colliderect(castle):
                win = True
                if ASSETS["win_sound"]:
                    try:
                        pygame.mixer.music.load(ASSETS["win_sound"])
                        pygame.mixer.music.play()
                    except: pass

            # Camera update
            camera_x = player.x - WIDTH // 3
            if camera_x < 0: camera_x = 0

        # ================= TEKENEN =================
        
        # 1. ALLES TEKENEN (Zolang we niet dood zijn)
        if not game_over:
            # Platforms
            for plat in platforms:
                if ASSETS["ground"]:
                    img = pygame.transform.scale(ASSETS["ground"], (plat.width, plat.height))
                    SCREEN.blit(img, (plat.x - camera_x, plat.y))
                else:
                    pygame.draw.rect(SCREEN, GROUND_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))

            # Kasteel & Vlag
            if win: flag_anim_progress = min(flag_anim_progress + 0.01, 1.0)
            shared.draw_castle_system(SCREEN, ASSETS, castle, flag_rect, camera_x, win, flag_anim_progress, HEIGHT)

            # Muntjes
            for c in coins:
                if ASSETS["coin"]: SCREEN.blit(ASSETS["coin"], (c.x - camera_x, c.y))
                else: pygame.draw.rect(SCREEN, YELLOW, (c.x - camera_x, c.y, c.width, c.height))

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
            
            # Win Scherm overlay (als je gewonnen hebt blijven we de wereld zien)
            if win and flag_anim_progress >= 1.0:
                SCREEN.blit(BIG_FONT.render("LEVEL GEHAALD!", True, YELLOW), (WIDTH//2 - 180, HEIGHT//2))
                SCREEN.blit(FONT.render("Druk op R voor menu/replay", True, BLACK), (WIDTH//2 - 140, HEIGHT//2 + 50))

        # 2. GAME OVER SCHERM (Zwart scherm zoals origineel)
        else: # if game_over == True
            SCREEN.fill(BLACK) # Maak alles zwart
            
            # Tekst centreren
            text1 = BIG_FONT.render("YOU DIED", True, RED)
            text2 = FONT.render("Press Enter to restart", True, (135, 206, 235)) # Sky Blue
            
            SCREEN.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 30))
            SCREEN.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 30))

        pygame.display.update()