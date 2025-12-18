import pygame
import sys
import math

# Imports van entities
from entities.player import Player
from entities.castle import Castle
# NIEUW: Importeer de vijand
from entities.enemies import PatrolEnemy

def speel(SCREEN, pause_func=None, assets=None):
    WIDTH, HEIGHT = SCREEN.get_size()
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont(None, 32)
    BIG_FONT = pygame.font.SysFont(None, 64)

    # Assets laden
    platform_original = assets.get("platform") 
    grond_original = assets.get("ground")
    grond_img_loaded = (grond_original is not None)
    platform_img_loaded = (platform_original is not None)

    # Kleuren
    SKY_BLUE = (135, 206, 235)
    GROUND_COLOR = (17, 184, 2)
    BLACK = (20, 20, 20)
    YELLOW = (255, 223, 0)
    RED = (220, 50, 50)

    # Variabelen
    player = Player(100, HEIGHT - 150, assets)
    castle = Castle(1800, HEIGHT - 200, 120, 150, assets)
    
    player_vel_y = 0
    speed = 5
    jump_power = -15
    gravity = 1
    on_ground = False
    game_over = False
    win = False
    camera_x = 0
    score = 0
    direction = 1
    walk_frame = 0
    anim_timer = 0
    
    # Platforms
    platforms = [
        pygame.Rect(0, HEIGHT - 70, 2500, 70),
        pygame.Rect(300, HEIGHT - 150, 120, 20),
        pygame.Rect(520, HEIGHT - 220, 120, 20),
        pygame.Rect(800, HEIGHT - 170, 120, 20),
        pygame.Rect(650, HEIGHT - 100, 80, 20),
        pygame.Rect(900, HEIGHT - 250, 100, 20),
    ]

    coins = [
        pygame.Rect(660, HEIGHT - 140, 20, 20),
        pygame.Rect(850, HEIGHT - 330, 20, 20),
        pygame.Rect(990, HEIGHT - 290, 20, 20),
    ]

    # NIEUW: Definitie van vijanden (posities)
    # We slaan alleen de startposities op om te kunnen resetten
    enemies_start_pos = [
        {"x": 450, "dir": -1},
        {"x": 750, "dir": 1},
        {"x": 1100, "dir": -1},
        {"x": 820, "dir": -1},
        {"x": 990, "dir": -1},
    ]
    
    enemies = []

    def reset_level():
        nonlocal player, player_vel_y, score, coins, enemies, win, game_over, camera_x
        player.rect.x = 100
        player.rect.y = HEIGHT - 150
        player_vel_y = 0
        score = 0
        win = False
        castle.win_state = False
        castle.anim_progress = 0.0
        game_over = False
        camera_x = 0
        coins = [pygame.Rect(660, HEIGHT - 140, 20, 20), pygame.Rect(910, HEIGHT - 290, 20, 20), pygame.Rect(930, HEIGHT - 290, 20, 20)]
        
        # NIEUW: Vijanden opnieuw aanmaken als objecten
        enemies.clear()
        for e in enemies_start_pos:
            # PatrolEnemy(x, y, start_dir, min_patrol, max_patrol, asset_manager)
            new_enemy = PatrolEnemy(e["x"], HEIGHT - 100, e["dir"], 300, 1900, assets)
            enemies.append(new_enemy)

    # Initialiseer level de eerste keer
    reset_level()

    # GAME LOOP
    running = True
    while running:
        dt = CLOCK.tick(60)

        if assets.get("bg"): SCREEN.blit(assets.get("bg"), (0,0))
        else: SCREEN.fill(SKY_BLUE)

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
                player.rect.x -= speed
                direction = -1
                is_moving = True
            if keys[pygame.K_RIGHT]:
                player.rect.x += speed
                direction = 1
                is_moving = True
            
            if is_moving and on_ground:
                anim_timer += dt
                if anim_timer > 150:
                    walk_frame = 1 - walk_frame
                    anim_timer = 0
            else: walk_frame = 0

            player.update_visuals(player_vel_y, on_ground, direction, walk_frame)
            player_vel_y += gravity
            player.rect.y += player_vel_y

            # Botsing Platform
            on_ground = False
            for plat in platforms:
                if player.rect.colliderect(plat) and player_vel_y >= 0:
                    if player.rect.bottom <= plat.top + 20:
                        player.rect.bottom = plat.top
                        player_vel_y = 0
                        on_ground = True

            # NIEUW: VIJANDEN UPDATE LOGICA
            for enemy in enemies[:]:
                # 1. Update beweging (zit nu in de class!)
                enemy.update()
                
                # 2. Check botsing met speler
                if player.rect.colliderect(enemy.rect):
                    # Spring op hoofd
                    if player_vel_y > 0 and player.rect.bottom < enemy.rect.centery + 10:
                        enemies.remove(enemy)
                        player_vel_y = -10
                        score += 50
                    else:
                        game_over = True

            # Muntjes
            for c in coins[:]:
                if player.rect.colliderect(c):
                    coins.remove(c)
                    score += 10

            if player.rect.y > HEIGHT: game_over = True

            if player.rect.colliderect(castle.rect):
                win = True
                castle.win_state = True
                if assets.get("win_sound") and castle.anim_progress == 0:
                    try:
                        pygame.mixer.music.load(assets.get("win_sound"))
                        pygame.mixer.music.play()
                    except: pass

            camera_x = player.rect.x - WIDTH // 3
            if camera_x < 0: camera_x = 0
        
        castle.update_animation()

        # ================= TEKENEN =================
        if not game_over:
            # Platforms tekenen (ingekort voor leesbaarheid, zelfde logica)
            for plat in platforms:
                draw_rect = (plat.x - camera_x, plat.y, plat.width, plat.height)
                is_main_ground = (plat.x == 0 and plat.width >= 1000)

                if not is_main_ground and platform_img_loaded:
                    try:
                        orig_w, orig_h = platform_original.get_size()
                        tile_h = plat.height
                        tile_w = int(orig_w * (tile_h / orig_h)) if orig_h else tile_h
                        if tile_w <= 0: tile_w = 40
                        tile_img = pygame.transform.scale(platform_original, (tile_w, tile_h))
                        plat_surface = pygame.Surface((plat.width, plat.height), pygame.SRCALPHA)
                        current_x = 0
                        while current_x < plat.width:
                            plat_surface.blit(tile_img, (current_x, 0))
                            current_x += tile_w
                        SCREEN.blit(plat_surface, (plat.x - camera_x, plat.y))
                    except: pygame.draw.rect(SCREEN, GROUND_COLOR, draw_rect)
                elif is_main_ground and grond_img_loaded:
                    try:
                        orig_w, orig_h = grond_original.get_size()
                        tile_h = plat.height
                        tile_w = int(orig_w * (tile_h / orig_h)) if orig_h else tile_h
                        if tile_w <= 0: tile_w = 64 
                        tile_img = pygame.transform.scale(grond_original, (tile_w, tile_h))
                        start_x = max(0, camera_x - plat.x)
                        end_x = min(plat.width, start_x + WIDTH + tile_w)
                        offset = start_x % tile_w
                        draw_cursor = start_x - offset
                        while draw_cursor < end_x:
                            blit_x = plat.x + draw_cursor - camera_x
                            SCREEN.blit(tile_img, (blit_x, plat.y))
                            draw_cursor += tile_w
                    except: pygame.draw.rect(SCREEN, GROUND_COLOR, draw_rect)
                else:
                    pygame.draw.rect(SCREEN, GROUND_COLOR, draw_rect)

            castle.draw(SCREEN, camera_x, HEIGHT)

            for c in coins:
                if assets.get("coin"):
                    t = pygame.time.get_ticks() / 1000.0
                    bob = math.sin(t * 2 * math.pi * 0.7) * 5
                    img = assets.get("coin")
                    draw_x = (c.x - camera_x) + (c.width // 2) - (img.get_width() // 2)
                    draw_y = c.y + (c.height // 2) - (img.get_height() // 2) + bob
                    SCREEN.blit(img, (draw_x, draw_y))
                else:
                    pygame.draw.rect(SCREEN, YELLOW, (c.x - camera_x, c.y, c.width, c.height))

            # NIEUW: VIJANDEN TEKENEN
            # Dit is nu super simpel omdat de class zelf weet hoe hij getekend wordt
            for enemy in enemies:
                enemy.draw(SCREEN, camera_x)

            player.draw(SCREEN, camera_x)

            score_text = FONT.render(f"Score: {score}", True, BLACK)
            SCREEN.blit(score_text, (20, 20))
            
            if win and castle.anim_progress >= 1.0:
                SCREEN.blit(BIG_FONT.render("LEVEL GEHAALD!", True, YELLOW), (WIDTH//2 - 180, HEIGHT//2))
                SCREEN.blit(FONT.render("Druk op R voor menu/replay", True, BLACK), (WIDTH//2 - 140, HEIGHT//2 + 50))

        else: 
            SCREEN.fill(BLACK)
            text1 = BIG_FONT.render("YOU DIED", True, RED)
            text2 = FONT.render("Press Enter to restart", True, (135, 206, 235))
            SCREEN.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 30))
            SCREEN.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 30))

        pygame.display.update()