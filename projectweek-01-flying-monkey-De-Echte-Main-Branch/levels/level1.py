import pygame
import sys
import math
try:
    from main import sfx_on
except ImportError:
    sfx_on = True

# Imports van entities
from entities.player import Player
from entities.castle import Castle
# NIEUW: Importeer de vijand
from entities.enemies import PatrolEnemy

def speel(SCREEN, pause_func=None, assets=None, sfx_on=True):
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
    # Zorg dat de onderkant van het kasteel gelijk is aan de grond (HEIGHT - 70)
    castle_height = 150
    ground_y = HEIGHT - 70
    castle = Castle(4000, ground_y - castle_height, 120, castle_height, assets, sfx_on)
    
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
    
    # Snake height is 60, so lowest platform must be at least 60px above ground
    snake_height = 60
    player_height = 80
    ground_thickness = 70
    min_platform_y = HEIGHT - ground_thickness - snake_height - 10  # 10px buffer
    max_platform_y = 0 + player_height + 10  # Highest platform cannot be higher than this
    # Redesigned platforms: more verticality, longer level
    # Platforms: no lower than enemy height, no higher than top - player height
    min_y = HEIGHT - ground_thickness - snake_height - 10
    max_y = player_height + 10
    platforms = [
        pygame.Rect(0, HEIGHT - ground_thickness, 4200, ground_thickness),  # ground (extended)
        pygame.Rect(300, HEIGHT - 160, 120, 20),
        pygame.Rect(600, HEIGHT - 220, 120, 20),
        pygame.Rect(900, HEIGHT - 180, 120, 20),
        pygame.Rect(1200, HEIGHT - 140, 120, 20),
        pygame.Rect(1500, HEIGHT - 200, 120, 20),
        pygame.Rect(1800, HEIGHT - 170, 120, 20),
        pygame.Rect(2100, HEIGHT - 130, 120, 20),
        pygame.Rect(2400, HEIGHT - 190, 120, 20),
        pygame.Rect(2700, HEIGHT - 160, 120, 20),
        pygame.Rect(3000, HEIGHT - 120, 120, 20),
        pygame.Rect(3300, HEIGHT - 180, 120, 20),
        pygame.Rect(3600, HEIGHT - 150, 120, 20),
        pygame.Rect(3800, HEIGHT - 210, 120, 20),
        pygame.Rect(3950, HEIGHT - 170, 120, 20),
    ]
    # Place 12 bananas directly above the first 12 platforms so they are always visible and collectible
    import random
    # Randomize the location of bananas slightly above each platform
    coins = []
    for plat in platforms[1:13]:
        x_offset = random.randint(-20, 20)
        y_offset = random.randint(-10, 10)
        coins.append(pygame.Rect(plat.x + plat.width // 2 - 10 + x_offset, plat.y - 30 + y_offset, 20, 20))

    # NIEUW: Definitie van vijanden (posities)
    # We slaan alleen de startposities op om te kunnen resetten
    enemies_start_pos = [
        {"x": 450, "dir": -1},
        {"x": 750, "dir": 1},
        {"x": 1100, "dir": -1},
        {"x": 820, "dir": -1},
        {"x": 990, "dir": -1},
        {"x": 1350, "dir": 1},
        {"x": 1600, "dir": -1},
        {"x": 2000, "dir": 1},
        {"x": 2500, "dir": -1},
        {"x": 3000, "dir": 1},
        {"x": 3500, "dir": -1},
        {"x": 3900, "dir": 1},
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
        # Do not override coins here
        # coins = [pygame.Rect(660, HEIGHT - 140, 20, 20), pygame.Rect(910, HEIGHT - 290, 20, 20), pygame.Rect(930, HEIGHT - 290, 20, 20)]
        
        # NIEUW: Vijanden opnieuw aanmaken als objecten
        enemies.clear()
        for e in enemies_start_pos:
            # PatrolEnemy(x, y, start_dir, min_patrol, max_patrol, asset_manager)
            new_enemy = PatrolEnemy(e["x"], HEIGHT - 100, e["dir"], 300, 1900, assets)
            enemies.append(new_enemy)

    # Initialiseer level de eerste keer
    reset_level()

    # Move platform generation to before the game loop so platforms are visible and consistent
    # Add more platforms with varied heights, all staying low (bottom half of screen)
    import random
    flag_x = 4000
    min_low_y = HEIGHT // 2
    max_low_y = HEIGHT - ground_thickness - snake_height - 10
    x = platforms[-1].x + 100
    while x < flag_x - 50:
        for _ in range(random.randint(1, 2)):
            plat_y = random.randint(min_low_y, max_low_y)
            new_plat = pygame.Rect(x, plat_y, 100, 20)
            platforms.append(new_plat)
            # Add 3 bananas per new platform
            for offset in [10, 40, 70]:
                coins.append(pygame.Rect(new_plat.x + offset, new_plat.y - 30, 20, 20))
        x += random.randint(80, 180)

    # Remove previous end platforms, add 3 new platforms closer to others for easier jumping
    # Remove platforms near flag pole if present
    platforms = [p for p in platforms if p.x < 3800 or p.x > 4100]
    # Add 3 new platforms spaced between existing ones
    platforms.append(pygame.Rect(800, HEIGHT - 200, 120, 20))
    platforms.append(pygame.Rect(1600, HEIGHT - 180, 120, 20))
    platforms.append(pygame.Rect(2500, HEIGHT - 170, 120, 20))
    # Sort platforms by x for logical order
    platforms.sort(key=lambda p: p.x)

    # GAME LOOP
    running = True
    while running:
        WIDTH, HEIGHT = SCREEN.get_size()
        dt = CLOCK.tick(60)

        # Always update castle's sfx_on to current value
        castle.sfx_on = sfx_on

        # Always clear the full screen
        bg = assets.get("bg")
        if bg:
            bg_scaled = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            SCREEN.blit(bg_scaled, (0, 0))
        else:
            SCREEN.fill(SKY_BLUE)

        pause_requested = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pause_func and not (game_over or win):
                        pause_requested = True
                    else: return "MENU"
                if event.key == pygame.K_UP and on_ground and not (win or game_over):
                    player_vel_y = jump_power
                if win and event.key == pygame.K_RETURN:
                    from levels import level2
                    return level2.speel(SCREEN, pause_func, assets, sfx_on)
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
            else:
                walk_frame = 0

            player.update_visuals(player_vel_y, on_ground, direction, walk_frame, is_moving)
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
                enemy.update()
                if player.rect.colliderect(enemy.rect):
                    # Spring op hoofd
                    if player_vel_y > 0 and player.rect.bottom < enemy.rect.centery + 10:
                        enemies.remove(enemy)
                        player_vel_y = -10
                        score += 50
                        # Speel oof sound alleen als sfx aan staat
                        oof_sound = assets.get("oof_sound")
                        if oof_sound and sfx_on:
                            try:
                                pygame.mixer.Sound(oof_sound).play()
                            except:
                                pygame.mixer.music.load(oof_sound)
                                pygame.mixer.music.play()
                    else:
                        game_over = True

            for c in coins[:]:
                if player.rect.colliderect(c):
                    coins.remove(c)
                    score += 10
                    # Speel coin sound alleen als sfx aan staat
                    coin_sound = assets.get("coin_sound")
                    if coin_sound and sfx_on:
                        try:
                            pygame.mixer.Sound(coin_sound).play()
                        except:
                            pygame.mixer.music.load(coin_sound)
                            pygame.mixer.music.play()

            if player.rect.y > HEIGHT: game_over = True

            if player.rect.colliderect(castle.rect):
                win = True
                castle.win_state = True
                # Win sound is now handled in Castle.update_animation() and respects sfx_on

            # Camera follows player horizontally only
            camera_x = player.rect.x - WIDTH // 3
            if camera_x < 0: camera_x = 0
        else:
            camera_y = 0
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
                # Show 'You Win' even higher on the screen
                win_text = BIG_FONT.render("You Win", True, YELLOW)
                SCREEN.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 200))
                next_text = FONT.render("Press ENTER for Level 2", True, BLACK)
                SCREEN.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 - 140))

        else: 
            SCREEN.fill(BLACK)
            text1 = BIG_FONT.render("YOU DIED", True, RED)
            text2 = FONT.render("Press Enter to restart", True, (135, 206, 235))
            SCREEN.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 30))
            SCREEN.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 30))

        pygame.display.update()
        # If pause was requested, capture the frame now and show pause menu
        if pause_requested:
            frozen_bg = SCREEN.copy()
            if pause_func(SCREEN, frozen_bg) == "MENU": return "MENU"