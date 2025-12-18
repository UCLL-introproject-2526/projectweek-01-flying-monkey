import pygame
import math
from entities import AssetLoader, Player, Enemy, Coin

def speel(SCREEN, pause_func=None):
    assets = AssetLoader()
    width, height = SCREEN.get_size()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 64)

    # Colors
    sky_blue = (135, 206, 235)
    ground_color = (17, 184, 2)
    red = (220, 50, 50)
    black = (20, 20, 20)
    white = (255, 255, 255)
    gray = (160, 160, 160)
    yellow = (255, 223, 0)
    green = (0, 120, 0)

    # Game state
    camera_x = 0
    win = False
    game_over = False
    score = 0

    # Platforms
    platforms = [
        pygame.Rect(0, height - 70, 4000, 70),
        pygame.Rect(300, height - 150, 120, 20),
        pygame.Rect(520, height - 220, 120, 20),
        pygame.Rect(800, height - 170, 120, 20),
        pygame.Rect(650, height - 100, 80, 20),
        pygame.Rect(900, height - 250, 100, 20),
    ]

    # Castle and flag
    castle = pygame.Rect(1800, height - 200, 120, 150)
    flag = pygame.Rect(1750, height - 250, 24, 200)

    # Coins
    coins = [
        Coin(pygame.Rect(660, height - 140, 20, 20)),
        Coin(pygame.Rect(910, height - 290, 20, 20)),
        Coin(pygame.Rect(930, height - 290, 20, 20)),
    ]

    # Enemies
    enemies = [
        Enemy(pygame.Rect(450, height - 100, 50, 40), -1, assets),
        Enemy(pygame.Rect(750, height - 100, 50, 40), 1, assets),
        Enemy(pygame.Rect(1100, height - 100, 50, 40), -1, assets),
        Enemy(pygame.Rect(820, height - 100, 50, 40), -1, assets),
        Enemy(pygame.Rect(990, height - 100, 50, 40), -1, assets),
    ]

    # Player
    player = Player(100, height - 100, assets)

    # Flag animation
    flag_animating = False
    flag_anim_time = 0.0
    flag_anim_duration = 4.0
    flag_anim_done = False

    def reposition_entities():
        nonlocal player, castle, enemies
        ground_plat = next((p for p in platforms if p.x == 0 and p.width >= 1000), platforms[0])
        player.rect.y = ground_plat.top - player.rect.height
        castle.y = ground_plat.top - castle.height
        for e in enemies:
            e.rect.y = ground_plat.top - e.rect.height

    # Reposition
    reposition_entities()

    def reset_game():
        nonlocal player, score, coins, enemies, win, camera_x, game_over, flag_animating, flag_anim_time, flag_anim_done
        player.rect.x = 100
        ground_plat = next((p for p in platforms if p.x == 0 and p.width >= 1000), platforms[0])
        player.rect.y = ground_plat.top - player.rect.height
        player.vel_y = 0
        score = 0
        camera_x = 0
        win = False
        game_over = False
        flag_animating = False
        flag_anim_time = 0.0
        flag_anim_done = False
        player.on_ground = False
        coins = [
            Coin(pygame.Rect(660, height - 140, 20, 20)),
            Coin(pygame.Rect(910, height - 290, 20, 20)),
            Coin(pygame.Rect(930, height - 290, 20, 20)),
        ]
        enemies = [
            Enemy(pygame.Rect(450, height - 100, 50, 40), -1, assets),
            Enemy(pygame.Rect(750, height - 100, 50, 40), 1, assets),
            Enemy(pygame.Rect(1100, height - 100, 50, 40), -1, assets),
            Enemy(pygame.Rect(820, height - 100, 50, 40), -1, assets),
            Enemy(pygame.Rect(990, height - 100, 50, 40), -1, assets),
        ]
        reposition_entities()

    def move_enemies_func():
        for e in enemies:
            e.move()

    def check_enemy_collisions_func():
        nonlocal player, game_over
        for e in enemies[:]:
            if player.rect.colliderect(e.rect):
                if player.vel_y > 0 and player.rect.bottom < e.rect.centery:
                    enemies.remove(e)
                    player.vel_y = -10
                    if assets.enemy_die_sound:
                        assets.enemy_die_sound.play()
                else:
                    game_over = True

    def check_coin_collisions_func():
        nonlocal score
        for c in coins[:]:
            if player.rect.colliderect(c.rect):
                coins.remove(c)
                score += 1
                if assets.coin_sound:
                    assets.coin_sound.play()

    def draw_world_func():
        # Background
        if assets.bg_img:
            SCREEN.blit(assets.bg_img, (0, 0))
        else:
            SCREEN.fill(sky_blue)

        # Platforms
        for plat in platforms:
            draw_rect = (plat.x - camera_x, plat.y, plat.width, plat.height)
            is_main_ground = (plat.x == 0 and plat.width >= 1000)
            if not is_main_ground and assets.wood_img:
                # Simplified wood tiling
                orig_w, orig_h = assets.wood_img.get_size()
                tile_h = plat.height
                tile_w = int(orig_w * (tile_h / orig_h)) if orig_h else tile_h
                tile_img = pygame.transform.scale(assets.wood_img, (tile_w, tile_h))
                x = 0
                while x < plat.width:
                    blit_x = plat.x + x - camera_x
                    SCREEN.blit(tile_img, (blit_x, plat.y))
                    x += tile_w
            elif assets.ground_img:
                # Simplified ground tiling
                orig_w, orig_h = assets.ground_img.get_size()
                tile_h = plat.height
                tile_w = int(orig_w * (tile_h / orig_h)) if orig_h else tile_h
                tile_img = pygame.transform.scale(assets.ground_img, (tile_w, tile_h))
                x = 0
                while x < plat.width:
                    blit_x = plat.x + x - camera_x
                    SCREEN.blit(tile_img, (blit_x, plat.y))
                    x += tile_w
            else:
                pygame.draw.rect(SCREEN, ground_color, draw_rect)

        # Coins
        for c in coins:
            c.draw(SCREEN, camera_x, assets)

        # Castle
        castle_draw_x = castle.x - camera_x
        if assets.castle_img:
            scale = 1.5
            scale_w = int(castle.width * scale)
            scale_h = int(castle.height * scale)
            castle_draw_y = castle.y - (scale_h - castle.height)
            castle_img = pygame.transform.scale(assets.castle_img, (scale_w, scale_h))
            SCREEN.blit(castle_img, (castle_draw_x, castle_draw_y))
        else:
            pygame.draw.rect(SCREEN, red, (castle_draw_x, castle.y, castle.width, castle.height))

        # Flag (simplified)
        if flag_anim_done:
            flag_draw_x = flag.x - camera_x
            if assets.flag_img:
                flag_w = int(flag.width * 1.8)
                flag_h = int(flag.height * 0.9)
                flag_img = pygame.transform.scale(assets.flag_img, (flag_w, flag_h))
                pole_x = flag_draw_x - 4 - 4
                pygame.draw.rect(SCREEN, gray, (pole_x, int(flag.y), 4, flag_h))
                SCREEN.blit(flag_img, (flag_draw_x, int(flag.y)))
            else:
                pole_x = flag_draw_x - 4 - 4
                pygame.draw.rect(SCREEN, gray, (pole_x, int(flag.y), 4, flag.height))
                pygame.draw.rect(SCREEN, gray, (flag_draw_x, flag.y, flag.width, flag.height))

    def draw_enemies_func():
        for e in enemies:
            e.draw(SCREEN, camera_x)

    # Main loop
    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if win:
                        return "MENU"
                    else:
                        if pause_func:
                            res = pause_func(SCREEN)
                            if res == "MENU":
                                return "MENU"
                if event.key == pygame.K_r and win:
                    reset_game()
                if event.key == pygame.K_RETURN and game_over:
                    reset_game()
                if event.key == pygame.K_UP and player.on_ground and not win and not game_over:
                    player.vel_y = player.jump_power

        keys = pygame.key.get_pressed()

        if not win and not game_over:
            player.move(keys, platforms)
            move_enemies_func()
            check_enemy_collisions_func()
            check_coin_collisions_func()

            dt_ms = clock.get_time()
            player.update_animation(dt_ms, keys)

            if player.rect.colliderect(castle) and player.rect.x >= castle.x - 10 and player.rect.bottom >= castle.top - 5:
                win = True
                if assets.win_sound:
                    assets.win_sound.play()
                if assets.flag_img:
                    flag_animating = True
                    flag_anim_time = 0.0
                    flag_anim_done = False

            if not win:
                camera_x = max(0, player.rect.x - width // 3)

            draw_world_func()
            draw_enemies_func()
            player.draw(SCREEN, camera_x)
            SCREEN.blit(font.render(f"Score: {score}", True, black), (20, 20))

        elif game_over:
            if assets.bg_img:
                SCREEN.blit(assets.bg_img, (0, 0))
            else:
                SCREEN.fill(sky_blue)
            text = big_font.render("YOU DIED", True, red)
            restart_text = font.render("Press Enter to restart", True, black)
            SCREEN.blit(text, (width//2 - text.get_width()//2, height//2 - 30))
            SCREEN.blit(restart_text, (width//2 - restart_text.get_width()//2, height//2 + 30))

        else:  # win
            if flag_animating:
                dt = clock.get_time() / 1000.0
                flag_anim_time = min(flag_anim_time + dt, flag_anim_duration)
                progress = flag_anim_time / flag_anim_duration

                draw_world_func()
                draw_enemies_func()
                player.draw(SCREEN, camera_x)
                SCREEN.blit(font.render(f"Score: {score}", True, black), (20, 20))

                # Simplified flag animation
                if progress >= 1.0:
                    flag_animating = False
                    flag_anim_done = True
            else:
                if assets.bg_img:
                    SCREEN.blit(assets.bg_img, (0, 0))
                else:
                    SCREEN.fill(sky_blue)
                text = big_font.render(f"YOU WIN! Score: {score}", True, white)
                restart_text = font.render("Press R to play again", True, white)
                SCREEN.blit(text, (width//2 - 150, height//2 - 20))
                SCREEN.blit(restart_text, (width//2 - 110, height//2 + 40))

        pygame.display.update()